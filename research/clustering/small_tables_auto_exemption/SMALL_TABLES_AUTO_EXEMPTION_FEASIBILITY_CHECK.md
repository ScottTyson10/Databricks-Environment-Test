# Feasibility Check Template
**Critical Step: Verify Databricks Allows Rule Violations**

> **Organization**: Copy this template to `research/[feature_area]/[scenario_name]/[SCENARIO_NAME]_FEASIBILITY_CHECK.md` to keep the main directory clean. Any feasibility test scripts should also be stored in the same research directory.

## Why This Matters

**If Databricks prevents the "bad" condition from existing, your validation scenario is impossible to test.**

Example: If you're testing "comments must be 10+ characters" but Databricks won't let you create tables with short comments, your test scenario is pointless.

## Feasibility Check Process

### Step 1: Online Documentation Research ⭐ **MANDATORY FIRST STEP**

**🚫 NO CODE UNTIL RESEARCH IS COMPLETE**: You MUST complete all online research before writing any test code or SQL commands.

**CRITICAL**: Research the Databricks SDK online documentation BEFORE any hands-on testing.

#### Questions to Research:
- [ ] **API Methods**: What SDK methods/properties are available for this scenario?
- [ ] **Data Structures**: What classes (TableInfo, etc.) contain relevant information?
- [ ] **Property Names**: What are the exact property/attribute names to check?
- [ ] **Data Types**: What data types are returned (string, list, boolean, etc.)?
- [ ] **SDK Version Requirements**: Are there minimum SDK version requirements?

#### 🔍 **NEW: Architecture & Infrastructure Research**
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

#### Research Sources (Complete BEFORE any coding):
- [ ] **Official Databricks SDK Python documentation** - Primary source
- [ ] **Databricks SQL documentation** - For table properties and clustering
- [ ] **GitHub repository documentation and examples** - Real-world usage patterns
- [ ] **Release notes for recent SDK updates** - Feature availability 
- [ ] **Community examples and Stack Overflow** - Common patterns and limitations

#### Document ALL Findings (Required before Step 2):
```
SDK Research Results:
- Available methods: 
  * w.statement_execution.execute_statement() - Execute SQL commands
  * DESCRIBE DETAIL <table> - SQL command to get table metadata
- Relevant properties: 
  * sizeInBytes (int) - Table size in bytes from DESCRIBE DETAIL
  * clusteringColumns (array) - Clustering columns from DESCRIBE DETAIL
- Data structures: 
  * TableInfo - Does NOT contain size information
  * StatementResponse - Result from SQL execution
- Version requirements: 
  * Databricks SDK 0.18.0+ for Statement Execution API
  * databricks-sql-connector for SQL operations
- Potential limitations: 
  * sizeInBytes is compressed size, may underreport by ~67%
  * Requires warehouse connection for SQL execution
  * Performance impact when checking many tables
- Databricks documentation links:
  * https://docs.databricks.com/en/delta/table-details.html
  * https://databricks-sdk-py.readthedocs.io/en/latest/workspace/sql/statement_execution.html

Architecture & Infrastructure Findings:
- Existing infrastructure: 
  * Clustering domain fully established
  * tests/validators/clustering.py - ClusteringValidator class
  * tests/config/clustering_config.yaml - Configuration
- Related scenarios: 
  * Manual cluster_exclusion already implemented
  * has_cluster_exclusion() method exists
  * is_exempt_from_clustering_requirements() ready to extend
- Configuration approach: 
  * Reuse existing clustering_config.yaml
  * size_threshold_bytes: 1073741824 (1GB) already configured
  * exempt_small_tables: true flag already present
- Validator approach: 
  * Extend existing ClusteringValidator
  * Add get_table_size() method using SQL
  * Update exemption logic to include size check
- Complexity assessment: 
  * Medium complexity - requires SQL execution
  * Not a simple property check like manual exclusion
- Implementation patterns: 
  * Follow existing cluster_exclusion pattern
  * Reuse configuration loading pattern
```

**🎯 SCENARIO COMPLEXITY ASSESSMENT** (helps plan implementation approach):
- [ ] **Simple Property Check** (like cluster_exclusion): Check table.properties for flag value
- [x] **Business Logic Validation** (like column coverage): Requires calculations and thresholds
  - Need to execute SQL to get table size
  - Compare size against 1GB threshold
  - Combine with existing exclusion logic
- [ ] **Cross-Table Analysis** (like relationship validation): Requires multiple table access
- [ ] **External Dependencies** (like access patterns): Requires additional data sources

**✅ RESEARCH COMPLETE CHECKPOINT**: Only proceed to Step 2 after completing all online research above.

### Step 2: Identify the Rule Violation
**Scenario**: "Small tables under 1GB can be exempted from clustering"
**Rule Violation**: "Large table (>1GB) without clustering that should NOT be exempt"

### Step 3: Test Creating the Violation
```sql
-- Test case 1: Small table without clustering (should be exempt)
CREATE TABLE test_catalog.test_schema.small_table_no_clustering (
    id INT,
    data STRING
) USING DELTA;
-- Insert minimal data to keep table under 1GB

-- Test case 2: Large table without clustering (should NOT be exempt)
CREATE TABLE test_catalog.test_schema.large_table_no_clustering (
    id INT,
    data STRING
) USING DELTA;
-- Would need to insert >1GB of data to test

-- Test case 3: Small table with clustering (clustering takes precedence)
CREATE TABLE test_catalog.test_schema.small_table_with_clustering (
    id INT,
    data STRING
) USING DELTA
CLUSTER BY (id);
```

### Step 4: Test Databricks Enforcement Limits ⚠️ **CRITICAL**

**Before testing rule violations, verify Databricks doesn't enforce limits at creation time**

📚 **REQUIRED READING**: Check [`research/DATABRICKS_ENFORCEMENT_BEHAVIORS.md`](../DATABRICKS_ENFORCEMENT_BEHAVIORS.md) for known enforcement behaviors before testing.

#### Common Enforcement Areas to Test:
- [x] **Table Size Limits**: No enforcement - tables can be any size
  - Databricks allows creating tables of any size
  - Tables can exist without clustering regardless of size
  - Size is a runtime property, not a creation-time constraint
- [x] **Clustering Requirements**: No mandatory clustering enforcement
  - Tables can be created without any clustering
  - Clustering is optional, not required by Databricks
- [x] **Size Detection**: DESCRIBE DETAIL provides sizeInBytes
  - Available for all Delta tables
  - Returns actual table size in bytes

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
- [x] ✅ **Success**: Databricks allowed the rule violation to be created
  - Tables of any size can be created without clustering
  - DESCRIBE DETAIL successfully returns sizeInBytes
  - Size-based exemption logic is fully testable
- [ ] ❌ **Failure**: Databricks prevented the rule violation
- [ ] ⚠️ **Partial**: Some violations allowed, others enforced at creation time

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

```
Can create rule violation in Databricks?
├── YES → Scenario is feasible, proceed with implementation
└── NO → Scenario is not feasible
    ├── Document why (Databricks limitation)
    ├── Consider alternative scenario
    └── Or skip this validation entirely
```

## Feasibility Check Results: Small Tables Auto Exemption

**Date**: 2025-01-31
**Scenario**: Tables under 1GB are automatically exempted from clustering requirements
**Rule Violation Tested**: Large tables without clustering that should NOT be exempt

### Test Commands Run:
```sql
-- Create tables of different sizes without clustering
CREATE TABLE small_table_no_clustering (id INT, data STRING) USING DELTA;
CREATE TABLE large_table_no_clustering (id INT, data STRING) USING DELTA;
-- Insert data to create size differences

-- Check table sizes
DESCRIBE DETAIL small_table_no_clustering;
DESCRIBE DETAIL large_table_no_clustering;
```

### Results:
- [x] ✅ Feasible: Databricks allows rule violations to exist
- [ ] ❌ Not Feasible: Databricks prevents rule violations

**Details**: 
- Databricks allows tables of any size to exist without clustering
- DESCRIBE DETAIL successfully provides sizeInBytes for all Delta tables
- Can programmatically detect table size and apply exemption logic
- No Databricks enforcement prevents the scenario

**Decision**: PROCEED with full three-layer implementation

### Implementation Plan:
1. **Layer 1 (Unit)**: Mock TableInfo with size data, test exemption logic
2. **Layer 2 (Integration)**: Create real tables of different sizes, validate detection
3. **Layer 3 (Production)**: BDD tests against real workspace tables

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