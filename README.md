# CampusFlow — Campus Helpdesk Ticket System

CampusFlow is a Python command-line application for managing campus IT helpdesk tickets. It helps support teams create, prioritize, assign, track, and report on issues affecting campus operations.

## Project Objectives

- Create and validate helpdesk tickets.
- Calculate ticket priorities based on urgency and the number of affected users.
- Assign tickets to support staff.
- Manage ticket status and workflow.
- Display an ordered queue of unresolved tickets.
- Generate ticket reports.
- Persist ticket data using JSON.

## Requirements

Each ticket contains:

- `id` — unique ticket identifier
- `title` — description of the issue
- `category` — Network, Hardware, Software, or Other
- `urgency` — low, medium, or high
- `affected_users` — positive integer
- `priority` — calculated priority
- `status` — open, in_progress, or resolved
- `assigned_to` — assigned support staff member

### Priority Rules

Priority is calculated in the following order:

1. **Critical:** urgency is high and at least 10 users are affected.
2. **High:** urgency is high or at least 10 users are affected.
3. **Medium:** urgency is medium or at least 3 users are affected.
4. **Low:** none of the conditions above apply.

### Ticket Workflow

Tickets follow the workflow `open → in_progress → resolved`.

- A ticket must be assigned before it can move to `in_progress`.
- A resolved ticket must be explicitly reopened before it can be modified.

### Work Queue

Unresolved tickets are ordered by priority: critical, high, medium, then low. Tickets with equal priority are ordered by ascending ticket ID.

## Project Structure

```text
campus-flow-c2t1/
├── campusflow/
├── docs/
│   ├── ai-learning-log.md
│   └── design-decisions.md
├── tests/
├── .gitignore
├── main.py
└── README.md
```

## Team Responsibilities

The project is developed by two engineers.

- **Team Lead:** ticket creation, input validation, priority calculation, and related tests.
- **Teammate:** ticket assignment, workflow transitions, work queue, reports, and related tests.
- **Shared responsibilities:** integration, JSON persistence coordination, code reviews, documentation, testing, and final demonstration.

## Development Setup

Python 3 is required.

1. Clone the repository.
2. Navigate into the project directory.
3. Optionally create and activate a virtual environment.
4. Implement the application and tests according to the agreed design.

Create a virtual environment on Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Running the Application

The CLI entry point is intended to be `main.py`.

```bash
python3 main.py
```

## Running Tests

Tests use Python's built-in `unittest` framework.

```bash
python3 -m unittest discover -s tests -v
```

The application and tests will become runnable as implementation progresses.

## Contribution Workflow

1. Keep `main` as the shared integration branch.
2. Create a feature branch for each task.
3. Commit changes with clear, descriptive messages.
4. Push the feature branch to GitHub.
5. Open a pull request targeting `main`.
6. Have the other engineer review and approve the pull request.
7. Address review feedback before merging.

Do not merge your own pull request without the required partner approval.

## Documentation

- `docs/design-decisions.md` — agreed architecture, interfaces, and design decisions.
- `docs/ai-learning-log.md` — each engineer's AI learning interactions and documented corrections or improvements to AI suggestions.

## Project Status

**Status:** Initial repository setup. Application implementation and automated tests are pending.