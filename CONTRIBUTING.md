# Contributing to Claude Conversations Archive

Thank you for your interest in contributing to this project! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and considerate in all interactions. We welcome contributions from everyone.

## How to Contribute

### Reporting Issues

1. Check if the issue already exists in the [Issues](https://github.com/khalafmh/claude-code-conversation-history-tracker/issues) section
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce (if applicable)
   - Expected vs actual behavior
   - Your environment details (OS, Python version)

### Suggesting Enhancements

1. Open an issue with the "enhancement" label
2. Clearly describe the feature and its benefits
3. Provide use cases and examples

### Submitting Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature-name`)
3. Make your changes
4. Add or update tests as needed
5. Ensure all tests pass
6. Commit with clear messages
7. Push to your fork
8. Open a Pull Request

## Development Setup

### Prerequisites

- Python 3.8 or higher
- `uv` package manager (recommended)

### Setting Up Development Environment

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/claude-code-conversation-history-tracker.git
cd claude-code-conversation-history-tracker

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
uv pip install -e ".[dev]"
```

## Testing Guidelines

### Running Tests

```bash
# Run all tests with coverage
python -m pytest test_export_claude_history.py --cov=export_claude_history --cov-report=term-missing

# Run specific test
python -m pytest test_export_claude_history.py::TestClaudeHistoryExporter::test_load_data_success

# Generate HTML coverage report
python -m pytest test_export_claude_history.py --cov=export_claude_history --cov-report=html
```

### Test Coverage Requirements

- **Current coverage**: 94.77%
- **Minimum required**: 90%
- **Standard for new code**: Must maintain ≥90% overall coverage
- **Goal**: Write comprehensive tests that catch real bugs, not just meet numbers

**Important**: Testing is not optional. Every PR must include tests for new functionality and maintain our 90% coverage standard. Good tests are as important as the code itself.

### Writing Tests

When adding new features:

1. Write tests BEFORE implementing the feature (TDD approach encouraged)
2. Test both happy paths and edge cases
3. Use meaningful test names that describe what's being tested
4. Mock external dependencies (file system, user input)
5. Keep tests focused and independent

Example test structure:
```python
def test_feature_description(self):
    """Test that feature does X when given Y"""
    # Arrange - set up test data
    
    # Act - execute the feature
    
    # Assert - verify the outcome
```

## Code Style Guidelines

### Python Code

- Follow PEP 8 conventions
- Use type hints where appropriate
- Maximum line length: 120 characters
- Use descriptive variable names
- Add docstrings to all public functions/classes

### Documentation

- Update README.md if adding user-facing features
- Update docstrings for API changes
- Include examples for complex features
- Keep documentation concise and clear

### Commit Messages

Follow conventional commit format:
```
type: brief description

Longer explanation if needed
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions/changes
- `refactor`: Code refactoring
- `style`: Formatting changes
- `chore`: Maintenance tasks

## Pull Request Process

1. **Before submitting**:
   - Rebase on latest main branch
   - Ensure all tests pass
   - Verify coverage is ≥90% (`python -m pytest test_export_claude_history.py --cov=export_claude_history`)
   - Update documentation if needed

2. **PR Description should include**:
   - What changes were made
   - Why they were needed
   - Any breaking changes
   - Testing performed

3. **Review process**:
   - All PRs require at least one review
   - Address review feedback promptly
   - Keep discussions focused and constructive

## Areas for Contribution

### High Priority

- Performance improvements for large JSON files
- Additional export formats (CSV, SQL)
- Session separation detection
- Claude response parsing (if available in future)

### Good First Issues

- Improve error messages
- Add more examples to documentation
- Enhance CLI help text
- Add input validation

### Future Enhancements

- GUI interface
- Cloud storage integration
- Conversation analytics
- Multi-project batch operations

## Questions?

If you have questions about contributing, feel free to:
1. Open an issue with the "question" label
2. Check existing issues and discussions

## Recognition

Contributors will be acknowledged in the project documentation. Thank you for helping improve this tool!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.