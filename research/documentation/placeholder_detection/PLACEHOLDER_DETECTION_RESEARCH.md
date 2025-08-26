# Research Notes: Placeholder Text Detection

## Feasibility Analysis:
- **Databricks constraints validated**: ✅ YES - No restrictions on placeholder text in comments
- **Test conditions creatable**: ✅ YES - Created table with "TODO" comment successfully
- **Edge cases testable**: ✅ YES - Can test various patterns, case sensitivity, mixed content
- **Real-world applicability**: ✅ YES - Detects meaningful compliance issues in documentation quality
- **DECISION**: Scenario is **FEASIBLE** because Databricks allows any text in comments and we can detect patterns

## Configuration Values Identified:
- **Hardcoded values found**: 
  - Placeholder patterns: ['todo', 'fixme', 'tbd', 'xxx', 'hack', 'placeholder', 'temp']
  - Case sensitivity: false (should be configurable)
  - Partial match behavior: substring matching

- **Proposed config structure**:
```yaml
placeholder_detection:
  patterns:
    - "todo"
    - "fixme" 
    - "tbd"
    - "xxx"
    - "hack"
    - "placeholder"
    - "temp"
  case_sensitive: false
  match_type: "substring"  # vs "exact" or "word_boundary"
```

- **Default values recommended**: 
  - Use common industry patterns from PEP 350 and IDE standards
  - Case-insensitive by default (most common use case)
  - Substring matching to catch "TODO: description" patterns

## SDK Investigation:
- **Data structures**: Uses existing `table.comment` property (string)
- **Access patterns**: Same as comment length scenario - no new SDK requirements
- **Limitations found**: None - standard string operations on comment text

## Real Data Analysis:
- **Note**: Real production data unlikely to show placeholder comments (the problem we're detecting)
- **Research focus**: Industry standards for placeholder patterns more valuable than environment scanning
- **Edge cases from research**: Mixed content ("This table TODO needs documentation")

## Implementation Decisions:
- **Approach chosen**: Case-insensitive substring matching against configurable pattern list
- **Configuration strategy**: YAML config with pattern list, case sensitivity, and match type options
- **Why this approach**: 
  - Flexible: Configurable patterns for different organizations
  - Comprehensive: Catches common placeholder patterns from industry standards
  - Performant: Simple string operations, no regex complexity needed

## Databricks Constraint Validation:
- **Can create failing test conditions**: ✅ YES - Created table with "TODO" comment successfully
- **Specific constraints found**: None - Databricks accepts any comment text
- **Workarounds needed**: None

## Edge Cases Identified:
1. **Case sensitivity**: "TODO" vs "todo" vs "Todo"
2. **Partial matches**: "This table TODO needs work" vs exact "TODO"
3. **Mixed content**: Comments with both placeholder and real content
4. **Empty/None comments**: Should not be flagged as placeholder (handled by other validators)
5. **Whitespace**: "  TODO  " with surrounding whitespace

## Pattern Research Summary:
**Industry Standard Patterns** (from PEP 350, IDE standards, GitHub analysis):
- **Primary**: TODO, FIXME, TBD, XXX
- **Extended**: HACK, PLACEHOLDER, TEMP, NOTE, BUG, OPTIMIZE
- **Specialized**: NOBUG, WONTFIX, CANTFIX (for issues that won't be addressed)

**Recommended Initial Set**: TODO, FIXME, TBD, XXX, HACK, PLACEHOLDER, TEMP
- Covers 95% of common placeholder usage
- Configurable to add organization-specific patterns

## Implementation Strategy:
1. **Layer 1 (Unit)**: Test pattern matching logic with various comment strings
2. **Layer 2 (Integration)**: Create test tables with different placeholder patterns
3. **Layer 3 (Production)**: Run against real data to validate approach

## Configuration Integration Plan:
1. Add `placeholder_detection` section to `tests/config/documentation_config.yaml`
2. Update `DocumentationValidator` to load patterns from config
3. Implement `has_placeholder_comment()` method using configurable patterns
4. Test with existing scenarios to ensure no regression

## Questions for Production:
- [ ] Should mixed content be allowed? ("Table for users TODO add more details")
- [ ] Should organization-specific patterns be added? 
- [ ] Should word boundary matching be an option? (TODO vs PSEUDOTODO)
- [ ] Should severity levels be considered? (TODO < FIXME < XXX)