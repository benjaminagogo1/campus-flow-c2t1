"""Central validation rules for CampusFlow.

Every rule lives here so the CLI, the business logic and the JSON loader all
agree. Functions raise ValueError with a friendly message when input is
invalid and never modify anything they are given.

Two groups of functions:
  * Input validators (validate_title, validate_category, ...): clean up what a
    person typed and return the canonical value to store.
  * Record validators (validate_ticket, validate_note, validate_collection):
    strictly check data that is ALREADY stored (for example loaded from JSON).
"""

import re

from campusflow.calculate_prio import calculate_priority

CATEGORIES = ["Network", "Hardware", "Software", "Other"]
URGENCIES = ["low", "medium", "high"]
STATUSES = ["open", "in_progress", "resolved"]
PRIORITIES = ["critical", "high", "medium", "low"]

TICKET_ID_PATTERN = re.compile(r"^T\d+$")
NOTE_ID_PATTERN = re.compile(r"^N\d+$")

NOTE_MIN_LENGTH = 5
NOTE_MAX_LENGTH = 300

REQUIRED_TICKET_KEYS = (
    "id",
    "title",
    "category",
    "urgency",
    "affected_users",
    "priority",
    "status",
    "assigned_to",
    "notes",
)
NOTE_KEYS = ("note_id", "author", "message")


def _is_blank(value):
    """True when value is not a string or is empty after trimming."""
    return not isinstance(value, str) or not value.strip()


def is_positive_int(value):
    """True only for real ints greater than 0 (bool is NOT accepted).

    In Python isinstance(True, int) is True because bool is a subclass of int,
    so booleans must be excluded explicitly.
    """
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


# ---------------------------------------------------------------------------
# Input validators (clean what a person typed, return the value to store)
# ---------------------------------------------------------------------------


def validate_title(title):
    if _is_blank(title):
        raise ValueError("Title cannot be blank.")
    return title.strip()


def validate_category(category):
    cleaned = str(category).strip().casefold()
    for allowed in CATEGORIES:
        if allowed.casefold() == cleaned:
            return allowed
    raise ValueError(f"Invalid category. Choose one of: {', '.join(CATEGORIES)}.")


def validate_urgency(urgency):
    cleaned = str(urgency).strip().casefold()
    if cleaned in URGENCIES:
        return cleaned
    raise ValueError(f"Invalid urgency. Choose one of: {', '.join(URGENCIES)}.")


def validate_affected_users(value):
    """Return a strictly positive int.

    Accepts a real int, or a string of plain digits (because the CLI hands us
    typed text). Rejects 0, negatives, floats, booleans and any other text.
    """
    message = "Affected users must be a whole number greater than 0."
    if isinstance(value, bool):
        raise ValueError(message)
    if isinstance(value, str):
        text = value.strip()
        if not (text.isascii() and text.isdigit()):
            raise ValueError(message)
        value = int(text)
    if not is_positive_int(value):
        raise ValueError(message)
    return value


def validate_staff_name(name):
    if _is_blank(name):
        raise ValueError("Staff name cannot be empty.")
    return name.strip()


def validate_author(author):
    if _is_blank(author):
        raise ValueError("Note author cannot be blank.")
    return author.strip()


def validate_note_message(message):
    """Return the trimmed message; it must be 5 to 300 characters long."""
    if not isinstance(message, str):
        raise ValueError("Note message must be text.")
    text = message.strip()
    if not NOTE_MIN_LENGTH <= len(text) <= NOTE_MAX_LENGTH:
        raise ValueError(
            f"Note message must be {NOTE_MIN_LENGTH} to {NOTE_MAX_LENGTH} "
            f"characters after trimming (yours has {len(text)})."
        )
    return text


def validate_ticket_id(ticket_id):
    """Return the ID in canonical upper-case form, e.g. ' t001 ' -> 'T001'."""
    if not isinstance(ticket_id, str):
        raise ValueError("Ticket ID must be text such as T001.")
    cleaned = ticket_id.strip().upper()
    if not TICKET_ID_PATTERN.match(cleaned):
        raise ValueError(f"Invalid ticket ID '{ticket_id}'. Use the form T001.")
    return cleaned


# ---------------------------------------------------------------------------
# Record validators (strict checks of stored data, used when loading JSON)
# ---------------------------------------------------------------------------


def validate_note(note):
    """Check one stored note. Raises ValueError if its shape is wrong."""
    if not isinstance(note, dict):
        raise ValueError("A note must be an object with note_id, author and message.")
    if set(note) != set(NOTE_KEYS):
        raise ValueError(f"A note must have exactly these fields: {', '.join(NOTE_KEYS)}.")
    note_id = note["note_id"]
    if not isinstance(note_id, str) or not NOTE_ID_PATTERN.match(note_id):
        raise ValueError(f"Invalid note ID {note_id!r}.")
    if _is_blank(note["author"]):
        raise ValueError(f"Note {note_id} has a blank author.")
    try:
        validate_note_message(note["message"])
    except ValueError as error:
        raise ValueError(f"Note {note_id}: {error}") from None


def validate_ticket(ticket):
    """Check that one stored ticket obeys every ticket invariant.

    Invariants: all required fields exist; id/title/category/urgency/status are
    legal; affected_users is a real positive int; priority is legal AND matches
    what calculate_priority would produce; an in_progress ticket has an
    assignee; notes is a list of well-formed notes with unique note IDs.
    """
    if not isinstance(ticket, dict):
        raise ValueError("Each ticket must be an object (dictionary).")

    missing = [key for key in REQUIRED_TICKET_KEYS if key not in ticket]
    if missing:
        raise ValueError(f"Ticket is missing required field(s): {', '.join(missing)}.")

    ticket_id = ticket["id"]
    if not isinstance(ticket_id, str) or not TICKET_ID_PATTERN.match(ticket_id):
        raise ValueError(f"Invalid ticket ID {ticket_id!r}.")
    label = f"Ticket {ticket_id}"

    if _is_blank(ticket["title"]):
        raise ValueError(f"{label}: title cannot be blank.")
    if ticket["category"] not in CATEGORIES:
        raise ValueError(f"{label}: invalid category {ticket['category']!r}.")
    if ticket["urgency"] not in URGENCIES:
        raise ValueError(f"{label}: invalid urgency {ticket['urgency']!r}.")
    if not is_positive_int(ticket["affected_users"]):
        raise ValueError(f"{label}: affected_users must be a whole number greater than 0.")
    if ticket["priority"] not in PRIORITIES:
        raise ValueError(f"{label}: invalid priority {ticket['priority']!r}.")

    expected = calculate_priority(ticket["urgency"], ticket["affected_users"])
    if ticket["priority"] != expected:
        raise ValueError(
            f"{label}: priority is '{ticket['priority']}' but urgency and "
            f"affected users give '{expected}'."
        )

    if ticket["status"] not in STATUSES:
        raise ValueError(f"{label}: invalid status {ticket['status']!r}.")

    assigned_to = ticket["assigned_to"]
    if assigned_to is not None and _is_blank(assigned_to):
        raise ValueError(f"{label}: assigned_to must be a name or null.")
    if ticket["status"] == "in_progress" and assigned_to is None:
        raise ValueError(f"{label}: an in_progress ticket must be assigned.")

    notes = ticket["notes"]
    if not isinstance(notes, list):
        raise ValueError(f"{label}: notes must be a list.")
    seen_note_ids = set()
    for note in notes:
        try:
            validate_note(note)
        except ValueError as error:
            raise ValueError(f"{label}: {error}") from None
        if note["note_id"] in seen_note_ids:
            raise ValueError(f"{label}: duplicate note ID {note['note_id']}.")
        seen_note_ids.add(note["note_id"])


def validate_collection(tickets):
    """Check a whole list of tickets, including that ticket IDs are unique."""
    if not isinstance(tickets, list):
        raise ValueError("Ticket data must be a list of tickets.")

    seen_ids = set()
    for position, ticket in enumerate(tickets, start=1):
        try:
            validate_ticket(ticket)
        except ValueError as error:
            raise ValueError(f"Record {position}: {error}") from None
        if ticket["id"] in seen_ids:
            raise ValueError(f"Duplicate ticket ID {ticket['id']}.")
        seen_ids.add(ticket["id"])