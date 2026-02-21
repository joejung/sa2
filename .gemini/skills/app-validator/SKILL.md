# Application Validation Skill

This skill provides mandatory validation steps for `sahelper` to ensure it remains functional and error-free.

## Validation Protocol

1.  **Package Integrity:** Verify that every directory in `sahelper/` has an `__init__.py` file.
2.  **Syntax & Imports:** Run a smoke test by importing the main module:
    `python -c "import sahelper.main"`
3.  **Database Check:** Verify that `init_db()` can run without errors and create the necessary SQLite tables.
4.  **Automated Tests:** Run the test suite:
    `pytest tests/`

## When to use
- ALWAYS run these checks before considering a task "complete".
- Run these checks after any major refactoring or dependency update.
