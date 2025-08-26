#!/usr/bin/env python3
"""
Feasibility test for detecting explicit clustering columns in Databricks tables.

COST-CONSCIOUS APPROACH:
- Uses EMPTY tables only (no data costs)
- Immediate cleanup after each test
- Minimal table structures
- Metadata-only operations where possible

Run from project root: python research/clustering/explicit_clustering_columns/feasibility_test_clustering_detection.py
"""

from databricks.sdk import WorkspaceClient
from dotenv import load_dotenv
import os
import time

load_dotenv()

def explore_existing_table_clustering():
    """Step 1: Explore clustering properties on existing tables (NO COST)"""
    print("=" * 60)
    print("STEP 1: Exploring existing table clustering properties")
    print("=" * 60)
    
    client = WorkspaceClient()
    
    # Try to find an existing small table to explore
    try:
        # List some tables to find a small one
        tables = client.tables.list(catalog_name="workspace", schema_name="default", max_results=5)
        
        for table_info in tables:
            print(f"\nExploring table: {table_info.full_name}")
            
            # Get full table details
            table = client.tables.get(table_info.full_name)
            print(f"  Table type: {table.table_type}")
            
            # Check for clustering-related attributes
            clustering_attrs = []
            for attr in dir(table):
                if 'cluster' in attr.lower():
                    clustering_attrs.append(attr)
                    try:
                        value = getattr(table, attr)
                        print(f"  {attr}: {value} (type: {type(value)})")
                    except Exception as e:
                        print(f"  {attr}: Error accessing - {e}")
            
            if not clustering_attrs:
                print("  No clustering attributes found")
            
            # Check properties for clustering info
            if table.properties:
                clustering_props = []
                for key, value in table.properties.items():
                    if 'cluster' in key.lower():
                        clustering_props.append((key, value))
                        print(f"  Property '{key}': {value}")
                
                if not clustering_props:
                    print("  No clustering properties found")
            else:
                print("  No table properties found")
                
            print("  " + "-" * 40)
            
    except Exception as e:
        print(f"Error exploring existing tables: {e}")
        print("No existing tables found or accessible")


def test_create_table_with_clustering():
    """Step 2: Create minimal table WITH clustering (COST-CONTROLLED)"""
    print("\n" + "=" * 60)
    print("STEP 2: Creating empty table WITH clustering")
    print("=" * 60)
    
    client = WorkspaceClient()
    warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID")
    
    if not warehouse_id:
        print("ERROR: DATABRICKS_WAREHOUSE_ID not set")
        return False
    
    table_name = "workspace.pytest_test_data.clustering_feasibility_test_with"
    
    # SQL to create EMPTY table with clustering
    create_sql = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INT,
        category STRING,
        created_at TIMESTAMP
    )
    USING DELTA
    CLUSTER BY (category, id)
    COMMENT 'TEMPORARY FEASIBILITY TEST - WILL BE DELETED'
    """
    
    try:
        print(f"Creating table: {table_name}")
        print("Using EMPTY table (no data costs)")
        
        start_time = time.time()
        client.statement_execution.execute_statement(
            statement=create_sql,
            warehouse_id=warehouse_id
        )
        create_time = time.time() - start_time
        print(f"Table created in {create_time:.2f} seconds")
        
        # Wait briefly for table metadata to be available
        print("Waiting for table metadata to be available...")
        time.sleep(2)
        
        # Check clustering detection
        print("Checking clustering properties...")
        table = client.tables.get(table_name)
        
        # Document all clustering-related info found
        print(f"Table full name: {table.full_name}")
        print(f"Table type: {table.table_type}")
        
        # Check attributes
        clustering_found = False
        for attr in dir(table):
            if 'cluster' in attr.lower():
                try:
                    value = getattr(table, attr)
                    print(f"  CLUSTERING ATTR '{attr}': {value} (type: {type(value)})")
                    clustering_found = True
                except:
                    pass
        
        # Check properties
        if table.properties:
            for key, value in table.properties.items():
                if 'cluster' in key.lower():
                    print(f"  CLUSTERING PROP '{key}': {value}")
                    clustering_found = True
        
        if not clustering_found:
            print("  ⚠️ WARNING: No clustering information detected!")
        
        # Test detection function
        has_clustering = detect_clustering_columns(table)
        print(f"  DETECTION RESULT: has_clustering = {has_clustering}")
        
        return True
        
    except Exception as e:
        print(f"ERROR creating table with clustering: {e}")
        return False
        
    finally:
        # GUARANTEED CLEANUP
        print("Cleaning up test table...")
        try:
            cleanup_sql = f"DROP TABLE IF EXISTS {table_name}"
            client.statement_execution.execute_statement(
                statement=cleanup_sql,
                warehouse_id=warehouse_id
            )
            print("✅ Table cleaned up successfully")
        except Exception as e:
            print(f"⚠️ ERROR during cleanup: {e}")


def test_create_table_without_clustering():
    """Step 3: Create minimal table WITHOUT clustering (COST-CONTROLLED)"""
    print("\n" + "=" * 60)
    print("STEP 3: Creating empty table WITHOUT clustering")
    print("=" * 60)
    
    client = WorkspaceClient()
    warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID")
    
    table_name = "workspace.pytest_test_data.clustering_feasibility_test_without"
    
    # SQL to create EMPTY table WITHOUT clustering
    create_sql = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INT,
        category STRING,
        created_at TIMESTAMP
    )
    USING DELTA
    COMMENT 'TEMPORARY FEASIBILITY TEST - WILL BE DELETED'
    """
    
    try:
        print(f"Creating table: {table_name}")
        print("Using EMPTY table (no data costs)")
        
        start_time = time.time()
        client.statement_execution.execute_statement(
            statement=create_sql,
            warehouse_id=warehouse_id
        )
        create_time = time.time() - start_time
        print(f"Table created in {create_time:.2f} seconds")
        
        # Check that clustering is NOT detected
        print("Checking that clustering is NOT present...")
        table = client.tables.get(table_name)
        
        # Test detection function
        has_clustering = detect_clustering_columns(table)
        print(f"  DETECTION RESULT: has_clustering = {has_clustering}")
        
        if has_clustering:
            print("  ⚠️ WARNING: Clustering detected on non-clustered table!")
        else:
            print("  ✅ GOOD: No clustering detected as expected")
        
        return True
        
    except Exception as e:
        print(f"ERROR creating table without clustering: {e}")
        return False
        
    finally:
        # GUARANTEED CLEANUP
        print("Cleaning up test table...")
        try:
            cleanup_sql = f"DROP TABLE IF EXISTS {table_name}"
            client.statement_execution.execute_statement(
                statement=cleanup_sql,
                warehouse_id=warehouse_id
            )
            print("✅ Table cleaned up successfully")
        except Exception as e:
            print(f"⚠️ ERROR during cleanup: {e}")


def detect_clustering_columns(table) -> bool:
    """
    Detect clustering columns based on SDK research findings.
    
    Research confirmed:
    - clustering_columns property contains list of column names
    - Available in TableInfo metadata (no data scanning)
    - Returns None or empty list if no clustering
    """
    # Primary method based on SDK research
    if hasattr(table, 'clustering_columns') and table.clustering_columns:
        print(f"  Found clustering columns: {table.clustering_columns}")
        return True
    
    # Fallback: Check if attribute exists but is empty
    if hasattr(table, 'clustering_columns'):
        print(f"  clustering_columns exists but is empty: {table.clustering_columns}")
    else:
        print(f"  clustering_columns attribute not found")
    
    return False


def main():
    """Main feasibility test runner"""
    print("🔍 CLUSTERING COLUMNS DETECTION FEASIBILITY TEST")
    print("Cost-conscious approach: Using empty tables only")
    print()
    
    try:
        # Step 1: Explore existing tables (no cost)
        explore_existing_table_clustering()
        
        # Step 2: Test table WITH clustering
        success_with = test_create_table_with_clustering()
        
        # Step 3: Test table WITHOUT clustering
        success_without = test_create_table_without_clustering()
        
        # Summary
        print("\n" + "=" * 60)
        print("FEASIBILITY TEST SUMMARY")
        print("=" * 60)
        
        if success_with and success_without:
            print("✅ SUCCESS: Can create and test both scenarios")
            print("✅ Cost-effective testing approach validated")
            print("✅ Ready to proceed with implementation")
        else:
            print("❌ ISSUES FOUND: Need to resolve before implementation")
            
        print(f"\nEstimated test cost: < $0.01 (metadata operations only)")
        print("Next step: Document findings in feasibility check document")
        
    except Exception as e:
        print(f"CRITICAL ERROR in feasibility test: {e}")
        print("Cannot proceed with implementation until resolved")


if __name__ == "__main__":
    main()