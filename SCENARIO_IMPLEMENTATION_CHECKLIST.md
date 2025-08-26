# Scenario Implementation Checklist
**Master Working Document for End-to-End Scenario Implementation**

## Instructions for Use

1. **Copy this template** for each new scenario (e.g., `COMMENT_LENGTH_IMPLEMENTATION.md`)
2. **Fill in scenario-specific details** in the "Scenario Information" section
3. **Work through each checklist item** systematically
4. **Check off items** as you complete them
5. **Document findings and decisions** in the provided spaces
6. **Use this as your single source of truth** during implementation
7. **Update the checklist after each phase** using the "📊 Phase X Checklist Update" sections
8. **Commit your progress** at the end of each phase to track implementation status

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
- [ ] Phase 1: Research - Not Started
- [ ] Phase 2: Layer 1 (Unit Tests) - Not Started
- [ ] Phase 3: Layer 2 (Integration Tests) - Not Started
- [ ] Phase 4: Layer 3 (Production Tests) - Not Started
- [ ] Phase 5: Documentation & Completion - Not Started

---

## Phase 1: Focused Research (1-2 days)

### 🔍 Environment Setup
- [ ] `make venv-dev` - Development environment ready
- [ ] `make test-connection` - Databricks connection verified
- [ ] Research workspace set up and documented

### 🔍 Feasibility Analysis
**⚠️ CRITICAL: Read SCENARIO_EXPANSION_PLAN.md Section 1 before proceeding**
**📋 USE: research/FEASIBILITY_CHECK_TEMPLATE.md for step-by-step guidance**

- [ ] **Databricks Constraint Check**: Can we create test conditions that violate this rule?
  - **MUST VERIFY**: Databricks allows objects that VIOLATE the rule to exist
  - **MUST TEST**: Actually create tables/columns that should fail validation
  - **MUST CONFIRM**: The "bad" condition is achievable, not prevented by Databricks
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
  [Add YAML structure here]
  ```

- [ ] **Default Values Recommended**: [Values with reasoning]

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
- [ ] **Research template completed** (copy from SCENARIO_EXPANSION_PLAN.md)
- [ ] **All findings documented** before proceeding to implementation
- [ ] **Implementation approach decided** and documented

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
  - File: `tests/integration/test_[scenario]_integration.py`
  - **Real Databricks objects**: Tables created and tested
  - **Session-scoped fixtures**: Optimal performance patterns used
  - **100% test coverage**: All created test conditions validated

- [ ] **Test table cleanup verified**:
  - Context managers ensure cleanup on success and failure
  - No test tables left behind after test runs

### ✅ Layer 2 Validation
- [ ] `make test-integration-[scenario]` - All integration tests pass
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
- [ ] `make test-production-[scenario]` - Production tests execute
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
- [ ] **New Make commands added** (if needed):
  - `make test-[scenario]` commands
  - Updated help documentation
  - Commands tested and working

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
- [ ] **Archive checklist**: Move to `research/[scenario]/` folder for reference

**Scenario Implementation Complete**: ✅ Ready for next scenario

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

## Notes & Decisions Log

[Use this space throughout implementation to capture decisions, blockers, and solutions]

**Decision Log**:
- [Date]: [Decision made and reasoning]

**Blocker Log**:
- [Date]: [Blocker encountered and resolution]

**Performance Notes**:
- [Any performance observations or optimizations made]