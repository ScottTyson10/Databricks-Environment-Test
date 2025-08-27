Feature: Databricks Metadata Compliance
  As a data platform administrator
  I want to ensure tables have proper metadata configuration
  So that data management and governance policies are enforced

  Background:
    Given I connect to the Databricks workspace
    And I have permissions to read table metadata and history

  # Required Properties Scenarios

  @metadata  @required_properties
  Scenario: Tables must have required metadata properties
    Given I discover all accessible tables with metadata filters
    When I check for required metadata properties
    Then every table should have: owner, purpose, data_source properties

  @metadata  @table_ownership
  Scenario: Tables must have valid owner information
    Given I discover all accessible tables with metadata filters
    When I validate table ownership metadata
    Then each table should have a valid owner property with contact information

  @metadata  @data_lineage
  Scenario: Tables must have data source information
    Given I discover all accessible tables with metadata filters
    When I check data source metadata
    Then each table should specify its data_source property

  # Naming Convention Scenarios

  @metadata  @naming_conventions
  Scenario: Table names must follow naming conventions
    Given I discover all accessible tables with metadata filters
    When I validate table naming conventions
    Then table names should match pattern: {domain}_{purpose}_{entity}

  @metadata  @schema_naming
  Scenario: Schema names must follow naming conventions
    Given I discover all accessible schemas with metadata filters
    When I validate schema naming conventions
    Then schema names should follow organizational standards

  # Storage and Location Scenarios

  @metadata  @managed_storage
  Scenario: Tables must use managed storage locations
    Given I discover all accessible tables with metadata filters
    When I check storage location compliance
    Then all tables should use managed storage (no external paths)

  @metadata  @storage_classification
  Scenario: Tables must have storage tier classification
    Given I discover all accessible tables with metadata filters
    When I check storage tier metadata
    Then tables should have classification: hot, warm, cold, or archive

  # Data Classification Scenarios

  @metadata  @data_classification
  Scenario: Tables must have valid data classification tags
    Given I discover all accessible tables with metadata filters
    When I check data classification metadata
    Then tables should have classification: public, internal, confidential, or restricted

  @metadata  @sensitivity_labeling
  Scenario: Tables with sensitive data must be properly labeled
    Given I discover all accessible tables with metadata filters
    When I scan for sensitive data patterns
    Then tables containing PII should have sensitivity labels

  # Production Environment Scenarios

  @metadata  @change_management
  Scenario: Production tables must have change management metadata
    Given I discover all accessible tables with metadata filters
    When I check production table metadata
    Then production tables should have: change_ticket, deployment_date properties

  @metadata  @environment_tagging
  Scenario: Tables must have environment tags
    Given I discover all accessible tables with metadata filters
    When I check environment classification
    Then each table should be tagged as: dev, test, staging, or prod