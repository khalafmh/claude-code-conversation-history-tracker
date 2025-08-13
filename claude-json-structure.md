# Claude Code ~/.claude.json Structure Documentation

## Overview
The `~/.claude.json` file is Claude Code's primary configuration and state file that stores user preferences, project-specific settings, and **conversation history** for each project. This document provides a comprehensive guide to its structure and how to extract prompt history.

## File Location
- **Path**: `~/.claude.json` (in user's home directory)
- **Format**: JSON
- **Size**: Can grow large (500KB+) with extensive project history

## Top-Level Structure

### Global Configuration Keys

| Key | Type | Description |
|-----|------|-------------|
| `autoConnectIde` | boolean | Auto-connect to IDE settings |
| `autoUpdates` | boolean | Enable automatic updates |
| `cachedChangelog` | object | Cached changelog data |
| `changelogLastFetched` | string | Timestamp of last changelog fetch |
| `claudeMaxTier` | string | User's Claude subscription tier |
| `customApiKeyResponses` | object | Custom API key configurations |
| `fallbackAvailableWarningThreshold` | number | Warning threshold for fallback |
| `firstStartTime` | string | First application start timestamp |
| `hasAvailableMaxSubscription` | boolean | Max subscription availability |
| `hasAvailableSubscription` | boolean | Subscription status |
| `hasCompletedOnboarding` | boolean | Onboarding completion status |
| `hasIdeAutoConnectDialogBeenShown` | boolean | IDE auto-connect dialog shown |
| `hasSeenTasksHint` | boolean | Tasks hint display status |
| `hasUsedBackslashReturn` | boolean | Backslash return usage flag |
| `installMethod` | string | Installation method used |
| `isQualifiedForDataSharing` | boolean | Data sharing qualification |
| `lastOnboardingVersion` | string | Last onboarding version seen |
| `lastReleaseNotesSeen` | string | Last release notes version |
| `maxSubscriptionNoticeCount` | number | Max subscription notice count |
| `memoryUsageCount` | number | Memory usage counter |
| `numStartups` | number | Application startup count |
| `oauthAccount` | object | OAuth account information |
| `promptQueueUseCount` | number | Prompt queue usage counter |
| `recommendedSubscription` | string | Recommended subscription type |
| `s1mAccessCache` | object | Access cache data |
| `statsigModel` | object | Statsig model configuration |
| `subscriptionNoticeCount` | number | Subscription notice count |
| `subscriptionUpsellShownCount` | number | Upsell display count |
| `tipsHistory` | array | Tips shown to user |
| `userID` | string | Unique user identifier |
| **`projects`** | object | **Project-specific data including prompt history** |

## Project Structure (`projects` key)

Each project is stored with its absolute path as the key. For example:
```json
"projects": {
  "/home/user/Projects/my-app": { ... }
}
```

### Project-Level Keys

| Key | Type | Description |
|-----|------|-------------|
| **`history`** | array | **Conversation/prompt history (max 100 entries)** |
| `allowedTools` | array | Allowed tools for this project |
| `disabledMcpjsonServers` | array | Disabled MCP JSON servers |
| `enabledMcpjsonServers` | array | Enabled MCP JSON servers |
| `exampleFiles` | array | Example files for context |
| `exampleFilesGeneratedAt` | string | Example files generation timestamp |
| `hasClaudeMdExternalIncludesApproved` | boolean | External includes approval |
| `hasClaudeMdExternalIncludesWarningShown` | boolean | External includes warning shown |
| `hasCompletedProjectOnboarding` | boolean | Project onboarding status |
| `hasTrustDialogAccepted` | boolean | Trust dialog acceptance |
| `hasTrustDialogHooksAccepted` | boolean | Trust dialog hooks acceptance |
| `lastTotalWebSearchRequests` | number | Web search request count |
| `mcpContextUris` | array | MCP context URIs |
| `mcpServers` | object | MCP server configurations |
| `projectOnboardingSeenCount` | number | Onboarding seen count |

## Prompt History Structure

### History Array
- **Location**: `projects.<project_path>.history`
- **Type**: Array of history entries
- **Order**: Reverse chronological (most recent first)
- **Limit**: Maximum 100 entries per project
- **Rotation**: Older entries are removed when limit is exceeded

### History Entry Structure
Each history entry contains:

| Field | Type | Description |
|-------|------|-------------|
| `display` | string | The actual prompt text entered by the user |
| `pastedContents` | array/null | Additional content pasted with the prompt (typically empty array or null) |

Example:
```json
{
  "display": "Create a function to parse JSON",
  "pastedContents": []
}
```

## Extracting Prompt History

### 1. Get All Projects with History
```bash
# List all projects and their history count
jq '.projects | to_entries | map({project: .key, count: (.value.history // [] | length)})' ~/.claude.json
```

### 2. Extract History for Specific Project
```bash
# Get all prompts for a specific project
PROJECT="/home/user/Projects/my-app"
jq --arg proj "$PROJECT" '.projects[$proj].history[].display' ~/.claude.json

# Or with explicit path
jq '.projects["/home/user/Projects/my-app"].history[].display' ~/.claude.json
```

### 3. Export History to Text File
```bash
# Export with line numbers
PROJECT="/home/user/Projects/my-app"
jq -r --arg proj "$PROJECT" '.projects[$proj].history[].display' ~/.claude.json | nl > prompts.txt

# Export with timestamps (reverse order to get chronological)
jq -r --arg proj "$PROJECT" '.projects[$proj].history | reverse | .[].display' ~/.claude.json > prompts_chronological.txt
```

### 4. Search Across All Projects
```bash
# Find all prompts containing a keyword
jq -r '.projects | to_entries[] | .value.history[]?.display | select(contains("function"))' ~/.claude.json

# Find prompts with project context
jq -r '.projects | to_entries[] | {project: .key, prompts: [.value.history[]?.display]} | select(.prompts | length > 0)' ~/.claude.json
```

### 5. Advanced Queries

#### Get Last N Prompts from All Projects
```bash
jq -r '.projects | to_entries[] | {project: .key, last_prompt: .value.history[0].display} | select(.last_prompt != null)' ~/.claude.json
```

#### Export All History to CSV
```bash
jq -r '.projects | to_entries[] | .key as $proj | .value.history[]? | [$proj, .display] | @csv' ~/.claude.json > all_prompts.csv
```

#### Count Total Prompts Across All Projects
```bash
jq '[.projects[].history | length] | add' ~/.claude.json
```

#### Find Projects with Most Activity
```bash
jq '.projects | to_entries | map({project: .key, count: (.value.history | length)}) | sort_by(.count) | reverse | .[0:10]' ~/.claude.json
```

## Python Script for History Extraction

```python
#!/usr/bin/env python3
import json
import os
from pathlib import Path
from datetime import datetime

def extract_claude_history():
    """Extract all Claude Code prompt history from ~/.claude.json"""
    
    claude_json = Path.home() / '.claude.json'
    
    if not claude_json.exists():
        print("Error: ~/.claude.json not found")
        return
    
    with open(claude_json, 'r') as f:
        data = json.load(f)
    
    projects = data.get('projects', {})
    
    # Create output directory
    output_dir = Path('claude_history_export')
    output_dir.mkdir(exist_ok=True)
    
    total_prompts = 0
    
    for project_path, project_data in projects.items():
        history = project_data.get('history', [])
        
        if not history:
            continue
        
        # Sanitize project path for filename
        safe_name = project_path.replace('/', '_').strip('_')
        output_file = output_dir / f"{safe_name}.txt"
        
        with open(output_file, 'w') as f:
            f.write(f"Project: {project_path}\n")
            f.write(f"Total prompts: {len(history)}\n")
            f.write("=" * 50 + "\n\n")
            
            # Reverse to get chronological order
            for i, entry in enumerate(reversed(history), 1):
                f.write(f"[{i}] {entry.get('display', '')}\n")
                if entry.get('pastedContents'):
                    f.write(f"    [Pasted content attached]\n")
                f.write("\n")
        
        total_prompts += len(history)
        print(f"Exported {len(history)} prompts from {project_path}")
    
    print(f"\nTotal prompts exported: {total_prompts}")
    print(f"Files saved in: {output_dir}")

if __name__ == "__main__":
    extract_claude_history()
```

## Important Notes

1. **Privacy**: The history contains all your prompts, so be careful when sharing this file
2. **Size Limit**: Each project maintains only the last 100 prompts
3. **Persistence**: History persists across Claude Code sessions
4. **Project Association**: History is tied to the absolute path of the project directory
5. **No Timestamps**: History entries don't include timestamps - only the relative order is preserved
6. **Response Not Stored**: Only user prompts are stored, not Claude's responses
7. **No Session Separation**: There's no way to distinguish between different conversation sessions

## Troubleshooting

### File Too Large
If the file is too large to process:
```bash
# Check file size
ls -lh ~/.claude.json

# Extract specific project only
jq '.projects["/path/to/project"]' ~/.claude.json > project_data.json
```

### Memory Issues with jq
For very large files, use streaming:
```bash
# Stream process (more memory efficient)
jq -c '.projects | keys[]' ~/.claude.json | while read proj; do
    jq --arg p "$proj" '.projects[$p].history' ~/.claude.json > "history_${proj//\//_}.json"
done
```

## Security Considerations

- The file may contain sensitive project paths and prompts
- No passwords or API keys should be in prompt history
- Consider excluding from backups if contains sensitive information
- File permissions should be user-readable only (600)

```bash
# Check permissions
ls -l ~/.claude.json

# Set secure permissions
chmod 600 ~/.claude.json
```