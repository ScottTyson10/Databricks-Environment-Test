# Column Coverage Threshold Feasibility Check
**Critical Step: Verify Databricks Allows Rule Violations**

**Scenario**: Column documentation must meet 80% threshold  
**Date**: 2025-08-23
**Status**: ✅ Feasibility Confirmed

## Why This Matters

**If Databricks prevents tables with low column documentation coverage, your validation scenario is impossible to test.**

Example: If you're testing "columns must have 80% documentation" but Databricks won't let you create tables with only 50% coverage, your test scenario is pointless.

## Feasibility Check Process

### 1. Identify the Rule Violation
**Scenario**: Column documentation must meet 80% threshold
**Rule Violation**: Tables with <80% column documentation coverage

### 2. Test Creating the Violation
Successfully created multiple test tables with varying documentation levels to confirm Databricks allows rule violations.

### 3. Document Results
- [x] ✅ **Success**: Databricks allowed tables with low column documentation coverage
- [ ] ❌ **Failure**: Databricks prevented the rule violation

## Feasibility Analysis Results

### ✅ Databricks Constraint Check
**Question**: Can we create tables with varying column documentation levels?
**Answer**: YES - Databricks allows:
- Tables with no column comments (0% documentation)
- Tables with partial column comments (any percentage)
- Tables with all columns commented (100% documentation)
- Edge case: Tables with 0 columns (empty tables)

### ✅ Test Condition Creation
Successfully created test tables with:
- 0% documentation (0 of 4 columns)
- 50% documentation (2 of 4 columns)
- 75% documentation (3 of 4 columns)
- 80% documentation (4 of 5 columns)
- 100% documentation (4 of 4 columns)
- 0 columns (edge case - Databricks allows this!)

### ✅ Edge Case Validation
- **0 columns**: Databricks allows creating tables with no columns
- **1 column**: Trivial case - either 0% or 100%
- **Large column counts**: No technical limitation found
- **Empty/whitespace comments**: Treated as undocumented
- **None comments**: Treated as undocumented

## SDK Research Findings

### Column Access Pattern
```python
table_info = client.tables.get("catalog.schema.table")
if table_info.columns:
    for col in table_info.columns:
        # col.name - column name (str)
        # col.type_text - data type (str)
        # col.comment - documentation (str or None)
```

### Column Comment Characteristics
- **Type**: `str` or `None` (never empty string from SDK)
- **Access**: Direct property access via `col.comment`
- **Validation**: Check for `None` and empty/whitespace strings

### Documentation Percentage Calculation
```python
documented_count = sum(
    1 for col in table.columns 
    if col.comment and col.comment.strip()
)
total_count = len(table.columns) if table.columns else 0
percentage = (documented_count / total_count * 100) if total_count > 0 else 0
```

## Configuration Values to Extract

### Required Configuration
```yaml
column_documentation:
  coverage_threshold: 80  # percentage (configurable)
  treat_whitespace_as_undocumented: true
  include_system_columns: true  # count all columns
```

### Optional Future Configuration
```yaml
column_documentation:
  per_schema_overrides:
    raw_data: 60  # lower threshold for raw data
    curated: 90  # higher threshold for curated data
  critical_columns_must_be_documented: true
```

## Business Logic Decisions

### What Counts as "Documented"?
**Decision**: A column is documented if:
- `comment` is not `None`
- `comment.strip()` is not empty
- Same logic as table comments for consistency

### What Columns Count Toward Percentage?
**Decision**: ALL columns count
- No exclusion of system columns (Databricks doesn't have hidden system columns in user tables)
- All user-defined columns are equal
- Simplest and most predictable approach

### Threshold Failure Handling
**Decision**: Strict threshold
- 79.9% fails an 80% threshold
- No rounding (use exact percentage)
- Clear pass/fail boundary

## Implementation Strategy

### Layer 1 (Unit Tests)
- Test percentage calculations with mock data
- Test edge cases (0 columns, 1 column, many columns)
- Test boundary conditions (79%, 80%, 81%)
- No Databricks dependencies

### Layer 2 (Integration Tests)
- Create real tables with specific documentation percentages
- Test discovery and validation flow
- Verify SDK column access patterns
- Session-scoped fixtures for performance

### Layer 3 (Production Tests)
- BDD step: "at least 80% of columns in each table should have comments"
- Report tables that fail the threshold
- Provide actionable compliance metrics
- Session-scoped discovery for efficiency

## Test Table Specifications

### Integration Test Tables Needed
1. **0% documented** - No columns have comments
2. **50% documented** - Half of columns have comments
3. **79% documented** - Just below threshold
4. **80% documented** - Exactly at threshold
5. **81% documented** - Just above threshold
6. **100% documented** - All columns have comments
7. **0 columns** - Edge case with no columns
8. **1 column documented** - Single column with comment
9. **1 column undocumented** - Single column without comment

## Risks and Mitigations

### Identified Risks
1. **Performance with many columns**: Tables with 100+ columns
   - **Mitigation**: Column access is already loaded, no additional API calls

2. **Mixed documentation quality**: Comments like "column1" or "TODO"
   - **Mitigation**: This scenario focuses on presence, not quality
   - **Future**: Could combine with placeholder detection

3. **Zero column tables**: Division by zero
   - **Mitigation**: Handle explicitly - 0 columns = 100% compliant (vacuous truth)

## Validation Logic Pseudocode

```python
def calculate_column_documentation_percentage(table: TableInfo) -> float:
    """Calculate percentage of columns with documentation."""
    if not table.columns:
        return 100.0  # No columns = vacuously true = 100% compliant
    
    documented = sum(
        1 for col in table.columns 
        if col.get('comment') and str(col['comment']).strip()
    )
    
    return (documented / len(table.columns)) * 100

def meets_column_documentation_threshold(
    table: TableInfo, 
    threshold: float = 80.0
) -> bool:
    """Check if table meets column documentation threshold."""
    return calculate_column_documentation_percentage(table) >= threshold
```

## Next Steps

1. ✅ Feasibility confirmed
2. ✅ SDK research complete
3. ✅ Configuration values identified
4. ⏳ Implement Layer 1 (Unit Tests)
5. ⏳ Implement Layer 2 (Integration Tests)
6. ⏳ Implement Layer 3 (Production Tests)
7. ⏳ Update configuration YAML
8. ⏳ Philosophy check after each layer

## Summary

✅ **READY FOR IMPLEMENTATION** - All research complete, feasibility confirmed, approach validated.