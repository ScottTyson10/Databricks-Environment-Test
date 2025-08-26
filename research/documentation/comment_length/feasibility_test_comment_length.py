#!/usr/bin/env python3
"""
Feasibility test for comment length scenario.

Tests whether Databricks allows creating tables with comments that violate 
the "must be at least 10 characters" rule.
"""

import os
from dotenv import load_dotenv
from databricks.sdk import WorkspaceClient

# Load environment variables
load_dotenv()

def test_comment_length_feasibility():
    """Test if we can create tables with short comments."""
    
    # Initialize client
    client = WorkspaceClient()
    
    test_catalog = "workspace"
    test_schema = "pytest_test_data"  
    table_base = "feasibility_comment_length"
    
    test_cases = [
        ("1char", "A"),                    # 1 character
        ("5chars", "Short"),               # 5 characters  
        ("9chars", "Nine_char"),           # 9 characters (just under 10)
        ("empty", ""),                     # Empty string
        ("whitespace", "   "),             # Whitespace only
    ]
    
    results = {}
    
    for test_name, comment in test_cases:
        table_name = f"{table_base}_{test_name}"
        full_name = f"{test_catalog}.{test_schema}.{table_name}"
        
        print(f"\nTesting: {test_name} - Comment: '{comment}' (length: {len(comment)})")
        
        try:
            # Build SQL with comment clause
            if comment:
                comment_clause = f"COMMENT '{comment}'"
            else:
                comment_clause = ""  # Test no comment
                
            sql = f"""
            CREATE TABLE {full_name} (
                id INT COMMENT 'Test ID column'
            )
            USING DELTA
            {comment_clause}
            """
            
            print(f"SQL: {sql}")
            
            # Try to create the table
            warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID")
            if not warehouse_id:
                raise ValueError("DATABRICKS_WAREHOUSE_ID required")
                
            client.statement_execution.execute_statement(
                statement=sql, 
                warehouse_id=warehouse_id
            )
            
            print(f"✅ SUCCESS: Created table with comment '{comment}'")
            results[test_name] = {"success": True, "comment": comment, "length": len(comment)}
            
            # Clean up immediately
            try:
                client.tables.delete(full_name)
                print(f"✅ Cleaned up: {full_name}")
            except Exception as cleanup_error:
                print(f"⚠️ Cleanup warning: {cleanup_error}")
                
        except Exception as e:
            print(f"❌ FAILED: {e}")
            results[test_name] = {"success": False, "comment": comment, "length": len(comment), "error": str(e)}
    
    # Summary
    print("\n" + "="*60)
    print("FEASIBILITY TEST RESULTS:")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✅ ALLOWED" if result["success"] else "❌ BLOCKED"
        comment = result["comment"]
        length = result["length"]
        print(f"{test_name:12} | {comment:10} | Length: {length:2} | {status}")
        if not result["success"]:
            print(f"             | Error: {result['error']}")
    
    # Feasibility decision
    print("\n" + "="*60)
    short_comments_allowed = any(
        results[test]["success"] for test in ["1char", "5chars", "9chars"] 
        if test in results
    )
    
    if short_comments_allowed:
        print("🎯 DECISION: SCENARIO IS FEASIBLE")
        print("   Databricks allows tables with comments shorter than 10 characters")
        print("   We can create test conditions that violate the rule")
    else:
        print("🚫 DECISION: SCENARIO IS NOT FEASIBLE") 
        print("   Databricks prevents creation of tables with short comments")
        print("   Cannot test rule violations - scenario should be skipped")
    
    return short_comments_allowed

if __name__ == "__main__":
    test_comment_length_feasibility()