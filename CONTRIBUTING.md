# Contributing to foundry-ontology-open

Thank you for your interest! Contributions are welcome.

## Development Setup

```bash
git clone https://github.com/cloudbadal007/foundry-ontology-open.git
cd foundry-ontology-open
pip install -e ".[dev]"
```

## Code Style

- **Black** for formatting
- **isort** for import sorting
- **mypy** for type checking

```bash
black foundry_ontology/ tests/
isort foundry_ontology/ tests/
```

## Tests

```bash
pytest -v
pytest --cov=foundry_ontology
```

## Pull Request Process

1. Fork the repo
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass and style checks pass
5. Submit a PR with a clear description

## Areas for Contribution

- Additional export formats
- More validation rule → SHACL mappings
- Performance improvements for ObjectStore
- Documentation and examples
