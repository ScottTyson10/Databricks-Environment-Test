# Databricks pytest-bdd Test Framework
# Clean, modular Makefile focused on usability

#==============================================================================
# Configuration
#==============================================================================

PYENV_NAME = smoke-tests
PYTHON_VERSION = 3.10
RESULTS_DIR = results

# Test Configuration
PYTEST_OPTS = -v --tb=short --maxfail=0
PYTEST_DEBUG_OPTS = -v --tb=long --maxfail=0 -s  
PYTEST_FAILFAST_OPTS = -v --tb=short -x

# Scenario Testing
SCENARIO ?= comment-length
LAYER ?= all
MODE ?= normal
SCENARIOS := comment-length table-comments placeholder-detection critical-columns column-coverage-threshold comprehensive explicit-clustering-columns cluster-by-auto delta-auto-optimization cluster-exclusion small-tables-auto-exemption

# Colors
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
NC = \033[0m

#==============================================================================
# Quick Start Commands (Most Common)
#==============================================================================

# Default target - show help
.DEFAULT_GOAL := help

# Quick setup for new users
setup:
	@echo "$(GREEN)🚀 Setting up Databricks Test Framework...$(NC)"
	$(MAKE) venv setup-env
	@echo "$(GREEN)✅ Setup complete! Edit .env then run: make test-connection$(NC)"

# Test Databricks connection
test-connection:
	@echo "$(YELLOW)Testing Databricks connection...$(NC)"
	@python -c "from databricks.sdk import WorkspaceClient; from dotenv import load_dotenv; load_dotenv(); w = WorkspaceClient(); print('✅ Connected to Databricks')" \
		&& echo "$(GREEN)✅ Connection successful$(NC)" \
		|| echo "$(RED)❌ Connection failed - check your .env file$(NC)"

# Run scenario tests (the main command most users need)
test-scenario:
	@echo "$(GREEN)🧪 Running scenario: $(SCENARIO), layer: $(LAYER), mode: $(MODE)$(NC)"
	@$(MAKE) _validate-scenario SCENARIO=$(SCENARIO)
	@if [ "$(LAYER)" = "all" ]; then \
		$(MAKE) _test-scenario-layer SCENARIO=$(SCENARIO) LAYER=unit MODE=$(MODE); \
		$(MAKE) _test-scenario-layer SCENARIO=$(SCENARIO) LAYER=integration MODE=$(MODE); \
		$(MAKE) _test-scenario-layer SCENARIO=$(SCENARIO) LAYER=production MODE=$(MODE); \
	else \
		$(MAKE) _test-scenario-layer SCENARIO=$(SCENARIO) LAYER=$(LAYER) MODE=$(MODE); \
	fi

#==============================================================================
# Scenario Management
#==============================================================================

# List available scenarios
list-scenarios:
	@echo "$(GREEN)📋 Available scenarios:$(NC)"
	@echo "$(SCENARIOS)" | tr ' ' '\n' | sed 's/^/  ✓ /'

# Show all testing options
list-test-options:
	@echo "$(GREEN)🎛️  Parameterized Testing Options:$(NC)"
	@echo ""
	@echo "$(YELLOW)SCENARIO:$(NC) $(SCENARIOS)"
	@echo "$(YELLOW)LAYER:$(NC)    unit | integration | production | all"
	@echo "$(YELLOW)MODE:$(NC)     normal | debug | failfast"
	@echo ""
	@echo "$(GREEN)💡 Examples:$(NC)"
	@echo "  make test-scenario SCENARIO=comment-length"
	@echo "  make test-scenario SCENARIO=comment-length LAYER=unit MODE=debug"

# Run all implemented scenarios
test-all-scenarios:
	@echo "$(GREEN)🚀 Running all scenarios...$(NC)"
	@for scenario in $(SCENARIOS); do \
		scenario_file=$$(echo $$scenario | sed 's/-/_/g'); \
		if [ -f "tests/integration/test_$${scenario_file}_integration.py" ]; then \
			$(MAKE) test-scenario SCENARIO=$$scenario LAYER=all MODE=normal; \
		else \
			echo "$(YELLOW)⏭️  Skipping $$scenario (not implemented yet)$(NC)"; \
		fi; \
	done

#==============================================================================
# Basic Test Commands
#==============================================================================

# Layer 1: Unit tests
test-unit:
	@echo "$(YELLOW)🧪 Running unit tests...$(NC)"
	pytest tests/unit/ $(PYTEST_OPTS)

# Layer 2: Integration tests  
test-integration:
	@echo "$(YELLOW)🔗 Running integration tests...$(NC)"
	@echo "$(RED)⚠️  This creates test tables in Databricks$(NC)"
	CREATE_TEST_TABLES=true pytest tests/integration/ $(PYTEST_OPTS)

# Code quality checks
quality:
	@echo "$(YELLOW)🔍 Running code quality checks...$(NC)"
	black tests/ --line-length 120
	ruff check tests/ --fix
	mypy tests/
	@echo "$(GREEN)✅ Quality checks complete$(NC)"

#==============================================================================
# Development Commands
#==============================================================================

# Show environment status
show-env:
	@echo "$(GREEN)🔧 Environment Status:$(NC)"
	@python -c "from dotenv import load_dotenv; import os; load_dotenv(); \
		host = os.getenv('DATABRICKS_HOST', 'NOT SET'); \
		token = os.getenv('DATABRICKS_TOKEN', 'NOT SET'); \
		print(f'  Host: {host}'); \
		print(f'  Token: {\"✅ Set\" if token != \"NOT SET\" else \"❌ Not Set\"}')"

# Clean results
clean:
	@echo "$(YELLOW)🧹 Cleaning results...$(NC)"
	@rm -rf $(RESULTS_DIR)/* && mkdir -p $(RESULTS_DIR)/logs
	@echo "$(GREEN)✅ Results cleaned$(NC)"

# Show recent results  
show-results:
	@echo "$(GREEN)📊 Recent Test Results:$(NC)"
	@ls -t $(RESULTS_DIR)/session_*.json 2>/dev/null | head -3 | while read file; do echo "  📄 $$file"; done || echo "  📭 No results yet"

#==============================================================================
# Internal Helper Functions
#==============================================================================

# Validate scenario exists
_validate-scenario:
	@if ! echo "$(SCENARIOS)" | grep -q "$(SCENARIO)"; then \
		echo "$(RED)❌ Unknown scenario '$(SCENARIO)'$(NC)"; \
		echo "$(YELLOW)💡 Available: $(SCENARIOS)$(NC)"; \
		exit 1; \
	fi

# Run specific scenario layer
_test-scenario-layer:
	@echo "$(YELLOW)  → $(SCENARIO) $(LAYER) ($(MODE))$(NC)"
	@case "$(LAYER)" in \
		unit) \
			case "$(SCENARIO)" in \
				comment-length) unit_test="tests/unit/documentation/test_table_comment_validators.py::TestCommentLengthValidation" ;; \
				placeholder-detection) unit_test="tests/unit/documentation/test_placeholder_validators.py::TestPlaceholderTextValidation" ;; \
				critical-columns) unit_test="tests/unit/documentation/test_critical_columns_validators.py::TestCriticalColumnDocumentation" ;; \
				column-coverage-threshold) unit_test="tests/unit/documentation/test_column_coverage_validators.py::TestColumnCoverageThreshold" ;; \
				table-comments) unit_test="tests/unit/documentation/test_table_comment_validators.py::TestTableCommentValidation" ;; \
				comprehensive) unit_test="tests/unit/documentation/test_comprehensive_validators.py::TestComprehensiveDocumentationValidator" ;; \
				explicit-clustering-columns) unit_test="tests/unit/clustering/test_explicit_clustering_validators.py::TestExplicitClusteringColumns" ;; \
				cluster-by-auto) unit_test="tests/unit/clustering/test_auto_clustering_validators.py::TestAutoClusteringDetection" ;; \
				delta-auto-optimization) unit_test="tests/unit/clustering/test_delta_auto_optimization_validators.py::TestDeltaAutoOptimizationValidators" ;; \
				cluster-exclusion) unit_test="tests/unit/clustering/test_cluster_exclusion_validators.py::TestClusterExclusionDetection" ;; \
				small-tables-auto-exemption) unit_test="tests/unit/clustering/test_size_exemption_validators.py::TestSizeExemptionValidators" ;; \
				*) unit_test="tests/unit/documentation/ -k $(SCENARIO)" ;; \
			esac; \
			case "$(MODE)" in \
				debug) pytest $$unit_test $(PYTEST_DEBUG_OPTS) ;; \
				failfast) pytest $$unit_test $(PYTEST_FAILFAST_OPTS) ;; \
				*) pytest $$unit_test $(PYTEST_OPTS) ;; \
			esac ;; \
		integration) \
			case "$(SCENARIO)" in \
				explicit-clustering-columns) integration_file="tests/integration/clustering/test_explicit_clustering_columns_integration.py" ;; \
				cluster-by-auto) integration_file="tests/integration/clustering/test_cluster_by_auto_integration.py" ;; \
				delta-auto-optimization) integration_file="tests/integration/clustering/test_delta_auto_optimization_integration.py" ;; \
				cluster-exclusion) integration_file="tests/integration/clustering/test_cluster_exclusion_integration.py" ;; \
				*) integration_file="tests/integration/documentation/test_$$(echo '$(SCENARIO)' | sed 's/-/_/g')_integration.py" ;; \
			esac; \
			case "$(MODE)" in \
				debug) CREATE_TEST_TABLES=true pytest "$$integration_file" $(PYTEST_DEBUG_OPTS) ;; \
				failfast) CREATE_TEST_TABLES=true pytest "$$integration_file" $(PYTEST_FAILFAST_OPTS) ;; \
				*) CREATE_TEST_TABLES=true pytest "$$integration_file" $(PYTEST_OPTS) ;; \
			esac ;; \
		production) \
			case "$(SCENARIO)" in \
				comment-length) marker="comment-length"; step_file="tests/step_definitions/documentation_steps.py" ;; \
				table-comments) marker="table-comments"; step_file="tests/step_definitions/documentation_steps.py" ;; \
				placeholder-detection) marker="placeholder-detection"; step_file="tests/step_definitions/documentation_steps.py" ;; \
				critical-columns) marker="critical-columns"; step_file="tests/step_definitions/documentation_steps.py" ;; \
				column-coverage-threshold) marker="column-coverage"; step_file="tests/step_definitions/documentation_steps.py" ;; \
				comprehensive) marker="comprehensive"; step_file="tests/step_definitions/documentation_steps.py" ;; \
				explicit-clustering-columns) marker="clustering_columns"; step_file="tests/step_definitions/clustering_steps.py" ;; \
				cluster-by-auto) marker="auto_clustering"; step_file="tests/step_definitions/clustering_steps.py" ;; \
				delta-auto-optimization) marker="delta_auto_optimization"; step_file="tests/step_definitions/clustering_steps.py" ;; \
				cluster-exclusion) marker="cluster_exclusion"; step_file="tests/step_definitions/clustering_steps.py" ;; \
				*) marker="$(SCENARIO)"; step_file="tests/step_definitions/documentation_steps.py" ;; \
			esac; \
			case "$(MODE)" in \
				debug) pytest "$$step_file" -m "$$marker" $(PYTEST_DEBUG_OPTS) ;; \
				failfast) pytest "$$step_file" -m "$$marker" $(PYTEST_FAILFAST_OPTS) ;; \
				*) pytest "$$step_file" -m "$$marker" $(PYTEST_OPTS) ;; \
			esac ;; \
		*) echo "$(RED)❌ Unknown layer '$(LAYER)'$(NC)"; exit 1 ;; \
	esac

#==============================================================================
# Advanced Setup (For Development)
#==============================================================================

# Create virtual environment
venv:
	@if ! pyenv versions --bare | grep -qx $(PYENV_NAME); then \
		echo "$(YELLOW)🔧 Creating virtual environment: $(PYENV_NAME)$(NC)"; \
		pyenv virtualenv $(PYTHON_VERSION) $(PYENV_NAME); \
		pyenv local $(PYENV_NAME); \
		pip install -r requirements.txt; \
	else \
		echo "$(GREEN)✅ Virtual environment exists: $(PYENV_NAME)$(NC)"; \
		pyenv local $(PYENV_NAME); \
	fi

# Setup environment file
setup-env:
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)📝 Creating .env file...$(NC)"; \
		cp .env.template .env; \
		echo "$(GREEN)✅ Created .env file$(NC)"; \
		echo "$(RED)🔑 Please edit .env with your Databricks credentials$(NC)"; \
	else \
		echo "$(GREEN)✅ .env file exists$(NC)"; \
	fi

#==============================================================================
# Help System
#==============================================================================

help:
	@echo "$(GREEN)🎯 Databricks pytest-bdd Test Framework$(NC)"
	@echo ""
	@echo "$(YELLOW)🚀 Quick Start:$(NC)"
	@echo "  make setup                    - Initial setup for new users"
	@echo "  make test-connection          - Test Databricks connection"
	@echo "  make test-scenario            - Run scenario tests (main command)"
	@echo ""
	@echo "$(YELLOW)🧪 Scenario Testing:$(NC)"
	@echo "  make test-scenario SCENARIO=comment-length LAYER=unit    - Run specific layer"
	@echo "  make test-scenario SCENARIO=comment-length MODE=debug    - Debug mode"
	@echo "  make list-scenarios           - Show available scenarios"
	@echo "  make list-test-options        - Show all testing options"
	@echo ""
	@echo "$(YELLOW)🔧 Development:$(NC)"
	@echo "  make test-unit                - Unit tests only"
	@echo "  make test-integration         - Integration tests only"
	@echo "  make quality                  - Code formatting & linting"
	@echo "  make show-env                 - Show environment status"
	@echo "  make clean                    - Clean test results"
	@echo ""
	@echo "$(GREEN)💡 For detailed options: make list-test-options$(NC)"

#==============================================================================
# Backward Compatibility
#==============================================================================

# Keep common legacy commands
test-scenario-comment-length:
	$(MAKE) test-scenario SCENARIO=comment-length LAYER=all MODE=normal

setup-dev: venv setup-env
	pip install -r requirements-dev.txt
	@echo "$(GREEN)✅ Development setup complete$(NC)"

#==============================================================================
# All Targets
#==============================================================================

.PHONY: help setup test-connection test-scenario list-scenarios list-test-options test-all-scenarios \
	test-unit test-integration quality show-env clean show-results \
	_validate-scenario _test-scenario-layer venv setup-env setup-dev test-scenario-comment-length