import unittest

from campusflow.reports import build_report, format_report


def make_ticket(priority, status):
    return {"priority": priority, "status": status}


class TestBuildReport(unittest.TestCase):
    def test_empty_report_has_all_keys_with_zero_counts(self):
        report = build_report([])
        self.assertEqual(report["total"], 0)
        self.assertEqual(
            report["by_status"],
            {"open": 0, "in_progress": 0, "resolved": 0},
        )
        self.assertEqual(
            report["by_priority"],
            {"critical": 0, "high": 0, "medium": 0, "low": 0},
        )

    def test_mixed_tickets_are_counted_correctly(self):
        tickets = [
            make_ticket("critical", "open"),
            make_ticket("medium", "open"),
            make_ticket("medium", "in_progress"),
        ]
        report = build_report(tickets)
        self.assertEqual(report["total"], 3)
        self.assertEqual(
            report["by_status"],
            {"open": 2, "in_progress": 1, "resolved": 0},
        )
        self.assertEqual(
            report["by_priority"],
            {"critical": 1, "high": 0, "medium": 2, "low": 0},
        )

    def test_categories_with_no_tickets_still_appear_as_zero(self):
        report = build_report([make_ticket("high", "resolved")])
        self.assertEqual(report["by_priority"]["low"], 0)
        self.assertEqual(report["by_priority"]["critical"], 0)
        self.assertEqual(report["by_status"]["open"], 0)
        self.assertEqual(report["by_status"]["resolved"], 1)

    def test_values_are_case_insensitive(self):
        report = build_report([make_ticket("HIGH", "OPEN")])
        self.assertEqual(report["by_priority"]["high"], 1)
        self.assertEqual(report["by_status"]["open"], 1)

    def test_unknown_values_count_in_total_but_not_in_breakdowns(self):
        report = build_report([make_ticket("urgent!!", "banana")])
        self.assertEqual(report["total"], 1)
        self.assertEqual(sum(report["by_status"].values()), 0)
        self.assertEqual(sum(report["by_priority"].values()), 0)

    def test_ticket_with_missing_fields_does_not_crash(self):
        report = build_report([{}])
        self.assertEqual(report["total"], 1)
        self.assertEqual(sum(report["by_status"].values()), 0)

    def test_all_resolved_tickets(self):
        tickets = [make_ticket("low", "resolved") for _ in range(4)]
        report = build_report(tickets)
        self.assertEqual(report["total"], 4)
        self.assertEqual(report["by_status"]["resolved"], 4)
        self.assertEqual(report["by_priority"]["low"], 4)

    def test_build_report_does_not_modify_input(self):
        tickets = [make_ticket("high", "open")]
        snapshot = [dict(t) for t in tickets]
        build_report(tickets)
        self.assertEqual(tickets, snapshot)


class TestFormatReport(unittest.TestCase):
    def test_format_empty_report(self):
        text = format_report(build_report([]))
        self.assertIn("Total tickets: 0", text)
        self.assertIn("open: 0", text)
        self.assertIn("critical: 0", text)

    def test_format_shows_counts(self):
        tickets = [
            make_ticket("critical", "open"),
            make_ticket("critical", "in_progress"),
        ]
        text = format_report(build_report(tickets))
        self.assertIn("Total tickets: 2", text)
        self.assertIn("critical: 2", text)
        self.assertIn("in_progress: 1", text)


if __name__ == "__main__":
    unittest.main()