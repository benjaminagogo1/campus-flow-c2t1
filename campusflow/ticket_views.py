import json
from pathlib import Path

TICKETS_FILE = Path(__file__).parent / "tickets.json"


def list_tickets(filename=TICKETS_FILE):
    """Return all saved tickets."""
    with open(filename, encoding="utf-8") as file:
        tickets = json.load(file)
    if not isinstance(tickets, list):
        raise ValueError("Ticket data must be a list.")
    return tickets


def view_ticket(ticket_id, filename=TICKETS_FILE):
    """Return a ticket by ID, or None if it does not exist."""
    for ticket in list_tickets(filename):
        if str(ticket.get("Id", "")).lower() == str(ticket_id).lower():
            return ticket
    return None


def display_tickets(filename=TICKETS_FILE):
    """Print all saved tickets."""
    tickets = list_tickets(filename)
    if not tickets:
        print("No tickets found.")
        return

    for ticket in tickets:
        print("-" * 30)
        for key, value in ticket.items():
            print(f"{key}: {value}")


def display_ticket(ticket_id, filename=TICKETS_FILE):
    """Print one ticket by ID."""
    ticket = view_ticket(ticket_id, filename)
    if ticket is None:
        print(f"Ticket '{ticket_id}' not found.")
        return

    for key, value in ticket.items():
        print(f"{key}: {value}")
