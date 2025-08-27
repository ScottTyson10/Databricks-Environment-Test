# Databricks Smoke Tests

A pytest-bdd framework for comprehensive Databricks compliance testing using a three-layer testing architecture.

## Overview

This framework provides automated testing for Databricks environments to detect data governance and best practice violations. It validates documentation standards, clustering configurations, and other compliance requirements to ensure your Databricks workspace follows organizational policies and performance optimization practices.

## Architecture

### Three-Layer Testing Approach

The framework uses a systematic three-layer architecture to ensure comprehensive validation:

1. **Layer 1 (Unit Tests)**: Fast validator logic tests with no external dependencies
   - Pure Python logic validation
   - Mock data testing
   - Rapid feedback during development

2. **Layer 2 (Integration Tests)**: Real Databricks object validation with test tables
   - Creates actual test tables in Databricks
   - Tests real SDK interactions
   - Validates end-to-end data flows

3. **Layer 3 (Production Tests)**: BDD tests against production data for compliance monitoring
   - Analyzes real production tables
   - Business-readable scenario validation
   - Compliance reporting and monitoring

### Key Components

- **Discovery Engine** (`tests/utils/discovery.py`): Discovers tables from Databricks workspace using configurable filters
- **Validators** (`tests/validators/`): Protocol-based validators for compliance rules
- **Table Factory** (`tests/fixtures/table_factory.py`): Context manager for creating/cleaning test tables
- **Step Definitions** (`tests/step_definitions/`): pytest-bdd step implementations for BDD scenarios

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

## Compliance Scenarios

### Currently Implemented

**Documentation Compliance**:
- Tables must have comments
- Table comments must not be placeholder text
- Table comments must meet minimum length requirements
- Column documentation coverage thresholds
- Critical column documentation validation
- Comprehensive documentation validation

**Clustering Compliance**:
- Tables with explicit clustering columns
- Tables with automatic clustering (clusterByAuto)
- Tables with delta auto-optimization (optimizeWrite + autoCompact)

### Planned Scenarios *(in development)*

- **Jobs Compliance**: Service principal usage, retry configuration, timeout settings
- **Maintenance Compliance**: Regular VACUUM operations, orphaned table detection
- **Metadata Compliance**: Required properties, naming conventions, data classification, environment tagging
- **Performance Optimization**: File size optimization, partitioning strategies, compression settings

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
# Run specific scenario (recommended approach)
make test-scenario SCENARIO=comment-length      # Run all layers for comment length
make test-scenario SCENARIO=critical-columns    # Run all layers for critical columns
make test-scenario SCENARIO=delta-auto-optimization  # Run clustering scenario

# Run specific layers
make test-unit                       # Layer 1: All unit tests
make test-integration                # Layer 2: All integration tests (creates test tables)

# Run by layer and scenario
make test-scenario SCENARIO=comment-length LAYER=unit        # Unit tests only
make test-scenario SCENARIO=comment-length LAYER=integration # Integration tests only
make test-scenario SCENARIO=comment-length LAYER=production  # BDD tests only

# Debug and development modes
make test-scenario SCENARIO=comment-length MODE=debug       # Verbose output
make test-scenario SCENARIO=comment-length MODE=failfast    # Stop on first failure

# List available options
make list-scenarios        # Show all available scenarios
make list-test-options     # Show all parameterization options
```

### Development Workflow

```bash
# Clean environment
make clean

# Code quality checks
make quality                         # Format, lint, and type check

# Environment status
make show-env                        # Check Databricks connection setup
make show-results                    # View recent test results

# Run all implemented scenarios
make test-all-scenarios              # Run all scenarios with full layers
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

## Development

### Installing Development Dependencies

```bash
pip install -r requirements-dev.txt
```

### Code Quality

```bash
# All-in-one code quality (recommended)
make quality

# Individual tools (if needed for specific issues)
black tests/ --line-length 120
ruff check tests/ --fix
mypy tests/
```

### Running Tests with Coverage

```bash
pytest --cov=tests --cov-report=html tests/
```

## Implemented Scenarios

The framework currently supports these compliance scenarios:

### Documentation Compliance
- **comment-length**: Table comments must meet minimum length requirements
- **table-comments**: Tables must have comments
- **placeholder-detection**: Table comments must not be placeholder text
- **critical-columns**: Critical columns must have documentation
- **column-coverage-threshold**: Tables must meet column documentation coverage thresholds
- **comprehensive**: Comprehensive documentation validation

### Clustering Compliance
- **explicit-clustering-columns**: Tables with clustering should use appropriate column selection
- **cluster-by-auto**: Tables can use clusterByAuto flag for automatic clustering
- **delta-auto-optimization**: Tables can use delta auto-optimization for clustering

Run any scenario with: `make test-scenario SCENARIO=[scenario-name]`

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

### Test Issues

```bash
# View recent test results
make show-results

# Clean test results and start fresh
make clean

# Run scenario in debug mode for detailed output
make test-scenario SCENARIO=[name] MODE=debug
```

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- Create an issue in the GitHub repository
- Check the research/ directory for detailed implementation notes
- Review CLAUDE.md for AI assistant guidance
