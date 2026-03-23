# Push to BaseRock-AI GitHub

Step-by-step guide to add the BaseRock-AI remote and push this project there.

---

## Prerequisites

- Git installed and configured
- Access to the [BaseRock-AI](https://github.com/BaseRock-AI) GitHub organisation
- A Personal Access Token (PAT) or SSH key with write access to the org

---

## Step 1 — Create the repo on GitHub

1. Go to [https://github.com/organizations/BaseRock-AI/repositories/new](https://github.com/organizations/BaseRock-AI/repositories/new)
2. Set **Repository name** to `todo_web_service_python`
3. Leave it **empty** (no README, .gitignore, or licence)
4. Click **Create repository**

---

## Step 2 — Add the BaseRock-AI remote

Open a terminal in the project root and run:

```bash
cd /Users/sachinkumar/Desktop/todo_web_service_python

git remote add baserock https://github.com/BaseRock-AI/todo_web_service_python.git
```

Verify both remotes are now listed:

```bash
git remote -v
```

Expected output:

```
baserock  https://github.com/BaseRock-AI/todo_web_service_python.git (fetch)
baserock  https://github.com/BaseRock-AI/todo_web_service_python.git (push)
origin    https://github.com/sachin-sapientai/todo_web_service_python.git (fetch)
origin    https://github.com/sachin-sapientai/todo_web_service_python.git (push)
```

---

## Step 3 — Push to BaseRock-AI

```bash
git push -u baserock main
```

You will be prompted for your GitHub username and a Personal Access Token (PAT).
If you use SSH, replace the URL in Step 2 with:

```
git@github.com:BaseRock-AI/todo_web_service_python.git
```

---

## Step 4 — Verify

Open your browser and go to:

```
https://github.com/BaseRock-AI/todo_web_service_python
```

You should see the full project with all commits.

---

## Future pushes

To push new changes to both remotes at the same time:

```bash
git push origin main      # push to sachin-sapientai
git push baserock main    # push to BaseRock-AI
```

Or set up a single `git push all` shortcut:

```bash
git remote add all https://github.com/sachin-sapientai/todo_web_service_python.git
git remote set-url --add --push all https://github.com/sachin-sapientai/todo_web_service_python.git
git remote set-url --add --push all https://github.com/BaseRock-AI/todo_web_service_python.git

# Now a single command pushes to both:
git push all main
```

---

## Quick Reference

| Command | What it does |
|---|---|
| `git remote -v` | List all configured remotes |
| `git push baserock main` | Push to BaseRock-AI repo |
| `git push origin main` | Push to sachin-sapientai repo |
| `git log --oneline -5` | Show last 5 commits before pushing |
