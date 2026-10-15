"""Ticket assignment, status workflow and the Open Work Queue.

Error convention for the whole project: invalid actions raise ValueError and
leave the ticket collection exactly as it was.
"""

from campusflow.validation import validate_staff_name

PRIORITY_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3}

# open -> in_progress -> resolved, and resolved -> open (explicit reopen).
ALLOWED_TRANSITIONS = {
    "open": {"in_progress"},
    "in_progress": {"resolved"},
    "resolved": {"open"},
}


def get_ticket(tickets, ticket_id):
    """Return the ticket whose ID matches (case-insensitive) or raise ValueError."""
    wanted = str(ticket_id).strip().upper()
    for ticket in tickets:
        if str(ticket.get("id", "")).upper() == wanted:
            return ticket
    raise ValueError(f"Ticket '{ticket_id}' was not found.")


def assign_ticket(tickets, ticket_id, staff_name):
    """Assign a ticket to a staff member.

    Rejected (nothing changes) when the name is blank, the ticket does not
    exist, or the ticket is resolved (it must be reopened first).
    """
    staff_name = validate_staff_name(staff_name)
    ticket = get_ticket(tickets, ticket_id)

    if str(ticket.get("status", "open")).lower() == "resolved":
        raise ValueError("Resolved tickets cannot be modified. Reopen the ticket first.")

    ticket["assigned_to"] = staff_name
    return ticket


def check_transition(ticket, new_status):
    """Return the normalised new status, or raise ValueError if not allowed."""
    new_status = str(new_status).strip().lower()
    if new_status not in ALLOWED_TRANSITIONS:
        raise ValueError("Invalid status. Choose open, in_progress or resolved.")

    current = str(ticket.get("status", "open")).lower()
    if new_status not in ALLOWED_TRANSITIONS.get(current, set()):
        raise ValueError(f"Cannot move ticket from {current} to {new_status}.")

    if new_status == "in_progress" and not ticket.get("assigned_to"):
        raise ValueError("Assign the ticket before starting work.")

    return new_status


def can_transition(ticket, new_status):
    """True if the ticket may move to new_status, otherwise False."""
    try:
        check_transition(ticket, new_status)
    except ValueError:
        return False
    return True


def update_status(tickets, ticket_id, new_status):
    """Move a ticket to a new status following the workflow rules."""
    ticket = get_ticket(tickets, ticket_id)
    ticket["status"] = check_transition(ticket, new_status)
    return ticket


def _queue_sort_key(ticket):
    """Sort by priority rank, then by the NUMERIC part of the ID (T9 before T10)."""
    digits = "".join(char for char in str(ticket.get("id", "")) if char.isdigit())
    priority = str(ticket.get("priority", "low")).lower()
    return PRIORITY_RANK.get(priority, len(PRIORITY_RANK)), int(digits or 0)


def get_work_queue(tickets):
    """The Open Work Queue: OPEN tickets only, critical to low, earlier IDs first.

    in_progress and resolved tickets are not part of this queue. The input
    list is never reordered or modified.
    """
    open_tickets = [
        ticket
        for ticket in tickets
        if str(ticket.get("status", "open")).lower() == "open"
    ]
    return sorted(open_tickets, key=_queue_sort_key)