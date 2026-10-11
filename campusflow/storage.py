import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "tickets.json"


class StorageError(Exception):
    """Raised when the ticket file exists but cannot be read safely."""


def load_tickets(filename=DATA_FILE):
    path = Path(filename)

    # Missing file or empty file: fresh start.
    if not path.exists():
        return []

    try:
        content = path.read_text(encoding="utf-8")
    except OSError as error:
        raise StorageError(f"Could not read {path}: {error}") from error

    if not content.strip():
        return []

    try:
        tickets = json.loads(content)
    except json.JSONDecodeError as error:
        raise StorageError(
            f"{path} contains invalid JSON ({error}). "
            "Fix or remove the file. Nothing was changed."
        ) from error

    if not isinstance(tickets, list):
        raise StorageError(f"{path} must contain a list of tickets.")

    return tickets


def save_tickets(tickets, filename=DATA_FILE):
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)

    
    temp_path = path.with_name(path.name + ".tmp")
    with open(temp_path, "w", encoding="utf-8") as file:
        json.dump(tickets, file, indent=4)
    temp_path.replace(path)