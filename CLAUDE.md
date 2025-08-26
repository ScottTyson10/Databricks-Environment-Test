# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A pytest-bdd test framework for validating Databricks table documentation compliance. The framework uses a three-layer testing architecture to ensure data governance standards are met.

## ⚠️ IMPORTANT CONFIGURATION REMINDERS

- **Configuration Loading**: The DocumentationValidator class MUST load configuration from `tests/config/documentation_config.yaml`
- **No Hardcoded Values**: Critical column patterns, validation thresholds, and placeholder patterns should come from config
- **Future Scenarios**: Always check that new scenarios load their configuration from YAML files, not hardcoded values

## Common Development Commands

### Initial Setup
```bash
make setup              # Complete environment setup (venv, dirs, .env)
make test-connection    # Verify Databricks connection
```

### Three-Layer Test Execution
```bash
# Layer 1: Unit Tests (no Databricks dependencies)
make test-unit                       # All unit tests
make test-unit-table-comments        # Table comment unit tests only

# Layer 2: Integration Tests (creates test tables)
make test-integration-table-comments # Table comment integration tests

# Layer 3: Production Tests (analyzes real data)
make test-production-table-comments  # Table comment BDD tests

# Run all layers for table comments
make test-table-comment-workflow
```

### Testing Single Scenarios
```bash
# Test discovery engine
make test-discovery

# List discovered tables
make list-tables

# Clean test results
make clean
```

## Architecture

### Three-Layer Testing Approach

1. **Unit Tests (Layer 1)**: Fast validator logic tests with no external dependencies
   - Location: `tests/unit/`
   - Run with: `make test-unit`

2. **Integration Tests (Layer 2)**: Creates real Databricks test tables for validation
   - Location: `tests/integration/`
   - Requires: `CREATE_TEST_TABLES=true`
   - Run with: `make test-integration`

3. **Production Tests (Layer 3)**: BDD tests against real production data
   - Location: `tests/features/` and `tests/step_definitions/`
   - Run with: `make test-production`

### Key Components

- **Discovery Engine** (`tests/utils/discovery.py`): Uses NamedTuple for immutable table info, discovers tables from Databricks workspace
- **Validators** (`tests/validators/documentation.py`): Protocol-based validators for documentation compliance
- **Table Factory** (`tests/fixtures/table_factory.py`): Context manager for creating/cleaning test tables
- **Step Definitions** (`tests/step_definitions/documentation_steps.py`): pytest-bdd step implementations

## Environment Configuration

Set these environment variables in `.env`:

```bash
# Required for all tests
DATABRICKS_HOST=
DATABRICKS_TOKEN=
DATABRICKS_WAREHOUSE_ID=

# Discovery configuration (optional)
DISCOVERY_TARGET_CATALOGS=workspace,samples
DISCOVERY_TARGET_SCHEMAS=pytest_test_data,information_schema
DISCOVERY_MAX_TABLES=5000
DISCOVERY_MAX_PER_SCHEMA=1000

# Integration tests only
CREATE_TEST_TABLES=true  # Only for integration tests
```

## Important Implementation Notes

1. **Always use Make commands** - Never run pip/pytest directly. The project uses Make as the primary workflow interface.

2. **Check Databricks enforcement behaviors BEFORE implementation** - Review `research/DATABRICKS_ENFORCEMENT_BEHAVIORS.md` to understand what Databricks prevents at table creation time. This affects testing strategies (unit-only vs full testing).

3. **Scope discipline** - The framework currently implements only the "Tables must have a comment" scenario. Additional validators can be added following the established patterns.

4. **Test table cleanup** - Integration tests use context managers to ensure test tables are always cleaned up, even on failure.

5. **Discovery limits** - Production tests use session-scoped discovery with configurable limits to prevent runaway operations.

6. **pytest patterns** - Use fixtures (`@pytest.fixture`), parametrize (`@pytest.mark.parametrize`), and markers (`@pytest.mark.integration`) for test organization.

7. **Data structure evolution** - When adding new data structures (e.g., ColumnInfo for critical columns), choose the appropriate location based on scope: discovery structures in `utils/discovery.py`, validation-specific in `validators/`, test-only in `fixtures/`.

8. **Pattern reuse** - Critical column patterns are already defined in `tests/config/documentation_config.yaml`. New scenarios should reuse existing configuration where possible.

8. **Research organization** - All research, feasibility testing, and exploratory files should be organized in scenario-specific subdirectories under `research/`. This keeps the main repository clean while preserving valuable implementation insights.

9. **Layer validation** - After completing each layer, validate using `make test-scenario SCENARIO=[name] LAYER=[unit|integration|production]`. Update the Makefile SCENARIOS list and unit test mapping when adding new scenarios.

10. **Implementation journaling** - Create a dedicated implementation journal in `research/[scenario_name]/[SCENARIO_NAME]_IMPLEMENTATION_JOURNAL.md` to track the complete implementation lifecycle, technical decisions, philosophy checks, and lessons learned.

## Scenario Expansion

For implementing additional scenarios, see `SCENARIO_EXPANSION_PLAN.md`. **Key principles:**

- **Research First**: Never implement without thorough Databricks SDK and real data research
- **Check Enforcement Behaviors**: Review `research/DATABRICKS_ENFORCEMENT_BEHAVIORS.md` before implementation
- **Mandatory Philosophy Checks**: Complete philosophy checks after each layer implementation  
- **Three-Layer Discipline**: Maintain Unit → Integration → Production architecture

## Future Integrations

- **CI/CD**: Will use Azure CI/CD agent pool (see Makefile TODOs)
- **Code Quality**: Will integrate with SonarQube for metrics and coverage (see results/results.py TODO)