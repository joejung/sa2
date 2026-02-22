# Git Safety Skill

This skill provides mandatory safety protocols for executing Git commands in this workspace to prevent environment-specific failures (like PowerShell '&&' errors) and ensure repository integrity.

## Protocols

1.  **NO Chained Commands:** Never use `&&` or `;` to chain commands in `run_shell_command`. PowerShell in this environment may not support them as expected.
    - **WRONG:** `git add . && git commit -m "..."`
    - **RIGHT:** Execute `git add .` in one tool call, then `git commit -m "..."` in the next.

2.  **Atomic Operations:** Perform each Git action (add, commit, push, branch, checkout) as a single, isolated tool call.

3.  **Verify State:** Always run `git status` before and after any modification to ensure you are operating on the intended files and that the operation succeeded.

4.  **Exhaustive Pathing:** When adding specific files, use their full relative paths from the root to avoid ambiguity.

5.  **No Chitchat in Messages:** Commit messages should be descriptive but professional, following the project's institutional standards.

## When to use
- ALWAYS run these protocols whenever performing ANY Git operation.
- Especially critical when preparing final releases or fixing build errors.
