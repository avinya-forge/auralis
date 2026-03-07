# standards/ultra_lean.md

## pipeline laws
1. **test fortress:** all code (core, gui, cli, utils) must be covered by tests. target coverage: 95%. mocking is mandatory for ui components. no regression is acceptable.
2. **lint zero:** zero tolerance for linting errors. `flake8` and `mypy` (strict mode, `disallow_untyped_defs = true`, no global ignores) must pass clean.
3. **complexity cap:** no function shall exceed a cyclomatic complexity of 10. refactor ruthlessly.
4. **latest stable env only:** always use the latest stable environment and dependencies unless strictly impossible.

## definition of done (dod)
a task is only "done" when it meets the following atomic criteria:
- [ ] **tested:** unit tests added/updated covering happy paths and edge cases.
- [ ] **linted:** passes all static analysis checks.
- [ ] **optimized:** o(n) or better complexity verified.
- [ ] **secured:** input sanitized, dependencies checked.
- [ ] **documented:** docstrings and relevant markdown updated.

## python standards
- **style guide:** follow pep 8.
- **line length:** 127 characters.
- **docstrings:** google style docstrings for all modules, classes, and functions.
- **type hinting:** use type hints for all function arguments and return values.
- **imports:** sort imports using `isort` (profile: black).
- **formatting:** use `black` for code formatting.

## git standards
- **commit messages:** descriptive, imperative mood (e.g., "add feature x", not "added feature x").
- **branching:** create feature branches from `main`. use descriptive names (e.g., `feature/add-wxpython-support`).
- **pull requests:** meaningful description, link to backlog item.

## Component Reusability Standards

- Avoid one-off components. Use and contribute to the unified framework.
- Any API MUST be documented first with a Swagger/OpenAPI contract in `docs/swagger.yaml` and mock data before implementation begins.
