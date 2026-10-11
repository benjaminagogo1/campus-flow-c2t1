import unittest
import os
import json
from campusflow.tickets import create_ticket

class TestCreateTicket(unittest.TestCase):

    def setUp(self):
        self.test_filename = "tickets.json"
        
        with open(self.test_filename, "w") as file:
            json.dump([], file)

    def tearDown(self):
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)

    def test_ticket_creation_saves_accurately(self):
        
        title = "Database Connection Timeout"
        category = "Software"
        urgency = "high"
        affected_users = 14
        priority = "critical"
        status = "open"
        assigned_to = "Admin"

        create_ticket(title, category, urgency, affected_users, priority, status, assigned_to)

        with open(self.test_filename, "r") as file:
            saved_data = json.load(file)

        self.assertEqual(len(saved_data), 1)

        created_ticket = saved_data[0]

        self.assertEqual(created_ticket["title"], title)
        self.assertEqual(created_ticket["category"], category)
        self.assertEqual(created_ticket["urgency"], urgency)
        self.assertEqual(created_ticket["priority"], priority)
        self.assertEqual(created_ticket["status"], status)
        self.assertEqual(created_ticket["assigned_to"], assigned_to)

        self.assertIsInstance(created_ticket["affected_users"], int)
        self.assertEqual(created_ticket["affected_users"], 14)
        
        self.assertIn("id", created_ticket)
        self.assertTrue(created_ticket["id"].startswith("T"))
