#!/usr/bin/env python3
"""slugplan — CLI tool for managing in-repo engineering workspace (.planning/).

Acts as the in-repo Confluence + Jira hub for human engineers and AI coding agents.
"""

import argparse
import hashlib
import os
import sys
from pathlib import Path

PLANNING_DIR = ".planning"

AGENTS_MD_TEMPLATE = """# Engineering Workspace Standard (.planning)

This repository follows the **SlugPlan** convention: `.planning/` serves as the in-repo Confluence, Jira, and Tool Workspace.

## Quick Orientation for AI Agents & Engineers:
1. **Source Code (`src/` or `lib/`):** Pure product code only. No planning notes, temporary test scratchpads, or loose docs.
2. **End-User Docs (`docs/`):** Public / user-facing documentation only (guides, installation, API references). Never put internal developer notes or architecture plans in `docs/`.
3. **Architecture RFC / Confluence (`.planning/ARCHITECTURE.md`):** The canonical source of truth for system layers, module boundaries, allowed dependencies, and invariants. Read this BEFORE writing or modifying code.
4. **Task Board / Jira (`.planning/jira/PROJECT_PLAN.md`):** Active epics, sprint milestones, and tasks. Check your active task here, and update progress as work is completed.
5. **Decisions / ADRs (`.planning/adr/`):** Architecture Decision Records documenting why specific trade-offs or technologies were chosen.
6. **Tool Workspaces (`.planning/<tool>/`):** Dedicated workspaces for development tools (e.g. `.planning/slugaudit/`, `.planning/codeguards/`). These store tool evidence and caches.

## Operating Rules for AI Agents:
- **Never guess architecture:** Always read `.planning/ARCHITECTURE.md` first.
- **Never clutter root or `docs/`:** Internal planning belongs strictly in `.planning/`.
- **Stay scoped:** Work only on the active task assigned in `.planning/jira/PROJECT_PLAN.md`.
"""

README_TEMPLATE = """# .planning/ — In-Repo Confluence, Jira & Tool Workspace

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
* Gitignore transient tool caches (like `project.db`, `*.wal`, `*.shm`) while keeping configuration committed.
"""

ARCHITECTURE_TEMPLATE = """---
modules: []
layers: []
allowed_dependencies: {}
enforce: []
---

# Architecture & System Design (Source of Truth)

> Canonical engineering document for system architecture, component boundaries, and invariants.

## 1. System Overview
<!-- High-level summary of what this system does and how components interact -->

## 2. Layers & Modules
<!-- Define architectural layers (e.g., transport, core, domain, storage) and their responsibilities -->

## 3. Dependency Rules & Boundaries
<!-- Explicitly state which modules are allowed to import from which other modules -->

## 4. Invariants & Quality Standards
<!-- Non-negotiable rules (e.g. error handling, logging, testing standards) -->
"""

PROJECT_PLAN_TEMPLATE = """# Project Plan & Sprint Board

> Active roadmap, milestones, and task checklists.

---

## Current Milestone: Milestone 1 — Initial Setup

### Active Tasks
- [ ] Task 1.1: Core architecture specification
- [ ] Task 1.2: Base engine implementation
- [ ] Task 1.3: Integration tests and verification

---

## Backlog / Future Milestones
- [ ] Milestone 2: Advanced features & optimizations
- [ ] Milestone 3: Production hardening & release
"""

ADR_TEMPLATE = """# ADR 0001: Initial Architecture & Workspace Convention

## Status
Accepted

## Context
We need a standardized, reproducible way for humans and AI coding agents to collaborate without architectural drift or cluttered repositories.

## Decision
Adopt the `.planning/` workspace convention (SlugPlan) as the in-repo Confluence, Jira, and Tool Workspace hub.

## Consequences
- Clean root directory and clean `docs/` folder dedicated to end-users.
- Deterministic onboarding for AI agents via `AGENTS.md` and `.planning/ARCHITECTURE.md`.
"""


def init_workspace(target_dir: Path, force: bool = False):
    """Scaffold .planning/ and AGENTS.md in the target project."""
    planning_path = target_dir / PLANNING_DIR
    jira_path = planning_path / "jira"
    adr_path = planning_path / "adr"
    agents_path = target_dir / "AGENTS.md"

    jira_path.mkdir(parents=True, exist_ok=True)
    adr_path.mkdir(parents=True, exist_ok=True)

    files_to_create = [
        (planning_path / "README.md", README_TEMPLATE),
        (planning_path / "ARCHITECTURE.md", ARCHITECTURE_TEMPLATE),
        (jira_path / "PROJECT_PLAN.md", PROJECT_PLAN_TEMPLATE),
        (adr_path / "0001-init.md", ADR_TEMPLATE),
        (agents_path, AGENTS_MD_TEMPLATE),
    ]

    created = 0
    for path, content in files_to_create:
        if not path.exists() or force:
            path.write_text(content.strip() + "\\n")
            print(f"  + Created {path.relative_to(target_dir)}")
            created += 1
        else:
            print(f"  - Exists (skipped) {path.relative_to(target_dir)}")

    # Update .gitignore if present or create basic one
    gitignore_path = target_dir / ".gitignore"
    ignore_entry = ".planning/*/*.db\\n.planning/*/*.db-wal\\n.planning/*/*.db-shm\\n"
    if gitignore_path.exists():
        existing_gi = gitignore_path.read_text()
        if ".planning/*/*.db" not in existing_gi:
            with open(gitignore_path, "a") as f:
                f.write("\\n# Tool caches in .planning\\n" + ignore_entry)
            print("  + Updated .gitignore with tool artifact exclusions")
    else:
        gitignore_path.write_text("# Tool caches in .planning\\n" + ignore_entry)
        print("  + Created .gitignore with tool artifact exclusions")

    print(f"\\nSlugPlan initialized successfully in {target_dir} ({created} files created).")


def check_doctor(target_dir: Path):
    """Verify health and compliance of .planning workspace."""
    print(f"Checking SlugPlan compliance for: {target_dir}\\n")
    planning_path = target_dir / PLANNING_DIR
    agents_path = target_dir / "AGENTS.md"

    checks = [
        ("AGENTS.md entrypoint", agents_path.exists()),
        (".planning/ directory", planning_path.is_dir()),
        (".planning/README.md guide", (planning_path / "README.md").exists()),
        (".planning/ARCHITECTURE.md (Confluence RFC)", (planning_path / "ARCHITECTURE.md").exists()),
        (".planning/jira/ (Task Board)", (planning_path / "jira").is_dir()),
        (".planning/jira/PROJECT_PLAN.md", (planning_path / "jira" / "PROJECT_PLAN.md").exists()),
        (".planning/adr/ (Decisions)", (planning_path / "adr").is_dir()),
    ]

    all_passed = True
    for name, passed in checks:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  [{status}] {name}")
        if not passed:
            all_passed = False

    # Check for misplaced internal docs in docs/
    docs_dir = target_dir / "docs"
    if docs_dir.is_dir():
        bad_patterns = ["*plan*", "*arch*", "*todo*", "*jira*", "*draft*"]
        found_misplaced = []
        for pat in bad_patterns:
            found_misplaced.extend(list(docs_dir.glob(pat)))
        if found_misplaced:
            print("\\n  [!] Warning: Found potential internal planning files in docs/ (should be in .planning/):")
            for f in set(found_misplaced):
                print(f"      - {f.relative_to(target_dir)}")

    print("\\nStatus: " + ("Workspace is healthy and fully compliant!" if all_passed else "Some required files are missing. Run 'slugplan init' to fix."))


def print_brief(target_dir: Path):
    """Output concise agent context briefing."""
    print("════════════════════════════════════════════════════════════")
    print(" SLUGPLAN AGENT BRIEFING (.planning Workspace)")
    print("════════════════════════════════════════════════════════════")
    print("1. Read '.planning/ARCHITECTURE.md' for system architecture & layer rules.")
    print("2. Read '.planning/jira/PROJECT_PLAN.md' for active tasks and sprint goals.")
    print("3. Check '.planning/adr/' for past architectural decisions.")
    print("4. Keep 'src/' pure product code; keep 'docs/' for end-users only.")
    print("5. Tool state and caches live inside '.planning/<tool-name>/'.")
    print("════════════════════════════════════════════════════════════")


def main():
    parser = argparse.ArgumentParser(description="SlugPlan: In-Repo Confluence, Jira & Tool Workspace Manager")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    init_p = subparsers.add_parser("init", help="Initialize .planning workspace and AGENTS.md in a project")
    init_p.add_argument("path", nargs="?", default=".", help="Project root directory (default: current dir)")
    init_p.add_argument("--force", action="store_true", help="Overwrite existing templates")

    doc_p = subparsers.add_parser("doctor", help="Check workspace compliance and detect misplaced docs")
    doc_p.add_argument("path", nargs="?", default=".", help="Project root directory (default: current dir)")

    brief_p = subparsers.add_parser("brief", help="Print the 5-point agent context briefing")
    brief_p.add_argument("path", nargs="?", default=".", help="Project root directory (default: current dir)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    target = Path(args.path).resolve()
    if args.command == "init":
        init_workspace(target, force=args.force)
    elif args.command == "doctor":
        check_doctor(target)
    elif args.command == "brief":
        print_brief(target)


if __name__ == "__main__":
    main()
