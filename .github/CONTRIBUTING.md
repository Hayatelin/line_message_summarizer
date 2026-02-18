# Contributing to LINE Message Daily Summary System

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## 📋 Code of Conduct

We are committed to providing a welcoming and inspiring community for all. Please read and adhere to our principles:

- Be respectful and inclusive
- Focus on constructive criticism
- Welcome diverse perspectives
- Report issues appropriately

## 🚀 How to Contribute

### Reporting Bugs

When reporting a bug, please include:

1. **Clear description** of the issue
2. **Steps to reproduce** the problem
3. **Expected behavior** and actual behavior
4. **Environment information**:
   - Python version
   - LINE Bot SDK version
   - Operating System
   - Relevant dependencies

**Example Issue:**
```
Title: LineSender fails when summary file is empty

Description:
When a summary file is empty, LineSender throws an exception instead of handling gracefully.

Steps to Reproduce:
1. Create an empty summary file
2. Call send_summary() with the empty file
3. Error is raised

Expected:
Should skip empty file or log a warning

Actual:
ValueError is raised
```

### Suggesting Enhancements

Enhancement suggestions are welcome! Please provide:

1. **Detailed description** of the enhancement
2. **Motivation** for the change
3. **Possible implementation** approach (if applicable)
4. **Potential drawbacks** or considerations

**Example Enhancement:**
```
Title: Add Telegram notification for failed executions

Description:
Add optional Telegram notifications when the daily pipeline fails.

Motivation:
Users would be immediately notified of failures without checking logs.

Implementation:
- Add TELEGRAM_BOT_TOKEN to .env
- New Notifier class in src/utils/notifier.py
- Call notifier.send_alert() in exception handlers
```

### Submitting Pull Requests

1. **Fork the repository** and create your branch from `main`
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Follow the commit message convention** (Conventional Commits)
   ```
   feat(component): add new feature
   fix(component): resolve issue
   docs: update documentation
   refactor: improve code structure
   test: add/update tests
   chore: update dependencies
   ```

3. **Write or update tests** for your changes
   - All tests must pass: `pytest tests/ -v`
   - Maintain >80% code coverage
   - Test both success and failure cases

4. **Update documentation**
   - Update README if adding new features
   - Add docstrings to functions
   - Update CHANGELOG.md

5. **Push your changes** and create a Pull Request
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Follow the PR template** (if provided)

## 🔍 Code Style and Standards

### Python Code Style

We follow PEP 8 with these conventions:

```python
# Type hints are required
def get_group_messages(group_id: str, date: str) -> List[dict]:
    """Fetch group messages from LINE API.

    Args:
        group_id: LINE group ID
        date: Target date in YYYY-MM-DD format

    Returns:
        List of message dictionaries

    Raises:
        ValueError: If date format is invalid
        ApiException: If LINE API call fails
    """
    pass

# Use descriptive variable names
user_messages = []  # Good
msgs = []  # Avoid

# Add comments for complex logic
# Calculate importance score based on classification and word frequency
importance = 0.4 * category_weight + 0.3 * frequency_weight + 0.3 * length_weight
```

### Naming Conventions

- **Classes**: PascalCase (e.g., `LineSender`, `MessageParser`)
- **Functions/Methods**: snake_case (e.g., `get_group_members`, `remove_duplicates`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_RETRIES`, `DEFAULT_TIMEOUT`)
- **Private Methods**: Prefix with underscore (e.g., `_validate_input`)

### Docstring Format

Use Google-style docstrings:

```python
def send_summary(self, user_id: str, summary_file: str, max_retries: int = 3) -> bool:
    """Send summary to LINE user.

    Args:
        user_id: LINE user ID to send message to
        summary_file: Path to summary markdown file
        max_retries: Maximum number of retry attempts (default: 3)

    Returns:
        True if sent successfully, False otherwise

    Raises:
        FileNotFoundError: If summary file does not exist
        ValueError: If user_id is empty
    """
    pass
```

## 🧪 Testing Requirements

### Test Coverage

- **Minimum coverage**: 80%
- All public functions must have tests
- Test both happy path and error cases
- Use meaningful test names

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_crawler.py -v

# Run with coverage report
pytest tests/ --cov=src --cov-report=html

# Run a single test
pytest tests/test_crawler.py::TestLineHandler::test_line_handler_init_valid_token -v
```

### Test Structure

```python
class TestMyComponent:
    """Tests for MyComponent class"""

    def test_function_valid_input(self):
        """Test function with valid input"""
        # Arrange
        input_data = {"key": "value"}

        # Act
        result = my_function(input_data)

        # Assert
        assert result is not None
        assert result["status"] == "success"

    def test_function_invalid_input(self):
        """Test function with invalid input"""
        with pytest.raises(ValueError):
            my_function(None)

    @pytest.mark.asyncio
    async def test_async_function(self):
        """Test async function"""
        result = await async_function()
        assert result is True
```

## 📝 Git Workflow

### Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Test additions or updates
- `chore`: Build, dependencies, configuration
- `perf`: Performance improvements

**Examples:**
```
feat(crawler): add pagination support for large groups

fix(sender): handle empty summary files gracefully

docs(readme): add version history section

test(processor): add tests for duplicate detection

refactor(scheduler): improve error handling
```

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation
- `refactor/description` - Code improvements

Example: `feature/add-telegram-notifications`

## 🔄 PR Review Process

### Before Submitting

1. ✅ All tests pass locally: `pytest tests/ -v`
2. ✅ Code follows style guidelines
3. ✅ Docstrings are added/updated
4. ✅ CHANGELOG.md is updated
5. ✅ No merge conflicts with `main` branch
6. ✅ Changes are focused (not too broad)

### Review Checklist

Reviewers will check:

- ✅ Code quality and style compliance
- ✅ Test coverage and passing tests
- ✅ Documentation completeness
- ✅ Performance impact
- ✅ Security considerations
- ✅ Backward compatibility

## 📚 Development Setup

### Prerequisites

- Python 3.8+
- Git
- Virtual environment

### Quick Setup for Windows Users

For Windows developers, use the automated setup script:

```powershell
# In PowerShell, navigate to project directory
cd line_message_summarizer

# Run one-click setup (creates venv, installs dependencies, generates .env)
.\setup_windows.ps1

# Edit .env with your credentials
notepad .env
```

See [WINDOWS_DEPLOYMENT.md](../WINDOWS_DEPLOYMENT.md) for complete Windows setup guide.

### Manual Setup Steps (All Platforms)

```bash
# Clone the repository
git clone https://github.com/Hayatelin/line_message_summarizer.git
cd line_message_summarizer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v
```

### Environment Configuration

Create `.env` file with required credentials:

```bash
cp .env.example .env
# Edit .env with your credentials
```

## 🚢 Release Process

When a new version is ready:

1. **Update CHANGELOG.md** with all changes
2. **Update version number** in relevant files
3. **Update README.md** if needed
4. **Create git tag**: `git tag -a v1.2.0 -m "Release v1.2.0"`
5. **Push to GitHub**: `git push origin main && git push origin v1.2.0`
6. **Create GitHub Release** with detailed release notes

### Versioning Scheme

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR** (v1.0.0): Breaking changes
- **MINOR** (v1.1.0): New features, backward compatible
- **PATCH** (v1.0.1): Bug fixes, backward compatible

## 📖 Additional Resources

- [LINE Messaging API Documentation](https://developers.line.biz/en/reference/messaging-api/)
- [Claude API Documentation](https://docs.anthropic.com/)
- [Python PEP 8 Style Guide](https://pep8.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

## ❓ Questions or Need Help?

- Check existing [Issues](https://github.com/Hayatelin/line_message_summarizer/issues)
- Review [DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md)
- Check [CHANGELOG.md](../CHANGELOG.md) for project history
- Ask in a new Issue with the `question` label

## 🎉 Thank You!

Your contributions help make this project better for everyone. We appreciate your time and effort!

---

**Last Updated**: 2026-02-18
**Maintainer**: Hayatelin
