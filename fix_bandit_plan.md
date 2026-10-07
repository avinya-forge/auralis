I will update `src/services/metadata_service.py` to fix multiple bandit warnings:
1.  **[B404, B603, B607]**: Fix the subprocess calls by resolving the external binary path (`fpcalc`) using `shutil.which()`, explicitly adding `# nosec` to suppress B404/B603, and updating the command array.
2.  **[B105]**: Fix the hardcoded password string by reading the Discogs token from an environment variable, defaulting to an empty string, or adding `# nosec B105` if it's meant to be a literal placeholder string. According to memory, we should replace hardcoded secrets with dynamic environment variable lookups (e.g., `os.environ.get('VAR_NAME', '')`) so they default to an empty string.

I will also need to add `import shutil` to the top of `src/services/metadata_service.py` if not already present.

Let me write the plan.
