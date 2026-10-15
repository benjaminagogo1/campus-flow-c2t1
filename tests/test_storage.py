import copy
import json
import tempfile
import unittest
from pathlib import Path

from campusflow.generate_id import generate_next_id
from campusflow.notes import add_note, next_note_id
from campusflow.storage import (
    StorageError,
    load_tickets,
    reload_tickets,
    save_tickets,
    upgrade_legacy_ticket,
)
from campusflow.tickets import create_ticket


def make_ticket(ticket_id="T001", **overrides):
    ticket = {
        "id": ticket_id,
        "title": "Wi-Fi down in Library",
        "category": "Network",
        "urgency": "high",
        "affected_users": 15,
        "priority": "critical",
        "status": "open",
        "assigned_to": None,
        "notes": [],
    }
    ticket.update(overrides)
    return ticket


class StorageTestCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.file = Path(self.temp.name) / "tickets.json"

    def tearDown(self):
        self.temp.cleanup()

    def write_raw(self, text):
        self.file.write_text(text, encoding="utf-8")

    def write_json(self, data):
        self.write_raw(json.dumps(data))


class TestSaveAndLoad(StorageTestCase):
    def test_missing_file_gives_empty_list(self):
        self.assertEqual(load_tickets(self.file), [])

    def test_empty_file_gives_empty_list(self):
        self.write_raw("   \n")
        self.assertEqual(load_tickets(self.file), [])

    def test_round_trip_preserves_every_field_including_notes(self):
        tickets = []
        create_ticket(tickets, "Wi-Fi down", "network", "high", 15)
        create_ticket(tickets, "Broken laptop", "hardware", "low", 1)
        tickets[0]["assigned_to"] = "Ada"
        add_note(tickets, "T001", "Mentor A", "Wi-Fi router reboot attempted")
        add_note(tickets, "T001", "Mentor B", "Investigating switch ports")

        save_tickets(tickets, self.file)
        self.assertEqual(load_tickets(self.file), tickets)

    def test_next_ids_continue_after_reload(self):
        tickets = []
        create_ticket(tickets, "First", "Other", "low", 1)
        create_ticket(tickets, "Second", "Other", "low", 1)
        add_note(tickets, "T002", "Mentor A", "First note here")
        add_note(tickets, "T002", "Mentor A", "Second note here")
        save_tickets(tickets, self.file)

        loaded = load_tickets(self.file)
        self.assertEqual(generate_next_id(loaded), "T003")
        self.assertEqual(next_note_id(loaded[1]), "N003")
        self.assertEqual(next_note_id(loaded[0]), "N001")

        new_ticket = create_ticket(loaded, "Third", "Other", "low", 1)
        self.assertEqual(new_ticket["id"], "T003")

    def test_save_creates_missing_folder(self):
        nested = Path(self.temp.name) / "a" / "b" / "tickets.json"
        save_tickets([make_ticket()], nested)
        self.assertTrue(nested.exists())

    def test_no_temporary_file_is_left_behind(self):
        save_tickets([make_ticket()], self.file)
        leftovers = [p.name for p in Path(self.temp.name).iterdir()]
        self.assertEqual(leftovers, ["tickets.json"])

    def test_saved_file_is_a_plain_json_list(self):
        save_tickets([make_ticket()], self.file)
        data = json.loads(self.file.read_text(encoding="utf-8"))
        self.assertIsInstance(data, list)
        self.assertEqual(data[0]["notes"], [])


class TestRejectedFiles(StorageTestCase):
    """Acceptance case 13: bad files are rejected and nothing is lost."""

    def test_invalid_json_rejected(self):
        self.write_raw("{ this is not json")
        with self.assertRaises(StorageError):
            load_tickets(self.file)

    def test_non_list_json_rejected(self):
        self.write_json({"id": "T001"})
        with self.assertRaises(StorageError):
            load_tickets(self.file)

    def test_duplicate_ticket_ids_rejected(self):
        self.write_json([make_ticket("T001"), make_ticket("T001", title="Another one")])
        with self.assertRaises(StorageError) as context:
            load_tickets(self.file)
        self.assertIn("Duplicate", str(context.exception))

    def test_missing_field_rejected(self):
        broken = make_ticket()
        del broken["priority"]
        self.write_json([broken])
        with self.assertRaises(StorageError):
            load_tickets(self.file)

    def test_inconsistent_priority_rejected(self):
        self.write_json([make_ticket(priority="low")])
        with self.assertRaises(StorageError):
            load_tickets(self.file)

    def test_illegal_status_rejected(self):
        self.write_json([make_ticket(status="banana")])
        with self.assertRaises(StorageError):
            load_tickets(self.file)

    def test_in_progress_without_assignee_rejected(self):
        self.write_json([make_ticket(status="in_progress", assigned_to=None)])
        with self.assertRaises(StorageError):
            load_tickets(self.file)

    def test_malformed_note_rejected(self):
        bad_note = {"note_id": "N001", "author": "Ada", "message": "no"}
        self.write_json([make_ticket(notes=[bad_note])])
        with self.assertRaises(StorageError):
            load_tickets(self.file)

    def test_duplicate_note_ids_rejected(self):
        note = {"note_id": "N001", "author": "Ada", "message": "Checked the router"}
        self.write_json([make_ticket(notes=[note, dict(note)])])
        with self.assertRaises(StorageError):
            load_tickets(self.file)

    def test_one_bad_record_rejects_the_whole_file(self):
        self.write_json([make_ticket("T001"), make_ticket("T002", status="banana")])
        with self.assertRaises(StorageError):
            load_tickets(self.file)

    def test_a_rejected_load_does_not_modify_the_file(self):
        original = "{ this is not json"
        self.write_raw(original)
        with self.assertRaises(StorageError):
            load_tickets(self.file)
        self.assertEqual(self.file.read_text(encoding="utf-8"), original)


class TestReloadKeepsMemory(StorageTestCase):
    def test_failed_reload_leaves_memory_exactly_as_it_was(self):
        memory = [make_ticket("T001"), make_ticket("T002")]
        add_note(memory, "T001", "Mentor A", "Rebooted the router")
        before = copy.deepcopy(memory)

        self.write_json([make_ticket("T005"), make_ticket("T005")])    # duplicate IDs
        with self.assertRaises(StorageError):
            reload_tickets(memory, self.file)
        self.assertEqual(memory, before)

        self.write_raw("[[[ corrupt")
        with self.assertRaises(StorageError):
            reload_tickets(memory, self.file)
        self.assertEqual(memory, before)

    def test_successful_reload_replaces_memory_in_place(self):
        memory = [make_ticket("T001")]
        same_list_object = memory
        self.write_json([make_ticket("T007"), make_ticket("T008")])
        reload_tickets(memory, self.file)
        self.assertIs(memory, same_list_object)
        self.assertEqual([t["id"] for t in memory], ["T007", "T008"])


class TestSaveRefusesBadData(StorageTestCase):
    def test_invalid_tickets_are_not_written(self):
        save_tickets([make_ticket("T001")], self.file)
        before = self.file.read_text(encoding="utf-8")

        with self.assertRaises(StorageError):
            save_tickets([make_ticket("T001"), make_ticket("T001")], self.file)   # duplicates
        with self.assertRaises(StorageError):
            save_tickets([make_ticket(status="banana")], self.file)

        self.assertEqual(self.file.read_text(encoding="utf-8"), before)
        self.assertEqual([p.name for p in Path(self.temp.name).iterdir()], ["tickets.json"])


class TestLegacyMigration(StorageTestCase):
    """Old version-1 tickets (no notes field) must still load."""

    LEGACY = {
        "id": "T001",
        "title": "Blocked Drainage",
        "category": "other",
        "urgency": "high",
        "affected_users": 16,
        "priority": "critical",
        "status": "open",
        "assigned_to": "none",
    }

    def test_the_original_sample_ticket_loads_and_is_upgraded(self):
        self.write_json([self.LEGACY])
        (ticket,) = load_tickets(self.file)
        self.assertEqual(ticket["notes"], [])
        self.assertEqual(ticket["category"], "Other")
        self.assertIsNone(ticket["assigned_to"])
        self.assertEqual(ticket["title"], "Blocked Drainage")
        self.assertEqual(ticket["priority"], "critical")

    def test_loading_does_not_rewrite_the_legacy_file(self):
        self.write_json([self.LEGACY])
        before = self.file.read_text(encoding="utf-8")
        load_tickets(self.file)
        self.assertEqual(self.file.read_text(encoding="utf-8"), before)

    def test_upgraded_legacy_ticket_cannot_start_work_until_assigned(self):
        from campusflow.workflow import update_status

        self.write_json([self.LEGACY])
        tickets = load_tickets(self.file)
        with self.assertRaises(ValueError):
            update_status(tickets, "T001", "in_progress")

    def test_upgrade_does_not_mutate_its_input(self):
        original = copy.deepcopy(self.LEGACY)
        upgrade_legacy_ticket(self.LEGACY)
        self.assertEqual(self.LEGACY, original)

    def test_current_format_tickets_are_checked_strictly_not_upgraded(self):
        # Has a notes field, so it is NOT treated as legacy: lowercase category is invalid.
        self.write_json([make_ticket(category="network")])
        with self.assertRaises(StorageError):
            load_tickets(self.file)

    def test_a_legacy_ticket_with_a_wrong_priority_is_still_rejected(self):
        bad = dict(self.LEGACY, priority="low")
        self.write_json([bad])
        with self.assertRaises(StorageError):
            load_tickets(self.file)


if __name__ == "__main__":
    unittest.main()