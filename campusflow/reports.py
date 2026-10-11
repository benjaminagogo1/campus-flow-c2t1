STATUSES = ["open", "in_progress", "resolved"]
PRIORITIES = ["critical", "high", "medium", "low"]


def build_report(tickets):
    by_status = {status: 0 for status in STATUSES}
    by_priority = {priority: 0 for priority in PRIORITIES}

    for ticket in tickets:
        status = str(ticket.get("status", "")).lower()
        priority = str(ticket.get("priority", "")).lower()
        if status in by_status:
            by_status[status] += 1
        if priority in by_priority:
            by_priority[priority] += 1

    return {
        "total": len(tickets),
        "by_status": by_status,
        "by_priority": by_priority,
    }


def format_report(report):
    lines = [f"Total tickets: {report['total']}", "By status:"]
    for status, count in report["by_status"].items():
        lines.append(f"  {status}: {count}")
    lines.append("By priority:")
    for priority, count in report["by_priority"].items():
        lines.append(f"  {priority}: {count}")
    return "\n".join(lines)