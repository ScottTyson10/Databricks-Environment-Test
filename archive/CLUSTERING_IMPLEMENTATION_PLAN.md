# Clustering Compliance Implementation Plan

## Overview
Implementation plan for `tests/features/databricks__clustering__compliance.feature` following a granular, bottom-up approach where individual scenarios are completed before comprehensive validation.

## Implementation Order (Granular → Comprehensive)

### Phase 1: Basic Clustering Detection
**Goal**: Establish foundation for detecting different clustering approaches

#### Scenario 1.1: Explicit Clustering Columns Detection
**Scenario**: "Tables with clustering should use appropriate column selection"
**Priority**: HIGH - Foundation for all other scenarios
**Research Focus**:
- How to access clustering columns via SDK (`table.clustering_columns`?)
- Data structure returned (list, string, property?)
- Handling tables without clustering

**Implementation**:
1. Research: Can we detect explicit clustering columns?
2. Layer 1: Unit test for `has_clustering_columns()` method
3. Layer 2: Integration test with tables with/without clustering
4. Layer 3: Production validation of real tables

**Config Values**:
```yaml
clustering:
  validation:
    require_clustering_columns: true
```

---

### Phase 2: Auto-Clustering Detection
**Goal**: Detect modern auto-clustering approaches

#### Scenario 2.1: ClusterByAuto Flag Detection
**Scenario**: "Tables can use clusterByAuto flag for automatic clustering"
**Priority**: HIGH - Common in newer Databricks versions
**Research Focus**:
- Access `clusterByAuto` property via SDK
- Property location (table properties? tags?)
- Boolean vs string value handling

**Implementation**:
1. Research: How to check clusterByAuto flag
2. Layer 1: Unit test for `has_auto_clustering()` method
3. Layer 2: Integration test with auto-clustered tables
4. Layer 3: Production validation

**Config Values**:
```yaml
clustering:
  auto_clustering:
    accept_cluster_by_auto: true
```

#### Scenario 2.2: Delta Auto-Optimization Detection
**Scenario**: "Tables can use delta auto-optimization for clustering"
**Priority**: MEDIUM - Alternative clustering approach
**Research Focus**:
- Access Delta table properties
- Check both `optimizeWrite` and `autoCompact`
- Handling non-Delta tables

**Implementation**:
1. Research: Access delta.autoOptimize.* properties
2. Layer 1: Unit test for `has_delta_auto_optimization()` method
3. Layer 2: Integration test with Delta optimized tables
4. Layer 3: Production validation

**Config Values**:
```yaml
clustering:
  auto_clustering:
    accept_delta_optimization: true
    require_both_optimize_flags: true  # Both optimizeWrite AND autoCompact
```

---

### Phase 3: Exemption Rules
**Goal**: Handle valid exemptions from clustering requirements

#### Scenario 3.1: Cluster Exclusion Flag
**Scenario**: "Tables can be exempted from clustering with cluster_exclusion flag"
**Priority**: HIGH - Explicit exemption mechanism
**Research Focus**:
- Where is `cluster_exclusion` stored? (property, tag, comment?)
- Boolean vs string handling
- Custom property creation in Databricks

**Implementation**:
1. Research: How to check/set cluster_exclusion flag
2. Layer 1: Unit test for `has_clustering_exemption()` method
3. Layer 2: Integration test with exempted tables
4. Layer 3: Production validation

**Config Values**:
```yaml
clustering:
  exemptions:
    honor_exclusion_flag: true
    exclusion_property_name: "cluster_exclusion"
```

#### Scenario 3.2: Size-Based Exemption
**Scenario**: "Small tables under 1GB can be exempted from clustering"
**Priority**: MEDIUM - Performance optimization
**Research Focus**:
- How to get table size via SDK
- Size units (bytes, MB, GB)
- Cost-effective testing approach

**Implementation**:
1. Research: Access table size programmatically
2. Layer 1: Unit test for `is_size_exempt()` method
3. Layer 2: Integration test with TEST threshold (1MB not 1GB)
4. Layer 3: Production validation with real threshold

**Config Values**:
```yaml
clustering:
  exemptions:
    size_threshold_bytes: 1073741824  # 1GB production
    test_size_threshold_bytes: 1048576  # 1MB for testing
    exempt_small_tables: true
```

---

### Phase 4: Validation Rules
**Goal**: Ensure consistency and prevent conflicts

#### Scenario 4.1: Conflict Detection
**Scenario**: "Tables cannot have conflicting clustering configurations"
**Priority**: MEDIUM - Data quality check
**Research Focus**:
- Reuse methods from Phases 1-3
- Define conflict rules clearly

**Implementation**:
1. Research: Define all possible conflicts
2. Layer 1: Unit test for `has_clustering_conflicts()` method
3. Layer 2: Integration test with conflicting configs
4. Layer 3: Production validation

**Conflict Rules**:
- Cannot have BOTH clustering columns AND cluster_exclusion=true
- Cannot have BOTH auto-clustering AND cluster_exclusion=true
- Warning if multiple clustering approaches used simultaneously

---

### Phase 5: Performance-Based Rules
**Goal**: Optimize based on actual usage patterns

#### Scenario 5.1: Large Table Clustering Requirement
**Scenario**: "Large tables over 1GB should have clustering enabled"
**Priority**: LOW - Depends on size detection from Phase 3
**Research Focus**:
- Reuse size detection from Phase 3.2
- Combine with clustering detection from Phases 1-2

**Implementation**:
1. Layer 1: Unit test for `large_table_has_clustering()` method
2. Layer 2: Integration test with test threshold
3. Layer 3: Production validation

#### Scenario 5.2: Frequently Accessed Tables (OPTIONAL)
**Scenario**: "Frequently accessed tables should prioritize clustering"
**Priority**: VERY LOW - Complex to implement
**Research Focus**:
- Table history API access
- Query log analysis
- Definition of "frequently accessed"

**Note**: May defer this scenario if SDK support is limited

---

### Phase 6: Comprehensive Validation
**Goal**: Combine all granular checks into business rules

#### Scenario 6.1: Comprehensive Clustering Compliance
**Scenario**: "Tables must have at least one valid clustering approach"
**Priority**: FINAL - Requires all previous phases
**Implementation**:
1. Combine validators from Phases 1-3
2. Apply business logic (must have clustering OR valid exemption)
3. Comprehensive reporting

**Business Logic**:
```python
is_compliant = (
    has_clustering_columns() OR 
    has_auto_clustering() OR 
    has_delta_optimization() OR 
    has_clustering_exemption() OR 
    is_size_exempt()
)
```

---

## Implementation Timeline

### Week 1: Foundation (Phase 1)
- [ ] Research clustering column detection
- [ ] Implement basic clustering detection
- [ ] Complete 3-layer tests

### Week 2: Auto-Clustering (Phase 2)
- [ ] Research auto-clustering flags
- [ ] Implement both auto-clustering scenarios
- [ ] Complete 3-layer tests

### Week 3: Exemptions (Phase 3)
- [ ] Research exemption mechanisms
- [ ] Implement exemption scenarios
- [ ] Complete 3-layer tests

### Week 4: Validation & Comprehensive (Phases 4-6)
- [ ] Implement conflict detection
- [ ] Implement comprehensive validation
- [ ] Complete all remaining scenarios

---

## Key Technical Challenges

1. **SDK Limitations**: Some properties may not be accessible
2. **Cost Management**: Large table testing needs careful design
3. **Property Storage**: Custom properties (cluster_exclusion) need consistent approach
4. **Performance**: Checking many tables' properties efficiently

## Success Criteria

- [ ] Each granular scenario works independently
- [ ] Integration tests use cost-effective thresholds
- [ ] Configuration is flexible and well-documented
- [ ] Comprehensive scenario correctly combines all granular checks
- [ ] Performance acceptable for production use

## Notes on Test Thresholds

For integration tests, we'll use smaller thresholds to avoid costs:
- **Production**: 1GB threshold for size-based rules
- **Integration Tests**: 1MB threshold for testing
- **Document** clearly that test thresholds differ from production

This ensures we can validate the logic without creating expensive large tables.