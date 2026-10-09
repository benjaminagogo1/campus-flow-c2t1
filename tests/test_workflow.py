import json
import tempfile
import unittest
from pathlib import Path

from campusflow.workflow import assign_ticket, update_status, get_work_queue


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file = str(Path(self.temp_dir.name) / "tickets.json")
        self.tickets = [
            {"Id": "T002", "Priority": "low", "Status": "open", "Assigned_to": None},
            {"Id": "T001", "Priority": "critical", "Status": "open", "Assigned_to": None},
            {"Id": "T003", "Priority": "high", "Status": "in_progress", "Assigned_to": "Sam"},
            {"Id": "T004", "Priority": "medium", "Status": "resolved", "Assigned_to": "Jo"},
        ]
        self.save()

    def tearDown(self):
        self.temp_dir.cleanup()

    def save(self):
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(self.tickets, f)

    def load(self):
        with open(self.file, encoding="utf-8") as f:
            return json.load(f)

    def test_assign_ticket(self):
        ticket = assign_ticket("T002", " Alex ", self.file)
        self.assertEqual(ticket["Assigned_to"], "Alex")
        self.assertEqual(self.load()[0]["Assigned_to"], "Alex")

    def test_reject_blank_staff_name(self):
        with self.assertRaises(ValueError):
            assign_ticket("T002", "   ", self.file)

    def test_reject_unknown_ticket(self):
        with self.assertRaises(ValueError):
            assign_ticket("T999", "Alex", self.file)

    def test_cannot_start_unassigned_ticket(self):
        with self.assertRaises(ValueError):
            update_status("T002", "in_progress", self.file)

    def test_assigned_ticket_can_start(self):
        assign_ticket("T002", "Alex", self.file)
        update_status("T002", "in_progress", self.file)
        self.assertEqual(self.load()[0]["Status"], "in_progress")

    def test_ticket_can_be_resolved(self):
        update_status("T003", "resolved", self.file)
        self.assertEqual(self.load()[2]["Status"], "resolved")

    def test_reject_invalid_transition(self):
        with self.assertRaises(ValueError):
            update_status("T004", "in_progress", self.file)

    def test_queue_priority_then_numeric_id(self):
        self.assertEqual(
            [t["Id"] for t in get_work_queue(self.file)],
            ["T001", "T003", "T002"],
        )


if __name__ == "__main__":
    unittest.main()
