import copy
import unittest

from campusflow.workflow import (
    assign_ticket,
    can_transition,
    get_work_queue,
    update_status,
)


def make_ticket(ticket_id, priority="low", status="open", assigned_to=None):
    return {
        "id": ticket_id,
        "title": f"Ticket {ticket_id}",
        "priority": priority,
        "status": status,
        "assigned_to": assigned_to,
    }


class TestAssignTicket(unittest.TestCase):
    def test_assigns_and_strips_name(self):
        tickets = [make_ticket("T001")]
        ticket = assign_ticket(tickets, "T001", "  Ada  ")
        self.assertEqual(ticket["assigned_to"], "Ada")
        self.assertEqual(tickets[0]["assigned_to"], "Ada")

    def test_ticket_id_is_case_insensitive(self):
        tickets = [make_ticket("T001")]
        assign_ticket(tickets, "t001", "Ada")
        self.assertEqual(tickets[0]["assigned_to"], "Ada")

    def test_empty_name_rejected(self):
        tickets = [make_ticket("T001")]
        with self.assertRaises(ValueError):
            assign_ticket(tickets, "T001", "   ")
        self.assertIsNone(tickets[0]["assigned_to"])

    def test_unknown_ticket_rejected(self):
        with self.assertRaises(ValueError):
            assign_ticket([make_ticket("T001")], "T999", "Ada")

    def test_resolved_ticket_cannot_be_assigned(self):
        tickets = [make_ticket("T001", status="resolved", assigned_to="Ada")]
        with self.assertRaises(ValueError):
            assign_ticket(tickets, "T001", "Bola")
        self.assertEqual(tickets[0]["assigned_to"], "Ada")

    def test_rejected_assignment_leaves_whole_collection_unchanged(self):
        tickets = [
            make_ticket("T001", status="resolved", assigned_to="Ada"),
            make_ticket("T002"),
        ]
        before = copy.deepcopy(tickets)
        with self.assertRaises(ValueError):
            assign_ticket(tickets, "T001", "Bola")
        with self.assertRaises(ValueError):
            assign_ticket(tickets, "T002", "   ")
        self.assertEqual(tickets, before)


class TestUpdateStatus(unittest.TestCase):
    def test_unassigned_ticket_cannot_start_work(self):
        tickets = [make_ticket("T001")]
        with self.assertRaises(ValueError):
            update_status(tickets, "T001", "in_progress")
        self.assertEqual(tickets[0]["status"], "open")

    def test_unassigned_rejection_leaves_whole_collection_unchanged(self):
        tickets = [make_ticket("T001"), make_ticket("T002", assigned_to="Ada")]
        before = copy.deepcopy(tickets)
        with self.assertRaises(ValueError):
            update_status(tickets, "T001", "in_progress")
        self.assertEqual(tickets, before)

    def test_assigned_ticket_progresses_to_resolved(self):
        tickets = [make_ticket("T001", assigned_to="Ada")]
        update_status(tickets, "T001", "in_progress")
        self.assertEqual(tickets[0]["status"], "in_progress")
        update_status(tickets, "T001", "resolved")
        self.assertEqual(tickets[0]["status"], "resolved")

    def test_cannot_skip_in_progress(self):
        tickets = [make_ticket("T001", assigned_to="Ada")]
        with self.assertRaises(ValueError):
            update_status(tickets, "T001", "resolved")
        self.assertEqual(tickets[0]["status"], "open")

    def test_invalid_status_rejected(self):
        tickets = [make_ticket("T001", assigned_to="Ada")]
        with self.assertRaises(ValueError):
            update_status(tickets, "T001", "banana")
        self.assertEqual(tickets[0]["status"], "open")

    def test_unknown_ticket_rejected(self):
        with self.assertRaises(ValueError):
            update_status([make_ticket("T001")], "T999", "in_progress")

    def test_status_input_is_normalized(self):
        tickets = [make_ticket("T001", assigned_to="Ada")]
        update_status(tickets, "T001", "  IN_PROGRESS ")
        self.assertEqual(tickets[0]["status"], "in_progress")

    def test_resolved_ticket_can_be_reopened(self):
        tickets = [make_ticket("T001", status="resolved", assigned_to="Ada")]
        update_status(tickets, "T001", "open")
        self.assertEqual(tickets[0]["status"], "open")

    def test_reopened_ticket_can_be_assigned_again(self):
        tickets = [make_ticket("T001", status="resolved", assigned_to="Ada")]
        update_status(tickets, "T001", "open")
        assign_ticket(tickets, "T001", "Bola")
        self.assertEqual(tickets[0]["assigned_to"], "Bola")

    def test_open_ticket_cannot_be_reopened(self):
        tickets = [make_ticket("T001")]
        with self.assertRaises(ValueError):
            update_status(tickets, "T001", "open")

    def test_in_progress_cannot_move_back_to_open(self):
        tickets = [make_ticket("T001", status="in_progress", assigned_to="Ada")]
        with self.assertRaises(ValueError):
            update_status(tickets, "T001", "open")
        self.assertEqual(tickets[0]["status"], "in_progress")


class TestCanTransition(unittest.TestCase):
    def test_unassigned_open_ticket_cannot_start(self):
        self.assertFalse(can_transition(make_ticket("T001"), "in_progress"))

    def test_assigned_open_ticket_can_start(self):
        self.assertTrue(can_transition(make_ticket("T001", assigned_to="Ada"), "in_progress"))

    def test_resolved_ticket_can_reopen(self):
        ticket = make_ticket("T001", status="resolved", assigned_to="Ada")
        self.assertTrue(can_transition(ticket, "open"))

    def test_open_ticket_cannot_jump_to_resolved(self):
        self.assertFalse(can_transition(make_ticket("T001", assigned_to="Ada"), "resolved"))

    def test_invalid_status_is_false_not_an_exception(self):
        self.assertFalse(can_transition(make_ticket("T001"), "banana"))

    def test_can_transition_never_changes_the_ticket(self):
        ticket = make_ticket("T001", assigned_to="Ada")
        before = copy.deepcopy(ticket)
        can_transition(ticket, "in_progress")
        self.assertEqual(ticket, before)


class TestGetWorkQueue(unittest.TestCase):
    def test_sorted_by_priority(self):
        tickets = [
            make_ticket("T001", "low"),
            make_ticket("T002", "critical"),
            make_ticket("T003", "medium"),
            make_ticket("T004", "high"),
        ]
        ids = [t["id"] for t in get_work_queue(tickets)]
        self.assertEqual(ids, ["T002", "T004", "T003", "T001"])

    def test_ties_broken_by_earlier_numeric_id(self):
        tickets = [
            make_ticket("T003", "high"),
            make_ticket("T001", "high"),
            make_ticket("T002", "high"),
        ]
        ids = [t["id"] for t in get_work_queue(tickets)]
        self.assertEqual(ids, ["T001", "T002", "T003"])

    def test_tie_break_is_numeric_not_alphabetical(self):
        tickets = [make_ticket("T10", "high"), make_ticket("T9", "high")]
        ids = [t["id"] for t in get_work_queue(tickets)]
        self.assertEqual(ids, ["T9", "T10"])

    def test_resolved_tickets_are_excluded(self):
        tickets = [
            make_ticket("T001", "critical", status="resolved"),
            make_ticket("T002", "low"),
        ]
        ids = [t["id"] for t in get_work_queue(tickets)]
        self.assertEqual(ids, ["T002"])

    def test_in_progress_tickets_are_excluded(self):
        # The Open Work Queue shows OPEN tickets only.
        tickets = [
            make_ticket("T001", "high", status="in_progress", assigned_to="Ada"),
            make_ticket("T002", "low"),
        ]
        ids = [t["id"] for t in get_work_queue(tickets)]
        self.assertEqual(ids, ["T002"])

    def test_queue_with_only_in_progress_and_resolved_is_empty(self):
        tickets = [
            make_ticket("T001", "high", status="in_progress", assigned_to="Ada"),
            make_ticket("T002", "low", status="resolved", assigned_to="Ada"),
        ]
        self.assertEqual(get_work_queue(tickets), [])

    def test_reopened_ticket_returns_to_the_queue(self):
        tickets = [make_ticket("T001", "high", status="resolved", assigned_to="Ada")]
        self.assertEqual(get_work_queue(tickets), [])
        update_status(tickets, "T001", "open")
        self.assertEqual([t["id"] for t in get_work_queue(tickets)], ["T001"])

    def test_empty_list_gives_empty_queue(self):
        self.assertEqual(get_work_queue([]), [])

    def test_queue_does_not_reorder_the_original_list(self):
        tickets = [make_ticket("T001", "low"), make_ticket("T002", "critical")]
        get_work_queue(tickets)
        self.assertEqual([t["id"] for t in tickets], ["T001", "T002"])


if __name__ == "__main__":
    unittest.main()