Feature: Databricks Maintenance Compliance
  As a data engineer
  I want to ensure tables are properly maintained
  So that performance and costs are optimized

  Background:
    Given I connect to the Databricks workspace
    And I have permissions to read table metadata and history

  # ============================================================================
  # VACUUM MAINTENANCE SCENARIOS
  # ============================================================================

  @maintenance @vacuum 
  Scenario: Delta tables must be vacuumed regularly
    Given I have test tables for maintenance vacuum compliance
    When I check for regular vacuum maintenance
    Then tables should have VACUUM operations within the last 30 days or be exempt

  @maintenance @vacuum 
  Scenario: Tables can be exempt from vacuum requirements
    Given I have test tables for maintenance vacuum compliance
    When I check for vacuum exemption tags
    Then tables with "no_vacuum_needed" property should be exempt from vacuum validation

  @maintenance @vacuum 
  Scenario: Tables with custom vacuum thresholds must be maintained accordingly
    Given I have test tables for maintenance vacuum compliance
    When I check for custom vacuum threshold compliance
    Then tables should be vacuumed within their specified custom threshold period

  @maintenance @vacuum 
  Scenario: Never-vacuumed tables should be identified
    Given I have test tables for maintenance vacuum compliance
    When I check for vacuum history
    Then tables that have never been vacuumed should be flagged for maintenance

  # ============================================================================
  # ORPHANED TABLE DETECTION SCENARIOS
  # ============================================================================

  @maintenance @orphaned 
  Scenario: Potentially orphaned tables must be identified
    Given I have test tables for maintenance orphaned detection
    When I check for table usage patterns
    Then tables with no recent access should be flagged as potentially orphaned

  @maintenance @orphaned 
  Scenario: Archive tables should not be considered orphaned
    Given I have test tables for maintenance orphaned detection
    When I check for orphaned status
    Then tables tagged as "archive" should not be flagged as orphaned

  @maintenance @orphaned 
  Scenario: Reference tables should not be considered orphaned
    Given I have test tables for maintenance orphaned detection
    When I check for orphaned status
    Then tables tagged as "reference" should not be flagged as orphaned

  @maintenance @orphaned 
  Scenario: Active tables with recent usage should not be orphaned
    Given I have test tables for maintenance orphaned detection
    When I check for table activity
    Then tables with recent reads or updates should not be flagged as orphaned