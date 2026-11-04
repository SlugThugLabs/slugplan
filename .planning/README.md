# .planning

This folder holds what is used to build this project. It is not part of the
product. End-user documentation goes in `docs/`, not here.

- `ARCHITECTURE.md`: the project's architecture requirements.
- Plans, decisions and notes for building the project.
- `<tool>/`: a development tool's working files, one folder per tool (for
  example `slugaudit/`). A tool creates and uses only its own folder and
  changes nothing else in `.planning/`.
