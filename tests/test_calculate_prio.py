import unittest
from campusflow.calcualate_prio import calculate_priority

class TestCalculatePriority(unittest.TestCase):
    
    def test_rule_1_critical(self):
        self.assertEqual(calculate_priority("high", 12), "critical")
        self.assertEqual(calculate_priority("high", 10), "critical")

    def test_rule_2_high(self):
        self.assertEqual(calculate_priority("high", 5), "high")
        self.assertEqual(calculate_priority("low", 10), "high")

    def test_rule_3_medium(self):
        self.assertEqual(calculate_priority("medium", 2), "medium")
        self.assertEqual(calculate_priority("low", 3), "medium")

    def test_rule_4_low(self):
        self.assertEqual(calculate_priority("low", 1), "low")
