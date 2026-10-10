import json


def assign_ticket(ticket_id, staff_name, filename="campusflow/tickets.json"):
    if not isinstance(staff_name, str) or not staff_name.strip():
        raise ValueError("Staff name cannot be empty.")

    with open(filename, encoding="utf-8") as file:
        tickets = json.load(file)

    for ticket in tickets:
        if ticket.get("Id") == ticket_id:
            ticket["Assigned_to"] = staff_name.strip()
            with open(filename, "w", encoding="utf-8") as file:
                json.dump(tickets, file, indent=4)
            return ticket

    raise ValueError(f"Ticket '{ticket_id}' was not found.")


def update_status(ticket_id, new_status, filename="campusflow/tickets.json"):
    allowed = {
        "open": {"in_progress"},
        "in_progress": {"resolved"},
        "resolved": set(),
    }
    if new_status not in allowed:
        raise ValueError("Invalid status.")

    with open(filename, encoding="utf-8") as file:
        tickets = json.load(file)

    for ticket in tickets:
        if ticket.get("Id") == ticket_id:
            current = ticket.get("Status", "open").lower()

            if new_status not in allowed.get(current, set()):
                raise ValueError(f"Cannot move ticket from {current} to {new_status}.")

            if new_status == "in_progress" and not (
                ticket.get("Assigned_to") or ticket.get("Assisgned_to")
            ):
                raise ValueError("Assign the ticket before starting work.")

            ticket["Status"] = new_status
            with open(filename, "w", encoding="utf-8") as file:
                json.dump(tickets, file, indent=4)
            return ticket

    raise ValueError(f"Ticket '{ticket_id}' was not found.")


def get_work_queue(filename="campusflow/tickets.json"):
    priority_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}

    with open(filename, encoding="utf-8") as file:
        tickets = json.load(file)

    queue = [
        ticket for ticket in tickets
        if ticket.get("Status", "open").lower() != "resolved"
    ]

    def sort_key(ticket):
        ticket_id = str(ticket.get("Id", "T0"))
        digits = "".join(char for char in ticket_id if char.isdigit())
        priority = str(ticket.get("Priority", "low")).lower()
        return priority_rank.get(priority, 4), int(digits or 0)

    return sorted(queue, key=sort_key)
