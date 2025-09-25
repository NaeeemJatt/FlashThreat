# Contributing to FlashThreat

Thank you for your interest in contributing to FlashThreat! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Node.js 16+
- Docker & Docker Compose
- Git

### Development Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/yourusername/flashthreat.git
   cd flashthreat
   ```

2. **Set up the development environment:**
   ```bash
   # Backend
   cd backend
   pip install poetry
   poetry install
   
   # Frontend
   cd ../frontend
   npm install
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start development services:**
   ```bash
   docker-compose up -d postgres redis
   ```

5. **Initialize database:**
   ```bash
   cd backend
   poetry run python init_db.py
   ```

## 🔧 Development Workflow

### Code Style

#### Python (Backend)
- Use **Black** for code formatting
- Use **isort** for import sorting
- Use **MyPy** for type checking
- Follow **PEP 8** guidelines

```bash
# Format code
poetry run black app/
poetry run isort app/

# Type checking
poetry run mypy app/
```

#### JavaScript (Frontend)
- Use **Prettier** for code formatting
- Use **ESLint** for linting
- Follow **React** best practices

```bash
# Format code
npm run format

# Lint code
npm run lint
```

### Testing

#### Backend Tests
```bash
cd backend
poetry run pytest
poetry run pytest --cov=app tests/  # With coverage
```

#### Frontend Tests
```bash
cd frontend
npm test
npm run test:coverage  # With coverage
```

#### Integration Tests
```bash
cd backend
poetry run pytest tests/test_integration.py
poetry run pytest tests/test_security.py
```

### Database Migrations

```bash
# Create new migration
cd backend
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## 📝 Pull Request Process

### Before Submitting

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**
   - Write clean, well-documented code
   - Add tests for new functionality
   - Update documentation if needed

3. **Run tests:**
   ```bash
   # Backend
   cd backend && poetry run pytest
   
   # Frontend
   cd frontend && npm test
   ```

4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

### Submitting a Pull Request

1. **Push your branch:**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request:**
   - Use a descriptive title
   - Provide a detailed description
   - Link any related issues
   - Include screenshots for UI changes

### Pull Request Guidelines

- **Title**: Use conventional commits format (feat:, fix:, docs:, etc.)
- **Description**: Explain what changes you made and why
- **Tests**: Ensure all tests pass
- **Documentation**: Update relevant documentation
- **Breaking Changes**: Clearly mark any breaking changes

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Environment details:**
   - OS and version
   - Python version
   - Node.js version
   - Docker version

2. **Steps to reproduce:**
   - Clear, numbered steps
   - Expected behavior
   - Actual behavior

3. **Additional context:**
   - Screenshots if applicable
   - Error messages
   - Log files

## ✨ Feature Requests

When requesting features, please include:

1. **Problem description:**
   - What problem does this solve?
   - Who would benefit from this feature?

2. **Proposed solution:**
   - How should this work?
   - Any specific requirements?

3. **Alternatives considered:**
   - What other solutions did you consider?
   - Why is this approach better?

## 📚 Documentation

### Code Documentation

- **Python**: Use docstrings for functions and classes
- **JavaScript**: Use JSDoc for functions and components
- **API**: Document all endpoints with examples

### User Documentation

- Update user guides for new features
- Add screenshots for UI changes
- Keep examples up to date

## 🔒 Security

### Security Issues

If you discover a security vulnerability, please:

1. **DO NOT** open a public issue
2. Email security@flashthreat.com (if available)
3. Include detailed information about the vulnerability
4. Allow time for the issue to be addressed before disclosure

### Security Best Practices

- Never commit API keys or secrets
- Use environment variables for configuration
- Follow secure coding practices
- Test security features thoroughly

## 🏷️ Release Process

### Version Numbering

We use [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Version bumped
- [ ] Security review completed

## 🤝 Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Provide constructive feedback
- Focus on what's best for the community

### Getting Help

- **Documentation**: Check the docs first
- **Issues**: Search existing issues before creating new ones
- **Discussions**: Use GitHub Discussions for questions
- **Discord/Slack**: Join our community channels (if available)

## 📋 Development Checklist

Before submitting code:

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New features have tests
- [ ] Documentation updated
- [ ] No breaking changes (or clearly marked)
- [ ] Security considerations addressed
- [ ] Performance impact considered

## 🎯 Areas for Contribution

### High Priority
- Bug fixes
- Security improvements
- Performance optimizations
- Test coverage improvements

### Medium Priority
- New features
- UI/UX improvements
- Documentation improvements
- Integration tests

### Low Priority
- Advanced features
- Enterprise capabilities
- Third-party integrations

## 📞 Contact

- **Issues**: [GitHub Issues](https://github.com/yourusername/flashthreat/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/flashthreat/discussions)
- **Email**: contact@flashthreat.com (if available)

Thank you for contributing to FlashThreat! 🚀
