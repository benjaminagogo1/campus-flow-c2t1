from campusflow.reports import build_report, format_report
from campusflow.create_note import add_note_ticket
from campusflow.storage import StorageError, load_tickets, save_tickets
from campusflow.tickets import (
    CATEGORIES,
    URGENCIES,
    create_ticket,
    validate_affected_users,
    validate_category,
    validate_title,
    validate_urgency,
)
from campusflow.workflow import assign_ticket, get_work_queue, update_status

TICKET_FIELDS = [
    "id",
    "title",
    "category",
    "urgency",
    "affected_users",
    "priority",
    "status",
    "assigned_to",
]

MENU = """
------ CampusFlow ------
\n1. Create ticket
2. List all tickets
3. View one ticket
4. Assign ticket
5. Change status 
6. Add note to ticket
7. Work queue
8. Report
0. Exit"""


def ask(prompt, validator):
    """Keep asking until the validator accepts the input."""
    while True:
        try:
            return validator(input(prompt))
        except ValueError as error:
            print(f"  Error: {error}")


def print_ticket(ticket):
    print("-" * 30)
    for field in TICKET_FIELDS:
        print(f"{field}: {ticket.get(field)}")


def find_ticket(tickets, ticket_id):
    for ticket in tickets:
        if str(ticket.get("id", "")).upper() == ticket_id:
            return ticket
    return None


def read_ticket_id():
    return input("Enter ticket ID (e.g. T001): ").strip().upper()


def handle_create(tickets):
    title = ask("Enter title: ", validate_title)
    category = ask(f"Enter category ({', '.join(CATEGORIES)}): ", validate_category)
    urgency = ask(f"Enter urgency ({', '.join(URGENCIES)}): ", validate_urgency)
    affected_users = ask("Enter affected users: ", validate_affected_users)

    ticket = create_ticket(tickets, title, category, urgency, affected_users)
    save_tickets(tickets)
    print(f"Created ticket {ticket['id']} with priority '{ticket['priority']}'.")


def handle_list(tickets):
    if not tickets:
        print("No tickets found.")
        return
    for ticket in tickets:
        print_ticket(ticket)


def handle_view(tickets):
    ticket_id = read_ticket_id()
    ticket = find_ticket(tickets, ticket_id)
    if ticket is None:
        print(f"Ticket '{ticket_id}' not found.")
        return
    print_ticket(ticket)


def handle_assign(tickets):
    ticket_id = read_ticket_id()
    staff_name = input("Enter staff member name: ")
    ticket = assign_ticket(tickets, ticket_id, staff_name)
    save_tickets(tickets)
    print(f"Ticket {ticket['id']} assigned to {ticket['assigned_to']}.")


def handle_status(tickets):
    ticket_id = read_ticket_id()
    new_status = input("Enter new status (open / in_progress / resolved): ")
    ticket = update_status(tickets, ticket_id, new_status.strip().lower())
    save_tickets(tickets)
    print(f"Ticket {ticket['id']} is now '{ticket['status']}'.")


def handle_add_note(tickets):
    ticket_id = read_ticket_id()
    
    ticket = find_ticket(tickets, ticket_id)
    if ticket is None:
        print(f"Error: Ticket '{ticket_id}' not found.")
        return
        
    author = input("Enter your name (Author): ").strip()
    message = input("Enter note message: ").strip()
    
    if not author or not message:
        print("Error: Author and message fields cannot be empty.")
        return

    ticket = add_note_ticket(ticket_id, author, message)
    save_tickets(tickets)
    print(f"Successfully added note to Ticket {ticket_id}!")


def handle_queue(tickets):
    queue = get_work_queue(tickets)
    if not queue:
        print("The work queue is empty.")
        return
    for position, ticket in enumerate(queue, start=1):
        print(
            f"{position}. {ticket['id']} | {ticket['priority']} | "
            f"{ticket['status']} | {ticket['title']}"
        )


def handle_report(tickets):
    print(format_report(build_report(tickets)))


ACTIONS = {
    "1": handle_create,
    "2": handle_list,
    "3": handle_view,
    "4": handle_assign,
    "5": handle_status,
    "6": handle_add_note,
    "7": handle_queue,
    "8": handle_report,
}


def main():
    try:
        tickets = load_tickets()
    except StorageError as error:
        print(f"Cannot start: {error}")
        return

    print("------ Welcome to CampusFlow ------")

    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()

        if choice == "0":
            print("Goodbye.")
            break

        action = ACTIONS.get(choice)
        if action is None:
            print("Invalid option. Choose a number from the menu.")
            continue

        try:
            action(tickets)
        except ValueError as error:
            print(f"Error: {error}")
        except OSError as error:
            print(f"Could not save tickets: {error}")


if __name__ == "__main__":
    main()