Feature: Databricks Clustering Compliance
  As a platform engineer
  I want to ensure tables have proper clustering configuration
  So that query performance is optimized

  Background:
    Given I connect to the Databricks workspace
    And I have permissions to read table metadata and history


  # Auto-Clustering Scenarios

  @clustering  @auto_clustering
  Scenario: Tables can use clusterByAuto flag for automatic clustering
    Given I discover all accessible tables with clustering filters
    When I check clusterByAuto flag configuration
    Then tables with clusterByAuto=true should be considered properly clustered

  @clustering  @delta_auto_optimization
  Scenario: Tables can use delta auto-optimization for clustering
    Given I discover all accessible tables with clustering filters
    When I check delta auto-optimization settings
    Then tables with both optimizeWrite=true and autoCompact=true should be considered clustered

  # Cluster Exclusion Scenarios

  @clustering  @exclusion
  Scenario: Tables can be exempted from clustering with cluster_exclusion flag
    Given I discover all accessible tables with clustering filters
    When I check cluster exclusion exemption flags
    Then tables with cluster_exclusion=true should be exempt from clustering requirements

  @clustering  @exclusion
  Scenario: Small tables under 1GB can be exempted from clustering
    Given I discover all accessible tables with clustering filters
    When I check table sizes and clustering exemption eligibility
    Then tables under 1GB should be automatically exempt from clustering requirements

  # Compliance Validation Scenarios

  @clustering  @compliance
  Scenario: Tables must have at least one valid clustering approach
    Given I discover all accessible tables with clustering filters
    When I validate comprehensive clustering compliance
    Then every table should have explicit columns, auto-clustering, or exemption flag

  @clustering  @compliance
  Scenario: Tables cannot have conflicting clustering configurations
    Given I discover all accessible tables with clustering filters
    When I check for clustering configuration conflicts
    Then no table should have both explicit clustering and cluster_exclusion flag
  
  @clustering  @validation
  Scenario: Clustering configurations should follow organizational standards
    Given I discover all accessible tables with clustering filters  
    When I validate clustering configurations against organizational policies
    Then clustering approaches should follow approved patterns and naming conventions

  # Performance-Based Clustering Requirements

  @clustering  @performance
  Scenario: Large tables over 1GB should have clustering enabled
    Given I discover all accessible tables with clustering filters
    When I check table sizes and clustering status for performance optimization
    Then tables over 1GB should have clustering or auto-optimization enabled

  @clustering  @performance  
  Scenario: Frequently accessed tables should prioritize clustering
    Given I discover all accessible tables with clustering filters
    When I analyze table access patterns and clustering status
    Then frequently accessed tables should have clustering configuration optimized

  # Explicit Clustering Column Scenarios
  @clustering  @clustering_columns
  Scenario: Tables with clustering should use appropriate column selection
    Given I discover all accessible tables with clustering filters
    When I validate clustering column appropriateness for workload
    Then clustering columns should align with common query patterns and data distribution
