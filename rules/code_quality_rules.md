# Code Quality Rules

**Priority**: ⚡ High (Should Follow)

## Overview
Code quality rules ensure maintainable, testable, and secure code.

## Rules

### CODE-001: Write Comprehensive Tests
- Unit tests for all functions
- Integration tests for workflows
- Minimum 80% code coverage
- Test edge cases and error conditions

### CODE-002: Follow Code Style Standards
- Consistent formatting
- Use linters (pylint, flake8, black)
- Follow PEP 8 for Python
- Maximum line length: 100 characters

### CODE-003: Document All Public APIs
- Docstrings for all public functions
- Type hints for parameters and returns
- Usage examples in documentation
- Keep documentation synchronized

### CODE-004: Never Bypass Code Review
- All changes require review
- Address review feedback
- No direct commits to main branch
- Use pull requests

### CODE-005: Run Tests Before Committing
- Execute test suite locally
- Fix failing tests
- Run linters
- Verify builds pass

### CODE-006: Keep Functions Small and Focused
- Single Responsibility Principle
- Maximum 50 lines per function
- Clear function names
- Minimize complexity

---

**Version**: 2.0.0  
**Last Updated**: 2025-12-08
