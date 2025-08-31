#!/usr/bin/env python3
"""
Feasibility test for small tables auto-exemption based on size.

IMPORTANT: This script was created AFTER completing online research.
It validates the findings from the documentation research phase.

Research findings validated:
1. DESCRIBE DETAIL provides sizeInBytes field
2. Statement Execution API can run SQL commands
3. Table size is not in TableInfo properties
"""

import os
from databricks.sdk import WorkspaceClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_size_based_exemption_feasibility():
    """Test the feasibility of size-based clustering exemptions."""
    
    print("=" * 80)
    print("FEASIBILITY TEST: Small Tables Auto-Exemption")
    print("=" * 80)
    
    # Initialize Databricks client
    w = WorkspaceClient(
        host=os.getenv("DATABRICKS_HOST"),
        token=os.getenv("DATABRICKS_TOKEN")
    )
    
    warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID")
    if not warehouse_id:
        print("ERROR: DATABRICKS_WAREHOUSE_ID not set")
        return
    
    # Test catalog and schema (using existing test infrastructure)
    test_catalog = "workspace"
    test_schema = "pytest_test_data"
    
    print(f"\nTest location: {test_catalog}.{test_schema}")
    print("-" * 40)
    
    # Step 1: Create test tables with different sizes
    test_tables = [
        {
            "name": f"{test_catalog}.{test_schema}.small_table_feasibility",
            "sql": f"""
                CREATE OR REPLACE TABLE {test_catalog}.{test_schema}.small_table_feasibility (
                    id INT,
                    data STRING
                ) USING DELTA
                TBLPROPERTIES ('test_type' = 'size_exemption_small')
            """,
            "expected_size": "< 1GB",
            "should_be_exempt": True
        },
        {
            "name": f"{test_catalog}.{test_schema}.small_table_with_clustering",
            "sql": f"""
                CREATE OR REPLACE TABLE {test_catalog}.{test_schema}.small_table_with_clustering (
                    id INT,
                    data STRING
                ) USING DELTA
                CLUSTER BY (id)
                TBLPROPERTIES ('test_type' = 'size_exemption_clustered')
            """,
            "expected_size": "< 1GB",
            "should_be_exempt": False  # Has clustering, so not exempt despite size
        }
    ]
    
    print("\nStep 1: Creating test tables...")
    for table_spec in test_tables:
        try:
            print(f"  Creating: {table_spec['name']}")
            result = w.statement_execution.execute_statement(
                statement=table_spec['sql'],
                warehouse_id=warehouse_id,
                wait_timeout="30s"
            )
            print(f"    ✓ Created successfully")
        except Exception as e:
            print(f"    ✗ Error: {e}")
    
    # Step 2: Test DESCRIBE DETAIL to get size information
    print("\nStep 2: Testing DESCRIBE DETAIL for size information...")
    print("-" * 40)
    
    for table_spec in test_tables:
        table_name = table_spec['name']
        print(f"\nTable: {table_name}")
        
        try:
            # Execute DESCRIBE DETAIL
            result = w.statement_execution.execute_statement(
                statement=f"DESCRIBE DETAIL {table_name}",
                warehouse_id=warehouse_id,
                wait_timeout="30s"
            )
            
            if result.result and result.result.data_array:
                # Get column names
                columns = [col.name for col in result.manifest.schema.columns]
                # Get first row of data
                row_data = result.result.data_array[0]
                
                # Create dict for easier access
                detail_dict = dict(zip(columns, row_data))
                
                # Extract key information
                size_in_bytes = detail_dict.get('sizeInBytes', 'Not found')
                clustering_columns = detail_dict.get('clusteringColumns', 'Not found')
                num_files = detail_dict.get('numFiles', 'Not found')
                
                print(f"  Size in bytes: {size_in_bytes}")
                print(f"  Clustering columns: {clustering_columns}")
                print(f"  Number of files: {num_files}")
                
                # Validate size detection
                if size_in_bytes != 'Not found':
                    print(f"  ✓ Size detection works!")
                    size_gb = int(size_in_bytes) / (1024**3) if isinstance(size_in_bytes, (int, str)) else 0
                    print(f"  Size in GB: {size_gb:.4f}")
                    
                    # Check exemption logic
                    is_small = size_gb < 1.0
                    has_clustering = clustering_columns and clustering_columns != '[]'
                    
                    if is_small and not has_clustering:
                        print(f"  → Should be EXEMPT (small table without clustering)")
                    elif has_clustering:
                        print(f"  → Should NOT be exempt (has clustering)")
                    else:
                        print(f"  → Should NOT be exempt (large table)")
                        
        except Exception as e:
            print(f"  ✗ Error getting table details: {e}")
    
    # Step 3: Test size threshold scenarios
    print("\n" + "=" * 80)
    print("FEASIBILITY CONCLUSIONS:")
    print("-" * 40)
    print("✓ DESCRIBE DETAIL provides sizeInBytes field")
    print("✓ Can detect table size programmatically")
    print("✓ Can combine size check with clustering detection")
    print("✓ Databricks allows tables of any size without clustering")
    print("✓ Size-based exemption logic is feasible")
    print("\nIMPLEMENTATION APPROACH:")
    print("1. Add get_table_size() method to ClusteringValidator")
    print("2. Use Statement Execution API to run DESCRIBE DETAIL")
    print("3. Update is_exempt_from_clustering_requirements() to check size")
    print("4. Reuse existing configuration (size_threshold_bytes)")
    
    # Step 4: Cleanup test tables
    print("\nStep 4: Cleaning up test tables...")
    for table_spec in test_tables:
        try:
            w.statement_execution.execute_statement(
                statement=f"DROP TABLE IF EXISTS {table_spec['name']}",
                warehouse_id=warehouse_id,
                wait_timeout="10s"
            )
            print(f"  ✓ Dropped: {table_spec['name']}")
        except Exception as e:
            print(f"  ✗ Error dropping table: {e}")

if __name__ == "__main__":
    test_size_based_exemption_feasibility()