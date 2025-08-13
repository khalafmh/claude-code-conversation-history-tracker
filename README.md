# Claude Conversations Archive

A comprehensive toolkit for exporting, archiving, and managing your Claude Code conversation history.

> **⚠️ IMPORTANT**: This is an **unofficial, third-party tool** not affiliated with Anthropic. Please read the [DISCLAIMER](DISCLAIMER.md) before use.
> 
> **🤖 AI-Generated**: This project was primarily created using AI assistance. See [AI_ATTRIBUTION.md](AI_ATTRIBUTION.md) for full transparency.

## Overview

This project provides tools to extract and archive conversation history from Claude Code's `~/.claude.json` configuration file. It supports both one-time exports and incremental syncing with intelligent deduplication.

## Features

- 📚 **Complete History Export** - Extract all conversation prompts from any Claude Code project
- 🔄 **Incremental Sync** - Automatically deduplicate and sync new prompts while preserving history
- 📝 **Multiple Export Formats** - Export to Markdown for reading or JSON for data processing
- 🕐 **Timestamp Tracking** - Track when each prompt was first synchronized
- 🔍 **Search Functionality** - Search across all your conversation history
- 📊 **Statistics** - View usage statistics across all projects
- 🤖 **Automatic Syncing** - Set up cron job for periodic synchronization

## Installation

1. Clone this repository:
```bash
git clone https://github.com/khalafmh/claude-code-conversation-history-tracker.git
cd claude-code-conversation-history-tracker
```

2. Ensure Python 3.8+ is installed:
```bash
python3 --version
```

3. **For users**: No additional dependencies required - uses Python standard library only

4. **For developers**: Install development dependencies using `uv`:
```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dev dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

## Usage

### Interactive Mode

Run without arguments for an interactive project selection menu:
```bash
python export_claude_history.py
```

### Export to Markdown

Export a single project or all projects to markdown format:
```bash
# Interactive selection
python export_claude_history.py

# Export all projects
python export_claude_history.py --all

# Custom output directory
python export_claude_history.py --all --output /path/to/output
```

### Sync to JSON

Incrementally sync conversation history to JSON files with deduplication:
```bash
# Interactive selection
python export_claude_history.py --sync

# Sync all projects
python export_claude_history.py --sync-all

# Custom output directory
python export_claude_history.py --sync-all --output /path/to/storage
```

### Search History

Search for prompts containing specific keywords:
```bash
python export_claude_history.py --search "function"
```

### View Statistics

Display statistics about your conversation history:
```bash
python export_claude_history.py --stats
```

### List Projects

List all projects with conversation history:
```bash
python export_claude_history.py --list
```

## Automatic Syncing

Set up a cron job to automatically sync your conversation history every 3 hours:

```bash
./setup_cron.sh
```

This will:
- Run every 3 hours at minute 0 (00:00, 03:00, 06:00, etc.)
- Sync all projects with deduplication
- Log output to `claude_history_json/sync.log`

To monitor sync activity:
```bash
tail -f claude_history_json/sync.log
```

To remove the cron job:
```bash
crontab -e  # Then delete the line containing export_claude_history.py
```

## File Structure

```
claude-conversations/
├── export_claude_history.py   # Main export script
├── test_export_claude_history.py # Unit tests (94.77% coverage)
├── setup_cron.sh              # Cron job setup script
├── pyproject.toml             # Project configuration
├── .coveragerc                # Test coverage settings
├── claude-json-structure.md   # Documentation of ~/.claude.json structure
├── LICENSE                    # MIT License
├── README.md                  # This file
├── DISCLAIMER.md              # Important usage disclaimers
├── AI_ATTRIBUTION.md          # AI development transparency
├── .gitignore                 # Excludes generated files from git
├── .venv/                     # Virtual environment (git-ignored)
├── htmlcov/                   # Coverage HTML reports (git-ignored)
├── claude_history_json/       # JSON sync output directory (git-ignored)
│   ├── project_name_history.json
│   └── sync.log              # Cron job log file
└── claude_history_export_*/   # Markdown export directories (git-ignored)
    ├── project_name.md
    └── INDEX.md
```

## JSON Output Format

Each project's JSON file contains:
```json
{
  "project_path": "/full/path/to/project",
  "project_name": "project-name",
  "last_updated": "2025-08-13T14:18:42.777851",
  "prompts": [
    {
      "text": "The actual prompt text",
      "hash": "29e5e056fdbebfad",
      "has_pasted_content": false,
      "first_seen": "2025-08-13T14:18:42.777851"
    }
  ]
}
```

## Markdown Output Format

Exported markdown files include:
- Project metadata (path, total prompts, export date)
- Configuration details (allowed tools, MCP servers)
- Chronologically ordered conversation history
- Visual indicators for prompts with pasted content

## Deduplication Algorithm

The sync feature uses intelligent deduplication that:
1. Generates hashes for each prompt to identify duplicates
2. Detects overlap sequences between existing and new prompts
3. Maintains chronological order while avoiding duplicates
4. Preserves the original `first_seen` timestamp for existing prompts

## Limitations

- Claude Code stores only the last 100 prompts per project
- Individual message timestamps are not available in ~/.claude.json
- Only user prompts are stored, not Claude's responses
- No session separation information is available

## Example Output

See [examples/example_output.md](examples/example_output.md) for sample outputs in both JSON and Markdown formats.

## Technical Documentation

For detailed information about the ~/.claude.json file structure and extraction methods, see [claude-json-structure.md](claude-json-structure.md).

## Privacy & Security

⚠️ **Your conversation history is sensitive data!**

- The history contains all your prompts, handle exported files with care
- JSON files may contain sensitive project paths and prompts
- Consider encrypting exports if they contain sensitive information
- The .gitignore file excludes all generated files from version control
- Review exports before sharing them with anyone
- You are responsible for compliance with any applicable data protection regulations

**Please read the full [DISCLAIMER](DISCLAIMER.md) for important information about data privacy, security, and usage responsibilities.**

## Development

### Running Tests

The project includes comprehensive unit tests with excellent code coverage (currently 94.77%). We maintain a **minimum coverage requirement of 90%**.

```bash
# Activate virtual environment
source .venv/bin/activate

# Run tests with coverage report
python -m pytest test_export_claude_history.py --cov=export_claude_history --cov-report=term-missing

# Generate HTML coverage report
python -m pytest test_export_claude_history.py --cov=export_claude_history --cov-report=html
# View report: open htmlcov/index.html
```

Testing is crucial for maintaining code quality and preventing regressions. All new features should include appropriate tests.

### Project Structure

```
├── export_claude_history.py   # Main script
├── test_export_claude_history.py  # Comprehensive test suite
├── pyproject.toml             # Project configuration and dependencies
├── .coveragerc                # Coverage configuration
└── .gitignore                 # Includes test artifacts
```

### Development Dependencies

- **pytest**: Testing framework
- **pytest-cov**: Coverage plugin for pytest
- **pytest-mock**: Mock object library
- **coverage**: Code coverage measurement

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

Quick overview:
1. Fork the repository
2. Create a feature branch
3. Write tests (maintain ≥90% coverage)
4. Make your changes
5. Submit a pull request

Testing is a core requirement - all new code must include tests to maintain our minimum 90% coverage standard.

For bug reports and feature requests, please use the [GitHub Issues](https://github.com/khalafmh/claude-code-conversation-history-tracker/issues) page.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Mahdi AlKhalaf <m@mahdi.pro>

## AI Attribution

This project was created with significant assistance from Claude (Anthropic's AI assistant). The majority of the code, documentation, and repository structure were generated through AI-assisted development using Claude Code.

### AI Contributions Include:
- Core Python script implementation
- Documentation and technical writing
- Code structure and algorithm design
- Testing and debugging approaches
- Repository setup and configuration

This project serves as both a useful tool and an example of AI-assisted software development.

---

🤖 Built to preserve and analyze Claude Code conversations  
🤝 Created through human-AI collaboration