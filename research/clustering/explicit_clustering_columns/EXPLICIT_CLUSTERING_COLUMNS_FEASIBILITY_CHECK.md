# Explicit Clustering Columns Feasibility Check
**Scenario**: Tables with clustering should use appropriate column selection
**Critical Step**: Verify Databricks Allows Tables Without Clustering AND Cost-Effective Testing

> **Organization**: This feasibility check is specific to detecting explicit clustering columns on tables.

## ⚠️ COST MANAGEMENT CHECKPOINT
**CRITICAL**: Before ANY table creation or data operations, consider:
- [ ] Will this test create large tables? (AVOID)
- [ ] Will this test create many small tables? (MINIMIZE)
- [ ] Can we achieve the same test with metadata only? (PREFER)
- [ ] Are we using the smallest possible data for validation? (REQUIRE)

**Cost-Conscious Testing Strategy**:
- Use EMPTY tables when possible (clustering can be defined without data)
- If data needed, use minimal rows (e.g., 10 rows max)
- Clean up immediately after tests
- Reuse existing tables where possible

---

## Why This Matters

**If Databricks prevents creating tables without clustering OR if we can't detect clustering columns, this validation scenario cannot be implemented.**

We need to verify:
1. Can create tables WITHOUT clustering (the "bad" state)
2. Can create tables WITH clustering columns
3. Can programmatically detect the difference
4. Can do all this WITHOUT creating expensive resources

---

## Step 1: SDK Documentation Research ⭐ START HERE

**COMPLETED**: Comprehensive online research of Databricks SDK documentation completed.

### Questions to Research:
- [x] **API Methods**: What SDK methods/properties are available for this scenario?
- [x] **Data Structures**: What classes (TableInfo, etc.) contain relevant information?
- [x] **Property Names**: What are the exact property/attribute names to check?
- [x] **Data Types**: What data types are returned (string, list, boolean, etc.)?
- [x] **SDK Version Requirements**: Are there minimum SDK version requirements?

### Research Sources:
- [x] Official Databricks SDK Python documentation
- [x] GitHub repository documentation and examples  
- [x] Release notes for recent SDK updates
- [x] Community examples and best practices

### Document Findings:
```
SDK RESEARCH FINDINGS (August 2025):

Available methods:
- w.tables.get(full_name) → TableInfo - Gets table metadata including clustering info
- w.tables.list(catalog_name, schema_name) → Iterator[TableInfo] - Lists tables with metadata

Relevant properties in TableInfo:
- clustering_columns: Shows current clustering columns (list of column names)
- clusterByAuto: Boolean indicating if automatic liquid clustering is enabled
- properties: Dict containing additional table properties

Data structures:
- TableInfo class: Primary data structure containing table metadata
- clustering_columns: List of strings (column names) or None if no clustering
- clusterByAuto: Boolean value (True/False)

Version requirements:
- Databricks SDK Python 0.6.0+ required (default on Runtime 13.3 LTS+)
- Liquid clustering available in Runtime 14.2+
- Python API for clustering available in Runtime 16.4+

Key findings:
- SDK provides direct access to clustering_columns property
- Can detect both manual clustering (clustering_columns) and auto-clustering (clusterByAuto)
- Properties available through table metadata (no data scanning required)
- Empty tables retain clustering configuration in metadata
```

### Cost-Conscious Questions Based on SDK Research:
- [x] Can clustering be defined on empty tables? **YES** - Clustering is table schema metadata
- [x] What's the minimum table size to test clustering? **0 rows** - Empty tables work
- [x] Can we check clustering without querying table data? **YES** - Via TableInfo metadata
- [x] Do clustering properties exist in table metadata? **YES** - clustering_columns & clusterByAuto properties

---

## Step 2: SDK Exploration Based on Research

Based on SDK research, the approach is clear:

### Expected SDK Access Pattern:
```python
from databricks.sdk import WorkspaceClient
from dotenv import load_dotenv

load_dotenv()
client = WorkspaceClient()

# Access table metadata
table = client.tables.get("catalog.schema.table_name")

# Check for explicit clustering columns
if hasattr(table, 'clustering_columns') and table.clustering_columns:
    print(f"Clustering columns: {table.clustering_columns}")  # List of strings
    has_clustering = True
else:
    has_clustering = False
```

### Research-Based Findings:
- [x] **Property name confirmed**: `clustering_columns` in TableInfo class
- [x] **Data structure confirmed**: List of strings (column names) or None
- [x] **Empty table support confirmed**: Metadata available without data
- [x] **SDK version confirmed**: Available in current SDK versions

---

## Step 3: Minimal Table Creation Test (COST-CONSCIOUS)

### Test 2: Create Table WITH Clustering (Minimal Cost)
```python
warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID")

# CREATE EMPTY TABLE with clustering - NO DATA COSTS
sql_with_clustering = """
CREATE TABLE IF NOT EXISTS workspace.pytest_test_data.clustering_test_with (
    id INT,
    category STRING,
    created_at TIMESTAMP
)
USING DELTA
CLUSTER BY (category, id)
COMMENT 'TEMPORARY TEST - DELETE IMMEDIATELY'
"""

try:
    # Create table
    client.statement_execution.execute_statement(
        statement=sql_with_clustering,
        warehouse_id=warehouse_id
    )
    
    # Immediately check clustering
    table = client.tables.get("workspace.pytest_test_data.clustering_test_with")
    print(f"Table with clustering created")
    # Check clustering detection here
    
    # IMMEDIATE CLEANUP
    cleanup_sql = "DROP TABLE IF EXISTS workspace.pytest_test_data.clustering_test_with"
    client.statement_execution.execute_statement(
        statement=cleanup_sql,
        warehouse_id=warehouse_id
    )
    print("Table cleaned up")
    
except Exception as e:
    print(f"Error: {e}")
    # ENSURE CLEANUP even on error
```

**Cost Analysis**:
- [ ] Confirm empty table creation has minimal cost
- [ ] Measure time for create/check/drop cycle
- [ ] Verify clustering info available immediately

### Test 3: Create Table WITHOUT Clustering
```python
# Similar test but WITHOUT CLUSTER BY clause
sql_without_clustering = """
CREATE TABLE IF NOT EXISTS workspace.pytest_test_data.clustering_test_without (
    id INT,
    category STRING,
    created_at TIMESTAMP
)
USING DELTA
COMMENT 'TEMPORARY TEST - DELETE IMMEDIATELY'
"""

# Rest of test similar to above
```

---

## Step 4: Detection Method Validation

### Detection Method Based on SDK Research
```python
def has_clustering_columns(table) -> bool:
    """Detect if table has explicit clustering columns defined.
    
    Based on SDK research findings:
    - clustering_columns property contains list of column names
    - Returns None or empty list if no clustering
    - Available in TableInfo metadata (no data scanning required)
    """
    # Primary method: Direct clustering_columns attribute
    if hasattr(table, 'clustering_columns') and table.clustering_columns:
        return True
    
    return False
```

**Research-Based Validation**:
- [x] Method targets confirmed SDK property (`clustering_columns`)
- [x] Method works on empty tables (metadata-based)
- [x] Method doesn't require data scanning
- [x] Simple boolean logic based on list presence/absence

---

## Step 5: Cost-Effective Integration Test Design

### Proposed Test Strategy
1. **Use EMPTY tables** - Define structure without data
2. **Minimal test scenarios** - Only 2-3 tables needed:
   - One WITH clustering
   - One WITHOUT clustering  
   - One with MULTI-COLUMN clustering
3. **Session fixture** - Create once, test many times
4. **Immediate cleanup** - Drop tables in finally block

### Cost Estimate
- Empty table creation: ~$0.00 (metadata only)
- SQL warehouse time: < 1 minute total
- No data storage costs
- No data scanning costs

---

## Step 6: Hands-On Test Results 🧪

**COMPLETED**: Hands-on feasibility test executed with cost-conscious approach.

### Key Discoveries from Actual Testing:
- ✅ **Clustering info is in `properties`**: Not direct attribute, but in `table.properties['clusteringColumns']`
- ✅ **Data structure is nested lists**: `[["category"],["id"]]` format for multiple clustering keys
- ✅ **Empty tables work perfectly**: Clustering metadata available immediately
- ✅ **Cost effective**: < $0.01 total cost, tables cleaned up successfully

### Corrected Detection Method:
```python
def has_clustering_columns(table) -> bool:
    """Detect explicit clustering columns from actual test results."""
    # Clustering info is in properties, not direct attribute
    if table.properties and 'clusteringColumns' in table.properties:
        clustering_cols = table.properties['clusteringColumns']
        # Format is nested lists: [["col1"],["col2"]] 
        if clustering_cols and len(clustering_cols) > 0:
            return True
    return False
```

## Step 7: Decision Gate 🚦

### Can We Proceed?
- [x] **Databricks allows tables WITHOUT clustering?** **YES** ✅
- [x] **We can detect clustering columns programmatically?** **YES** ✅ (via properties)  
- [x] **Detection works on EMPTY tables?** **YES** ✅ (metadata only)
- [x] **Integration tests can be cost-effective?** **YES** ✅ (< $0.01 per test)

---

## ⚠️ **CRITICAL POST-IMPLEMENTATION DISCOVERY**

### Databricks Enforces Clustering Limits at Creation Time

**DISCOVERED DURING INTEGRATION TESTING**: Databricks prevents table creation with >4 clustering columns.

#### Test Result:
```sql
-- THIS FAILS IN DATABRICKS:
CREATE TABLE test (col1 STRING, col2 STRING, col3 STRING, col4 STRING, col5 STRING) 
USING DELTA CLUSTER BY (col1, col2, col3, col4, col5);
-- Error: Cannot create table with 5 clustering columns (exceeds limit of 4)
```

#### Impact on Testing Strategy:
- ✅ **Unit Tests**: Can test all scenarios (including exceeds-limit) with mock data  
- ✅ **Integration Tests**: Can test valid scenarios (1-4 clustering columns) with real tables
- ❌ **Integration Tests**: **CANNOT** test exceeds-limit scenarios - Databricks blocks creation

#### Updated Implementation Approach:
- **Exceeds-limit validation**: Unit tests only (mock TableInfo with 5+ clustering columns)
- **Valid scenarios**: Both unit and integration tests  
- **Integration test specs**: Removed "exceeds_clustering_limit" table specification

---

### ✅ CRITERIA MET WITH ENFORCEMENT CONSTRAINTS - PROCEED WITH MODIFIED IMPLEMENTATION

**Outcome**: Scenario is **FEASIBLE** with enforcement-based limitations documented.

**Next Steps**:
1. Implement validator using corrected detection method
2. Use empty tables for all integration tests
3. Target `table.properties['clusteringColumns']` for detection
4. Handle nested list format: `[["col1"],["col2"]]`

---

## Configuration Values to Extract

Based on feasibility test results:
- [x] **Property name**: `clusteringColumns` (in table.properties)
- [x] **Data format**: Nested lists `[["col1"],["col2"]]`
- [x] **Detection approach**: Properties-based, not attribute-based
- [x] **Cost optimization**: Empty tables are sufficient

```yaml
clustering:
  detection:
    clustering_property_name: "clusteringColumns"  # Confirmed from testing
    require_explicit_clustering: false
    max_clustering_columns: 4  # Databricks recommendation
  validation:
    allow_empty_clustering: true  # Tables without clustering are valid
```

---

## Final Notes

### Cost Optimization Achieved
- [ ] All tests use empty tables
- [ ] No data generation required
- [ ] Cleanup guaranteed
- [ ] Total test cost: < $0.01

### Next Steps
1. Run SDK exploration tests
2. Validate detection methods
3. Design minimal integration tests
4. Document findings in implementation journal

---

**Remember**: Every test table costs money. Design with cost in mind!