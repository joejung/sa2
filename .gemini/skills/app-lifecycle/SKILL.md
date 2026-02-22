# App Lifecycle Skill

This skill provides protocols for managing the application's runtime state (starting and stopping the GUI) from within the CLI environment.

## Protocols

1.  **Launch Application:**
    - Use `run_shell_command` with `command="run_sa.cmd"` and `is_background=True`.
    - Always verify if the process started by checking the tool output for Background PIDs.

2.  **Terminate Application (Windows):**
    - To stop the application, use:
      `taskkill /F /FI "WINDOWTITLE eq SAHelper*"` (if applicable) or filter by command line:
      `wmic process where "commandline like '%sahelper.main%'" delete` (more targeted).
    - Alternatively, if the PID is known from the launch call, use `taskkill /F /PID <PID> /T`.

3.  **Stability Check:**
    - After launching, wait at least 5 seconds and check if the process is still running using `tasklist` or `wmic`.

## When to use
- When the user asks to "run the app" or "start the app".
- When the user asks to "close the app" or "stop the app".
- Before running automated functional tests that require the GUI to be closed (or open).
