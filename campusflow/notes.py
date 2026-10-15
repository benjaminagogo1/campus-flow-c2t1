"""Structured follow-up notes attached to tickets.

A note is {"note_id": "N001", "author": "...", "message": "..."}.
Note IDs are per ticket (every ticket starts at N001); a note is identified by
its ticket ID plus its note ID.

Error convention (same as the rest of the project): invalid actions raise
ValueError and leave the ticket collection exactly as it was.
"""

import re

from campusflow.validation import validate_author, validate_note_message
from campusflow.workflow import get_ticket

NOTE_ALLOWED_STATUSES = ("open", "in_progress")

_NOTE_ID_NUMBER = re.compile(r"^N(\d+)$", re.IGNORECASE)


def _note_number(note):
    """Numeric part of a note ID ('N010' -> 10); 0 if the ID is malformed."""
    match = _NOTE_ID_NUMBER.match(str(note.get("note_id", "")))
    return int(match.group(1)) if match else 0


def next_note_id(ticket):
    """The next note ID for this ticket: highest existing number + 1.

    Derived from the notes that actually exist, so a rejected note can never
    use up an ID, and IDs keep counting correctly after a save and reload.
    """
    highest = max((_note_number(note) for note in ticket.get("notes", [])), default=0)
    return f"N{highest + 1:03d}"


def add_note(tickets, ticket_id, author, message):
    """Add a follow-up note to an open or in_progress ticket and return it.

    Rejected (nothing changes, no note ID consumed) when the ticket does not
    exist, is resolved, the author is blank, or the message is not 5 to 300
    characters after trimming.
    """
    ticket = get_ticket(tickets, ticket_id)

    status = str(ticket.get("status", "open")).lower()
    if status not in NOTE_ALLOWED_STATUSES:
        raise ValueError(
            "Notes can only be added to open or in_progress tickets "
            f"(this ticket is {status}). Reopen it first."
        )

    author = validate_author(author)
    message = validate_note_message(message)

    # Every check has passed; only now do we change anything.
    note = {
        "note_id": next_note_id(ticket),
        "author": author,
        "message": message,
    }
    ticket.setdefault("notes", []).append(note)
    return note


def get_notes(tickets, ticket_id):
    """Return copies of a ticket's notes in note-ID order (N002 before N010)."""
    ticket = get_ticket(tickets, ticket_id)
    ordered = sorted(ticket.get("notes", []), key=_note_number)
    return [dict(note) for note in ordered]