# SplitSmart — Expense Splitter (Assignment 1)

A simple command-line SplitSmart application that models users, groups, expenses and debt settlement. This repository implements the UML model provided for the assignment and includes a small CLI, unit tests, and a demo/integration script.

## Repository contents
- `splitsmart/` — package with the application code
  - `models.py` — domain classes: `User`, `Expense` (+ subclasses), `BalanceSheet`, `Debt`, `Group`.
  - `app.py` — menu-driven CLI (interactive) and simple JSON save/load.
- `tests/` — unit tests (unittest)
- `demo_test.py` — scripted integration check that exercises common flows (add users/groups/expenses, view debts, settle up, save/load).

## Quickstart — requirements
- Python 3.8 or newer

Optional: create and activate a virtual environment.

## Run the interactive CLI
Start the app and use the on-screen menu:

```bash
python -m splitsmart.app
```

The menu provides options to add users, create groups, add expenses (equal/unequal/percent/shares), view debts, record settlements, and save/load state.

## Run the integration/demo script
To run the scripted scenario that was used during development (it also verifies core flows programmatically):

```bash
python demo_test.py
```

You should see printed debt states and a final "All checks passed" when the script completes.

## Run unit tests
Use Python's `unittest` discovery to run the tests included in `tests/`:

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
```

All tests in this repository passed during development.

## Design notes & important behavior
- Balance model: `BalanceSheet` maintains a net balance per user. Positive = others owe this user; negative = this user owes others.
- Expense splitting: supports equal, custom unequal amounts, percent-based, and share-count splits. Shares are rounded to 2 decimals; small rounding remainders are adjusted to the payer's share.
- Debt simplification: a greedy algorithm matches largest creditors with largest debtors to produce a reduced list of pairwise debts (correct but not necessarily minimal in count).
- Settlement: when a user pays another to settle, net balances are updated so that the payer's net position increases (they owe less) and the receiver's decreases (they are owed less). This was corrected after initial implementation and is covered by the integration script.
- Persistence: current JSON save format stores users, groups (member names) and expense summaries. It does not fully serialize expense split details; extending save/load to fully persist all expense types is a suggested next step.

## Files of interest
- `splitsmart/models.py` — main domain logic and debt simplification algorithm.
- `splitsmart/app.py` — CLI entry point (interactive usage).
- `tests/test_models.py` — unit tests for core behaviors.
- `demo_test.py` — integration script used to validate flows.

## Next improvements (suggestions)
- Full serialization/deserialization of expenses so a saved snapshot fully restores debts and expense history.
- Additional tests for rounding edge cases, invalid inputs, and CLI input validation.
- Improve the CLI UX and provide clearer prompts/help text.

---

If you'd like, I can now:
- Extend save/load to persist full expense details and balances, or
- Add more tests and edge-case coverage, or
- Improve the CLI prompts and input validation.

