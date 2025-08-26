# Databricks Smoke Tests

A pytest-bdd framework for validating Databricks table documentation compliance using a three-layer testing architecture.

## Overview

This framework provides automated testing for data governance compliance in Databricks environments, ensuring tables and columns meet documentation standards.

## Features

- **Three-Layer Testing Architecture**:
  - **Layer 1 (Unit Tests)**: Fast validator logic tests with no external dependencies
  - **Layer 2 (Integration Tests)**: Real Databricks object validation with test tables
  - **Layer 3 (Production Tests)**: BDD tests against production data for compliance monitoring

- **Documentation Compliance Scenarios**:
  - Tables must have comments
  - Table comments must not be placeholder text
  - Table comments must meet minimum length requirements
  - Column documentation coverage thresholds
  - Critical column documentation validation

## Quick Start

### Prerequisites

- Python 3.10+
- Databricks workspace access
- SQL warehouse for query execution

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourorg/databricks-smoke-tests.git
cd databricks-smoke-tests
```

2. Set up the environment:
```bash
make setup
```

3. Configure your Databricks credentials:
```bash
cp .env.template .env
# Edit .env with your Databricks credentials
```

4. Verify the connection:
```bash
make test-connection
```

## Usage

### Running Tests

```bash
# Run all three layers
make test-all-layers

# Run specific layers
make test-unit                       # Layer 1: Unit tests
make test-integration                 # Layer 2: Integration tests (creates test tables)
make test-production                  # Layer 3: Production BDD tests

# Run specific scenario
make test-table-comment-workflow     # Complete table comment validation
```

### Development Workflow

```bash
# Clean environment
make clean

# Run unit tests during development
make test-unit-table-comments

# Run integration tests with real tables
make test-integration-table-comments

# Validate against production data
make test-production-table-comments
```

## Configuration

### Environment Variables

Key configuration in `.env`:

```bash
# Databricks connection
DATABRICKS_HOST=https://xxx.cloud.databricks.com
DATABRICKS_TOKEN=your-token
DATABRICKS_WAREHOUSE_ID=warehouse-id

# Discovery configuration
DISCOVERY_TARGET_CATALOGS=workspace,samples
DISCOVERY_MAX_TABLES=5000

# Test configuration
CREATE_TEST_TABLES=false  # Set to true for integration tests only
```

### Discovery Targeting

Control which tables are discovered for validation:

```bash
# Target specific catalogs
DISCOVERY_TARGET_CATALOGS=workspace,samples

# Target specific schemas
DISCOVERY_TARGET_SCHEMAS=pytest_test_data,production_data

# Set safety limits
DISCOVERY_MAX_TABLES=5000
DISCOVERY_MAX_PER_SCHEMA=1000
```

## Project Structure

```
databricks-smoke-tests/
├── Makefile                    # Primary workflow interface
├── pyproject.toml              # Python project configuration
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Development dependencies
├── tests/
│   ├── unit/                   # Layer 1: Unit tests
│   ├── integration/            # Layer 2: Integration tests
│   ├── features/               # BDD feature files
│   ├── step_definitions/       # Layer 3: Production step definitions
│   ├── utils/                  # Discovery engine
│   ├── validators/             # Compliance validators
│   └── fixtures/               # Test data factories
└── results/                    # Test results and reports
```

## Development

### Installing Development Dependencies

```bash
pip install -r requirements-dev.txt
```

### Code Quality

```bash
# Format code
black tests/
isort tests/

# Lint code
ruff check tests/

# Type checking
mypy tests/
```

### Running Tests with Coverage

```bash
pytest --cov=tests --cov-report=html tests/
```

## CI/CD Integration

The framework is designed for CI/CD pipelines:

```bash
# Validate CI environment
make ci-validate

# Run CI test suite with reports
make ci-test
```

Future integrations:
- Azure CI/CD agent pool (see Makefile TODOs)
- SonarQube for code quality metrics

## Contributing

1. Follow the three-layer architecture pattern
2. Use Make commands for all operations
3. Write unit tests for new validators
4. Create integration tests for end-to-end scenarios
5. Update feature files for new business requirements

## Best Practices

1. **Always use Make commands** - Never run pip/pytest directly
2. **Maintain scope discipline** - Implement only required scenarios
3. **Use context managers** - Ensure proper cleanup of test resources
4. **Session-scoped fixtures** - Optimize performance for expensive operations
5. **Follow pytest patterns** - Use fixtures, parametrize, and markers

## Troubleshooting

### Connection Issues

```bash
# Verify environment variables
make show-env

# Test Databricks connection
make test-connection
```

### Discovery Issues

```bash
# Test discovery engine
make test-discovery

# List discovered tables
make list-tables
```

### Test Failures

```bash
# View test results
make show-results

# Open HTML report
make open-report
```

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- Create an issue in the GitHub repository
- Check the IMPLEMENTATION_JOURNAL.md for detailed implementation notes
- Review CLAUDE.md for AI assistant guidance# databricks-pytest
