# Project Mandates (sa2)

## Global Rules
- **File Length Limit:** No file should exceed 1500 lines. Refactor and split if it approaches this limit.
- **Logging:** Implement comprehensive logging using Python's `logging` module. Ensure error states and critical transitions are logged.

## Agents & Roles
The following custom agents are available in `.gemini/agents/`:
1. **planner**: Python/PyQt expert for architecture and planning.
2. **refactorer**: SW design and clean code expert.
3. **tester**: Functional testing and validation expert.
4. **requirer**: Requirements documentation expert.
5. **fin_advisor**: Financial expert (CFO / Trading Advisor).

## Functional Requirements
- **Crawling eting alpha:** Use Playwright for crawling.
- **UI Framework:** Use PyQt6 for the application interface (replaces Streamlit).
- **Captcha Bypass:** For the "eting alpha" site, aim for graceful handling. *Note: Avoid direct bypass tools that violate site terms; prefer browser stealth techniques or manual session injection where applicable.*

## Skills
- **coding-rules**: Activated via `.gemini/skills/coding-rules/`.
- **app-validator**: Activated via `.gemini/skills/app-validator/`.
- **git-safety**: Activated via `.gemini/skills/git-safety/`.
