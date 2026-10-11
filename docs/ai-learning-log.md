## Fellow: Otete Benjamin Agogo - Engineer A:

### Interaction #1 — GitHub Issues Creation & Structuring
- **Problem:** I understood the high-level purpose of GitHub Issues for sprint planning, but I needed to learn the exact steps to create them and how to structure them properly with acceptance criteria.

- **My initial understanding:** I knew issues act as task trackers for a repository, but I was unsure how to write actionable descriptions or format them for a team environment.

- **Prompt to AI:** "Explain how to create and structure effective GitHub Issues for a software project using a simple example. Do not code my project."

- **Useful AI guidance:** AI explained the repository "Issues" tab workflow, the importance of concise titles, and how to use markdown checklists for clear acceptance criteria.

- **My independent experiment/test:** I navigated to our `campusflow` repository on GitHub, clicked the "Issues" tab, and created our first real sprint issue with a formatted acceptance criteria checklist.

- **Verification source or result:** Verified that the issue was successfully posted, assigned, and visible on our repository dashboard ready for tracking.

- **Decision:** Accepted; we adopted this structure for creating all of our major feature issues for Phase 2.

- **Related file/commit:** GitHub Repository Issues tab (`campusflow-c2t2/issues`)

- **What I can now explain without AI:** How to navigate to the Issues tab, write a well-defined task title, break down requirements using checklist items, and set up a proper task tracker for a team project.






## Fellow: Otete Benjamin Agogo - Engineer A:

### Interaction #2 — Ticket Assignment & Dictionary Updates

- **Problem:** I needed to understand how to search through a collection of tickets (stored as a list of dictionaries) by a unique ID and safely update its assigned staff member without corrupting other records or crashing on unknown IDs.


- **My initial understanding:** I knew how to use a standard `for` loop to iterate through a list, but I wasn't sure about the cleanest pattern for finding a target dictionary, modifying its key-value pairs in-place, and handling "not found" errors cleanly.


- **Prompt to AI:** "Explain how to find and update a target dictionary inside a list based on a specific key match using a small, unrelated example. Do not code my project."


- **Useful AI guidance:** AI explained how to loop through the list, check for a matching identifier condition, update the dictionary properties directly, and return a clear success or failure status if the item doesn't exist.


- **My independent experiment/test:** I wrote a tiny standalone test script with a mock list of user dictionaries, searched for a specific ID, updated an attribute, and tested what happens when an invalid ID is passed.


- **Verification source or result:** Ran the script in my terminal and verified that the target record updated successfully while all other records remained untouched.


- **Decision:** Accepted; this approach will be used for the ticket assignment and workflow feature logic.


- **Related file/commit:** `campusflow/workflow.py` (or assignment logic branch)

- **What I can now explain without AI:** How to iterate through a list of dictionaries, locate a record using a unique identifier, safely modify its fields, and handle cases where an ID cannot be found.



