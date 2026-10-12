## Input Validation Strategy (revised after trade-off discovery)

Validation rules live in small functions in `campusflow/tickets.py`
(validate_title, validate_category, validate_urgency, validate_affected_users)
that raise ValueError. The CLI calls them as each value is typed, so the user
still gets immediate feedback and re-enters only the field that failed.
Reason: the rules can be unit-tested without interactive input, as the sprint
guide requires.

**What we found:** checks written inside the `input()` loop can't be tested
by themselves. The sprint guide requires tests such as "zero affected users
is rejected", so the rules needed to be functions we can call directly.

## OTETE BENJAMIN AGOGO - Engineer A:
Responsible for ticket assignment, the status workflow lifecycle, work queues, and reporting (along with matching unit tests).

## KPENSALEN THOMAS - Engineer B:
Responsible for ticket creation, inline input validation, and the priority calculation engine (along with matching unit tests).

## Data Structure:
Tickets will be stored as a list of dictionaries (or a dictionary keyed by ID, depending on your choice) to make JSON serialization and queue sorting straightforward.

## Error Handling:
Invalid inputs or illegal state transitions will raise standard Python exceptions (or return explicit error strings/tuples) so the CLI can cleanly catch them and display helpful user errors without crashing or corrupting data. Ownership:
A dedicated storage.py module will handle loading and saving JSON data, which both engineers will import and utilize.
