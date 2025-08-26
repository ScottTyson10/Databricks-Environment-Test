# Scenario Expansion Plan
**Building on the Proven Three-Layer Architecture Foundation**

## 🚨 CRITICAL SUCCESS PRINCIPLES

### 1. RESEARCH FIRST - NO EXCEPTIONS
**NEVER implement without thorough research. This is non-negotiable.**

Before writing ANY code for a new scenario:
- [ ] **Databricks Documentation Research**: Check official Databricks docs for feature constraints and limitations
- [ ] **Review Known Enforcement Behaviors**: Check `research/DATABRICKS_ENFORCEMENT_BEHAVIORS.md` for documented constraints
- [ ] **Scenario Feasibility Analysis**: 
  - **Critical**: Verify Databricks allows objects that VIOLATE the rule to exist
  - **Test**: Actually create tables/columns that should fail validation  
  - **Confirm**: The "bad" condition is achievable, not prevented by Databricks
- [ ] **Configuration Value Extraction**: Identify all hardcoded values that should be configurable
- [ ] Research Databricks SDK data structures for the specific feature
- [ ] Understand real-world data patterns and edge cases
- [ ] Document findings before implementation begins
- [ ] Validate assumptions with focused testing (create test cases to verify behavior)

**🚨 FEASIBILITY EXAMPLE**: For "comments must be 10+ characters" - can you actually create a table with a 5-character comment? If Databricks prevents this, the scenario is not testable.

### 2. MANDATORY PHILOSOPHY CHECKS
**After ANY significant work, STOP and complete ALL philosophy checks:**

Philosophy checks are **learning and improvement mechanisms** - they often reveal issues that require iteration.

✅ **Required after each component:**
1. Add entry to `IMPLEMENTATION_JOURNAL.md` "Post-Implementation Philosophy Check"
2. Update "Overall Architecture Insights" if patterns changed
3. Update "Recommendations for Future Scenarios" with lessons learned
4. Check if "Final Assessment" needs updating
5. Use TodoWrite to track these mandatory updates

🔄 **If Philosophy Check Reveals Issues:**
- **This is normal and expected** - philosophy checks are meant to catch problems
- **Address the issues** before proceeding to the next phase
- **Repeat/revise previous work** if needed based on learnings
- **Re-run the philosophy check** until no significant issues remain
- **Document the iteration process** - this is valuable learning

**Common issues philosophy checks reveal:**
- Architecture violations (wrong layer dependencies)
- Performance problems (integration tests too slow)
- Scope creep (added features not in requirements)
- Missing edge cases (incomplete test coverage)
- Configuration issues (hardcoded values found)

### 3. THREE-LAYER DISCIPLINE
**Maintain the proven architecture that delivered success:**
- Layer 1 (Unit): Fast validator logic, no dependencies
- Layer 2 (Integration): Real Databricks objects with test tables
- Layer 3 (Production): BDD against real data

### 4. INTEGRATION TEST FIXTURE USAGE - MANDATORY PATTERN
**ALWAYS use test fixtures properly in integration tests to ensure reliability:**

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

**Fixture Pattern Benefits:**
- **Isolation**: Tests use only their designated tables
- **Reliability**: No dependency on discovery order or parallel test interference
- **Debugging**: Clear error messages show exact table names
- **Maintainability**: Changes to table naming don't break tests

**Mandatory Requirements:**
- Every integration test class MUST have `_get_table_by_fixture_key` helper method
- Parametrized tests MUST use fixture keys, not hardcoded table name patterns
- Never search discovered tables by `table.table == "hardcoded_name"`
- Always use `table.full_name` for exact matching
- Remove unused fixture parameters to avoid linter warnings
- Use class-scoped fixtures for stateless components (`validator`, `integration_discovery`)

### 5. TEST-IMPLEMENTATION ALIGNMENT
**Based on recent learnings from placeholder detection fix:**

When implementation strategies evolve (e.g., from substring to word boundary matching):
- **Document the exact matching strategy** in code comments and journal
- **Update test cases to align** with the new strategy
- **Remove obsolete test cases** that were valid for old implementation but not new
- **Choose precision over coverage** - better to have accurate detection with fewer false positives
- **Test cases must reflect actual implementation behavior**, not historical approaches

## Current Status: Three Scenarios Complete ✅

**Implemented Scenarios:**

1. **"Tables must have a comment" scenario - FULLY IMPLEMENTED:**
   - Unit tests: 19 tests passing, comprehensive coverage
   - Integration tests: 11 tests, organized in `tests/integration/documentation/`
   - Production tests: BDD with tag-based isolation (`@table-comments`)

2. **"Table comments must be at least 10 characters" scenario - FULLY IMPLEMENTED:**
   - Unit tests: 22 tests passing, boundary & edge case testing
   - Integration tests: 17 tests, organized in `tests/integration/documentation/`
   - Production tests: BDD with tag-based isolation (`@comment-length`)

3. **"Table comments must not be placeholder text" scenario - FULLY IMPLEMENTED:**
   - Unit tests: 10 tests passing, pattern matching validation
   - Integration tests: 25 tests (after removing obsolete mixed_content test)
   - Production tests: BDD with tag-based isolation (`@placeholder-detection`)
   - Uses word boundary detection for precision over broad substring matching

4. **"Column documentation must meet coverage threshold" scenario - FULLY IMPLEMENTED:**
   - Unit tests: 9 tests passing, percentage calculations & boundary conditions
   - Integration tests: 17 tests, real Databricks table testing with 10 coverage scenarios
   - Production tests: BDD with tag-based isolation (`@column-coverage`)
   - Configuration-driven thresholds (80% from `documentation_config.yaml`)

5. **"Tables should have comprehensive documentation" scenario - FULLY IMPLEMENTED:**
   - **COMPREHENSIVE SCENARIO PATTERN**: Combines all individual checks into business-logic assessment
   - **Simple Production Focus**: All 5 checks must pass (no complex flexible rules)
   - **Complete Failure Reporting**: Lists ALL failed tables with specific reasons
   - Production-only scenario using `ComprehensiveDocumentationValidator`
   - No unit/integration layers - leverages existing individual validators
   - Configuration: `comprehensive_rules.required_checks` in `documentation_config.yaml`

**Key Infrastructure Improvements:**
- ✅ Parameterized Makefile system: `make test-scenario SCENARIO=X LAYER=Y MODE=Z`
- ✅ Tag-based BDD isolation for production tests
- ✅ Integration tests organized by domain (`tests/integration/documentation/`)
- ✅ Proper fixture usage patterns documented and enforced
- ✅ Class-scoped fixtures for performance optimization

**This foundation proves our approach works. Now we expand systematically.**

## Scenario Feasibility and Configuration Analysis

**MANDATORY: Complete this analysis for each scenario before any implementation**

### Feasibility Analysis Framework

For each scenario, we must validate:
1. **Databricks Constraints**: Can we actually create test conditions that violate the rule?
2. **Edge Case Testability**: Can we test boundary conditions and failure scenarios?
3. **Real-World Applicability**: Does this scenario detect meaningful compliance issues?

### Configuration Value Extraction

All configurable values must be moved to `tests/config/documentation_config.yaml`:
- Numeric thresholds (80%, 10 characters, etc.)
- Pattern definitions (placeholder text patterns)
- Business rules (critical column patterns)
- Validation settings (what counts as "documented")

### Data Structure Evolution Pattern
**Lesson learned from Critical Column Documentation implementation:**

When a scenario requires new data structures:

1. **Choose the appropriate location based on scope:**
   - `tests/utils/discovery.py` - For discovery-related structures (TableInfo, ColumnInfo)
   - `tests/validators/` - For validation-specific structures (e.g., ValidationResult, ComplianceReport)
   - `tests/models/` - For domain models if they grow complex enough
   - Within the validator class - For simple internal structures specific to one validator

2. **Location decision tree:**
   ```
   Is it used across multiple components?
   ├── YES → Place in shared location (utils/ or models/)
   └── NO → Is it specific to validation logic?
       ├── YES → Place in validators/ module
       └── NO → Is it only for test fixtures?
           ├── YES → Place in fixtures/ module
           └── NO → Reconsider if it's needed
   ```

3. **Implementation checklist:**
   - [ ] Create scenario research directory and journal: `research/[scenario_name]/[SCENARIO_NAME]_IMPLEMENTATION_JOURNAL.md`
   - [ ] Define the NamedTuple/dataclass in the appropriate location
   - [ ] Update all consumers to use the new type
   - [ ] Handle SDK None values - SDK may return None for fields we expect as strings
   - [ ] Add scenario to Makefile SCENARIOS list and unit test mapping
   - [ ] Run mypy early - Type checking catches these issues before integration tests
   - [ ] Validate layer completion: `make test-scenario SCENARIO=[name] LAYER=[completed-layer]`
   - [ ] Update implementation journal after each layer
   - [ ] Document why you chose that location in a comment

**Example:** ColumnInfo went in `discovery.py` because it's a core part of table discovery data, used by both discovery_engine and validators.

### Research File Organization Pattern

**New requirement (2025-08-25)**: All research and feasibility testing files must be organized in the `research/` directory:

```bash
# Create research directory for new scenario
mkdir research/[scenario_name]

# Move all research artifacts including scripts
mv [SCENARIO_NAME]_FEASIBILITY_CHECK.md research/[scenario_name]/
mv [SCENARIO_NAME]_RESEARCH.md research/[scenario_name]/
mv feasibility_test_*.py research/[scenario_name]/
mv test_*_feasibility.py research/[scenario_name]/
mv explore_*.py research/[scenario_name]/
```

**Benefits:**
- Keeps main directory clean and focused
- Preserves valuable research for future reference
- Makes it clear what files are temporary vs. permanent
- Easier to find related research documents

**Example:** Critical Column Documentation research is in `research/documentation/critical_columns_documentation/`

### Layer Validation Pattern

**New requirement (2025-08-25)**: After completing each layer, validate using the parameterized Make command system:

```bash
# After completing each layer, run validation
make test-scenario SCENARIO=[scenario-name] LAYER=unit          # Layer 1 validation
make test-scenario SCENARIO=[scenario-name] LAYER=integration   # Layer 2 validation  
make test-scenario SCENARIO=[scenario-name] LAYER=production    # Layer 3 validation
make test-scenario SCENARIO=[scenario-name] LAYER=all          # Full scenario validation
```

**Makefile Configuration Required:**
1. Add scenario to `SCENARIOS` list in Makefile
2. Add unit test class mapping in `_test-scenario-layer` function
3. Integration and production tests follow naming conventions automatically

**Example for critical-columns scenario:**
```makefile
# In Makefile
SCENARIOS := comment-length table-comments placeholder-detection critical-columns

# In _test-scenario-layer function  
critical-columns) unit_test="tests/unit/documentation/test_critical_columns_validators.py::TestCriticalColumnDocumentation" ;;
```

**Benefits:**
- Immediate validation after each layer completion
- Consistent testing interface across all scenarios
- Clear pass/fail feedback for layer implementation
- Integration with existing CI/CD patterns

### Implementation Journal Pattern

**New requirement (2025-08-25)**: Each scenario must have its own implementation journal for detailed tracking:

```bash
# Create research directory and scenario journal together
mkdir research/[feature_area]/[scenario_name]
cp research/SCENARIO_JOURNAL_TEMPLATE.md research/[feature_area]/[scenario_name]/[SCENARIO_NAME]_IMPLEMENTATION_JOURNAL.md

# All scenario artifacts in one place:
# - Implementation journal (tracks full lifecycle)  
# - Feasibility checks, exploration scripts, detailed analysis
```

**Journal Structure:**
- **Timeline**: Track research, Layer 1, Layer 2, Layer 3 phases
- **Technical decisions**: Document key implementation choices and rationale
- **Philosophy check results**: Record findings after each layer
- **Issues and resolutions**: Track problems encountered and solutions
- **Lessons learned**: Capture insights for future scenarios

**Benefits:**
- **Detailed tracking**: Complete history of scenario implementation
- **Knowledge preservation**: Technical decisions and reasoning documented
- **Problem solving**: Issues and solutions available for similar scenarios
- **Philosophy check accountability**: Ensures mandatory checks are completed

**Example**: `research/documentation/critical_columns_documentation/CRITICAL_COLUMNS_IMPLEMENTATION_JOURNAL.md` tracks the critical column scenario from research through completion.

## Comprehensive Scenario Implementation Pattern

**New Pattern Established**: For scenarios that combine multiple existing validation checks into business-logic-driven overall assessments.

### When to Use Comprehensive Scenarios
- **Business Decision Making**: Need holistic assessment for production readiness
- **Multiple Individual Scenarios Exist**: Combine 3+ related individual checks
- **Governance Requirements**: Business rules require ALL checks to pass
- **Actionable Reporting**: Need complete failure details for remediation

### Comprehensive Scenario Architecture

**1. Simple Production-Only Pattern:**
```yaml
comprehensive_rules:
  required_checks:
    - "table_has_comment"
    - "table_comment_length" 
    - "no_placeholder_comments"
    - "column_coverage >= 80"
    - "critical_columns_documented"
```

**2. Specialized Validator:**
- **Location**: `tests/validators/comprehensive.py`
- **Purpose**: Combines existing individual validators
- **No Business Logic Duplication**: Reuses existing validation methods
- **Rich Reporting**: Detailed statistics and complete failure lists

**3. Production-Only Implementation:**
- **Skip Unit/Integration**: Leverage existing individual scenario tests
- **BDD Feature Integration**: Direct production scenario with `@comprehensive` tag
- **Step Definitions**: Two steps - assessment and verification
- **Complete Failure Reporting**: List ALL non-compliant tables with reasons

### Implementation Checklist

**Configuration Setup:**
- [ ] Add `comprehensive_rules` section to `documentation_config.yaml`
- [ ] Define `required_checks` list combining individual scenario checks
- [ ] Update `config_loader.py` with `get_comprehensive_rules()` method

**Validator Implementation:**
- [ ] Create `tests/validators/comprehensive.py`
- [ ] Implement `ComprehensiveDocumentationValidator` class
- [ ] Use existing individual validators (no logic duplication)
- [ ] Return detailed results with individual check breakdowns

**Feature Integration:**
- [ ] Add `@comprehensive` scenario to BDD feature file
- [ ] Implement two step definitions: assessment (`@when`) and verification (`@then`)
- [ ] Ensure complete failure listing (not just examples)
- [ ] Add scenario to Makefile `SCENARIOS` list and marker mapping

**Testing and Validation:**
- [ ] Test with `make test-scenario SCENARIO=comprehensive LAYER=production`
- [ ] Verify all failed tables are listed with specific reasons
- [ ] Confirm individual check statistics are reported
- [ ] Validate configuration integration works correctly

### Key Implementation Principles

**Reuse Over Duplication:**
- Comprehensive validators MUST reuse existing individual validators
- No reimplementation of validation logic
- Shared configuration values from individual scenarios

**Complete Transparency:**
- List ALL failed tables, not just examples
- Show specific failure reasons for each table
- Report individual check compliance rates
- Provide actionable details for remediation

**Simple Business Logic:**
- Start with "all checks must pass" approach
- Avoid complex flexible rules until needed
- Configuration-driven check selection
- Clear pass/fail criteria

### Future Extensions

**When Comprehensive Scenarios Grow Complex:**
- Add flexible rule engine (OR/AND logic, weighted scoring)
- Profile-based rules (development vs production)
- Domain-specific comprehensive validators
- Custom aggregation strategies

**Example Use Cases:**
- Data Quality Comprehensive Check (combines completeness, accuracy, consistency)
- Security Comprehensive Check (combines access controls, encryption, audit)
- Performance Comprehensive Check (combines query performance, storage, indexing)

**This pattern provides the foundation for sophisticated business-rule-driven validation while maintaining architectural simplicity.**

## Remaining Scenarios Analysis

From `tests/features/databricks__documentation__compliance.feature`:

### 1. Table Comments Must Not Be Placeholder Text

**Feasibility Analysis:**
- [ ] **Databricks Constraint Check**: Can we create tables with placeholder comments? (Verify no Databricks restrictions)
- [ ] **Test Condition Creation**: Can we create test tables with various placeholder patterns?
- [ ] **Edge Case Validation**: Can we test tables with mixed placeholder/real content?

**Configuration Values to Extract:**
- [ ] **Placeholder Patterns**: Move hardcoded patterns like "TODO", "FIXME" to config YAML
- [ ] **Case Sensitivity**: Should pattern matching be case-sensitive? (config setting)
- [ ] **Partial Match Rules**: How to handle comments that contain both placeholder and real text

**Research Requirements:**
- [ ] **SDK Research**: How do we detect placeholder patterns in comments?
- [ ] **Pattern Research**: What placeholder patterns should we detect? (research common patterns in literature/best practices)
- [ ] **Configuration Research**: Should placeholder patterns be configurable?
- [ ] **Edge Cases**: Empty strings, whitespace, mixed content with placeholders
- [ ] **Optional Real Data**: Only if existing tables happen to have placeholder comments (unlikely)

### 2. Table Comments Must Be At Least 10 Characters ✅ **COMPLETED**

**Feasibility Analysis:**
- [x] **Databricks Constraint Check**: ✅ Confirmed - Databricks allows comments of any length (1-9 characters work)
- [x] **Test Condition Creation**: ✅ Created test tables with 1, 5, 9, 10, 11+ character comments
- [x] **Edge Case Validation**: ✅ Tested whitespace-only, Unicode, empty, and None comments

**Configuration Values to Extract:**
- [x] **Minimum Length Threshold**: ✅ Added `minimum_comment_length: 10` to config YAML
- [x] **Whitespace Handling**: ✅ Decided whitespace counts toward length (all characters count)
- [x] **Character Counting Method**: ✅ Using Unicode-aware Python `len()` function

**Research Requirements:**
- [x] **Business Logic Research**: ✅ 10 characters ensures meaningful vs placeholder comments
- [x] **Unicode Research**: ✅ Python `len()` correctly handles multi-byte Unicode characters
- [x] **Edge Cases**: ✅ All edge cases documented and tested (whitespace, Unicode, None, boundaries)
- [x] **Length Validation Research**: ✅ Tested all string scenarios, simple `len()` works perfectly
- [x] **SDK Integration**: ✅ `table.comment` property provides direct string access

### 3. Column Documentation Must Meet 80% Threshold ✅ **RESEARCH COMPLETE**

**Feasibility Analysis:**
- [x] **Databricks Constraint Check**: ✅ Can create tables with any documentation level (0%, 50%, 79%, 80%, 100%)
- [x] **Test Condition Creation**: ✅ Successfully created tables with precise percentages
- [x] **Edge Case Validation**: ✅ Databricks allows 0-column tables! Handled as 100% compliant (vacuous truth)

**Configuration Values to Extract:**
- [x] **Coverage Threshold**: ✅ Will add `column_documentation_coverage_threshold: 80` to config
- [x] **Column Inclusion Rules**: ✅ ALL columns count (no system column exclusion needed)
- [x] **Documentation Definition**: ✅ Same as table comments: not None and not empty/whitespace

**Research Requirements:**
- [x] **SDK Research**: ✅ Access via `table.columns[].comment` property
- [x] **Calculation Research**: ✅ Count all columns equally, simple percentage calculation
- [x] **Configuration Research**: ✅ Start with global threshold, can add per-schema overrides later
- [x] **Statistical Testing**: ✅ Tested 0%, 50%, 75%, 79%, 80%, 81%, 100% cases
- [x] **Edge Cases**: ✅ 0-column tables handled as 100% compliant

**Implementation Ready**: See `research/COLUMN_DOCUMENTATION_RESEARCH.md` for complete details

### 4. Critical Columns Must Be Documented

**Feasibility Analysis:**
- [ ] **Databricks Constraint Check**: Can we create tables with columns matching critical patterns but without documentation?
- [ ] **Test Condition Creation**: Can we create tables with critical columns (PII, keys) with and without comments?
- [ ] **Edge Case Validation**: What about columns that partially match patterns? Case sensitivity?

**Configuration Values to Extract:**
- [ ] **Critical Column Patterns**: Move hardcoded patterns to config YAML (e.g., `*_id`, `email`, `password`)
- [ ] **Pattern Matching Rules**: Case sensitivity, exact match vs. partial match settings
- [ ] **Documentation Requirements**: What level of documentation is required for critical columns?

**Research Requirements:**
- [ ] **Pattern Research**: How do we identify "critical" columns (PII, keys, etc.)?
- [ ] **Configuration Research**: How should critical column patterns be defined?
- [ ] **SDK Research**: Can we detect column types, constraints, or other metadata?
- [ ] **Industry Standards**: What columns are typically considered critical in data governance?
- [ ] **Optional Real Data**: Only if you want to see actual column naming patterns in your environment

### 5. Comprehensive Documentation Check

**Feasibility Analysis:**
- [ ] **Databricks Constraint Check**: Can we create tables that fail multiple validation rules simultaneously?
- [ ] **Test Condition Creation**: Can we create tables with complex combinations of compliance failures?
- [ ] **Edge Case Validation**: How do conflicting validations interact? Performance with large datasets?

**Configuration Values to Extract:**
- [ ] **Validation Selection**: Which validations are included in "comprehensive"? (configurable subset)
- [ ] **Aggregation Rules**: How are multiple failures combined? (fail-fast vs. collect-all)
- [ ] **Reporting Thresholds**: When does comprehensive check fail? (any failure vs. percentage)

**Research Requirements:**
- [ ] **Integration Research**: How do we combine multiple validation results?
- [ ] **Performance Research**: Can we run all checks efficiently?
- [ ] **Reporting Research**: How should comprehensive results be structured?
- [ ] **Configuration Research**: Should users be able to customize the comprehensive check?

## Configuration Management Strategy

### Current Configuration File
`tests/config/documentation_config.yaml` currently contains basic patterns. We need to expand it systematically.

### Configuration Values to Add:
```yaml
# Validation Thresholds
minimum_comment_length: 10
column_documentation_coverage_threshold: 80  # percentage

# Placeholder Detection
placeholder_patterns:
  - "todo"
  - "fixme" 
  - "tbd"
  - "placeholder"
case_sensitive_placeholders: false
allow_mixed_placeholder_content: false

# Critical Columns
critical_column_patterns:
  - pattern: "*_id"
    description: "Identifier columns"
  - pattern: "email"
    description: "Email address columns"  
  - pattern: "password"
    description: "Password columns"
critical_column_case_sensitive: false

# Column Coverage Rules
include_system_columns: false
require_non_empty_comments: true
require_non_whitespace_comments: true

# Comprehensive Documentation Assessment (✅ IMPLEMENTED)
comprehensive_rules:
  required_checks:
    - "table_has_comment"
    - "table_comment_length" 
    - "no_placeholder_comments"
    - "column_coverage >= 80"
    - "critical_columns_documented"
```

### Configuration Update Process:
1. **Before implementing any scenario**: Identify all hardcoded values
2. **Add to config YAML**: Define structure and default values
3. **Update existing code**: Modify current validators to use config
4. **Test configuration**: Verify config changes work with existing tests

## Implementation Strategy: Focused Scenario-by-Scenario Approach

**Complete each scenario end-to-end before moving to the next one.**

### Scenario Implementation Cycle (Repeat for Each Scenario)

```
┌─────────────────────────────────────────────────────────────┐
│ 1. FOCUSED RESEARCH PHASE (1-2 days)                       │
│    ├── Feasibility Analysis                                │
│    ├── Configuration Value Extraction                      │
│    ├── SDK & Real Data Investigation                       │
│    └── Document All Findings                               │
├─────────────────────────────────────────────────────────────┤
│ 2. LAYER 1: UNIT TESTS                                     │
│    ├── Implement validator methods                         │
│    ├── Write comprehensive unit tests                      │
│    └── MANDATORY PHILOSOPHY CHECK                          │
├─────────────────────────────────────────────────────────────┤
│ 3. LAYER 2: INTEGRATION TESTS                              │
│    ├── Create test table specifications                    │
│    ├── Implement integration tests                         │
│    └── MANDATORY PHILOSOPHY CHECK                          │
├─────────────────────────────────────────────────────────────┤
│ 4. LAYER 3: PRODUCTION TESTS                               │
│    ├── Implement BDD step definitions                      │
│    ├── Test against real data                              │
│    └── MANDATORY PHILOSOPHY CHECK                          │
├─────────────────────────────────────────────────────────────┤
│ 5. COMPLETION                                               │
│    ├── Update documentation                                │
│    ├── 🚨 CRITICAL: Update Makefile & help commands        │
│    ├── Capture learnings for future scenarios              │
│    └── Final validation & move to next scenario            │
└─────────────────────────────────────────────────────────────┘
```

### Implementation Order (Simplest to Most Complex)
1. **Comment Length Validation** (extends existing comment logic) ✅ **COMPLETED**
2. **Placeholder Text Detection** (pattern matching on existing comments)
3. **Critical Column Documentation** (new column analysis)
4. **Column Coverage Threshold** (statistical analysis)

### Future Integration Scenarios (After Core Scenarios Complete)
5. **Comprehensive Check** (integration of all individual validators - implement after 1-4 complete)

### Make Command Updates (Step 5 of Each Scenario)

**✅ SOLVED: Elegant Parameterized Testing System**

**No longer need individual commands per scenario!** We now use a parameterized system that scales automatically:

#### New Elegant Approach (Current):
```bash
# Parameterized testing - works for any scenario
make test-scenario SCENARIO=comment-length                    # All layers
make test-scenario SCENARIO=comment-length LAYER=integration  # Specific layer  
make test-scenario SCENARIO=comment-length MODE=debug         # Debug mode
make test-scenario SCENARIO=comment-length LAYER=unit MODE=failfast # Combined

# Scenario management
make list-scenarios         # See available scenarios
make test-all-scenarios     # Run all implemented scenarios
```

#### What You Need to Do for New Scenarios:
1. **Add scenario name** to `SCENARIOS` variable in Makefile
2. **Update unit test mapping** in `_test-scenario-layer` function (if needed)  
3. **That's it!** The system automatically handles all combinations

#### Benefits of Clean Approach:
- **Scales automatically**: No individual commands needed per scenario
- **Consistent interface**: Same parameters work for all scenarios
- **Flexible combinations**: Mix and match SCENARIO, LAYER, and MODE
- **Self-documenting**: `make list-scenarios` shows what's available
- **Maintainable**: Single implementation handles all scenarios
- **Clean codebase**: No command explosion or legacy cruft

#### Implementation Example:
```bash
# In Makefile, currently implemented scenarios:
SCENARIOS := comment-length table-comments

# To add new scenarios, just update the SCENARIOS variable:
# SCENARIOS := comment-length table-comments placeholder-detection

# Everything else works automatically!
make test-scenario SCENARIO=comment-length LAYER=integration

# Core commands remain simple:
make test-unit           # All unit tests
make test-integration    # All integration tests (now organized in documentation/ folder)
```

#### Removed Legacy Commands:
- ~~`test-unit-table-comments`~~ → Use `make test-scenario SCENARIO=comment-length LAYER=unit`
- ~~`test-integration-comment-length`~~ → Use `make test-scenario SCENARIO=comment-length LAYER=integration`
- ~~`test-*-debug`~~ → Use `make test-scenario MODE=debug`
- ~~`test-*-failfast`~~ → Use `make test-scenario MODE=failfast`

### Strengthened Philosophy Check Requirements

**Based on learnings from comment length implementation failures:**

#### Layer 2 Philosophy Check Must Include:
1. **Environment Verification**: 
   - Confirm clean test schema (no leftover research tables)
   - Verify table creation and cleanup works correctly
   - Test that discovery finds exactly expected tables

2. **Databricks Behavior Validation**:
   - Verify actual SDK behavior matches assumptions
   - Test edge cases like empty strings, None values, special characters
   - Document any platform-specific behavior discovered

3. **Test Robustness**:
   - Ensure tests filter results appropriately (no hard-coded counts)
   - Verify tests work in environments with pre-existing data
   - Test error handling for missing/unexpected data

#### Layer 3 Philosophy Check Must Include:
1. **BDD Integration**:
   - Verify step definitions execute without errors
   - Test that scenarios run against real discovered data
   - Confirm compliance reporting works correctly

2. **Production Readiness**:
   - Test that scenarios handle large datasets gracefully
   - Verify performance with realistic data volumes
   - Confirm error handling and logging work in production context

### Integration Test Organization

**All integration tests are now organized by domain for scalability:**

```
tests/integration/
├── documentation/           # Documentation compliance tests
│   ├── test_comment_length_integration.py    (17 tests)
│   └── test_table_comments_integration.py    (11 tests)
└── [future domains]/       # e.g., security/, performance/, data_quality/
```

**Benefits:**
- Clear domain separation
- Easy to find related tests
- Prevents overwhelming flat structure
- Scales to hundreds of test files

### Captured Learnings from Comment Length Implementation

**For Future Scenario Implementations:**

1. **Test Data Accuracy**: Always verify test data character counts manually
   - Issue: Test claimed `"   test   "` was 9 chars, actually 10 chars
   - Solution: Use `python -c "print(len('string'))"` to verify test expectations

2. **Configuration Integration**: Load config values in validator `__init__`
   - Pattern: `self.minimum_comment_length = config['validation_thresholds']['minimum_comment_length']`
   - Current: Using hardcoded value `10` until config loader implemented

3. **Unicode Handling**: Python's `len()` correctly counts Unicode characters
   - Verified: `len("🚀")` returns 1 (character count, not bytes)
   - Recommendation: Continue using `len()` for all future length validations

4. **Edge Case Testing Patterns**: 
   - Boundary conditions: exactly N-1, N, N+1 characters
   - None handling: Always check for None before string operations
   - Whitespace: Test leading, trailing, and embedded whitespace separately

5. **Test Organization**: Use pytest classes to group related test scenarios
   - Pattern: `TestCommentLengthValidation` class for all length-related tests
   - Benefit: Clear organization and shared fixtures

6. **Environment Cleanup**: Always clean up research/feasibility test artifacts
   - Issue: Leftover `feasibility_comment_length_1char` table broke integration tests
   - Solution: Create dedicated cleanup scripts or use proper test isolation
   - Lesson: Philosophy checks should verify clean test environment

7. **Databricks Behavior Verification**: Test actual Databricks behavior, not assumptions
   - Issue: Assumed empty string comments stay as `""`, but Databricks converts to `None`
   - Solution: Always test against real Databricks to verify SDK behavior
   - Lesson: Layer 2 integration tests must validate actual platform behavior

8. **Test Robustness**: Filter test results instead of assuming exact counts
   - Issue: Hard-coded table count assumptions broke when environment had extra tables
   - Solution: Filter to only tables created by the test using naming patterns
   - Pattern: `[table for table in discovered if table.name.startswith("test_")]`

9. **Comprehensive Failure Reporting**: Default to showing ALL failures for complete picture
   - **Philosophy**: Continue on failure by default (`--maxfail=0`) for comprehensive reports
   - **Rationale**: Integration tests, unit tests, and production BDD should show all issues
   - **Commands Available**:
     - Default: `make test-*` (continue on failure, see all issues)
     - Debug: `make test-*-debug` (detailed tracebacks + continue on failure)
     - Fail-fast: `make test-*-failfast` (stop on first failure, quick feedback)
   - **Benefit**: Developers can fix multiple issues in one cycle instead of iterative debugging

10. **Elegant Parameterized Testing System**: Avoid command explosion with scalable architecture
   - **Problem**: Individual commands per scenario (6+ commands × 5 scenarios = 30+ commands)
   - **Solution**: Parameterized `make test-scenario SCENARIO=X LAYER=Y MODE=Z` approach
   - **Benefits**: Scales automatically, consistent interface, flexible combinations
   - **Implementation**: Single function handles all scenarios with parameter mapping
   - **Future-proof**: Adding scenarios requires only updating `SCENARIOS` variable

## Detailed Research Commands and Steps

### Research Phase Commands (For Each Scenario)
```bash
# 1. Environment setup
make venv-dev
make test-connection

# 2. SDK and requirements research (primary focus)
# - Read Databricks SDK documentation for relevant APIs
# - Understand the feature file requirements precisely
# - Research edge cases and failure conditions

# 3. Optional data exploration (if relevant)
make test-discovery  # Only if you need to understand existing patterns
make list-tables     # Only if you need to see real table structures
# NOTE: Existing data might not show the problems you're trying to detect

# 4. Focused test case creation
# - Create small test cases to understand data structures
# - Test SDK behavior with edge cases
# - Validate assumptions with minimal examples
```

### Implementation Phase Pattern (For Each Scenario)

Each scenario follows this exact pattern - complete one step before moving to the next:

#### 1. Focused Research (1-2 days)
- [ ] Complete feasibility analysis for THIS scenario only
- [ ] Extract configuration values for THIS scenario only  
- [ ] Research SDK patterns for THIS scenario only
- [ ] Document findings using research template
- [ ] **DECISION GATE**: Is scenario feasible? If no, document why and skip

#### 2. Layer 1: Unit Tests
- [ ] Implement new validator method(s)
- [ ] Write comprehensive unit tests with pytest patterns
- [ ] Update existing tests if needed
- [ ] Run `make test-unit` - all tests must pass
- [ ] **MANDATORY PHILOSOPHY CHECK** - update journal
  - [ ] If issues found: address them and repeat until check passes
  - [ ] Document any iterations and learnings

#### 3. Layer 2: Integration Tests  
- [ ] Create test table specifications
- [ ] Implement integration tests with real Databricks objects
- [ ] Run `make test-integration` - all tests must pass
- [ ] **MANDATORY PHILOSOPHY CHECK** - update journal
  - [ ] If issues found: address them and repeat until check passes
  - [ ] Document any iterations and learnings

#### 4. Layer 3: Production Tests
- [ ] Implement BDD step definitions
- [ ] Test against real production data
- [ ] Run `make test-production` - verify results make sense
- [ ] **MANDATORY PHILOSOPHY CHECK** - update journal
  - [ ] If issues found: address them and repeat until check passes
  - [ ] Document any iterations and learnings

#### 5. Completion & Documentation
- [ ] Update README.md with new scenario
- [ ] Update CLAUDE.md with new commands
- [ ] Add Make commands for new scenario
- [ ] Run `make quality` - all checks must pass
- [ ] **FINAL VALIDATION**: Full three-layer test suite passes
- [ ] **MOVE TO NEXT SCENARIO** - start research phase for next one

## Reference: Scenario-Specific Research Questions

**IMPORTANT**: Use these sections ONLY when you're actively researching that specific scenario. Do NOT research all scenarios upfront.

**Current recommendation**: Start with **Comment Length Validation** as it's the simplest extension of existing logic.

## Mandatory Research Documentation

### For Each Scenario, Document:
1. **SDK Findings**: Exact data structures and access patterns
2. **Real Data Patterns**: What we observed in actual environments
3. **Edge Cases**: Unusual situations that need handling
4. **Performance Considerations**: Any scalability concerns
5. **Configuration Decisions**: What should be configurable vs. hardcoded

### Research Template:
```markdown
## Research Notes: [Scenario Name]

### Feasibility Analysis:
- Databricks constraints validated: [Y/N]
- Test conditions creatable: [Y/N] 
- Edge cases testable: [Y/N]
- Real-world applicability: [Y/N]
- **DECISION**: Scenario is feasible/not feasible because: [reason]

### Configuration Values Identified:
- Hardcoded values found: [list]
- Proposed config structure: [YAML structure]
- Default values recommended: [values with reasoning]

### SDK Investigation:
- Data structures: 
- Access patterns:
- Limitations found:

### Real Data Analysis (if relevant):
- Patterns observed: [only if existing data was useful for research]
- Edge cases found: [from real data, if any]
- Performance considerations: [if tested with realistic data volumes]
- Note: Often existing data won't show the problems we're trying to detect

### Implementation Decisions:
- Approach chosen:
- Configuration strategy:
- Why this approach:

### Databricks Constraint Validation:
- Can create failing test conditions: [Y/N]
- Specific constraints found: [list]
- Workarounds needed: [list]

### Questions for Production:
- [ ] Issue 1
- [ ] Issue 2
```

## Success Criteria

### Before Implementation:
- [ ] **Feasibility analysis complete**: Scenario proven testable in Databricks
- [ ] **Configuration values extracted**: All hardcoded values identified and moved to config
- [ ] All research documented for target scenario
- [ ] Data access patterns verified with real environment
- [ ] Edge cases identified and documented
- [ ] Implementation approach validated

### After Each Layer:
- [ ] All tests passing
- [ ] Philosophy check completed and documented in journal
- [ ] Performance acceptable (Layer 2 < 30 seconds, Layer 3 reasonable)
- [ ] Code quality checks passing (`make quality`)

### After Each Scenario:
- [ ] Three-layer architecture maintained
- [ ] Integration with existing Make commands
- [ ] Documentation updated (README, CLAUDE.md)
- [ ] Lessons learned captured in journal

## Risk Mitigation

### Common Pitfalls to Avoid:
1. **Skipping research** → Implementing based on assumptions
2. **Scope creep** → Adding features not in the feature file
3. **Architecture drift** → Breaking three-layer separation
4. **Performance regression** → Not testing with realistic data volumes
5. **Missing philosophy checks** → Losing track of lessons learned

### Mitigation Strategies:
1. **Research checkpoints** → No code without documented research
2. **Scope discipline** → Stick to exact feature file requirements
3. **Architecture validation** → Verify layer separation in each implementation
4. **Performance baselines** → Establish and maintain performance targets
5. **Philosophy check enforcement** → Use TodoWrite to track mandatory checks

## Getting Started

### Immediate Next Steps:
1. **Choose first scenario**: Recommend starting with **Comment Length Validation** (simplest)
2. **Begin focused research phase** for that scenario ONLY (1-2 days)
3. **Use research template** to document findings
4. **Complete full implementation cycle** before moving to next scenario

### Example: Starting with Comment Length Validation

```bash
# Step 1: Research Phase (1-2 days)
make venv-dev
make test-connection

# Primary research (focus here):
# - Read feature file: "comments must be at least 10 characters"
# - Research Databricks SDK: how to access table.comment
# - Test edge cases: unicode, whitespace, empty strings
# - Extract config: move "10" to YAML as minimum_comment_length

# Optional (only if needed):
# make test-discovery  # Might not show short comments (the problem we're detecting)

# Step 2-5: Implementation (following the cycle pattern)
# Layer 1 → Philosophy Check → Layer 2 → Philosophy Check → Layer 3 → Philosophy Check → Documentation
```

### Critical Success Factors:
- **Stay focused**: Research and implement ONE scenario completely before starting the next
- **Validate feasibility**: Don't implement scenarios that can't be properly tested
- **Extract configuration**: Move all hardcoded values to YAML before implementing
- **Embrace iterative philosophy checks**: Expect to find issues and iterate based on learnings
- **Complete philosophy checks**: These are mandatory quality gates, not optional checkboxes
- **Test incrementally**: Each layer must pass before moving to the next

**Remember: This focused, scenario-by-scenario approach with immediate validation loops will deliver better results than trying to research everything upfront.**