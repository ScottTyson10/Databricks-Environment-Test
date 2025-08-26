# Databricks Enforcement Behaviors

**Purpose**: Document known Databricks enforcement behaviors that prevent certain table configurations from being created, affecting integration test strategies.

---

## 📋 **Known Enforcement Behaviors**

### 🔗 **Clustering Constraints**

#### Clustering Column Limits
- **Enforcement**: Databricks **prevents** table creation with >4 clustering columns
- **Discovered**: During explicit clustering columns integration testing (2025-08-26)
- **Failed Command**:
```sql
CREATE TABLE test (
    col1 STRING, col2 STRING, col3 STRING, col4 STRING, col5 STRING
) 
USING DELTA 
CLUSTER BY (col1, col2, col3, col4, col5);  -- FAILS: 5 columns exceeds limit
```
- **Error**: Table creation fails when clustering columns exceed 4-column limit
- **Testing Impact**: 
  - ✅ **Unit Tests**: Can test exceeds-limit scenarios with mock data
  - ❌ **Integration Tests**: Cannot create tables that exceed clustering limits
- **Workaround**: Test limits validation in unit tests only

---

## 💬 **Comment Constraints** 
*(To be documented as discovered)*

### Comment Length Limits
- **Status**: Not yet tested
- **Expected**: May have maximum comment length limits
- **Test Needed**: Try creating tables with extremely long comments (>1000 chars)

---

## 📊 **Column Constraints**
*(To be documented as discovered)*  

### Column Count Limits
- **Status**: Not yet tested  
- **Expected**: May have maximum column count limits
- **Test Needed**: Try creating tables with excessive columns (>1000)

---

## 🏷️ **Naming Constraints**
*(To be documented as discovered)*

### Table/Column Name Restrictions
- **Status**: Not yet tested
- **Expected**: May enforce naming conventions/restrictions
- **Test Needed**: Try invalid characters, reserved words, length limits

---

## 📝 **Template for New Discoveries**

When you discover a new enforcement behavior, add it using this template:

```markdown
### [Constraint Name]
- **Enforcement**: Databricks **prevents/allows** [behavior]
- **Discovered**: During [scenario] testing ([date])
- **Failed Command**:
```sql
[Include the actual SQL that failed]
```
- **Error**: [Record the exact error message]
- **Testing Impact**: 
  - ✅ **What can still be tested**: [List scenarios that work]
  - ❌ **What cannot be tested**: [List blocked scenarios]
- **Workaround**: [How to test the validation logic despite the constraint]
```

---

## 🎯 **Integration Testing Strategy Implications**

### General Principles:
1. **Databricks Enforced = Unit Test Only**: If Databricks prevents creation, test validation logic in unit tests with mock data
2. **Databricks Allows = Full Testing**: If Databricks allows creation, test in both unit and integration layers  
3. **Document Everything**: Always update this file when discovering new enforcement behaviors

### Testing Layer Decision Tree:
```
Does Databricks allow creating the "bad" condition?
├── YES → Test in both Unit and Integration layers
└── NO → Test validation logic in Unit tests only
    ├── Use mock TableInfo with "bad" condition
    └── Integration tests focus on valid scenarios only
```

---

## 🔄 **Maintenance**

**Update Frequency**: Immediately upon discovering new enforcement behaviors
**Review Schedule**: Before implementing each new validation scenario  
**Purpose**: Prevent wasted implementation effort and guide testing strategies

**Last Updated**: 2025-08-26 (Added clustering column limits)