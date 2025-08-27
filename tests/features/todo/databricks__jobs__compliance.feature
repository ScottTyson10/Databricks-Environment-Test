Feature: Databricks Job Compliance
  As a platform administrator
  I want to ensure all jobs follow security and reliability best practices
  So that our data platform is secure and reliable

  Background:
    Given I connect to the Databricks workspace

  @jobs @service-principal
  Scenario: All jobs should use service principals
    Given I discover all accessible jobs
    When I validate service principal compliance for all discovered jobs
    Then all jobs should have proper service principal configuration

  @jobs @retry
  Scenario: All jobs should have proper retry configuration
    Given I discover all accessible jobs
    When I validate retry compliance for all discovered jobs
    Then all jobs should have adequate retry configuration

  @jobs @timeout
  Scenario: All jobs should have appropriate timeout settings
    Given I discover all accessible jobs
    When I validate timeout compliance for all discovered jobs
    Then all jobs should have reasonable timeout settings