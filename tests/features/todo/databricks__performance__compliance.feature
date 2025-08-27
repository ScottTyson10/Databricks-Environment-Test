Feature: Databricks Performance Optimization
  As a platform engineer
  I want to ensure tables and clusters are optimized
  So that queries run efficiently and costs are controlled

  Background:
    Given I connect to the Databricks workspace
    And I have permissions to read table metadata and history

  # ============================================================================
  # FILE SIZE OPTIMIZATION SCENARIOS
  # ============================================================================

  @performance @file-sizing 
  Scenario: Delta tables must have optimal file sizes
    Given I have test tables for performance file size optimization
    When I check for optimal file size configuration
    Then tables should have file sizes optimized for query performance

  @performance @file-sizing 
  Scenario: Tables should use auto-optimize for file management
    Given I have test tables for performance file size optimization
    When I check for auto-optimize configuration
    Then tables should have auto-optimize enabled for write operations

  @performance @file-sizing 
  Scenario: Tables should have appropriate compression settings
    Given I have test tables for performance file size optimization
    When I check for compression configuration
    Then tables should use efficient compression algorithms

  @performance @file-sizing 
  Scenario: Small file problems should be identified
    Given I have test tables for performance file size optimization
    When I check for small file issues
    Then tables with excessive small files should be flagged for optimization

  # ============================================================================
  # PARTITIONING OPTIMIZATION SCENARIOS
  # ============================================================================

  @performance @partitions 
  Scenario: Tables must have appropriate partitioning strategies
    Given I have test tables for performance partition optimization
    When I check for partitioning strategies
    Then tables should have optimal partitioning for their access patterns

  @performance @partitions 
  Scenario: Tables should not be over-partitioned
    Given I have test tables for performance partition optimization
    When I check for over-partitioning
    Then tables should not have excessive partition columns

  @performance @partitions 
  Scenario: Partition columns should be well-chosen
    Given I have test tables for performance partition optimization
    When I check for partition column selection
    Then partition columns should have appropriate cardinality for efficient pruning

  @performance @partitions 
  Scenario: Large tables without partitioning should be identified
    Given I have test tables for performance partition optimization
    When I check for missing partitioning
    Then large tables without partitioning should be flagged for optimization