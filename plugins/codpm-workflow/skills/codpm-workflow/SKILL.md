---
name: codpm-workflow
description: Run codpm-workflow from the installed public package CLI.
---

# codpm-workflow

This public workflow skill is for a fresh public repository install.

Install the package first:

```bash
python -m pip install git+https://github.com/YaofeiHe/codpm-public.git
```

Use the installed CLI or module entrypoint; do not call a private local checkout path.

```bash
codpm --help
```

Do not read local credentials, private runtime directories, `.env`, tokens, cookies, browser profiles, or host-specific paths.
