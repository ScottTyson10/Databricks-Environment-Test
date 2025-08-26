# Scenario Implementation Quick Reference
**Essential Commands and Reminders for Scenario Development**

## 🚀 Getting Started

```bash
# 1. Create research directory  
mkdir research/[feature_area]/[scenario_name]

# 2. Copy templates to research directory
cp research/SCENARIO_JOURNAL_TEMPLATE.md research/[feature_area]/[scenario_name]/[SCENARIO_NAME]_IMPLEMENTATION_JOURNAL.md
cp SCENARIO_IMPLEMENTATION_CHECKLIST.md research/[feature_area]/[scenario_name]/[SCENARIO_NAME]_IMPLEMENTATION.md
cp research/FEASIBILITY_CHECK_TEMPLATE.md research/[feature_area]/[scenario_name]/[SCENARIO_NAME]_FEASIBILITY_CHECK.md

# 3. Setup environment
make venv-dev
make test-connection

# 4. Start research phase
# Focus: SDK docs, requirements, feasibility - NOT existing data exploration
# Note: Any feasibility test scripts should be created in the research/[feature_area]/[scenario_name]/ directory
# Note: Update implementation journal throughout the process
```

## 📋 Phase Overview

```
Research (1-2 days) → Layer 1 → Philosophy Check → Layer 2 → Philosophy Check → Layer 3 → Philosophy Check → Documentation
```

## 🔍 Research Phase Essentials

### ✅ Must Complete Before Coding
**⚠️ ALWAYS re-read SCENARIO_EXPANSION_PLAN.md Section 1 first - do not skip this**
**📋 USE research/FEASIBILITY_CHECK_TEMPLATE.md for step-by-step testing**

- [ ] **Feasibility confirmed** - can create objects that VIOLATE the rule?
  - [ ] Actually tested creating "bad" objects in Databricks
  - [ ] Confirmed Databricks allows the failing condition to exist
- [ ] **Config values extracted** - all hardcoded values identified
- [ ] **SDK behavior understood** - data structures and edge cases
- [ ] **DECISION GATE PASSED** - scenario is implementable

### ⚠️ Research Anti-Patterns
- ❌ **Don't skip feasibility testing** - always verify Databricks allows "bad" objects to exist
- ❌ **Don't rely on existing data** - it probably won't show the problems you're detecting
- ❌ **Don't skip config extraction** - hardcoded values will cause problems later
- ❌ **Don't assume SDK behavior** - test edge cases yourself
- ❌ **Don't leave feasibility scripts in main directory** - move all research artifacts to research/[feature_area]/[scenario_name]/

## 🏗️ Implementation Commands

### Layer 1: Unit Tests
```bash
# Implementation
vim tests/validators/documentation.py    # Add validator methods
vim tests/unit/documentation/test_*_validators.py  # Add unit tests (organized by scenario)
vim tests/config/documentation_config.yaml  # Add config values

# Add scenario to Makefile
vim Makefile            # Add scenario to SCENARIOS list and unit test mapping

# Validation
make test-scenario SCENARIO=[scenario-name] LAYER=unit  # Must pass
make quality           # Must pass
```

### Layer 2: Integration Tests
```bash
# Implementation  
vim tests/fixtures/table_factory.py     # Add test table specs
vim tests/integration/documentation/test_[scenario]_integration.py  # Add integration tests

# Validation
make test-scenario SCENARIO=[scenario-name] LAYER=integration  # Must pass in < 30 seconds
# Verify 100% coverage of test scenarios
```

### Layer 3: Production Tests
```bash
# Implementation
vim tests/step_definitions/documentation_steps.py  # Add/update step definitions
vim tests/features/databricks__documentation__compliance.feature  # Update BDD scenarios

# Validation
make test-scenario SCENARIO=[scenario-name] LAYER=production  # Must execute and provide meaningful results
```

## 🔄 Philosophy Check Reminders

### After Each Layer - MANDATORY
1. **Update scenario journal** - `research/[feature_area]/[scenario_name]/[SCENARIO_NAME]_IMPLEMENTATION_JOURNAL.md`
2. **Update main journal** - `IMPLEMENTATION_JOURNAL.md` (if architectural changes)
3. **Update architecture insights** - if patterns changed
4. **Update recommendations** - lessons learned
5. **Use TodoWrite** - track mandatory updates

### 🔄 If Issues Found (Normal!)
- **Address issues** before proceeding
- **Iterate until clean** - don't skip this
- **Document learnings** - valuable for future scenarios

### 🏗️ Data Structure Changes
When your scenario needs new data structures:

```bash
# 1. Decide location based on scope
# - Shared across components? → utils/ or models/
# - Validator-specific? → validators/
# - Test-only? → fixtures/

# 2. Define the structure
vim tests/[appropriate_location]/[module].py

# 3. Update consumers and check types
make quality  # Catches type mismatches early
```

## ⚡ Common Pitfalls

| Pitfall | Prevention |
|---------|------------|
| **Skipping feasibility check** | Always verify Databricks allows objects that VIOLATE the rule to exist |
| **Hardcoded values** | Extract ALL configurable values to YAML first |
| **Missing philosophy checks** | Use TodoWrite to track - they're not optional |
| **Poor test coverage** | Integration tests must validate 100% of created scenarios |
| **Architecture violations** | Keep layers separate - unit has no dependencies |
| **Wrong data structure location** | Use decision tree to choose appropriate module |

## 📊 Success Criteria Checklist

### Research Phase
- [ ] Feasibility confirmed with actual test cases
- [ ] All config values extracted to YAML
- [ ] SDK behavior tested and documented
- [ ] Requirements fully understood

### Implementation Phase
- [ ] Layer 1: `make test-unit` passes, < 5 seconds
- [ ] Layer 2: `make test-integration` passes, < 30 seconds  
- [ ] Layer 3: `make test-production` provides business value
- [ ] Philosophy checks completed after each layer

### Completion Phase
- [ ] `make quality` passes
- [ ] Full three-layer test suite works
- [ ] Documentation updated (README, CLAUDE.md)
- [ ] Configuration properly integrated

## 🎯 Recommended Implementation Order

1. **Comment Length Validation** (simplest - extends existing logic)
2. **Placeholder Text Detection** (pattern matching)
3. **Critical Column Documentation** (new column analysis)
4. **Column Coverage Threshold** (statistical analysis)
5. **Comprehensive Check** (integration of all validators)

## 🆘 When Stuck

### Research Phase Issues
- **Can't create failing conditions** → Scenario may not be feasible, document why
- **SDK unclear** → Create small test cases to understand behavior
- **Requirements ambiguous** → Document assumptions and proceed

### Implementation Issues
- **Tests failing** → Check layer separation, verify config integration
- **Performance slow** → Review session fixtures, check discovery limits
- **Philosophy check fails** → Normal! Address issues and iterate

### Integration Issues  
- **Can't create test tables** → Check Databricks permissions and SQL syntax
- **Test cleanup fails** → Verify context managers and error handling
- **Coverage incomplete** → Ensure all test scenarios are actually validated

## 📞 Key Files Quick Access

```bash
# Critical process files (READ FIRST)
SCENARIO_EXPANSION_PLAN.md                         # Section 1: Research principles
research/FEASIBILITY_CHECK_TEMPLATE.md             # Step-by-step feasibility testing
SCENARIO_IMPLEMENTATION_CHECKLIST.md               # Detailed working document
research/SCENARIO_JOURNAL_TEMPLATE.md              # Implementation journal template

# Research organization
research/                                           # All research and feasibility files
research/[feature_area]/[scenario_name]/           # Scenario-specific research
research/README.md                                  # Research organization guide

# Primary implementation files
tests/validators/documentation.py                    # Validator logic
tests/config/documentation_config.yaml              # Configuration
tests/unit/documentation/test_*_validators.py      # Unit tests (organized by scenario)
tests/integration/test_[scenario]_integration.py    # Integration tests
tests/step_definitions/documentation_steps.py       # BDD steps

# Documentation files  
README.md                                            # User documentation
CLAUDE.md                                           # AI assistant guidance
IMPLEMENTATION_JOURNAL.md                          # Architecture philosophy checks
research/[feature_area]/[scenario_name]/[SCENARIO_NAME]_IMPLEMENTATION_JOURNAL.md  # Scenario tracking
```

---

## 💡 Layer Validation Examples

After implementing each layer, validate using the make command system:

```bash
# Example: critical-columns scenario layer validation
make test-scenario SCENARIO=critical-columns LAYER=unit         # 43 tests pass
make test-scenario SCENARIO=critical-columns LAYER=integration  # Will be ready after Layer 2
make test-scenario SCENARIO=critical-columns LAYER=production   # Will be ready after Layer 3

# Other scenario examples  
make test-scenario SCENARIO=table-comments LAYER=unit          # 19 tests pass
make test-scenario SCENARIO=comment-length LAYER=unit          # 22 tests pass
make test-scenario SCENARIO=placeholder-detection LAYER=unit   # 10 tests pass

# Debug mode for troubleshooting
make test-scenario SCENARIO=critical-columns LAYER=unit MODE=debug
```

---

**Remember: Focus, iterate, and document. Each scenario builds on the proven foundation!**