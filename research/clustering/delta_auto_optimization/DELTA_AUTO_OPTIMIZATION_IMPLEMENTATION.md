# Scenario Implementation Checklist
**Master Working Document for End-to-End Scenario Implementation**

## Instructions for Use

1. **Copy this template** for each new scenario (e.g., `COMMENT_LENGTH_IMPLEMENTATION.md`)
2. **Fill in scenario-specific details** in the "Scenario Information" section
3. **Work through each checklist item** systematically
4. **Check off items** as you complete them
5. **Document findings and decisions** in the provided spaces
6. **Use this as your single source of truth** during implementation

---

## Scenario Information

**Scenario Name**: Tables can use delta auto-optimization for clustering

**Feature File Location**: `tests/features/databricks__clustering__compliance.feature`

**Scenario Description**: 
```gherkin
@clustering  @auto_clustering
Scenario: Tables can use delta auto-optimization for clustering
  Given I discover all accessible tables with clustering filters
  When I check delta auto-optimization settings
  Then tables with both optimizeWrite=true and autoCompact=true should be considered clustered
```

**Implementation Priority**: 2 (builds on cluster-by-auto foundation)

**Estimated Timeline**: Research: 1 day, Implementation: 1 day

---

## Phase 1: Focused Research (1-2 days)

### 🔍 Environment Setup
- [x] `make venv-dev` - Development environment ready
- [x] `make test-connection` - Databricks connection verified
- [x] Research workspace set up and documented

### 🔍 Feasibility Analysis
**⚠️ CRITICAL: Read SCENARIO_EXPANSION_PLAN.md Section 1 before proceeding**
**📋 USE: research/FEASIBILITY_CHECK_TEMPLATE.md for step-by-step guidance**

- [ ] **Databricks SDK Documentation Research**: Research delta auto-optimization properties
  - **MUST RESEARCH**: Databricks SDK documentation for delta auto-optimization settings
  - **MUST IDENTIFY**: Property names for optimizeWrite and autoCompact flags  
  - **MUST UNDERSTAND**: How these properties are exposed in table metadata
  - **Documentation Sources**: [List sources researched]
  
- [ ] **Databricks Constraint Check**: Can we create test conditions that violate this rule?
  - **MUST VERIFY**: Databricks allows tables with only one optimization flag enabled
  - **MUST TEST**: Actually create tables with different optimization combinations
  - **MUST CONFIRM**: The "both required" condition is achievable and detectable
  - **Findings**: [Document what you discovered]
  - **Test Cases Created**: [List small test cases you created to verify]
  
- [ ] **Edge Case Testability**: Can we test boundary conditions and failure scenarios?
  - **Edge Cases Identified**: [List specific edge cases]
  - **Testability Confirmed**: [Y/N with explanation]
  
- [ ] **Real-World Applicability**: Does this scenario detect meaningful compliance issues?
  - **Business Value**: [Explain why this validation matters]
  - **Problem Frequency**: [How often is this likely to be an issue?]

- [ ] **DECISION GATE**: Is scenario feasible? 
  - **Decision**: ✅ Feasible / ❌ Not Feasible
  - **Reasoning**: [If not feasible, document why and STOP here]

### ⚙️ Configuration Value Extraction
- [ ] **Hardcoded Values Identified**: [List all values that should be configurable]
  ```yaml
  # Proposed config structure:
  delta_auto_optimization:
    optimize_write_property: "optimizeWrite"  
    optimize_write_value: "true"
    auto_compact_property: "autoCompact"
    auto_compact_value: "true" 
    require_both_flags: true
  ```

- [ ] **Default Values Recommended**: [Values with reasoning]

- [ ] **Configuration Dependencies**: [Any config that affects existing scenarios]

### 🔧 SDK Investigation
- [ ] **Data Structures Research**: How to access delta auto-optimization data?
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
  - **GIVEN conditions**: Discover all accessible tables with clustering filters
  - **WHEN actions**: Check delta auto-optimization settings  
  - **THEN expectations**: Tables with both optimizeWrite=true AND autoCompact=true should be considered clustered

- [ ] **Business Logic Questions Answered**:
  - [List any questions about the requirements and their answers]

### 📝 Research Documentation
- [ ] **Research template completed** (copy from SCENARIO_EXPANSION_PLAN.md)
- [ ] **All findings documented** before proceeding to implementation
- [ ] **Implementation approach decided** and documented

**Research Phase Complete**: ✅ Ready to proceed / ❌ Need more research

---

## Phase 2: Layer 1 - Unit Tests

### 🧪 Validator Implementation
- [ ] **New validator method(s) created**:
  - Method name(s): [e.g., `has_delta_auto_optimization()`, `has_optimize_write()`, `has_auto_compact()`]
  - Location: `tests/validators/clustering.py`
  - **Implementation notes**: [Key decisions made]

- [ ] **Configuration integration**:
  - [ ] Config values moved to `tests/config/clustering_config.yaml`
  - [ ] Validator uses config instead of hardcoded values
  - [ ] Default values documented

### 🧪 Unit Test Implementation
- [ ] **Comprehensive unit tests written**:
  - Files: `tests/unit/clustering/test_delta_auto_optimization_validators.py`
  - **Test cases**: [List main test scenarios]
  - **Edge cases covered**: [List edge cases tested]
  - **pytest patterns used**: fixtures, parametrize, markers

- [ ] **Existing tests updated** (if needed):
  - [Document any changes to existing unit tests]

### ✅ Layer 1 Validation
- [ ] `make test-unit` - All unit tests pass
- [ ] `make quality` - Code quality checks pass
- [ ] **Performance acceptable**: Unit tests run quickly (< 5 seconds)

### 🔄 Layer 1 Philosophy Check
- [ ] **Post-Implementation Philosophy Check completed**:
  - Entry added to `IMPLEMENTATION_JOURNAL.md`
  - "Overall Architecture Insights" updated if needed
  - "Recommendations for Future Scenarios" updated
  - TodoWrite used to track updates

- [ ] **Issues found during philosophy check**:
  - [ ] No issues found ✅
  - [ ] Issues found and addressed: [Document issues and how resolved]
  - [ ] Philosophy check re-run until passed

**Layer 1 Complete**: ✅ Ready for Layer 2 / ❌ Need to address issues

---

## Phase 3: Layer 2 - Integration Tests

### 🏭 Test Table Specifications
- [ ] **Test table specs created**:
  - File: `tests/fixtures/clustering/delta_auto_optimization_specs.py`
  - **Test scenarios**: [List table types needed for testing]
  - **Expected outcomes**: [Which tables should pass/fail validation]

### 🏭 Integration Test Implementation
- [ ] **Integration tests written**:
  - File: `tests/integration/clustering/test_delta_auto_optimization_integration.py`
  - **Real Databricks objects**: Tables created and tested
  - **Session-scoped fixtures**: Optimal performance patterns used
  - **100% test coverage**: All created test conditions validated

- [ ] **Test table cleanup verified**:
  - Context managers ensure cleanup on success and failure
  - No test tables left behind after test runs

### ✅ Layer 2 Validation
- [ ] `make test-integration-delta-auto-optimization` - All integration tests pass
- [ ] **Performance acceptable**: Integration tests complete in < 30 seconds
- [ ] **Test coverage complete**: All test scenarios validated

### 🔄 Layer 2 Philosophy Check
- [ ] **Post-Implementation Philosophy Check completed**:
  - Entry added to `IMPLEMENTATION_JOURNAL.md`
  - Architecture insights updated
  - Lessons learned documented
  - TodoWrite used to track updates

- [ ] **Issues found during philosophy check**:
  - [ ] No issues found ✅
  - [ ] Issues found and addressed: [Document issues and how resolved]
  - [ ] Philosophy check re-run until passed

**Layer 2 Complete**: ✅ Ready for Layer 3 / ❌ Need to address issues

---

## Phase 4: Layer 3 - Production Tests

### 🎭 BDD Step Definitions
- [ ] **Step definitions implemented**:
  - File: `tests/step_definitions/clustering_steps.py`
  - **New steps added**: [List any new step definitions needed]
  - **Existing steps reused**: [List existing steps that work]

- [ ] **Real data validation**:
  - Tests run against actual production data
  - Results make business sense
  - Discovery limits respected

### 🎭 Production Test Execution
- [ ] `make test-production-delta-auto-optimization` - Production tests execute
- [ ] **Results analyzed**: [Document compliance rate and findings]
- [ ] **Performance acceptable**: Production tests complete in reasonable time

### ✅ Layer 3 Validation
- [ ] **BDD scenario passes**: Feature file scenario implemented correctly
- [ ] **Real compliance data**: Actual violations detected (if any)
- [ ] **Reporting functional**: Results properly logged and accessible

### 🔄 Layer 3 Philosophy Check
- [ ] **Post-Implementation Philosophy Check completed**:
  - Entry added to `IMPLEMENTATION_JOURNAL.md`
  - Final assessment updated
  - Production insights documented
  - TodoWrite used to track updates

- [ ] **Issues found during philosophy check**:
  - [ ] No issues found ✅
  - [ ] Issues found and addressed: [Document issues and how resolved]
  - [ ] Philosophy check re-run until passed

**Layer 3 Complete**: ✅ Ready for Completion / ❌ Need to address issues

---

## Phase 5: Completion & Documentation

### 📚 Documentation Updates
- [ ] **README.md updated**: [If needed for new patterns]
- [ ] **CLAUDE.md updated**: [If new Make commands added]

### 🔧 Make Commands
- [ ] **Make commands integrated**: 
  - `make test-scenario SCENARIO=delta-auto-optimization LAYER=[unit|integration|production]`
  - All commands tested and working across all three layers
  - Help documentation covers the pattern

### ✅ Final Validation
- [ ] **Code formatting**: `black` and `ruff` pass
- [ ] **Type checking**: `mypy` passes without ignore flags
- [ ] **Full three-layer test suite**: All layers pass independently
- [ ] **End-to-end validation**: Complete workflow works from unit tests to production analysis
- [ ] **Documentation complete**: Implementation details documented

### 🎯 Scenario Completion
- [ ] **Implementation journal updated**: Final production insights documented
- [ ] **Lessons learned captured**: Delta auto-optimization patterns documented
- [ ] **Success metrics met**: All acceptance criteria satisfied

---

## Summary & Handoff

### Implementation Results
**Scenario**: Tables can use delta auto-optimization for clustering
**Status**: ✅ Complete / ❌ Incomplete
**Timeline**: Research: [X days], Implementation: [Y days]
**Issues encountered**: [Major challenges and how resolved]

### Key Learnings
- [List top 3-5 learnings that will help with future scenarios]

### Recommendations for Next Scenario
- [Any recommendations based on this implementation experience]

### Configuration Changes Made
```yaml
# Configuration added to clustering_config.yaml:
[Show the actual config added]
```

### Files Modified/Created
- [ ] `tests/validators/clustering.py` - [changes made]
- [ ] `tests/unit/clustering/test_delta_auto_optimization_validators.py` - [created]
- [ ] `tests/integration/clustering/test_delta_auto_optimization_integration.py` - [created]
- [ ] `tests/fixtures/clustering/delta_auto_optimization_specs.py` - [created]
- [ ] `tests/step_definitions/clustering_steps.py` - [changes made]
- [ ] `tests/config/clustering_config.yaml` - [changes made]
- [ ] `Makefile` - [changes made]

---

## Notes & Decisions Log

[Use this space throughout implementation to capture decisions, blockers, and solutions]

**Decision Log**:
- [Date]: [Decision made and reasoning]

**Blocker Log**:
- [Date]: [Blocker encountered and resolution]

**Performance Notes**:
- [Any performance observations or optimizations made]