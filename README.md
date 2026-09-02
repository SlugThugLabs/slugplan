# SlugPlan (`slugplan`)

> CLI tool for managing in-repo engineering workspaces (`.planning/`) as a unified Confluence, Jira, and Tool Workspace hub for humans and AI coding agents.

---

## 1. What This Is

**SlugPlan** establishes and maintains the `.planning/` standard across your repositories. It guarantees that any AI coding agent (Claude, OpenAI Codex, Hermes, OpenCode, DeepSeek, Gemini) dropping into a project immediately knows:
1. Where system architecture and invariants live (`.planning/ARCHITECTURE.md` - Confluence).
2. Where active sprint tasks and milestones live (`.planning/jira/PROJECT_PLAN.md` - Jira).
3. Where architecture trade-offs live (`.planning/adr/` - ADRs).
4. Where developer tools store their state (`.planning/<tool>/`, e.g., `slugaudit`, `codeguards`).
5. That `docs/` is reserved strictly for end-users, and `src/` is pure application code.

---

## 2. Quick Start

```bash
# Initialize a project with the .planning/ workspace and AGENTS.md
slugplan init /path/to/project

# Check project compliance and detect misplaced internal docs in docs/
slugplan doctor /path/to/project

# Print the 5-point agent briefing
slugplan brief
```

---

## 3. Directory Layout Scaffolded by `slugplan`

```text
my-project/
├── AGENTS.md                 <-- Read automatically on turn 1 by AI coding agents
├── src/                      <-- Pure product code
├── docs/                     <-- End-user documentation ONLY
└── .planning/                <-- In-Repo Confluence + Jira + Tool Hub
    ├── README.md             <-- Guide explaining the workspace to any agent/engineer
    ├── ARCHITECTURE.md       <-- System Design RFC & Invariants (Source of Truth)
    ├── jira/
    │   └── PROJECT_PLAN.md   <-- Active sprint tasks & milestones
    ├── adr/
    │   └── 0001-init.md      <-- Architecture Decision Records
    ├── slugaudit/            <-- Tool evidence workspace (AST index / project.db)
    └── codeguards/           <-- Tool governance workspace (Rule check state)
```

---

## 4. Why This Solves the AI Workflow Problem

* **Zero Re-explaining:** You never have to explain your directory conventions or where notes go to new models. `AGENTS.md` and `.planning/README.md` anchor every session immediately.
* **Separation of Concerns:** End-user docs (`docs/`) stay pristine. Internal planning docs and tool caches stay in `.planning/`.
* **Tool Harmony:** Tools like `slugaudit` and `CodeGuards` naturally integrate into `.planning/<tool>/` without cluttering project roots.
