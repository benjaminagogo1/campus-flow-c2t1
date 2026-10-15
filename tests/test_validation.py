import copy
import unittest

from campusflow.generate_id import generate_next_id, next_ticket_id
from campusflow.validation import (
    NOTE_MAX_LENGTH,
    NOTE_MIN_LENGTH,
    validate_affected_users,
    validate_author,
    validate_collection,
    validate_note_message,
    validate_staff_name,
    validate_ticket,
    validate_ticket_id,
)


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


class TestAffectedUsersEdgeCases(unittest.TestCase):
    """Acceptance case 04: 0, negative, float and boolean are all rejected."""

    def test_rejects_every_invalid_kind(self):
        for bad in (0, -1, -100, 2.5, 3.0, True, False, None, "0", "-4", "2.5", "", "  ", "abc", [5]):
            with self.subTest(value=bad):
                with self.assertRaises(ValueError):
                    validate_affected_users(bad)

    def test_unicode_digits_are_rejected(self):
        # "²".isdigit() is True in Python, but it is not a usable whole number.
        with self.assertRaises(ValueError):
            validate_affected_users("²")

    def test_accepts_positive_whole_numbers(self):
        self.assertEqual(validate_affected_users(1), 1)
        self.assertEqual(validate_affected_users(" 007 "), 7)


class TestNoteMessageBoundaries(unittest.TestCase):
    def test_length_boundaries(self):
        self.assertEqual(NOTE_MIN_LENGTH, 5)
        self.assertEqual(NOTE_MAX_LENGTH, 300)
        with self.assertRaises(ValueError):
            validate_note_message("a" * 4)
        self.assertEqual(validate_note_message("a" * 5), "a" * 5)
        self.assertEqual(validate_note_message("a" * 300), "a" * 300)
        with self.assertRaises(ValueError):
            validate_note_message("a" * 301)

    def test_length_is_measured_after_trimming(self):
        with self.assertRaises(ValueError):
            validate_note_message("   abcd   ")
        self.assertEqual(validate_note_message("   abcde   "), "abcde")

    def test_non_text_rejected(self):
        for bad in (None, 12345, ["hello"]):
            with self.subTest(value=bad):
                with self.assertRaises(ValueError):
                    validate_note_message(bad)


class TestSmallValidators(unittest.TestCase):
    def test_blank_author_and_staff_rejected(self):
        for bad in ("", "   ", None, 5):
            with self.subTest(value=bad):
                with self.assertRaises(ValueError):
                    validate_author(bad)
                with self.assertRaises(ValueError):
                    validate_staff_name(bad)

    def test_author_and_staff_are_trimmed(self):
        self.assertEqual(validate_author("  Mentor A "), "Mentor A")
        self.assertEqual(validate_staff_name("  Ada "), "Ada")

    def test_ticket_id_is_normalised_and_checked(self):
        self.assertEqual(validate_ticket_id(" t001 "), "T001")
        for bad in ("", "001", "TICKET1", "T", "T1A", None, 7):
            with self.subTest(value=bad):
                with self.assertRaises(ValueError):
                    validate_ticket_id(bad)


class TestValidateTicket(unittest.TestCase):
    def test_a_valid_ticket_passes(self):
        validate_ticket(make_ticket())

    def test_missing_field_rejected(self):
        for key in ("id", "title", "category", "urgency", "affected_users",
                    "priority", "status", "assigned_to", "notes"):
            with self.subTest(missing=key):
                ticket = make_ticket()
                del ticket[key]
                with self.assertRaises(ValueError):
                    validate_ticket(ticket)

    def test_illegal_values_rejected(self):
        bad_changes = [
            {"id": "BAD"},
            {"id": 5},
            {"title": "   "},
            {"category": "network"},          # must be the canonical spelling
            {"urgency": "urgent"},
            {"affected_users": 0},
            {"affected_users": True},
            {"affected_users": "15"},         # stored data must be a real int
            {"priority": "urgent"},
            {"status": "banana"},
            {"assigned_to": "   "},
            {"notes": "not a list"},
        ]
        for change in bad_changes:
            with self.subTest(change=change):
                with self.assertRaises(ValueError):
                    validate_ticket(make_ticket(**change))

    def test_priority_must_match_the_rules(self):
        # high urgency + 15 users is critical, so "low" is inconsistent.
        with self.assertRaises(ValueError):
            validate_ticket(make_ticket(priority="low"))

    def test_in_progress_ticket_must_be_assigned(self):
        with self.assertRaises(ValueError):
            validate_ticket(make_ticket(status="in_progress", assigned_to=None))
        validate_ticket(make_ticket(status="in_progress", assigned_to="Ada"))

    def test_malformed_notes_rejected(self):
        good = {"note_id": "N001", "author": "Ada", "message": "Checked the router"}
        bad_notes = [
            "text",
            {"note_id": "N001", "author": "Ada"},                          # missing message
            {**good, "extra": 1},                                          # unknown field
            {**good, "note_id": "X1"},
            {**good, "author": " "},
            {**good, "message": "abc"},                                    # too short
        ]
        for bad in bad_notes:
            with self.subTest(note=bad):
                with self.assertRaises(ValueError):
                    validate_ticket(make_ticket(notes=[bad]))

    def test_duplicate_note_ids_within_a_ticket_rejected(self):
        note = {"note_id": "N001", "author": "Ada", "message": "Checked the router"}
        with self.assertRaises(ValueError):
            validate_ticket(make_ticket(notes=[note, dict(note)]))

    def test_same_note_id_on_different_tickets_is_fine(self):
        note = {"note_id": "N001", "author": "Ada", "message": "Checked the router"}
        validate_collection([
            make_ticket("T001", notes=[dict(note)]),
            make_ticket("T002", notes=[dict(note)]),
        ])

    def test_validation_never_modifies_the_ticket(self):
        ticket = make_ticket()
        before = copy.deepcopy(ticket)
        validate_ticket(ticket)
        self.assertEqual(ticket, before)


class TestValidateCollection(unittest.TestCase):
    def test_empty_list_is_valid(self):
        validate_collection([])

    def test_must_be_a_list(self):
        for bad in ({}, "tickets", None, 5):
            with self.subTest(value=bad):
                with self.assertRaises(ValueError):
                    validate_collection(bad)

    def test_duplicate_ticket_ids_rejected(self):
        with self.assertRaises(ValueError):
            validate_collection([make_ticket("T001"), make_ticket("T001")])

    def test_one_bad_record_rejects_everything(self):
        with self.assertRaises(ValueError):
            validate_collection([make_ticket("T001"), make_ticket("T002", status="banana")])

    def test_non_dict_record_rejected(self):
        with self.assertRaises(ValueError):
            validate_collection([make_ticket("T001"), "oops"])


class TestIdGeneration(unittest.TestCase):
    def test_empty_list_starts_at_001(self):
        self.assertEqual(generate_next_id([]), "T001")
        self.assertEqual(next_ticket_id([]), "T001")

    def test_uses_highest_number_not_the_count(self):
        self.assertEqual(next_ticket_id([{"id": "T001"}, {"id": "T009"}]), "T010")

    def test_numeric_not_alphabetical(self):
        # "T9" sorts after "T10" as text, but 10 is the larger number.
        self.assertEqual(next_ticket_id([{"id": "T9"}, {"id": "T10"}]), "T011")

    def test_custom_prefix(self):
        self.assertEqual(generate_next_id([{"id": "N004"}], prefix="N"), "N005")


if __name__ == "__main__":
    unittest.main()