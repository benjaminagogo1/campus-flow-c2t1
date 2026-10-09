# Contributing Guide

## Branching
- `main` is the stable branch.
- Create a separate branch for each task.
- Use prefixes such as `docs/`, `feat/`, `fix/`, and `chore/`.

## Commits
- Make small, focused commits.
- Use clear commit messages.
- Do not commit secrets, virtual environments, or generated files.

## Pull Requests
- Push your task branch to GitHub.
- Open a pull request into `main`.
- The other team member should review changes before merging.
- Resolve review feedback before merging.

## Teamwork
- Agree on task ownership before working on shared files.
- Communicate before changing files assigned to the other teammate.


# Commit Message Guidelines

Use clear, descriptive commit messages that explain the change.

Examples:
- `docs: update repository documentation`
- `feat: implement ticket priority calculation`
- `fix: validate affected users input`
- `test: add ticket validation tests`
- `chore: update repository configuration`

## Code Quality and Testing

- Write tests for new features and bug fixes.
- Run relevant tests before opening a pull request.
- Keep pull requests focused on one task.
- Update documentation when project behavior or setup changes.
- Follow the agreed project structure and design decisions.

## Files and Secrets

- Never commit passwords, API keys, access tokens, or other secrets.
- Keep virtual environments and generated files out of version control.
- Follow the repository's `.gitignore` rules.
- Do not commit local `.env` files.

## Pull Request Approval

- Both team members must review changes carefully.
- Address review feedback before merging.
- The author must not merge their own pull request without the other team member's approval.

## Shared Responsibilities

Both team members are responsible for:
- Communicating changes that affect shared code or interfaces.
- Reviewing pull requests.
- Keeping documentation accurate.
- Coordinating integration and resolving merge conflicts.
- Ensuring the application and tests work together.