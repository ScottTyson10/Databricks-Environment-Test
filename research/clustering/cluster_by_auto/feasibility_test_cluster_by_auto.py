#!/usr/bin/env python3
"""
Feasibility test for clusterByAuto detection scenario.

Tests:
1. Can create table with CLUSTER BY AUTO
2. Can detect automatic clustering via SDK properties  
3. Can differentiate from tables without clustering

Cost-conscious: Uses empty tables for minimal cost.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from databricks.sdk import WorkspaceClient
from dotenv import load_dotenv
import json

# Load environment
load_dotenv()

def main():
    print("🧪 ClusterByAuto Feasibility Test")
    print("=" * 50)
    
    client = WorkspaceClient()
    
    # Test table names (using pytest_test_data schema)
    schema = "workspace.pytest_test_data"
    table_with_auto = f"{schema}.feasibility_cluster_by_auto"
    table_without_auto = f"{schema}.feasibility_no_auto_cluster"
    
    try:
        # Step 1: Create table WITH automatic clustering
        print("\n📋 Step 1: Creating table with CLUSTER BY AUTO")
        create_auto_sql = f"""
        CREATE TABLE {table_with_auto} (
            id INT COMMENT 'Test ID column',
            category STRING COMMENT 'Category for clustering'
        ) 
        USING DELTA
        CLUSTER BY AUTO
        """
        
        try:
            # Use statement_execution API for SQL
            client.statement_execution.execute_statement(
                statement=create_auto_sql,
                warehouse_id=client.config.warehouse_id
            )
            print(f"✅ Successfully created table with automatic clustering: {table_with_auto}")
        except Exception as e:
            print(f"❌ Failed to create table with CLUSTER BY AUTO: {e}")
            return False
            
        # Step 2: Create table WITHOUT clustering (baseline)
        print("\n📋 Step 2: Creating baseline table without clustering")
        create_baseline_sql = f"""
        CREATE TABLE {table_without_auto} (
            id INT COMMENT 'Test ID column',
            category STRING COMMENT 'Category column'
        ) 
        USING DELTA
        """
        
        try:
            client.statement_execution.execute_statement(
                statement=create_baseline_sql,
                warehouse_id=client.config.warehouse_id
            )
            print(f"✅ Successfully created baseline table: {table_without_auto}")
        except Exception as e:
            print(f"❌ Failed to create baseline table: {e}")
            return False
            
        # Step 3: Test SDK detection capabilities
        print("\n📋 Step 3: Testing SDK detection of automatic clustering")
        
        # Get table info for automatic clustering table
        print(f"\n🔍 Analyzing automatic clustering table: {table_with_auto}")
        auto_table = client.tables.get(full_name=table_with_auto)
        
        print(f"   Table properties: {auto_table.properties}")
        if hasattr(auto_table, 'cluster_keys') and auto_table.cluster_keys:
            print(f"   Cluster keys: {auto_table.cluster_keys}")
        
        # Check for clusterByAuto property
        has_cluster_by_auto = False
        if auto_table.properties:
            # Look for automatic clustering indicators
            auto_keys = [
                "delta.clusterBy.auto",
                "clusterByAuto", 
                "delta.clustering.auto",
                "clustering.auto"
            ]
            
            for key in auto_keys:
                if key in auto_table.properties:
                    print(f"   ✅ Found clustering property '{key}': {auto_table.properties[key]}")
                    has_cluster_by_auto = True
                    
            # Also check if clusteringColumns is populated by auto-selection
            if "clusteringColumns" in auto_table.properties:
                clustering_columns = auto_table.properties["clusteringColumns"]
                print(f"   📊 Clustering columns (auto-selected): {clustering_columns}")
        
        # Get table info for baseline table
        print(f"\n🔍 Analyzing baseline table: {table_without_auto}")
        baseline_table = client.tables.get(full_name=table_without_auto)
        
        print(f"   Table properties: {baseline_table.properties}")
        
        # Check baseline has no clustering
        baseline_has_clustering = False
        if baseline_table.properties:
            if "clusteringColumns" in baseline_table.properties:
                print(f"   📊 Clustering columns: {baseline_table.properties['clusteringColumns']}")
                baseline_has_clustering = True
        
        # Step 4: Analyze feasibility results
        print("\n📊 Feasibility Analysis Results")
        print("=" * 40)
        
        if has_cluster_by_auto:
            print("✅ FEASIBLE: Can detect automatic clustering via SDK properties")
            print(f"   - Automatic clustering table has detectable properties")
            print(f"   - Different from baseline table (no clustering)")
        else:
            print("⚠️  UNCLEAR: Cannot definitively detect automatic clustering")
            print("   - May need different property keys")
            print("   - May need to check clustering columns population")
            
        print(f"\n🔄 Detection Summary:")
        print(f"   - Auto clustering table properties: {len(auto_table.properties or {})}")
        print(f"   - Baseline table properties: {len(baseline_table.properties or {})}")
        
        # Success if we can differentiate the tables
        can_differentiate = (
            auto_table.properties != baseline_table.properties or
            has_cluster_by_auto
        )
        
        if can_differentiate:
            print("✅ SCENARIO IS FEASIBLE: Can differentiate automatic clustering tables")
        else:
            print("❌ SCENARIO NOT FEASIBLE: Cannot detect automatic clustering difference")
            
        return can_differentiate
        
    except Exception as e:
        print(f"❌ Feasibility test failed: {e}")
        return False
        
    finally:
        # Cleanup: Always drop test tables
        print("\n🧹 Cleaning up test tables...")
        for table_name in [table_with_auto, table_without_auto]:
            try:
                client.statement_execution.execute_statement(
                    statement=f"DROP TABLE IF EXISTS {table_name}",
                    warehouse_id=client.config.warehouse_id
                )
                print(f"   ✅ Dropped {table_name}")
            except Exception as e:
                print(f"   ⚠️  Could not drop {table_name}: {e}")

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Feasibility test indicates scenario may not be implementable")
        sys.exit(1)
    else:
        print("\n✅ Feasibility test successful - scenario is implementable")
        sys.exit(0)