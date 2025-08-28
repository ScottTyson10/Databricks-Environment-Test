# Clustering Compliance Implementation Order

## Overview
Implementation order for `tests/features/databricks__clustering__compliance.feature` following the proven granular-to-comprehensive approach. This order prioritizes individual detection capabilities before validation rules, and validation rules before comprehensive business logic.

## Implementation Status Legend
- ✅ **IMPLEMENTED** - All three layers complete (unit, integration, production)
- 🔄 **IN PROGRESS** - Partially implemented 
- ❌ **NOT IMPLEMENTED** - No implementation started

---

## **Phase 1: Foundation - Basic Detection Capabilities**
*Priority: Establish core clustering detection before any validation rules*

### ✅ 1. Explicit clustering columns detection  
**Scenario**: Basic clustering column detection capability (not in BDD feature yet)
- **Status**: FULLY IMPLEMENTED - All 3 layers complete (scenario: explicit-clustering-columns)
- **Rationale**: Foundation for all other scenarios - detects explicit clustering columns
- **Granular**: Tests basic clustering column detection via `clusteringColumns` property
- **Research**: Uses `table.properties["clusteringColumns"]` via Databricks SDK
- **Layer Strategy**: All 3 layers (unit: 10 tests, integration: working, production: working)
- **Configuration**: `clustering_detection.clustering_property_name: "clusteringColumns"`

### ✅ 2. Tables can use clusterByAuto flag for automatic clustering
**Scenario**: `@clustering @auto_clustering`
- **Status**: FULLY IMPLEMENTED - All 3 layers complete
- **Rationale**: Modern auto-clustering detection, independent capability
- **Granular**: Tests single property (`clusterByAuto=true`)
- **Research Focus**: Location and format of clusterByAuto property in SDK
- **Layer Strategy**: All 3 layers
- **Configuration**: `clustering.auto_clustering.accept_cluster_by_auto: true`

### ✅ 3. Tables can use delta auto-optimization for clustering
**Scenario**: `@clustering @delta_auto_optimization`
- **Status**: FULLY IMPLEMENTED - All 3 layers complete
- **Rationale**: Alternative clustering approach, independent capability  
- **Granular**: Tests specific Delta properties (`optimizeWrite` + `autoCompact`)
- **Research Focus**: Access to delta table properties via SDK
- **Layer Strategy**: All 3 layers
- **Configuration**: 
  ```yaml
  clustering.auto_clustering:
    accept_delta_optimization: true
    require_both_optimize_flags: true
  ```

---

## **Phase 2: Exemption Rules**
*Priority: Handle valid exemptions before validation rules*

### ❌ 4. Tables can be exempted from clustering with cluster_exclusion flag
**Scenario**: `@clustering @exclusion`
- **Status**: NOT IMPLEMENTED
- **Rationale**: Explicit exemption mechanism, independent capability
- **Granular**: Tests single exemption property
- **Research Focus**: Custom property storage/access in Databricks
- **Layer Strategy**: All 3 layers
- **Configuration**: 
  ```yaml
  clustering.exemptions:
    honor_exclusion_flag: true
    exclusion_property_name: "cluster_exclusion"
  ```

### ❌ 5. Small tables under 1GB can be exempted from clustering
**Scenario**: `@clustering @exclusion`
- **Status**: NOT IMPLEMENTED
- **Rationale**: Size-based exemption, independent capability
- **Granular**: Tests table size detection and threshold logic
- **Research Focus**: How to get table size via SDK
- **Layer Strategy**: All 3 layers (use small test threshold like 1MB for integration)
- **Configuration**: 
  ```yaml
  clustering.exemptions:
    size_threshold_bytes: 1073741824  # 1GB production
    test_size_threshold_bytes: 1048576  # 1MB testing
    exempt_small_tables: true
  ```

---

## **Phase 3: Validation Rules** 
*Priority: Conflict detection after individual capabilities established*

### ❌ 6. Tables cannot have conflicting clustering configurations
**Scenario**: `@clustering @compliance`
- **Status**: NOT IMPLEMENTED
- **Rationale**: Uses detection from Phases 1-2, adds conflict logic
- **Semi-comprehensive**: Combines multiple detections but focused validation
- **Research Focus**: Define specific conflict rules clearly
- **Layer Strategy**: All 3 layers
- **Conflict Rules**:
  - Cannot have BOTH clustering columns AND cluster_exclusion=true
  - Cannot have BOTH auto-clustering AND cluster_exclusion=true
  - Warning if multiple clustering approaches used simultaneously

### ❌ 7. Clustering configurations should follow organizational standards
**Scenario**: `@clustering @validation`
- **Status**: NOT IMPLEMENTED
- **Rationale**: Organizational policy validation using established patterns
- **Semi-comprehensive**: Uses detection capabilities + policy rules
- **Research Focus**: Define what "organizational standards" means
- **Layer Strategy**: All 3 layers

---

## **Phase 4: Performance-Based Rules**
*Priority: Performance optimization rules after core functionality*

### ❌ 8. Large tables over 1GB should have clustering enabled
**Scenario**: `@clustering @performance`
- **Status**: NOT IMPLEMENTED
- **Rationale**: Combines size detection (Phase 2) with clustering detection (Phase 1)
- **Semi-comprehensive**: Uses multiple granular capabilities
- **Research Focus**: Reuse size detection from Phase 2 scenario
- **Layer Strategy**: All 3 layers
- **Configuration**: `clustering.performance.large_table_threshold_bytes: 1073741824`

### ❌ 9. Tables with clustering should use appropriate column selection
**Scenario**: `@clustering @clustering_columns`
- **Status**: NOT IMPLEMENTED
- **Rationale**: Complex performance validation - clustering columns should align with query patterns
- **Semi-comprehensive**: Requires clustering detection + access pattern analysis
- **Research Focus**: How to analyze table access patterns and validate clustering column appropriateness
- **Layer Strategy**: May be production-only if SDK limitations exist for access pattern analysis
- **Risk**: High complexity, requires both clustering column detection AND query pattern analysis

### ❌ 10. Frequently accessed tables should prioritize clustering
**Scenario**: `@clustering @performance`
- **Status**: NOT IMPLEMENTED
- **Rationale**: Most complex scenario requiring access pattern analysis
- **Semi-comprehensive**: Advanced performance optimization
- **Research Focus**: Table history/query log access via SDK (may be limited)
- **Layer Strategy**: May be production-only if SDK limitations exist
- **Risk**: High complexity, may need to be deferred if SDK access is limited

---

## **Phase 5: Comprehensive Business Rules**
*Priority: Final comprehensive validation using all granular capabilities*

### ❌ 11. Tables must have at least one valid clustering approach
**Scenario**: `@clustering @compliance`
- **Status**: NOT IMPLEMENTED
- **Rationale**: COMPREHENSIVE - combines ALL detection capabilities into business logic
- **Comprehensive**: Master scenario requiring phases 1-4 complete
- **Business Logic**: 
  ```python
  is_compliant = (
      has_clustering_columns() OR 
      has_auto_clustering() OR 
      has_delta_optimization() OR 
      has_clustering_exemption() OR 
      is_size_exempt()
  )
  ```
- **Layer Strategy**: Primarily production-focused, may skip unit/integration

---

## Implementation Guidelines

### Research Requirements (MANDATORY before implementation)
- [ ] **Check Databricks enforcement behaviors** - Review `research/DATABRICKS_ENFORCEMENT_BEHAVIORS.md`
- [ ] **Verify feasibility** - Can tables exist that violate each rule?
- [ ] **Test actual SDK data structures** and property access patterns
- [ ] **Document cost implications** for large table testing
- [ ] **Create feasibility check** using `research/FEASIBILITY_CHECK_TEMPLATE.md`

### Configuration Strategy
All configuration values should be added to `tests/config/documentation_config.yaml`:

```yaml
clustering:
  validation:
    require_clustering_columns: true
  auto_clustering:
    accept_cluster_by_auto: true
    accept_delta_optimization: true
    require_both_optimize_flags: true
  exemptions:
    honor_exclusion_flag: true
    exclusion_property_name: "cluster_exclusion"
    size_threshold_bytes: 1073741824  # 1GB production
    test_size_threshold_bytes: 1048576  # 1MB testing
    exempt_small_tables: true
  performance:
    large_table_threshold_bytes: 1073741824
```

### Testing Strategy
- **Integration tests**: Use cost-effective thresholds (1MB not 1GB)
- **Fixture patterns**: Follow established `_get_table_by_fixture_key` helper pattern
- **Layer validation**: Use `make test-scenario SCENARIO=clustering-X LAYER=Y` after each phase
- **Makefile integration**: Add scenarios to SCENARIOS list for parameterized commands

### Implementation Workflow
1. **Create scenario research directory**: `research/clustering/[scenario_name]/`
2. **Complete feasibility research** before any coding
3. **Implement Layer 1 (Unit)** → validate with `make test-scenario`
4. **Implement Layer 2 (Integration)** → validate with `make test-scenario`  
5. **Implement Layer 3 (Production)** → validate with `make test-scenario`
6. **Complete philosophy checks** and update implementation journal
7. **Update Makefile SCENARIOS list** for new scenario commands

### Success Criteria
- [ ] Each granular scenario works independently
- [ ] Integration tests use cost-effective thresholds  
- [ ] Configuration is flexible and well-documented
- [ ] Comprehensive scenario correctly combines all granular checks
- [ ] Performance acceptable for production use
- [ ] All scenarios follow established three-layer architecture

---

## Notes

### Cost Management
For integration tests, use smaller thresholds to avoid costs:
- **Production**: 1GB threshold for size-based rules
- **Integration Tests**: 1MB threshold for testing
- **Document clearly** that test thresholds differ from production

### Priority Adjustments
If research reveals SDK limitations:
- **Scenario 9** (frequently accessed tables) may need to be deferred or simplified
- **Focus on phases 1-3** as core functionality
- **Phase 4-5** can be implemented as enhancements

This ensures core clustering detection and validation works even if advanced analytics scenarios face technical limitations.