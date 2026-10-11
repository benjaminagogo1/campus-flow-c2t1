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






## Fellow: Kpensalen Thomas Aondongu - Engineer B: 
### Interaction #1 - Ticket Creation (Automated Ticket ID Generation)

- **Problem:** The system specifications required the unique ticket identifier (`id`) to be automatically generated rather than hardcoded during manual creation.

- **My Initial Understanding:** I understood how to capture user input and structure the ticket within a list of dictionaries, but I lacked the mechanism to auto-generate sequentially structured, unique IDs.

- **Prompt to AI:** "Explain how I can generate a unique ID with a specific prefix dynamically in Python based on an existing JSON data structure."
- **Useful AI Guidance:** The AI explained how to build an ID generator function that accepts the dataset and a target prefix as parameters. It walked through looping through the existing list to check the highest current ID, splitting the number from the prefix, incrementing it by 1 for the new ticket, and defaulting to a fresh starting ID if the list is empty.

- **My Independent Experiment/Test:** I wrote an isolated, lightweight script to test the sequential number generation along with the string prefix combination.

- **Verification Source or Result:** I executed the script in the terminal and confirmed it consistently outputted correctly formatted sequential IDs (e.g., `T1`, `T2`).

- **Decision:** I successfully integrated this function as a separate module (`generate_id.py`) and called it within my main workflow creation block.

- **Related Files/Commits:** `campusflow/tickets.py`, `campusflow/generate_id.py`

- **What I Can Now Explain Without AI:** How to read and write JSON data safely using Python's file operations, how to safely iterate over lists of dictionaries to manipulate keys and values, and how to implement `try/except` guard rails to handle edge cases like missing or corrupted files.


## Fellow: Kpensalen Thomas Aondongu - Engineer B: 
### Interaction #2 - Application Control Flow & Entry Point (`main.py`)

- **Problem:** Structuring the overall runtime loop, managing data flow between validation checks, and optimizing block indentations for readability.


- **My Initial Understanding:** I knew how to collect and validate standard user inputs against defined constraints, but I needed to verify best practices for chaining compound conditional evaluations within a persistent loop execution.


- **Prompt to AI:** "Explain indentation scoping rules in Python and best practices for structuring continuous runtime control flow."

- **Useful AI Guidance:** The AI clarified how lexical scoping works via Python's structural whitespace. It demonstrated how to group input validation checks within a continuous `while True` loop, showing how to correctly indent nested blocks so that code execution branches logically and cleanly without creating scoping leaks.

- **Decision:** I aligned the core runtime cycle in `main.py` according to these scoping rules, ensuring variables pass seamlessly down into the core function endpoints.

- **Related Files/Commits:** `main.py`

- **What I Can Now Explain Without AI:** How to construct a sanitization layer for terminal inputs, how to enforce validation boundaries using iteration states, and how absolute namespace imports operate across custom packages.




    
## Fellow: Otete Benjamin Agogo - Engineer A:

### Interaction #3 — Priority Engine Rule Ordering & Edge Case Validation

- **Problem:** I needed to implement the exact priority calculation rules (Section 1.3) to ensure tickets are correctly classified as `critical`, `high`, `medium`, or `low` based on urgency and affected users in the specified order.


- **My initial understanding:** I knew we needed sequential condition checks, but I wasn't sure how to structure the `if/elif` blocks so that overlapping conditions wouldn't trigger the wrong priority level.


- **Prompt to AI:** "Provide a Python function snippet that calculates ticket priority based on urgency ('high', 'medium', 'low') and affected users (integer). Do not write my full application."


- **Useful AI guidance:** AI provided a multi-branch `if/elif` structure, but it placed the check for `affected_users >= 10` *before* checking if the urgency was `high`. 

- **My independent experiment/test:** I tested AI's proposed code logic against our project rules (Rule 1: high urgency AND 10+ affected users $\rightarrow$ critical). I discovered that checking affected users first caused a ticket with *low* urgency and 12 users to incorrectly trigger a higher priority tier than allowed by our rules.


- **Verification source or result:** Compared the output against the sprint guide's exact specification table and realized the rule sequence was out of order.

- **Decision:** **Rejected/Improved.** I rejected AI's initial condition ordering and manually restructured the `if/elif` block to strictly enforce the priority rules in the exact order required: Rule 1 (high urgency AND $\ge 10$ users), Rule 2 (high urgency OR $\ge 10$ users), Rule 3 (medium urgency OR $\ge 3$ users), and Rule 4 (remaining as low).


- **Related file/commit:** `campusflow/tickets.py` & `tests/test_tickets.py`
- **What I can now explain without AI:** How to sequence conditional logic carefully to match precise business rules, why strict rule ordering matters for ticket classification, and how to write unit tests to verify boundary conditions.







## Fellow: Kpensalen Thomas Aondongu - Engineer B: 
### Interaction #3 - Automated Unit Testing (`test_calculate_prio.py`, `test_tickets.py`)

- **Problem:** I had never written an automated test suite in Python, making the setup and architectural patterns feel unfamiliar and challenging initially.


- **My Initial Understanding:** Null (no prior experience with software testing execution layers).


- **Prompt to AI:** "Provide resources, documentations, or study materials to learn how to write an automated test file in Python."


- **Useful AI Guidance:** The AI provided high-quality documentation links and broke down the fundamentals of Python testing frameworks. It explained the core differences between `pytest` (which requires external installation) and `unittest` (the built-in standard library option). It also taught me the foundational concept of `assert` statements, explaining how Python uses them to programmatically verify code logic.


- **Decision:** I started by creating basic isolated functions to experiment with writing simple test scripts. Once I was comfortable with the mechanics, I designed and structured the comprehensive `unittest` files for both our priority calculation and ticket storage logic.


- **Related Files/Commits:** `tests/test_tickets.py`, `tests/test_calculate_prio.py`


- **What I Can Now Explain Without AI:** The structural differences between `pytest` and `unittest` frameworks, how to implement `assert` checking mechanisms, and how to configure automated test runners to evaluate file structures.
