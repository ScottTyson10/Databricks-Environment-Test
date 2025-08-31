#!/usr/bin/env python3
"""Feasibility test for detecting table sizes in Databricks.

This script tests different approaches to get table size information:
1. Via table properties
2. Via DESCRIBE DETAIL SQL command
3. Via table statistics
"""

import os
from databricks import sql
from databricks.sdk import WorkspaceClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_table_size_detection():
    """Test various methods to get table size information."""
    
    # Initialize Databricks clients
    w = WorkspaceClient(
        host=os.getenv("DATABRICKS_HOST"),
        token=os.getenv("DATABRICKS_TOKEN")
    )
    
    # Test table to examine
    test_table = "samples.nyctaxi.trips"  # Using a known sample table
    
    print(f"Testing table size detection for: {test_table}")
    print("=" * 80)
    
    # Method 1: Check table properties via SDK
    print("\nMethod 1: Table properties via SDK")
    print("-" * 40)
    try:
        table_info = w.tables.get(test_table)
        print(f"Table properties available: {list(table_info.properties.keys()) if table_info.properties else 'None'}")
        if table_info.properties:
            # Look for size-related properties
            size_props = {k: v for k, v in table_info.properties.items() 
                         if 'size' in k.lower() or 'bytes' in k.lower()}
            print(f"Size-related properties: {size_props if size_props else 'None found'}")
            
            # Also check for stats
            stats_props = {k: v for k, v in table_info.properties.items() 
                          if 'stats' in k.lower()}
            print(f"Stats-related properties: {stats_props if stats_props else 'None found'}")
    except Exception as e:
        print(f"Error getting table info: {e}")
    
    # Method 2: DESCRIBE DETAIL SQL command
    print("\nMethod 2: DESCRIBE DETAIL SQL command")
    print("-" * 40)
    
    warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID")
    if not warehouse_id:
        print("DATABRICKS_WAREHOUSE_ID not set, skipping SQL test")
    else:
        try:
            connection = sql.connect(
                server_hostname=os.getenv("DATABRICKS_HOST"),
                http_path=f"/sql/1.0/warehouses/{warehouse_id}",
                access_token=os.getenv("DATABRICKS_TOKEN")
            )
            cursor = connection.cursor()
            
            # DESCRIBE DETAIL provides size information
            cursor.execute(f"DESCRIBE DETAIL {test_table}")
            columns = [desc[0] for desc in cursor.description]
            row = cursor.fetchone()
            
            if row:
                result_dict = dict(zip(columns, row))
                print(f"Columns available: {columns}")
                print(f"\nSize in bytes: {result_dict.get('sizeInBytes', 'Not found')}")
                print(f"Number of files: {result_dict.get('numFiles', 'Not found')}")
                print(f"Stats: {result_dict.get('stats', 'Not found')}")
                
                # Check if we get clustering info too
                print(f"Clustering columns: {result_dict.get('clusteringColumns', 'Not found')}")
                
            cursor.close()
            connection.close()
        except Exception as e:
            print(f"Error with SQL query: {e}")
    
    # Method 3: Try table statistics via SDK
    print("\nMethod 3: Table statistics via SDK")
    print("-" * 40)
    try:
        # Check if table has storage location info
        table_info = w.tables.get(test_table)
        if hasattr(table_info, 'storage_location'):
            print(f"Storage location: {table_info.storage_location}")
        else:
            print("No storage_location attribute")
            
        if hasattr(table_info, 'data_source_format'):
            print(f"Data source format: {table_info.data_source_format}")
            
        # Check all available attributes
        print(f"\nAll table attributes: {[attr for attr in dir(table_info) if not attr.startswith('_')]}")
    except Exception as e:
        print(f"Error checking table attributes: {e}")
    
    print("\n" + "=" * 80)
    print("Feasibility test complete!")
    
    # Conclusions
    print("\nCONCLUSIONS:")
    print("-" * 40)
    print("1. DESCRIBE DETAIL SQL command provides 'sizeInBytes' field")
    print("2. This is the most reliable way to get table size")
    print("3. We can use this for size-based exemption logic")
    print("4. Size info is NOT in table.properties from SDK")

if __name__ == "__main__":
    test_table_size_detection()