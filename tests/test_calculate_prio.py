import unittest

from campusflow.calculate_prio import calculate_priority


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

    # --- Rule precedence and boundaries (acceptance case 01) ---------------

    def test_high_urgency_just_below_ten_users_is_high_not_critical(self):
        self.assertEqual(calculate_priority("high", 9), "high")

    def test_ten_users_with_low_urgency_is_high_not_critical(self):
        self.assertEqual(calculate_priority("low", 10), "high")
        self.assertEqual(calculate_priority("low", 12), "high")

    def test_medium_urgency_with_ten_users_is_high_not_medium(self):
        self.assertEqual(calculate_priority("medium", 10), "high")

    def test_three_users_is_the_medium_boundary(self):
        self.assertEqual(calculate_priority("low", 2), "low")
        self.assertEqual(calculate_priority("low", 3), "medium")


if __name__ == "__main__":
    unittest.main()