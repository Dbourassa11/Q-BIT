# Contributing to Q-BIT

Thank you for your interest in contributing to Q-BIT! This document provides guidelines and instructions for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/Q-BIT.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Run tests: `pytest tests/`
6. Commit your changes: `git commit -m "Description of changes"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Open a Pull Request

## Development Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-asyncio pytest-cov black ruff mypy

# Run tests
pytest tests/

# Run linters
black python/ tests/
ruff check python/ tests/
mypy python/
```

## Code Style

- Follow PEP 8 style guidelines
- Use type hints for all function signatures
- Write docstrings for all public classes and methods
- Keep line length to 88 characters (Black default)
- Use meaningful variable and function names

## Testing

- Write tests for all new features
- Ensure all tests pass before submitting PR
- Aim for high test coverage
- Use pytest fixtures for common setup
- Mark async tests with `@pytest.mark.asyncio`

## Pull Request Guidelines

- Provide a clear description of the changes
- Reference any related issues
- Include tests for new functionality
- Update documentation as needed
- Ensure CI checks pass

## Commit Messages

- Use clear and descriptive commit messages
- Start with a verb (Add, Fix, Update, etc.)
- Keep first line under 50 characters
- Provide detailed explanation in body if needed

Example:
```
Add stigmergic coordination layer

- Implement StigmergicEnvironment with async operations
- Add support for in-memory and Redis backends
- Include comprehensive tests
```

## Questions?

Open an issue or contact the maintainers.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
