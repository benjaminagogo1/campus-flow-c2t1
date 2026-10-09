import json
import tempfile
import unittest
from pathlib import Path

from campusflow.ticket_views import list_tickets, view_ticket


class TestTicketViews(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.file = Path(self.temp.name) / "tickets.json"
        self.tickets = [
            {"Id": "T001", "Title": "WiFi issue", "Status": "open"},
            {"Id": "T002", "Title": "Broken laptop", "Status": "resolved"},
        ]
        self.file.write_text(json.dumps(self.tickets), encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_list_all_tickets(self):
        self.assertEqual(list_tickets(self.file), self.tickets)

    def test_list_empty_tickets(self):
        self.file.write_text("[]", encoding="utf-8")
        self.assertEqual(list_tickets(self.file), [])

    def test_view_ticket_by_id(self):
        self.assertEqual(view_ticket("T001", self.file), self.tickets[0])

    def test_ticket_id_case_insensitive(self):
        self.assertEqual(view_ticket("t001", self.file), self.tickets[0])

    def test_missing_ticket_returns_none(self):
        self.assertIsNone(view_ticket("T999", self.file))


if __name__ == "__main__":
    unittest.main()
