# Contributing to Auralis

Thank you for your interest in contributing to Auralis! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a new branch for your changes
4. Make your changes
5. Push your changes to your fork
6. Submit a pull request

## Development Environment

1. Install Python 3.8 or higher
2. Install development dependencies:
   ```
   pip install -r requirements.txt
   pip install -e .
   pip install flake8 black isort mypy pytest pytest-cov
   ```

3. For optional features:
   ```
   python setup_language_detection.py
   python setup_audio_similarity.py
   ```

## Coding Standards

We use several tools to maintain code quality:

- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

To check your code:

```bash
# Format code
black src tests

# Sort imports
isort src tests

# Lint code
flake8 src tests

# Type check
mypy src
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/
```

## Pull Request Process

1. Ensure your code follows the coding standards
2. Update the documentation as needed
3. Add tests for new functionality
4. Ensure all tests pass
5. Update the CHANGELOG.md with your changes
6. The PR should be reviewed by at least one maintainer

## Feature Requests

Please use GitHub issues to submit feature requests. Provide as much detail as possible about the feature and why it would be beneficial.

## Bug Reports

Please use GitHub issues to report bugs. Include:

1. Steps to reproduce the bug
2. Expected behavior
3. Actual behavior
4. Screenshots if applicable
5. System information (OS, Python version, etc.)

## License

By contributing to Auralis, you agree that your contributions will be licensed under the project's MIT License. 