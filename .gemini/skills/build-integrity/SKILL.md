# Build Integrity Skill

This skill provides the "Double-Check" protocol to ensure the application is completely free of syntax errors, broken dependencies, and initialization failures before any task is marked as finished.

## Protocols

1.  **Project-Wide Compilation:**
    - Run `python -m compileall .`
    - Any reported syntax errors MUST be fixed before proceeding.

2.  **Exhaustive Import Verification:**
    - Verify that every core service and UI component can be imported without triggering side effects or errors.
    - Run: `python -c "import sahelper.main; import sahelper.ui.main_window; import sahelper.services.automation; import sahelper.ui.portfolio; import sahelper.ui.analysis; import sahelper.ui.screener; import sahelper.ui.ai_assistant; import sahelper.ui.alerts; import sahelper.ui.heatmap; import sahelper.ui.news_feed"`

3.  **Dependency Alignment:**
    - Verify that all imports in the source code match the packages listed in `requirements.txt`.

4.  **Database Bootstrapping:**
    - Verify that `init_db()` runs and establishes the schema correctly.

## When to use
- ALWAYS run these checks before concluding a Directives task.
- Run after any code change, even if it seems "minor".
- Use this to guarantee a "Zero Build Error" state.
