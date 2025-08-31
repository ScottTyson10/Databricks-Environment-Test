# Feasibility Check Template
**Critical Step: Verify Databricks Allows Rule Violations**

> **Organization**: Copy this template to `research/[feature_area]/[scenario_name]/[SCENARIO_NAME]_FEASIBILITY_CHECK.md` to keep the main directory clean. Any feasibility test scripts should also be stored in the same research directory.

## Why This Matters

**If Databricks prevents the "bad" condition from existing, your validation scenario is impossible to test.**

Example: If you're testing "comments must be 10+ characters" but Databricks won't let you create tables with short comments, your test scenario is pointless.

## Feasibility Check Process

### Step 1: Online Documentation Research ⭐ **MANDATORY FIRST STEP**

# ⛔ STOP! DO NOT WRITE ANY CODE YET! ⛔

**🚫 ABSOLUTELY NO CODE UNTIL RESEARCH IS COMPLETE**: You MUST complete ALL online research using WebSearch/WebFetch tools BEFORE writing any test code, SQL commands, or Python scripts.

**CRITICAL REQUIREMENT**: 
1. ✅ FIRST: Use WebSearch to find Databricks SDK documentation
2. ✅ SECOND: Use WebFetch to read relevant documentation pages
3. ✅ THIRD: Document findings in this template
4. ❌ ONLY THEN: Write test code to validate your research

**WHY THIS MATTERS**: Writing code before research leads to:
- Wasted time on incorrect approaches
- Missing simpler solutions that are documented
- Creating unnecessary complexity
- Violating the research-first principle

#### 🔍 **STEP 1A: Architecture & Infrastructure Discovery** (CRITICAL - can save days of work)
This step MUST be done first to avoid rebuilding existing infrastructure!
- [ ] **Existing Infrastructure Check**: Does this scenario belong to an existing domain (clustering, documentation, etc.)?
  - Search for related validators: `find tests/ -name "*validator*.py" -exec grep -l "domain_keyword" {} \;`
  - Check for domain-specific config files: `ls tests/config/*_config.yaml`
- [ ] **Related Scenarios**: Are there similar scenarios already implemented?
  - Check feature files for related scenarios: `grep -r "similar_keyword" tests/features/`
  - Look for existing test patterns: `find tests/ -name "*test*" -exec grep -l "related_concept" {} \;`
- [ ] **Configuration Domain**: Does this need new config or extend existing config?
  - Check if domain-specific config exists (e.g., `clustering_config.yaml` vs `documentation_config.yaml`)
- [ ] **Validator Class**: Which validator should be extended/used?
  - Document existing validators and their purposes
  - Determine if new validator needed or existing one can be extended

#### 🔍 **STEP 1B: Databricks SDK & API Research**

#### API & SDK Questions to Research:
- [ ] **API Methods**: What SDK methods/properties are available for this scenario?
- [ ] **Data Structures**: What classes (TableInfo, etc.) contain relevant information?
- [ ] **Property Names**: What are the exact property/attribute names to check?
- [ ] **Data Types**: What data types are returned (string, list, boolean, etc.)?
- [ ] **SDK Version Requirements**: Are there minimum SDK version requirements?

#### Research Sources (Complete BEFORE any coding):
- [ ] **Official Databricks SDK Python documentation** - Primary source
- [ ] **Databricks SQL documentation** - For table properties and clustering
- [ ] **GitHub repository documentation and examples** - Real-world usage patterns
- [ ] **Release notes for recent SDK updates** - Feature availability 
- [ ] **Community examples and Stack Overflow** - Common patterns and limitations

#### Document ALL Findings (Required before Step 2):
```
[Record your complete SDK research findings here - NO CODING until this is filled out]

SDK Research Results:
- Available methods: [List exact method names]
- Relevant properties: [Property names and expected data types]  
- Data structures: [Classes that contain the information]
- Version requirements: [Minimum SDK versions needed]
- Potential limitations: [Any restrictions or known issues found]
- Databricks documentation links: [Save URLs for future reference]

Architecture & Infrastructure Findings:
- Existing infrastructure: [Domain, validators, config files found]
- Related scenarios: [Similar scenarios already implemented]
- Configuration approach: [New config section vs. existing file]
- Validator approach: [Which validator to extend/use]
- Complexity assessment: [Simple property check vs. complex business logic]
- Implementation patterns: [Existing patterns that can be reused]
```

**🎯 SCENARIO COMPLEXITY ASSESSMENT** (helps plan implementation approach):
- [ ] **Simple Property Check** (like cluster_exclusion): Check table.properties for flag value
- [ ] **Business Logic Validation** (like column coverage): Requires calculations and thresholds
- [ ] **Cross-Table Analysis** (like relationship validation): Requires multiple table access
- [ ] **External Dependencies** (like access patterns): Requires additional data sources

#### ✅ **MANDATORY RESEARCH VALIDATION CHECKPOINT** ✅

**🔍 STEP 1A VALIDATION** - Infrastructure & Architecture Discovery Complete:
- [ ] **Existing Infrastructure Check** - Documented what domain infrastructure exists
- [ ] **Related Scenarios** - Identified similar scenarios already implemented  
- [ ] **Configuration Domain** - Determined config approach (new/extend existing)
- [ ] **Validator Class** - Identified which validator to extend/use

**🔍 STEP 1B VALIDATION** - Databricks SDK & API Research Complete:
- [ ] **API Methods** - Documented exact SDK methods/properties available
- [ ] **Data Structures** - Identified relevant classes and data structures
- [ ] **Property Names** - Listed exact property/attribute names to check
- [ ] **Data Types** - Documented return types (string, list, boolean, etc.)
- [ ] **SDK Version Requirements** - Identified minimum versions needed
- [ ] **Research Sources** - Completed all documentation sources research

**📝 DOCUMENTATION VALIDATION**:
- [ ] **All findings documented** - Complete research findings section filled out
- [ ] **Scenario complexity assessed** - Implementation approach identified

- [ ] **Review known constraints**: Check `research/DATABRICKS_ENFORCEMENT_BEHAVIORS.md`

⛔ **DO NOT PROCEED** until ALL boxes above are checked! Incomplete research leads to failed implementations.

### Step 2: Identify the Rule Violation
**Scenario**: [e.g., "Table comments must be at least 10 characters"]
**Rule Violation**: [e.g., "Table with 5-character comment"]

### Step 3: Test Creating the Violation
```sql
-- Example test case for comment length
CREATE TABLE test_catalog.test_schema.feasibility_test (
    id INT COMMENT 'Test column'
) COMMENT 'Short'  -- Only 5 characters
USING DELTA;
```

### Step 4: Test Databricks Enforcement Limits ⚠️ **CRITICAL**

**Before testing rule violations, verify Databricks doesn't enforce limits at creation time**

📚 **REQUIRED READING**: Check [`research/DATABRICKS_ENFORCEMENT_BEHAVIORS.md`](../DATABRICKS_ENFORCEMENT_BEHAVIORS.md) for known enforcement behaviors before testing.

#### Common Enforcement Areas to Test:
- [ ] **Clustering Limits**: Try creating table with >4 clustering columns
- [ ] **Comment Length**: Try extremely long table/column comments (>1000 chars)  
- [ ] **Column Count**: Try tables with excessive columns (>1000)
- [ ] **Data Type Restrictions**: Try unsupported data type combinations
- [ ] **Naming Restrictions**: Try invalid table/column names
- [ ] **Schema Validation**: Try malformed schema definitions

#### Test Pattern:
```sql
-- Example: Test clustering column limits
CREATE TABLE test_limits (
    col1 STRING, col2 STRING, col3 STRING, 
    col4 STRING, col5 STRING  -- 5th column
) 
USING DELTA
CLUSTER BY (col1, col2, col3, col4, col5);  -- 5 clustering columns (over limit)
```

#### Document Enforcement Behavior:
- [ ] **Allowed**: Databricks permits creation, validation scenario is feasible
- [ ] **Blocked**: Databricks rejects at creation time
  - **Error message**: [Record the exact error]
  - **Impact**: Cannot test "exceeds limit" scenarios in integration tests
  - **Solution**: Test limits in unit tests with mock data only

### Step 5: Document Results
- [ ] ✅ **Success**: Databricks allowed the rule violation to be created
- [ ] ❌ **Failure**: Databricks prevented the rule violation
  - **Error message**: [Record the exact error]
  - **Conclusion**: Scenario is not feasible
- [ ] ⚠️ **Partial**: Some violations allowed, others enforced at creation time
  - **Allowed violations**: [List what can be tested in integration]
  - **Blocked violations**: [List what must be unit-tested only]

### 4. Test Edge Cases
- [ ] Minimum boundary: [e.g., 1-character comment]
- [ ] Zero boundary: [e.g., empty comment]
- [ ] Special cases: [e.g., whitespace-only comment]

### 5. Clean Up Test Objects
```sql
-- Always clean up your test objects
DROP TABLE IF EXISTS test_catalog.test_schema.feasibility_test;
```

## Common Scenarios to Test

### Comment Length
```sql
-- Test short comments
CREATE TABLE test (...) COMMENT 'Hi';  -- 2 chars
CREATE TABLE test (...) COMMENT '';    -- empty
CREATE TABLE test (...) COMMENT '   '; -- whitespace only
```

### Placeholder Comments
```sql
-- Test placeholder patterns
CREATE TABLE test (...) COMMENT 'TODO: add comment';
CREATE TABLE test (...) COMMENT 'FIXME';
CREATE TABLE test (...) COMMENT 'TBD - update later';
```

### Column Documentation
```sql
-- Test undocumented columns
CREATE TABLE test (
    documented_col INT COMMENT 'This has documentation',
    undocumented_col STRING  -- No comment
);
```

### Critical Columns
```sql
-- Test critical columns without documentation
CREATE TABLE test (
    user_id INT,           -- Critical ID column, no comment
    email STRING,          -- Critical PII column, no comment
    password_hash STRING   -- Critical security column, no comment
);
```

### Column-Level Validation
```sql
-- Test column documentation
CREATE TABLE test (
    critical_column INT,          -- No comment on critical field
    regular_column STRING COMMENT 'Has comment'
);

-- Verify column access via SDK
-- Check: Can you access col.name, col.comment, col.type_text?
-- Check: Are comments None or empty string when missing?
```

## Decision Tree
#### 🚨 **CRITICAL DECISION GATE** 🚨
```
Can create rule violation in Databricks?
├── YES → Scenario is feasible, proceed with implementation
└── NO → Scenario is not feasible
    ├── Document why (Databricks limitation)
    ├── Consider alternative scenario
    └── Or skip this validation entirely
```

## Template for Documentation

```markdown
## Feasibility Check Results: [Scenario Name]

**Date**: [Date]
**Scenario**: [Description]
**Rule Violation Tested**: [What bad condition you tried to create]

### Test Commands Run:
```sql
[Include actual SQL/commands you tested]
```

### Results:
- [ ] ✅ Feasible: Databricks allows rule violations to exist
- [ ] ❌ Not Feasible: Databricks prevents rule violations

**Details**: [Explain what happened]

**Decision**: [Proceed/Skip/Modify scenario]
```

---

---

## 🔄 **POST-IMPLEMENTATION UPDATES REQUIRED**

**CRITICAL**: If you discover enforcement behaviors during implementation that weren't caught during feasibility testing, you MUST update both this document AND [`research/DATABRICKS_ENFORCEMENT_BEHAVIORS.md`](../DATABRICKS_ENFORCEMENT_BEHAVIORS.md).

### Update Template for Discoveries:
```markdown
## ⚠️ **CRITICAL POST-IMPLEMENTATION DISCOVERY**

### [Brief Description of What Was Discovered]

**DISCOVERED DURING [PHASE]**: [What enforcement/limitation was found]

#### Test Result:
```sql
-- Example of what failed/succeeded unexpectedly
[Include the actual command that revealed the limitation]
```

#### Impact on Testing Strategy:
- ✅ **What still works**: [What can be tested as planned]  
- ❌ **What doesn't work**: [What cannot be tested due to Databricks enforcement]

#### Updated Implementation Approach:
- [How the implementation was modified to work around the limitation]
- [Which test layers can/cannot test certain scenarios]
```

### When to Update:
- [ ] **During Implementation**: Any time Databricks blocks something you expected to work
- [ ] **During Testing**: When integration tests fail due to Databricks enforcement  
- [ ] **During Production**: When real-world behavior differs from expectations

### Purpose:
- **Prevent future teams** from making the same assumptions
- **Document Databricks enforcement behaviors** for reference
- **Guide testing strategy decisions** for similar scenarios

---

**Remember: This check must be done BEFORE any implementation work. It's the foundation that determines if your scenario is even possible to test.**

**AND: Update this document when reality differs from feasibility assumptions.**