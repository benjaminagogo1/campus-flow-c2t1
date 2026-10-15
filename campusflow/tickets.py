"""Ticket creation.

The validators now live in campusflow.validation. They are re-exported here so
existing imports such as `from campusflow.tickets import validate_title` keep
working.
"""

from campusflow.calculate_prio import calculate_priority
from campusflow.generate_id import generate_next_id
from campusflow.validation import (
    CATEGORIES,
    URGENCIES,
    validate_affected_users,
    validate_category,
    validate_title,
    validate_urgency,
)

__all__ = [
    "CATEGORIES",
    "URGENCIES",
    "create_ticket",
    "validate_affected_users",
    "validate_category",
    "validate_title",
    "validate_urgency",
]


def create_ticket(tickets, title, category, urgency, affected_users):
    """Validate the inputs, then append and return a new ticket.

    Contract: if ANY input is invalid a ValueError is raised and `tickets` is
    left exactly as it was (validate before mutate). On success the ticket is
    open, unassigned, has a calculated priority and an empty notes list.
    """
    title = validate_title(title)
    category = validate_category(category)
    urgency = validate_urgency(urgency)
    affected_users = validate_affected_users(affected_users)

    ticket = {
        "id": generate_next_id(tickets),
        "title": title,
        "category": category,
        "urgency": urgency,
        "affected_users": affected_users,
        "priority": calculate_priority(urgency, affected_users),
        "status": "open",
        "assigned_to": None,
        "notes": [],
    }
    tickets.append(ticket)
    return ticket