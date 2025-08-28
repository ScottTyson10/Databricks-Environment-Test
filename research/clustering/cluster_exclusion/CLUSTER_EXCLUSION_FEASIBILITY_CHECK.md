# Feasibility Check Template
**Critical Step: Verify Databricks Allows Rule Violations**

> **Organization**: Copy this template to `research/[feature_area]/[scenario_name]/[SCENARIO_NAME]_FEASIBILITY_CHECK.md` to keep the main directory clean. Any feasibility test scripts should also be stored in the same research directory.

## Why This Matters

**If Databricks prevents the "bad" condition from existing, your validation scenario is impossible to test.**

Example: If you're testing "comments must be 10+ characters" but Databricks won't let you create tables with short comments, your test scenario is pointless.

## Feasibility Check Process

### Step 1: SDK Documentation Research ⭐ START HERE

**CRITICAL**: Research the Databricks SDK online documentation BEFORE any hands-on testing.

#### Questions to Research:
- [ ] **API Methods**: What SDK methods/properties are available for this scenario?
- [ ] **Data Structures**: What classes (TableInfo, etc.) contain relevant information?
- [ ] **Property Names**: What are the exact property/attribute names to check?
- [ ] **Data Types**: What data types are returned (string, list, boolean, etc.)?
- [ ] **SDK Version Requirements**: Are there minimum SDK version requirements?

#### Research Sources:
- [ ] Official Databricks SDK Python documentation
- [ ] GitHub repository documentation and examples  
- [ ] Release notes for recent SDK updates
- [ ] Community examples and best practices

#### Document Findings:
```
SDK Research Results:
- Available methods: client.tables.get(full_name), client.tables.list(catalog, schema)
- Relevant properties: sdk_table.properties (dict[str, Any]), properties accessible via TableInfo.properties
- Data structures: databricks.sdk.service.catalog.TableInfo (SDK), tests.utils.discovery.TableInfo (our wrapper)
- Version requirements: Databricks SDK for Python (current version in use)
- Potential limitations: cluster_exclusion property not found in official documentation
- Databricks documentation links: 
  - https://databricks-sdk-py.readthedocs.io/en/latest/workspace/catalog/tables.html
  - https://databricks-sdk-py.readthedocs.io/en/latest/dbdataclasses/catalog.html
  
Research Findings:
- CRITICAL: No documentation found for 'cluster_exclusion' property in official Databricks docs
- Table properties are accessible via sdk_table.properties and get passed through our discovery engine
- Current codebase already handles table properties in discovery_engine.py line 175-179
- Existing TableInfo class includes properties field (dict[str, Any] | None)
- Properties are extracted and passed to our TableInfo wrapper correctly
```

**⚠️ CRITICAL FINDING**: The 'cluster_exclusion' property is not documented in official Databricks documentation. This may be:
1. A custom/organizational property
2. A feature in development  
3. A property that doesn't exist in current Databricks offerings

**✅ RESEARCH COMPLETE CHECKPOINT**: Research complete - proceeding to feasibility testing to determine if cluster_exclusion can be set as a table property.

### Step 2: Identify the Rule Violation
**Scenario**: "Tables can be exempted from clustering with cluster_exclusion flag"
**Rule Violation**: "Table without cluster_exclusion=true should be subject to clustering requirements"
**Exemption Test**: "Table with cluster_exclusion=true should be exempt from clustering requirements"

### Step 3: Test Creating the Cluster Exclusion Property
```sql
-- Test if cluster_exclusion property can be set
CREATE TABLE workspace.pytest_test_data.cluster_exclusion_feasibility_test (
    id INT COMMENT 'Test column for cluster exclusion feasibility',
    name STRING COMMENT 'Test name column'
) 
USING DELTA
TBLPROPERTIES (
    'cluster_exclusion' = 'true'
);
```

**Expected Test Outcomes:**
1. **✅ Success**: Table created with cluster_exclusion=true property → Scenario is feasible
2. **❌ Failure**: Databricks rejects the property → Scenario is not feasible as written
3. **⚠️ Partial**: Table created but property ignored → Need further investigation

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
- [x] ✅ **Success**: Databricks allowed the cluster_exclusion property to be created
  - **Test Result**: Table created successfully with cluster_exclusion='true'
  - **Property Verification**: cluster_exclusion property is accessible via table properties
  - **Value Type**: String ('true')
  - **Conclusion**: Scenario is feasible - cluster_exclusion can be set and retrieved
- [ ] ❌ **Failure**: Databricks prevented the rule violation
- [ ] ⚠️ **Partial**: Some violations allowed, others enforced at creation time

**FEASIBILITY DECISION**: ✅ **PROCEED WITH IMPLEMENTATION**
- Databricks allows setting arbitrary table properties including cluster_exclusion
- The property is preserved and accessible via SDK table properties
- Our existing discovery engine already handles table properties correctly
- No Databricks enforcement prevents testing this scenario

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

## Template for Documentation

```markdown
## Feasibility Check Results: Cluster Exclusion Scenario

**Date**: 2025-08-28
**Scenario**: "Tables can be exempted from clustering with cluster_exclusion flag"
**Rule Violation Tested**: Tables with cluster_exclusion='true' should be exempt from clustering requirements

### Test Commands Run:
```sql
-- Test table creation with cluster_exclusion property
CREATE TABLE workspace.pytest_test_data.cluster_exclusion_feasibility_test (
    id INT COMMENT 'Test column for cluster exclusion feasibility',
    name STRING COMMENT 'Test name column'
) 
USING DELTA
TBLPROPERTIES (
    'cluster_exclusion' = 'true'
);

-- Verification via SDK
client.tables.get(table_name).properties
discovery_engine.discover_tables()  # Find table and check properties
```

### Results:
- [x] ✅ Feasible: Databricks allows cluster_exclusion property to be set and retrieved
- [ ] ❌ Not Feasible: Databricks prevents rule violations

**Details**: 
- ✅ Table created successfully with cluster_exclusion='true'
- ✅ Property is accessible via SDK table.properties['cluster_exclusion'] = 'true'
- ✅ Discovery engine correctly extracts the property
- ✅ Configuration already exists in clustering_config.yaml (exemptions section)
- ✅ ClusteringValidator infrastructure already exists

**Decision**: ✅ **PROCEED WITH IMPLEMENTATION**

**Architecture Notes**:
- ClusteringValidator class already exists with comprehensive clustering detection
- Configuration system ready in clustering_config.yaml
- Discovery engine handles properties correctly  
- Need to add exemption methods to ClusteringValidator
- Need to add config loader methods for exemption settings
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