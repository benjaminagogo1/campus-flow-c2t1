"""Safe JSON persistence for tickets.

File format: a JSON list of ticket objects. Each ticket has the fields
id, title, category, urgency, affected_users, priority, status, assigned_to
and notes (a list of {note_id, author, message}).

Safety rules:
  * Loading parses AND validates the whole file before returning anything, so
    a bad file can never leave the program holding half-loaded data.
  * Saving refuses to write invalid data, and writes to a temporary file that
    replaces the real file only when the write has fully succeeded.
"""

import json
import os
from pathlib import Path

from validation import CATEGORIES, URGENCIES, validate_collection

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "tickets.json"

# Old versions of the app stored "no assignee" as text such as "none".
_LEGACY_NO_ASSIGNEE = {"", "none", "null", "n/a", "na", "unassigned", "-"}


class StorageError(ValueError):
    """Raised when the ticket file cannot be read, or fails validation."""


def upgrade_legacy_ticket(record):
    """Bring a version-1 ticket up to the current format (returns a copy).

    A version-1 ticket has no "notes" field. For those records only we:
      * add "notes": []
      * fix the case of category and urgency (for example "other" -> "Other")
      * turn placeholder assignees such as "none" into null, so an unassigned
        ticket cannot slip into in_progress

    Records that already have "notes" are current-format and are returned
    unchanged, so they are checked strictly. The file on disk is not touched
    by this function; the upgraded form is only written on the next save.
    """
    if not isinstance(record, dict) or "notes" in record:
        return record

    upgraded = dict(record)
    upgraded["notes"] = []

    category = upgraded.get("category")
    if isinstance(category, str):
        for allowed in CATEGORIES:
            if allowed.casefold() == category.strip().casefold():
                upgraded["category"] = allowed

    urgency = upgraded.get("urgency")
    if isinstance(urgency, str) and urgency.strip().casefold() in URGENCIES:
        upgraded["urgency"] = urgency.strip().casefold()

    assigned_to = upgraded.get("assigned_to")
    if isinstance(assigned_to, str) and assigned_to.strip().casefold() in _LEGACY_NO_ASSIGNEE:
        upgraded["assigned_to"] = None

    return upgraded


def load_tickets(filename=DATA_FILE):
    """Read, upgrade and fully validate the ticket file; return a new list.

    A missing or empty file gives an empty list. Anything unreadable, invalid
    JSON, or failing validation (missing fields, duplicate IDs, bad priority,
    bad notes, ...) raises StorageError. Nothing is modified on failure.
    """
    path = Path(filename)

    if not path.exists():
        return []

    try:
        content = path.read_text(encoding="utf-8")
    except OSError as error:
        raise StorageError(f"Could not read {path}: {error}") from error

    if not content.strip():
        return []

    try:
        data = json.loads(content)
    except json.JSONDecodeError as error:
        raise StorageError(
            f"{path} contains invalid JSON ({error}). "
            "Fix or remove the file. Nothing was changed."
        ) from error

    if not isinstance(data, list):
        raise StorageError(f"{path} must contain a list of tickets. Nothing was changed.")

    tickets = [upgrade_legacy_ticket(record) for record in data]

    try:
        validate_collection(tickets)
    except ValueError as error:
        raise StorageError(f"{path} failed validation: {error} Nothing was changed.") from error

    return tickets


def save_tickets(tickets, filename=DATA_FILE):
    """Validate, then write the tickets to disk atomically.

    Invalid data raises StorageError and the existing file is left untouched.
    A failed write raises OSError and also leaves the existing file untouched.
    """
    try:
        validate_collection(tickets)
    except ValueError as error:
        raise StorageError(f"Refusing to save invalid ticket data: {error}") from error

    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)

    temp_path = path.with_name(path.name + ".tmp")
    try:
        with open(temp_path, "w", encoding="utf-8") as file:
            json.dump(tickets, file, indent=4)
            file.write("\n")
            file.flush()
            os.fsync(file.fileno())
        temp_path.replace(path)
    except OSError:
        try:
            temp_path.unlink()
        except OSError:
            pass
        raise


def reload_tickets(tickets, filename=DATA_FILE):
    """Replace the contents of the in-memory list with the file's contents.

    The file is loaded and validated completely first. If that fails,
    StorageError is raised BEFORE the in-memory list is touched, so the
    current data is never partly overwritten.
    """
    fresh = load_tickets(filename)
    tickets[:] = fresh
    return tickets