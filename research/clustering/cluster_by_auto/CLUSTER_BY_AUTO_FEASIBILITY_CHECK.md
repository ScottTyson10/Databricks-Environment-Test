# Feasibility Check: ClusterByAuto Scenario
**Critical Step: Verify Databricks Allows Rule Violations**

**Scenario**: "Tables can use clusterByAuto flag for automatic clustering"
**Feature File**: tests/features/databricks__clustering__compliance.feature

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
✅ SDK Research for clusterByAuto/Automatic Liquid Clustering COMPLETE:

- Available methods: client.tables.get(full_name) → TableInfo with properties
- Relevant properties: 
  * "delta.clusterBy.auto" property (confirmed from community discussions)
  * Properties stored in table.properties dictionary (same pattern as clusteringColumns)
  * Can also check via clusteringColumns field for system-selected columns
- Data structures: TableInfo.properties (dict[str, Any]) - same as explicit clustering
- Version requirements: Databricks Runtime 15.4 LTS+ for automatic clustering
- SQL syntax: CLUSTER BY AUTO clause confirmed
- PySpark API: .option("clusterBy.auto", "true") available
- Detection approach: Check table.properties for clustering configuration flags
- Potential limitations:
  * Unity Catalog managed tables only
  * Requires predictive optimization enabled
  * System automatically selects clustering columns (not manual)
```

### Step 2: Identify the Rule Violation
**Scenario**: "Tables can use clusterByAuto flag for automatic clustering"
**Rule Violation**: NOT APPLICABLE - This is a positive detection scenario

**Note**: This scenario validates DETECTION of automatic clustering, not rule violations.
We need to test:
1. Can create table with CLUSTER BY AUTO enabled
2. Can create table WITHOUT automatic clustering  
3. Can detect the difference via SDK properties

### Step 3: Test Creating the Detection Scenarios
```sql
-- Test case 1: Table WITH automatic clustering
CREATE TABLE test_catalog.test_schema.feasibility_auto_cluster (
    id INT COMMENT 'Test column',
    category STRING COMMENT 'Category column'
) 
USING DELTA
CLUSTER BY AUTO;  -- Enable automatic clustering

-- Test case 2: Table WITHOUT automatic clustering (baseline)
CREATE TABLE test_catalog.test_schema.feasibility_no_auto_cluster (
    id INT COMMENT 'Test column',
    category STRING COMMENT 'Category column'
) 
USING DELTA;  -- No clustering specified
```

### Step 4: Test Results ✅ COMPLETE

**✅ FEASIBILITY TEST SUCCESSFUL**

**Test Execution Date**: 2025-01-26
**Test Script**: `feasibility_test_cluster_by_auto.py`

#### Key Findings:
- ✅ **Table creation successful**: Both `CLUSTER BY AUTO` and baseline tables created without issues
- ✅ **Property detection confirmed**: `clusterByAuto: 'true'` property found in automatic clustering tables
- ✅ **Clear differentiation**: Auto clustering tables have 20 properties vs 10 in baseline tables
- ✅ **No enforcement blocks**: Databricks allows both scenarios to be created

#### Specific Properties Detected:
```
Automatic clustering table properties:
- 'clusterByAuto': 'true'  ← PRIMARY DETECTION KEY
- 'clusteringColumns': '[]'  ← Empty initially (system will populate)
- 'delta.feature.clustering': 'supported'
- Plus standard Delta properties...

Baseline table properties:
- No clusterByAuto property
- No clustering-related properties
- Standard Delta properties only
```

### Step 5: Final Assessment ✅ COMPLETE

- [x] ✅ **Success**: Scenario is fully feasible and implementable
  - **Detection method**: `table.properties['clusterByAuto'] == 'true'`
  - **Property availability**: Confirmed via SDK TableInfo.properties
  - **Cost impact**: Minimal (empty tables sufficient for testing)

#### Implementation Approach Confirmed:
1. **Unit Tests**: Mock TableInfo with `clusterByAuto` property
2. **Integration Tests**: Create actual tables with `CLUSTER BY AUTO` clause
3. **Production Tests**: Analyze real data for automatic clustering adoption

#### Configuration Values Identified:
```yaml
# Proposed config additions
auto_clustering_detection:
  cluster_by_auto_property: "clusterByAuto"
  cluster_by_auto_value: "true"
  require_cluster_by_auto: false
```

#### Enforcement Testing Notes:
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

---

## 🎯 FEASIBILITY CONCLUSION: CLUSTER BY AUTO SCENARIO

### ✅ SCENARIO IS FULLY FEASIBLE AND READY FOR IMPLEMENTATION

**Decision**: **PROCEED** with Layer 1 (Unit Tests) implementation

**Confidence Level**: **HIGH** - Clear detection method confirmed

**Key Success Factors**:
- ✅ Reliable property detection via `clusterByAuto: 'true'`
- ✅ No Databricks enforcement blocking test scenarios  
- ✅ Cost-effective testing approach (empty tables work perfectly)
- ✅ Clear differentiation from non-automatic clustering tables
- ✅ Established configuration approach ready for implementation

**Next Steps**: 
1. Begin Layer 1: Unit Tests implementation
2. Create clustering validator method for automatic clustering detection
3. Extend clustering configuration with clusterByAuto settings

---

**Remember: This check must be done BEFORE any implementation work. It's the foundation that determines if your scenario is even possible to test.**

**✅ FEASIBILITY CHECK COMPLETE - READY FOR IMPLEMENTATION**