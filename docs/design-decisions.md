## Input Validation Strategy:
Team responsibilities have been formally distributed. We agreed that input validation will occur inline as data is received, rather than delegating checks to a separate standalone validation function, ensuring immediate feedback upon entry.
Feature Ownership:

## OTETE BENJAMIN AGOGO - Engineer A:
Responsible for ticket assignment, the status workflow lifecycle, work queues, and reporting (along with matching unit tests).

## KPENSALEN THOMAS - Engineer B:
Responsible for ticket creation, inline input validation, and the priority calculation engine (along with matching unit tests).

## Data Structure:
Tickets will be stored as a list of dictionaries (or a dictionary keyed by ID, depending on your choice) to make JSON serialization and queue sorting straightforward.

## Error Handling:
Invalid inputs or illegal state transitions will raise standard Python exceptions (or return explicit error strings/tuples) so the CLI can cleanly catch them and display helpful user errors without crashing or corrupting data. Ownership:
A dedicated storage.py module will handle loading and saving JSON data, which both engineers will import and utilize.
