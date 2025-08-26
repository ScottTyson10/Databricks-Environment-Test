Feature: Databricks Documentation Compliance
  As a data governance officer
  I want to ensure tables have proper documentation
  So that data usage and meaning is clear to consumers

  Background:
    Given I connect to the Databricks workspace
    And I have permissions to read table metadata and history

  # Table Comment Validation Scenarios (IMPLEMENTED)
  @table-comments
  Scenario: Tables must have a comment
    Given I discover all accessible tables with documentation filters
    When I check if tables have comments
    Then every table should have a non-empty comment field

  @comment-length
  Scenario: Table comments must meet minimum length requirement
    Given I discover all accessible tables with documentation filters
    When I check table comment lengths
    Then every table comment should meet the minimum length requirement from configuration

  @placeholder-detection
  Scenario: Table comments must not be placeholder text
    Given I discover all accessible tables with documentation filters
    When I check for placeholder text in table comments
    Then no table should have placeholder text in comments

  @column-coverage
  Scenario: Column documentation must meet coverage threshold
    Given I discover all accessible tables with documentation filters
    When I calculate column documentation coverage with configured threshold
    Then columns in each table should meet the coverage threshold from configuration

  @critical-columns
  Scenario: Critical columns must be documented
    Given I discover all accessible tables with documentation filters
    When I check documentation for critical columns defined in configuration
    Then all critical columns should have comprehensive documentation

  # Comprehensive Documentation Check (combines all checks)
  
  @comprehensive
  Scenario: Tables should have comprehensive documentation
    Given I discover all accessible tables with documentation filters
    When I perform a comprehensive documentation check
    Then every table should meet all comprehensive documentation requirements
