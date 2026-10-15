import copy
import unittest

from campusflow.notes import add_note, get_notes, next_note_id
from campusflow.workflow import assign_ticket, update_status


def make_ticket(ticket_id="T001", status="open", assigned_to=None, notes=None):
    return {
        "id": ticket_id,
        "title": f"Ticket {ticket_id}",
        "category": "Network",
        "urgency": "low",
        "affected_users": 1,
        "priority": "low",
        "status": status,
        "assigned_to": assigned_to,
        "notes": notes if notes is not None else [],
    }


def make_note(note_id, message="Checked the router"):
    return {"note_id": note_id, "author": "Ada", "message": message}


class TestAddNote(unittest.TestCase):
    def test_valid_note_on_open_ticket_gets_first_id(self):
        tickets = [make_ticket()]
        note = add_note(tickets, "T001", "Mentor A", "Wi-Fi router reboot attempted")
        self.assertEqual(
            note,
            {"note_id": "N001", "author": "Mentor A", "message": "Wi-Fi router reboot attempted"},
        )
        self.assertEqual(tickets[0]["notes"], [note])

    def test_second_note_gets_next_id(self):
        tickets = [make_ticket()]
        add_note(tickets, "T001", "Mentor A", "Wi-Fi router reboot attempted")
        second = add_note(tickets, "T001", "Mentor B", "Investigating switch ports")
        self.assertEqual(second["note_id"], "N002")
        self.assertEqual(len(tickets[0]["notes"]), 2)

    def test_author_and_message_are_trimmed(self):
        tickets = [make_ticket()]
        note = add_note(tickets, "T001", "  Mentor A  ", "   Rebooted the router   ")
        self.assertEqual(note["author"], "Mentor A")
        self.assertEqual(note["message"], "Rebooted the router")

    def test_note_allowed_on_in_progress_ticket(self):
        tickets = [make_ticket(status="in_progress", assigned_to="Ada")]
        note = add_note(tickets, "T001", "Mentor A", "Replacing the switch")
        self.assertEqual(note["note_id"], "N001")

    def test_ticket_id_is_case_insensitive(self):
        tickets = [make_ticket()]
        add_note(tickets, "t001", "Mentor A", "Rebooted the router")
        self.assertEqual(len(tickets[0]["notes"]), 1)

    def test_unknown_ticket_rejected(self):
        tickets = [make_ticket()]
        with self.assertRaises(ValueError):
            add_note(tickets, "T999", "Mentor A", "Rebooted the router")

    def test_every_ticket_numbers_its_own_notes_from_n001(self):
        tickets = [make_ticket("T001"), make_ticket("T002")]
        add_note(tickets, "T001", "Mentor A", "Rebooted the router")
        first_on_t002 = add_note(tickets, "T002", "Mentor A", "Checked the cable")
        self.assertEqual(first_on_t002["note_id"], "N001")


class TestRejectedNotes(unittest.TestCase):
    def test_blank_author_rejected(self):
        tickets = [make_ticket()]
        for bad in ("", "   ", None):
            with self.subTest(author=bad):
                with self.assertRaises(ValueError):
                    add_note(tickets, "T001", bad, "Rebooted the router")
        self.assertEqual(tickets[0]["notes"], [])

    def test_too_short_message_rejected(self):
        tickets = [make_ticket()]
        for bad in ("", "    ", "abcd", "  abcd  "):
            with self.subTest(message=bad):
                with self.assertRaises(ValueError):
                    add_note(tickets, "T001", "Mentor A", bad)
        self.assertEqual(tickets[0]["notes"], [])

    def test_too_long_message_rejected(self):
        tickets = [make_ticket()]
        with self.assertRaises(ValueError):
            add_note(tickets, "T001", "Mentor A", "x" * 301)
        self.assertEqual(tickets[0]["notes"], [])

    def test_message_at_the_limits_is_accepted(self):
        tickets = [make_ticket()]
        add_note(tickets, "T001", "Mentor A", "x" * 5)
        add_note(tickets, "T001", "Mentor A", "x" * 300)
        self.assertEqual([n["note_id"] for n in tickets[0]["notes"]], ["N001", "N002"])

    def test_rejected_note_does_not_consume_an_id(self):
        tickets = [make_ticket()]
        add_note(tickets, "T001", "Mentor A", "Rebooted the router")      # N001
        with self.assertRaises(ValueError):
            add_note(tickets, "T001", "Mentor A", "no")                   # rejected
        with self.assertRaises(ValueError):
            add_note(tickets, "T001", "  ", "Long enough message")        # rejected
        next_note = add_note(tickets, "T001", "Mentor A", "Checked the cable")
        self.assertEqual(next_note["note_id"], "N002")

    def test_rejected_note_leaves_whole_collection_unchanged(self):
        tickets = [
            make_ticket("T001", notes=[make_note("N001")]),
            make_ticket("T002", status="resolved", assigned_to="Ada"),
        ]
        before = copy.deepcopy(tickets)
        with self.assertRaises(ValueError):
            add_note(tickets, "T001", "Mentor A", "no")
        with self.assertRaises(ValueError):
            add_note(tickets, "T002", "Mentor A", "A perfectly fine message")
        self.assertEqual(tickets, before)


class TestNotesAndWorkflow(unittest.TestCase):
    """Acceptance case 07 and the example from the sprint guide."""

    def test_note_on_resolved_ticket_rejected(self):
        tickets = [make_ticket(status="resolved", assigned_to="Ada")]
        with self.assertRaises(ValueError):
            add_note(tickets, "T001", "Mentor A", "A perfectly fine message")
        self.assertEqual(tickets[0]["notes"], [])

    def test_full_sprint_example(self):
        tickets = [make_ticket()]
        assign_ticket(tickets, "T001", "Ada")
        update_status(tickets, "T001", "in_progress")

        self.assertEqual(
            add_note(tickets, "T001", "Mentor A", "Wi-Fi router reboot attempted")["note_id"],
            "N001",
        )
        self.assertEqual(
            add_note(tickets, "T001", "Mentor B", "Investigating switch ports")["note_id"],
            "N002",
        )

        update_status(tickets, "T001", "resolved")
        with self.assertRaises(ValueError):
            add_note(tickets, "T001", "Mentor A", "Trying to add after resolve")
        self.assertEqual(len(tickets[0]["notes"]), 2)       # earlier notes retained

        update_status(tickets, "T001", "open")              # reopen
        third = add_note(tickets, "T001", "Mentor A", "Back to investigate")
        self.assertEqual(third["note_id"], "N003")          # the rejected attempt used no ID
        self.assertEqual([n["note_id"] for n in tickets[0]["notes"]], ["N001", "N002", "N003"])

    def test_notes_survive_resolve_and_reopen(self):
        tickets = [make_ticket(status="in_progress", assigned_to="Ada",
                               notes=[make_note("N001")])]
        before = copy.deepcopy(tickets[0]["notes"])
        update_status(tickets, "T001", "resolved")
        update_status(tickets, "T001", "open")
        self.assertEqual(tickets[0]["notes"], before)


class TestNextNoteId(unittest.TestCase):
    def test_empty_ticket_starts_at_n001(self):
        self.assertEqual(next_note_id(make_ticket()), "N001")

    def test_uses_highest_number_not_the_count(self):
        ticket = make_ticket(notes=[make_note("N001"), make_note("N005")])
        self.assertEqual(next_note_id(ticket), "N006")

    def test_rolls_over_to_four_digits_correctly(self):
        ticket = make_ticket(notes=[make_note("N009")])
        self.assertEqual(next_note_id(ticket), "N010")

    def test_ticket_without_a_notes_key_does_not_crash(self):
        self.assertEqual(next_note_id({"id": "T001"}), "N001")


class TestGetNotes(unittest.TestCase):
    def test_notes_are_returned_in_numeric_id_order(self):
        ticket = make_ticket(notes=[make_note("N010"), make_note("N002"), make_note("N001")])
        ids = [n["note_id"] for n in get_notes([ticket], "T001")]
        self.assertEqual(ids, ["N001", "N002", "N010"])

    def test_ticket_with_no_notes_gives_empty_list(self):
        self.assertEqual(get_notes([make_ticket()], "T001"), [])

    def test_unknown_ticket_rejected(self):
        with self.assertRaises(ValueError):
            get_notes([make_ticket()], "T999")

    def test_viewing_notes_does_not_change_the_ticket(self):
        tickets = [make_ticket(notes=[make_note("N002"), make_note("N001")])]
        before = copy.deepcopy(tickets)
        result = get_notes(tickets, "T001")
        result[0]["message"] = "edited the copy"
        self.assertEqual(tickets, before)


if __name__ == "__main__":
    unittest.main()