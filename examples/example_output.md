# Example Output

## Interactive Menu
```
==============================================================
CLAUDE CODE PROJECTS WITH HISTORY
==============================================================
  1. [100 prompts] /home/user/Projects/my-web-app
  2. [ 85 prompts] /home/user/Projects/data-analysis
  3. [ 42 prompts] /home/user/Projects/cli-tool
==============================================================
  0. Export ALL projects
  q. Quit
==============================================================

Select project number: 
```

## JSON Sync Output
```json
{
  "project_path": "/home/user/Projects/my-web-app",
  "project_name": "my-web-app",
  "last_updated": "2025-08-13T14:18:42.777851",
  "prompts": [
    {
      "text": "Help me create a React component for user authentication",
      "hash": "29e5e056fdbebfad",
      "has_pasted_content": false,
      "first_seen": "2025-08-13T14:18:42.777851"
    },
    {
      "text": "Add error handling to the login form",
      "hash": "03b8960242b5254f",
      "has_pasted_content": true,
      "first_seen": "2025-08-13T14:18:42.777851"
    }
  ]
}
```

## Markdown Export Sample
```markdown
# Claude Code Conversation History

## Project: my-web-app

### Metadata

- **Full Path:** `/home/user/Projects/my-web-app`
- **Total Prompts:** 100
- **Export Date:** 2025-08-13 14:18:42

---

## Conversation History

> **Note:** Prompts are shown in chronological order (oldest first)

### Prompt #1

`Help me create a React component for user authentication`

---

### Prompt #2

> **Note:** This prompt included pasted content

`Add error handling to the login form`

---
```