# Scenario Implementation Checklist
**Master Working Document for End-to-End Scenario Implementation**

## 🎯 Key Implementation Principles

### **Research First - No Exceptions**
- NEVER implement without thorough feasibility research
- Test that Databricks allows rule violations to exist
- Extract all business rule values to configuration
- Document SDK behavior with real testing

### **Three-Layer Architecture Discipline** 
- **Layer 1 (Unit)**: Fast validator logic, no external dependencies
- **Layer 2 (Integration)**: Real Databricks objects with proper cleanup
- **Layer 3 (Production)**: BDD against real data with business value

### **Philosophy Check Enforcement**
- MANDATORY after each layer - not optional
- Use TodoWrite to track philosophy check completion
- Address issues found before proceeding to next layer
- Document learnings and iterate if needed

### **Test-Implementation Alignment**
- When implementation evolves, update ALL test cases to match
- Remove obsolete tests that don't reflect current behavior
- Choose precision over coverage - accurate detection matters
- Document exact matching strategies in code comments

## ⚠️ Risk Mitigation

### **Common Pitfalls to Avoid:**
1. **Skipping research** → Implementing based on assumptions
2. **Scope creep** → Adding features not in the feature file  
3. **Architecture drift** → Breaking three-layer separation
4. **Performance regression** → Not testing with realistic data volumes
5. **Missing philosophy checks** → Losing track of lessons learned

### **Mitigation Strategies:**
1. **Research checkpoints** → No code without documented research
2. **Scope discipline** → Stick to exact feature file requirements
3. **Architecture validation** → Verify layer separation in each implementation
4. **Performance baselines** → Establish and maintain performance targets
5. **Philosophy check enforcement** → Use TodoWrite to track mandatory checks

## 🚀 Quick Start Guide
After reading this full checklist once, use this summary for subsequent scenarios:

1. **Setup**: Copy template → Fill scenario info → Create feature branch
2. **Research**: Feasibility check → Config extraction → SDK investigation → Document
3. **Layer 1**: Validator implementation → Unit tests → Philosophy check
4. **Layer 2**: Test table specs → Integration tests → Philosophy check  
5. **Layer 3**: BDD steps → Production tests → Philosophy check
6. **Complete**: Update docs → Quality checks → Merge → Archive

## 📁 File Structure for New Scenarios
```
tests/
├── unit/documentation/test_[scenario]_validators.py       # Unit tests
├── integration/documentation/test_[scenario]_integration.py # Integration tests
├── step_definitions/documentation_steps.py                # Update with new steps
├── fixtures/table_factory.py                             # Add TABLE_SPECS
└── config/documentation_config.yaml                      # Add configuration

research/documentation/[scenario_name]/
├── [SCENARIO_NAME]_IMPLEMENTATION.md                     # This checklist (archived after completion)
├── [SCENARIO_NAME]_JOURNAL.md                           # Scenario journal from template
├── [SCENARIO_NAME]_FEASIBILITY_CHECK.md                 # Feasibility analysis
└── test_scripts/                                        # Any exploration scripts
```

## Instructions for Use

1. **Copy this template** for each new scenario (e.g., `PLACEHOLDER_DETECTION_IMPLEMENTATION.md`)
2. **Create scenario journal** from `research/SCENARIO_JOURNAL_TEMPLATE.md`
3. **Fill in scenario-specific details** in the "Scenario Information" section
4. **Start with Phase 0** - Create feature branch before any implementation work
5. **Work through each phase systematically** - Don't skip phases or checklist items
6. **Check off items** as you complete them and document findings in provided spaces
7. **Use this as your single source of truth** during implementation
8. **Update both checklist and journal** after each phase
9. **Commit your progress** at the end of each phase to track implementation status
10. **Complete with Phase 6** - Merge to main and archive documents

### 📝 Document Relationships
- **This Checklist**: Your working document for tracking implementation progress
- **Scenario Journal** (`research/[area]/[scenario]/[SCENARIO]_JOURNAL.md`): Technical decisions, philosophy checks, lessons learned
- **Feasibility Check** (`research/[area]/[scenario]/[SCENARIO]_FEASIBILITY_CHECK.md`): Research findings and constraint validation

---

## Scenario Information

**Scenario Name**: [e.g., "Table Comments Must Be At Least 10 Characters"]

**Feature File Location**: `tests/features/databricks__documentation__compliance.feature`

**Scenario Description**: 
```gherkin
[Copy the exact scenario from the feature file here]
```

**Implementation Priority**: [1-5, where 1 is simplest]

**Estimated Timeline**: [Research: X days, Implementation: Y days]

**Current Status**: 
- [ ] Phase 0: Git Workflow Setup - Not Started
- [ ] Phase 1: Research - Not Started
- [ ] Phase 2: Layer 1 (Unit Tests) - Not Started
- [ ] Phase 3: Layer 2 (Integration Tests) - Not Started
- [ ] Phase 4: Layer 3 (Production Tests) - Not Started
- [ ] Phase 5: Documentation & Completion - Not Started
- [ ] Phase 6: Git Integration & Cleanup - Not Started

---

## Phase 0: Git Workflow Setup

### 🌿 Branch Management
- [ ] **Current work committed**: Ensure main branch is clean or current work is committed
- [ ] **Create feature branch**: `git checkout -b feature/[scenario-name]` (e.g., `feature/placeholder-detection`)
- [ ] **Branch naming convention**: Use kebab-case matching the SCENARIO name from Makefile

### 📂 Document Setup
- [ ] **Create research directory**: `mkdir -p research/documentation/[scenario_name]`
- [ ] **Copy this checklist**: `cp SCENARIO_IMPLEMENTATION_CHECKLIST.md research/documentation/[scenario_name]/[SCENARIO_NAME]_IMPLEMENTATION.md`
- [ ] **Create scenario journal**: `cp research/SCENARIO_JOURNAL_TEMPLATE.md research/documentation/[scenario_name]/[SCENARIO_NAME]_JOURNAL.md`
- [ ] **Fill in initial details**: Update scenario name, dates, and description in both documents

### 📊 Phase 0 Checklist Update  
- [ ] **Update implementation checklist**: Mark Phase 0 complete
- [ ] **Document branch name**: Record feature branch name in checklist
- [ ] **Commit initial setup**: 
  ```bash
  git add research/documentation/[scenario_name]/
  git commit -m "Phase 0: Created feature branch and documents for [scenario name]"
  ```

**Phase 0 Complete**: ✅ Ready for research / ❌ Need to address git setup

---

## Phase 1: Focused Research (1-2 days)

### 🔍 Environment Setup
- [ ] `make venv-dev` - Development environment ready
- [ ] `make test-connection` - Databricks connection verified

### 🔍 Feasibility Analysis
- [ ] **Create and complete feasibility check**: 
  ```bash
  cp research/FEASIBILITY_CHECK_TEMPLATE.md \
     research/documentation/[scenario_name]/[SCENARIO_NAME]_FEASIBILITY_CHECK.md
  ```
  Follow the template completely - it covers SDK research, constraint testing, edge cases

- [ ] **Review known constraints**: Check `research/DATABRICKS_ENFORCEMENT_BEHAVIORS.md`

- [ ] **DECISION GATE**: Is scenario feasible? 
  - **Decision**: ✅ Feasible / ❌ Not Feasible
  - **Reasoning**: [If not feasible, document why and STOP here]

### ⚙️ Configuration Value Extraction
- [ ] **Identify business rule values**: Extract validation criteria that define pass/fail conditions
  - Thresholds (e.g., minimum length: 10, coverage percentage: 80)
  - Pattern lists (e.g., placeholder words: ["todo", "fixme", "tbd"])
  - Critical identifiers (e.g., PII column patterns: ["*_id", "email", "ssn"])
  - Validation flags (e.g., case_sensitive: false)

- [ ] **Add to config YAML** (`tests/config/documentation_config.yaml`):
  ```yaml
  # Example: Extract business rules, not implementation details
  placeholder_detection:
    patterns:          # Business rule: what words indicate placeholder text
      - "todo"
      - "fixme"
      - "tbd"
      - "placeholder"
    case_sensitive: false     # Business rule: how to match patterns
    
  # NOT: connection strings, file paths, or implementation details
  ```

- [ ] **Default Values Recommended**: [Values with reasoning]

- [ ] **Update ConfigLoader** (`tests/config/config_loader.py`):
  ```python
  # Add method to load new config section
  def get_placeholder_config(self):
      return self.config.get('placeholder_detection', {})
  ```

- [ ] **Configuration Dependencies**: [Any config that affects existing scenarios]

### 🔧 SDK Investigation
- [ ] **Data Structures Research**: How to access the relevant data?
  - **SDK Methods**: [List specific SDK methods/properties]
  - **Data Types**: [Document return types and structures]
  - **Access Patterns**: [How to get from client to the data you need]

- [ ] **Limitations Found**: [Any SDK limitations that affect implementation]

- [ ] **Edge Case Behavior**: [How does SDK handle edge cases?]
  ```python
  # Test cases created to understand SDK behavior:
  [Include small code snippets of your testing]
  ```

### 📋 Requirements Analysis
- [ ] **Feature File Requirements**: Exact requirements understood
  - **GIVEN conditions**: [What setup is required]
  - **WHEN actions**: [What triggers the validation]
  - **THEN expectations**: [What constitutes pass/fail]

- [ ] **Business Logic Questions Answered**:
  - [List any questions about the requirements and their answers]

### 📝 Research Documentation
- [ ] **Feasibility check completed** with all findings documented
- [ ] **Business rule values identified** and ready for configuration
- [ ] **Implementation approach decided** based on research findings

### 📊 Phase 1 Checklist Update
- [ ] **Update implementation checklist**: Mark all Phase 1 items as complete
- [ ] **Document research findings**: Add specific details to each section
- [ ] **Commit checklist progress**: `git add [checklist].md && git commit -m "Phase 1: Research complete"`

**Research Phase Complete**: ✅ Ready to proceed / ❌ Need more research

---

## Phase 2: Layer 1 - Unit Tests

### 🧪 Validator Implementation
- [ ] **New validator method(s) created**:
  - Method name(s): [e.g., `has_minimum_length()`]
  - Location: `tests/validators/documentation.py`
  - **Implementation notes**: [Key decisions made]

- [ ] **Configuration integration**:
  - [ ] Config values moved to `tests/config/documentation_config.yaml`
  - [ ] Validator uses config instead of hardcoded values
  - [ ] Default values documented

### 🧪 Unit Test Implementation
- [ ] **Comprehensive unit tests written**:
  - Files: `tests/unit/documentation/test_*_validators.py` (organized by scenario)
  - **Test cases**: [List main test scenarios]
  - **Edge cases covered**: [List edge cases tested]
  - **pytest patterns used**: fixtures, parametrize, markers

- [ ] **Existing tests updated** (if needed):
  - [Document any changes to existing unit tests]

### ✅ Layer 1 Validation
- [ ] **Run unit tests**: `make test-scenario SCENARIO=[scenario-name] LAYER=unit`
- [ ] **Run all unit tests**: `make test-unit` - All must pass
- [ ] **Code quality**: `make quality` - All checks pass
- [ ] **Performance acceptable**: Unit tests run quickly (< 5 seconds)

### 🔄 Layer 1 Philosophy Check

#### Philosophy Check Questions
- [ ] **Clean Implementation Check**:
  - ❓ Am I solving this requirement from first principles, or copying existing patterns?
  - ❓ Is this the most elegant modern Python approach?
  - ❓ Would this implementation make sense to someone who's never seen the existing code?

- [ ] **Requirements-Driven Check**:
  - ❓ What exactly does the feature file require here?
  - ❓ Am I adding complexity that isn't actually required?

- [ ] **Architecture Check**:
  - ❓ Does this maintain clean separation between the three layers?
  - ❓ Is this component reusable for other scenarios?
  - ❓ Am I introducing dependencies that violate layer boundaries?

#### Documentation and Improvements
- [ ] **Update scenario journal** (`research/documentation/[scenario]/[SCENARIO]_JOURNAL.md`):
  - Record philosophy check results in "After Layer 1" section
  - Document any architecture insights discovered
  - Note recommendations for future scenarios
  - Propose improvements based on development findings

- [ ] **Issues found during philosophy check**:
  - [ ] No issues found ✅
  - [ ] Issues found: **Check [🔧 Common Issues & Troubleshooting](#-common-issues--troubleshooting) section**
  - [ ] Issues addressed: [Document issues and how resolved]
  - [ ] Philosophy check re-run until passed

### 📊 Phase 2 Checklist Update
- [ ] **Update implementation checklist**: Mark all Phase 2/Layer 1 items as complete
- [ ] **Document test results**: Add test counts, coverage, and performance metrics
- [ ] **Update status in checklist header**: Show Layer 1 complete
- [ ] **Commit checklist progress**: `git add [checklist].md && git commit -m "Phase 2/Layer 1: Unit tests complete"`

**Layer 1 Complete**: ✅ Ready for Layer 2 / ❌ Need to address issues

---

## Phase 3: Layer 2 - Integration Tests

### 🏭 Test Table Specifications
- [ ] **Test table specs created**:
  - File: `tests/fixtures/table_factory.py` (update TABLE_SPECS)
  - **Test scenarios**: [List table types needed for testing]
  - **Expected outcomes**: [Which tables should pass/fail validation]

### 🏭 Integration Test Implementation
- [ ] **Integration tests written**:
  - File: `tests/integration/documentation/test_[scenario]_integration.py`
  - **Real Databricks objects**: Tables created and tested
  - **Session-scoped fixtures**: Optimal performance patterns used
  - **100% test coverage**: All created test conditions validated

- [ ] **Use proper fixture pattern** (MANDATORY for reliability):

  ❌ **NEVER do this** (fragile pattern that causes flaky tests):
  ```python
  def test_something(self, test_tables, validator, integration_discovery):
      discovered_tables = integration_discovery.discover_tables()
      # ❌ BAD: Searching by hardcoded table names
      for table in discovered_tables:
          if table.table == "some_hardcoded_name":  # FRAGILE!
              target_table = table
  ```

  ✅ **ALWAYS do this** (robust pattern using fixtures):
  ```python
  def _get_table_by_fixture_key(self, fixture_dict, key, discovered_tables):
      """Helper to get a table by fixture key from discovered tables."""
      table_name = fixture_dict[key]
      for table in discovered_tables:
          if table.full_name == table_name:
              return table
      return None

  def test_something(self, test_tables, validator, integration_discovery):
      # ✅ GOOD: Use fixture mapping to get specific table
      target_table = self._get_table_by_fixture_key(
          test_tables, "specific_fixture_key", integration_discovery.discover_tables()
      )
  ```

- [ ] **Test table cleanup verified**:
  - Context managers ensure cleanup on success and failure
  - No test tables left behind after test runs

### ✅ Layer 2 Validation
- [ ] **Run integration tests**: `make test-scenario SCENARIO=[scenario-name] LAYER=integration`
- [ ] **Debug if needed**: `make test-scenario SCENARIO=[scenario-name] LAYER=integration MODE=debug`
- [ ] **Performance acceptable**: Integration tests complete in < 30 seconds
- [ ] **Test coverage complete**: All test scenarios validated

### 🔄 Layer 2 Philosophy Check

#### Philosophy Check Questions
- [ ] **Integration Test Quality**:
  - ❓ Do tests properly isolate and use only their designated tables?
  - ❓ Is cleanup guaranteed even if tests fail?
  - ❓ Are we testing actual Databricks behavior, not assumptions?

- [ ] **Performance Check**:
  - ❓ Do integration tests complete in reasonable time (< 30 seconds)?
  - ❓ Are we using session-scoped fixtures appropriately?

#### Documentation and Improvements  
- [ ] **Update scenario journal** (`research/documentation/[scenario]/[SCENARIO]_JOURNAL.md`):
  - Record philosophy check results in "After Layer 2" section
  - Document any Databricks behavior discoveries
  - Note performance optimizations made
  - Propose improvements for integration test patterns

- [ ] **Issues found during philosophy check**:
  - [ ] No issues found ✅
  - [ ] Issues found: **Check [🔧 Common Issues & Troubleshooting](#-common-issues--troubleshooting) section**
  - [ ] Issues addressed: [Document issues and how resolved]
  - [ ] Philosophy check re-run until passed

### 📊 Phase 3 Checklist Update
- [ ] **Update implementation checklist**: Mark all Phase 3/Layer 2 items as complete
- [ ] **Document integration test results**: Tables created, test counts, cleanup verification
- [ ] **Update status in checklist header**: Show Layer 2 complete
- [ ] **Commit checklist progress**: `git add [checklist].md && git commit -m "Phase 3/Layer 2: Integration tests complete"`

**Layer 2 Complete**: ✅ Ready for Layer 3 / ❌ Need to address issues

---

## Phase 4: Layer 3 - Production Tests

### 🎭 BDD Step Definitions
- [ ] **Step definitions implemented**:
  - File: `tests/step_definitions/documentation_steps.py`
  - **New steps added**: [List any new step definitions needed]
  - **Existing steps reused**: [List existing steps that work]

- [ ] **Real data validation**:
  - Tests run against actual production data
  - Results make business sense
  - Discovery limits respected

### 🎭 Production Test Execution
- [ ] **Run production tests**: `make test-scenario SCENARIO=[scenario-name] LAYER=production`
- [ ] **Run all layers**: `make test-scenario SCENARIO=[scenario-name] LAYER=all`
- [ ] **Results analyzed**: [Document compliance rate and findings]
- [ ] **Performance acceptable**: Production tests complete in reasonable time

### ✅ Layer 3 Validation
- [ ] **BDD scenario passes**: Feature file scenario implemented correctly
- [ ] **Real compliance data**: Actual violations detected (if any)
- [ ] **Reporting functional**: Results properly logged and accessible

### 🔄 Layer 3 Philosophy Check

#### Philosophy Check Questions
- [ ] **Production Readiness**:
  - ❓ Do BDD scenarios accurately reflect business requirements?
  - ❓ Are we providing actionable compliance insights?
  - ❓ Does the scenario handle real-world data gracefully?

- [ ] **End-to-End Validation**:
  - ❓ Does the complete three-layer implementation work cohesively?
  - ❓ Are all configuration values properly externalized?
  - ❓ Is the implementation maintainable and well-documented?

#### Documentation and Improvements
- [ ] **Update scenario journal** (`research/documentation/[scenario]/[SCENARIO]_JOURNAL.md`):
  - Record philosophy check results in "After Layer 3" section
  - Document production insights and compliance findings
  - Finalize recommendations for similar scenarios
  - Complete "Final Status" section

- [ ] **Issues found during philosophy check**:
  - [ ] No issues found ✅
  - [ ] Issues found: **Check [🔧 Common Issues & Troubleshooting](#-common-issues--troubleshooting) section**
  - [ ] Issues addressed: [Document issues and how resolved]
  - [ ] Philosophy check re-run until passed

### 📊 Phase 4 Checklist Update
- [ ] **Update implementation checklist**: Mark all Phase 4/Layer 3 items as complete
- [ ] **Document production test results**: Real data findings, compliance rates, performance
- [ ] **Update status in checklist header**: Show Layer 3 complete
- [ ] **Commit checklist progress**: `git add [checklist].md && git commit -m "Phase 4/Layer 3: Production tests complete"`

**Layer 3 Complete**: ✅ Ready for Completion / ❌ Need to address issues

---

## Phase 5: Completion & Documentation

### 📚 Documentation Updates
- [ ] **README.md updated**:
  - New scenario added to feature list
  - Usage examples included
  - Any new commands documented

- [ ] **CLAUDE.md updated**:
  - New Make commands added
  - Implementation notes for future AI assistants
  - Any architectural changes documented

### 🔧 Make Commands
- [ ] **Update Makefile SCENARIOS list**:
  ```makefile
  SCENARIOS := table-comments comment-length placeholder-detection [new-scenario]
  ```
- [ ] **Add unit test mapping** (if needed):
  ```makefile
  [scenario-name]) unit_test="tests/unit/documentation/test_[scenario]_validators.py::TestClass" ;;
  ```
- [ ] **Verify commands work**:
  ```bash
  make list-scenarios  # Should show new scenario
  make test-scenario SCENARIO=[scenario-name] LAYER=all
  ```

### ✅ Final Validation
- [ ] `make quality` - All code quality checks pass
- [ ] **Full three-layer test suite**: All layers pass independently
- [ ] **End-to-end validation**: Complete workflow works
- [ ] **Documentation complete**: All docs updated

### 🎯 Scenario Completion
- [ ] **Implementation journal updated**: Final notes added
- [ ] **Lessons learned captured**: For future scenario implementations
- [ ] **Success metrics met**: All acceptance criteria satisfied

### 📊 Phase 5 Final Checklist Update
- [ ] **Update implementation checklist**: Mark all Phase 5 items as complete
- [ ] **Fill in Summary & Handoff section**: Complete all retrospective information
- [ ] **Update status in checklist header**: Show scenario COMPLETE
- [ ] **Final commit**: `git add [checklist].md && git commit -m "Phase 5: [Scenario name] implementation complete"`

**Scenario Implementation Complete**: ✅ Ready for git merge

---

## Phase 6: Git Integration & Cleanup

### 🌿 Git Merge Process
- [ ] **Commit final changes**: Ensure all changes are committed on feature branch
- [ ] **Clean local development files**: `git status` and `git restore` any local settings/cache files (e.g., `.claude/settings.local.json`)
- [ ] **Switch to main**: `git checkout main`
- [ ] **Pull latest main**: `git pull origin main` - Ensure main is up to date
- [ ] **Merge feature branch**: `git merge feature/[scenario-name]` - Fast-forward merge
- [ ] **Verify clean state**: `git status` shows clean working directory
- [ ] **Push to main**: `git push origin main`
- [ ] **Delete feature branch**: `git branch -d feature/[scenario-name]` - Clean up local branch

### 🧹 Cleanup & Verification
- [ ] **Archive implementation checklist**: If checklist is in root directory, move to `research/[scenario]/` folder (if already in research, mark complete)
- [ ] **Update main documentation (if needed)**: Add scenario to README only if it introduces new user-facing features
- [ ] **Post-merge verification**: `make test-scenario SCENARIO=[scenario-name] LAYER=all` to confirm integration success

### 📊 Phase 6 Final Checklist Update
- [ ] **Mark Phase 6 complete**: All git integration steps finished
- [ ] **Update scenario status**: Mark as fully integrated into main branch
- [ ] **Document completion**: Final commit with completion message

**Phase 6 Complete**: ✅ Scenario fully integrated / ❌ Need to address merge issues

---

## Summary & Handoff

### Implementation Results
**Scenario**: [Name]
**Status**: ✅ Complete / ❌ Incomplete
**Timeline**: Research: [X days], Implementation: [Y days]
**Issues encountered**: [Major challenges and how resolved]

### Key Learnings
- [List top 3-5 learnings that will help with future scenarios]

### Recommendations for Next Scenario
- [Any recommendations based on this implementation experience]

### Configuration Changes Made
```yaml
# Configuration added to documentation_config.yaml:
[Show the actual config added]
```

### Files Modified/Created
- [ ] `tests/validators/documentation.py` - [changes made]
- [ ] `tests/unit/documentation/test_*_validators.py` - [organized by scenario]
- [ ] `tests/integration/test_[scenario]_integration.py` - [created/modified]
- [ ] `tests/step_definitions/documentation_steps.py` - [changes made]
- [ ] `tests/config/documentation_config.yaml` - [changes made]
- [ ] `README.md` - [changes made]
- [ ] `CLAUDE.md` - [changes made]
- [ ] `Makefile` - [changes made]

---

## 🔧 Common Issues & Troubleshooting

### Philosophy Check Issues
**Problem**: Philosophy check reveals hardcoded values  
**Solution**: Move values to `documentation_config.yaml`, update validator to load from config

**Problem**: Integration tests have dependency on discovery order  
**Solution**: Use fixture mapping pattern with `_get_table_by_fixture_key()` helper

**Problem**: Tests fail due to leftover research tables  
**Solution**: Clean test environment: `make clean-test-tables` or manually drop tables

### Integration Test Issues
**Problem**: Context manager not cleaning up tables on test failure  
**Solution**: Ensure cleanup in `finally` block or use pytest fixture with proper teardown

**Problem**: Tests timeout when creating many tables  
**Solution**: Use session-scoped fixtures, create tables once per test class

**Problem**: "Table not found" errors in integration tests  
**Solution**: Check `test_tables` fixture returns full table names with catalog.schema prefix

### BDD/Production Issues
**Problem**: Step definitions not found  
**Solution**: Ensure exact text match between feature file and `@given/@when/@then` decorators

**Problem**: Production tests run against too many tables  
**Solution**: Check `DISCOVERY_MAX_TABLES` env variable, use appropriate limits

**Problem**: BDD tests not isolated  
**Solution**: Use scenario tags (e.g., `@placeholder-detection`) and run with marker

### Configuration Issues
**Problem**: New config values not being loaded  
**Solution**: Update `ConfigLoader` class methods to include new config sections

**Problem**: Tests using different config than validator  
**Solution**: Ensure both load from same `documentation_config.yaml` file

## Notes & Decisions Log

[Use this space throughout implementation to capture decisions, blockers, and solutions]

**Decision Log**:
- [Date]: [Decision made and reasoning]

**Blocker Log**:
- [Date]: [Blocker encountered and resolution]

**Performance Notes**:
- [Any performance observations or optimizations made]