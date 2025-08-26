# Research Directory

This directory contains all research, feasibility testing, and exploratory work done during scenario development. Research files should be organized by scenario to keep the main repository clean.

## Directory Structure

```
research/
├── README.md                               # This file
├── FEASIBILITY_CHECK_TEMPLATE.md          # Template for feasibility checks  
├── DATABRICKS_ENFORCEMENT_BEHAVIORS.md    # Known Databricks enforcement constraints
├── SCENARIO_JOURNAL_TEMPLATE.md           # Template for implementation journals
├── documentation/                         # Documentation-related scenario research
│   ├── comment_length/                    # Comment length scenario research
│   │   ├── COMMENT_LENGTH_IMPLEMENTATION.md
│   │   └── feasibility_test_comment_length.py
│   ├── placeholder_detection/             # Placeholder detection scenario research
│   │   └── PLACEHOLDER_DETECTION_RESEARCH.md
│   ├── critical_columns_documentation/    # Critical column scenario research
│   │   ├── CRITICAL_COLUMNS_FEASIBILITY_CHECK.md
│   │   └── CRITICAL_COLUMNS_IMPLEMENTATION_JOURNAL.md
│   └── column_coverage_threshold/         # Column coverage threshold scenario research
│       └── COLUMN_COVERAGE_THRESHOLD_FEASIBILITY_CHECK.md
└── [future_feature]/                      # Research for future feature areas
    └── [scenario_name]/                   # Research for specific scenarios
        ├── [SCENARIO_NAME]_FEASIBILITY_CHECK.md
        ├── [SCENARIO_NAME]_IMPLEMENTATION_JOURNAL.md
        ├── [SCENARIO_NAME]_RESEARCH.md
        ├── feasibility_test_[scenario].py
        └── explore_[feature].py
```

## Research File Types

### Feasibility Check Documents
- **Purpose**: Document whether a scenario can be implemented in Databricks
- **Naming**: `[SCENARIO_NAME]_FEASIBILITY_CHECK.md`
- **Content**: Test results, SDK limitations, edge cases

### Implementation Journals
- **Purpose**: Track complete implementation lifecycle from research to completion
- **Naming**: `[SCENARIO_NAME]_IMPLEMENTATION_JOURNAL.md`
- **Content**: Timeline, technical decisions, philosophy checks, lessons learned

### Research Documents
- **Purpose**: Detailed analysis of requirements, SDK behavior, configuration needs
- **Naming**: `[SCENARIO_NAME]_RESEARCH.md` or `[SCENARIO_NAME]_IMPLEMENTATION.md`
- **Content**: Technical findings, implementation decisions, architecture notes

### Test Scripts  
- **Purpose**: One-off scripts for testing feasibility, exploring SDK behavior
- **Naming**: `feasibility_test_[scenario].py` or `test_[scenario]_feasibility.py`
- **Content**: Temporary code for validation, not part of main test suite
- **Requirement**: ALL feasibility scripts must be stored in research directory, not main directory

## Guidelines

1. **Check enforcement behaviors first**: Review `DATABRICKS_ENFORCEMENT_BEHAVIORS.md` before starting new scenario research
2. **Create feature directory first**: `mkdir research/[feature_area]` (e.g., `documentation`, `performance`, `security`)
3. **Create scenario directory**: `mkdir research/[feature_area]/[scenario_name]`
4. **Move research files**: Keep main directory clean by moving all research artifacts including feasibility scripts
5. **Update enforcement behaviors**: Add discovered constraints to `DATABRICKS_ENFORCEMENT_BEHAVIORS.md`
6. **Reference in main docs**: Update main documentation to point to research directory  
7. **Preserve history**: Research documents contain valuable implementation decisions

## Integration with Main Documentation

- Main documentation should reference research files when relevant
- Use relative paths: `See research/documentation/critical_columns_documentation/CRITICAL_COLUMNS_FEASIBILITY_CHECK.md`
- Keep research accessible but out of the main workflow

## Current Feature Areas

### Documentation
All scenarios related to table and column documentation compliance:
- `comment_length` - Table comment minimum length validation
- `placeholder_detection` - Placeholder text detection in comments
- `critical_columns_documentation` - Critical column documentation requirements
- `column_coverage_threshold` - Column documentation coverage thresholds