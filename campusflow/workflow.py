PRIORITY_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3}

# open -> in_progress -> resolved, and resolved -> open is the explicit reopen.
ALLOWED_TRANSITIONS = {
    "open": {"in_progress"},
    "in_progress": {"resolved"},
    "resolved": {"open"},
}


def get_ticket(tickets, ticket_id):
    wanted = str(ticket_id).strip().upper()
    for ticket in tickets:
        if str(ticket.get("id", "")).upper() == wanted:
            return ticket
    raise ValueError(f"Ticket '{ticket_id}' was not found.")


def assign_ticket(tickets, ticket_id, staff_name):
    if not isinstance(staff_name, str) or not staff_name.strip():
        raise ValueError("Staff name cannot be empty.")

    ticket = get_ticket(tickets, ticket_id)

    if str(ticket.get("status", "open")).lower() == "resolved":
        raise ValueError("Resolved tickets cannot be modified. Reopen the ticket first.")

    ticket["assigned_to"] = staff_name.strip()
    return ticket


def update_status(tickets, ticket_id, new_status):
    new_status = str(new_status).strip().lower()
    if new_status not in ALLOWED_TRANSITIONS:
        raise ValueError("Invalid status. Choose open, in_progress or resolved.")

    ticket = get_ticket(tickets, ticket_id)
    current = str(ticket.get("status", "open")).lower()

    if new_status not in ALLOWED_TRANSITIONS.get(current, set()):
        raise ValueError(f"Cannot move ticket from {current} to {new_status}.")

    if new_status == "in_progress" and not ticket.get("assigned_to"):
        raise ValueError("Assign the ticket before starting work.")

    ticket["status"] = new_status
    return ticket


def _queue_sort_key(ticket):
    digits = "".join(char for char in str(ticket.get("id", "")) if char.isdigit())
    priority = str(ticket.get("priority", "low")).lower()
    return PRIORITY_RANK.get(priority, len(PRIORITY_RANK)), int(digits or 0)


def get_work_queue(tickets):
    unresolved = [
        ticket
        for ticket in tickets
        if str(ticket.get("status", "open")).lower() != "resolved"
    ]
    return sorted(unresolved, key=_queue_sort_key)