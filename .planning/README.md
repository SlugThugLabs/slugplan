# .planning/ — In-Repo Confluence, Jira & Tool Workspace

> This directory is the internal engineering hub for this project. It provides complete project context, architecture design docs, task tracking, and tool state directly inside the repository.

---

## Why `.planning/` Exists

In modern engineering (especially when collaborating with AI coding agents):
1. **`docs/` is for End-Users:** `docs/` contains public documentation, user manuals, and API guides. Internal architectural plans, meeting notes, and task checklists do NOT belong in `docs/`.
2. **`.planning/` is for Engineers & AI Agents:** It acts as an in-repo mirror of Confluence (RFCs, design docs) and Jira (sprints, task boards) so that any engineer or disposable AI agent has instant, version-controlled access to project truth without external tools.
3. **Clean Root & Source Tree:** Keeps `src/` and the repo root free from developer scratchpads, transient notes, and tool-specific database caches.

---

## Directory Structure

```text
.planning/
├── README.md                 <-- This guide (workspace standard & rules)
├── ARCHITECTURE.md           <-- System Design RFC & Invariants (Source of Truth)
├── jira/                     <-- Sprint & Task Board
│   └── PROJECT_PLAN.md       <-- Active milestones, tasks, and completion state
├── adr/                      <-- Architecture Decision Records ("Why we chose X over Y")
│   └── 0001-init.md
├── slugaudit/                <-- Tool Workspace (AST index, database evidence)
└── codeguards/               <-- Tool Workspace (Architecture enforcement state)
```

---

## How to Use This Hub

### 1. The Architecture RFC (`ARCHITECTURE.md`)
* Contains system layers, module dependencies, data flows, and security constraints.
* Must be reviewed and updated whenever system boundaries or contracts change.

### 2. The Task Board (`jira/PROJECT_PLAN.md`)
* Organizes active work into Phases / Milestones.
* Tracks pending, in-progress, and completed tasks.

### 3. Tool Workspaces (`.planning/<tool>/`)
* Tools like **SlugAudit** and **CodeGuards** store their project-scoped databases, indexes, and evidence here.
* Gitignore transient tool caches (like `project.db`, `*.wal`, `*.shm`) while keeping configuration committed.\n