# Application Validation Skill

This skill provides mandatory validation steps for `sahelper` to ensure it remains functional and error-free.

## Validation Protocol

1.  **Package Integrity:** Verify that every directory in `sahelper/` has an `__init__.py` file.
2.  **Syntax & Compilation:** Run `python -m compileall .` to catch syntax errors project-wide.
3.  **Exhaustive Import Check:** Verify all core components can be imported:
    `python -c "import sahelper.main; import sahelper.ui.main_window; import sahelper.services.automation; import sahelper.ui.portfolio; import sahelper.ui.analysis; import sahelper.ui.screener; import sahelper.ui.ai_assistant; import sahelper.ui.alerts; import sahelper.ui.heatmap; import sahelper.ui.news_feed"`
4.  **Database Check:** Verify that `init_db()` can run without errors and create the necessary SQLite tables.
5.  **Automated Tests:** Run the test suite:
    `pytest tests/`

## When to use
- ALWAYS run these checks before considering a task "complete".
- Run these checks after any major refactoring or dependency update.
