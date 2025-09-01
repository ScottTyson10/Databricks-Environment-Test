"""Unit tests for SchemaDetector class.

Tests the research-based schema detection implementation with proper mocking
and edge case validation.
"""

import pytest
from unittest.mock import Mock, MagicMock
from databricks.sdk.service.catalog import ColumnInfo, ColumnTypeName

from tests.utils.schema_detector import SchemaDetector, SchemaDetectionError


class TestSchemaDetector:
    """Unit tests for SchemaDetector with comprehensive method coverage."""
    
    @pytest.fixture
    def mock_client(self):
        """Mock Databricks WorkspaceClient."""
        return Mock()
    
    @pytest.fixture
    def detector(self, mock_client):
        """SchemaDetector instance with mocked client."""
        return SchemaDetector(mock_client, warehouse_id="test-warehouse")
    
    def test_native_sdk_success(self, detector, mock_client):
        """Test successful schema detection via native SDK."""
        # Setup mock table info
        mock_table_info = Mock()
        mock_table_info.columns = [
            ColumnInfo(name="id", type_name=ColumnTypeName.LONG),
            ColumnInfo(name="data", type_name=ColumnTypeName.STRING),
        ]
        mock_client.tables.get.return_value = mock_table_info
        
        result = detector.get_table_schema("workspace.test.table")
        
        assert result == [("id", "LONG"), ("data", "STRING")]
        mock_client.tables.get.assert_called_once_with("workspace.test.table")
    
    def test_native_sdk_no_columns(self, detector, mock_client):
        """Test native SDK failure when table has no columns."""
        mock_table_info = Mock()
        mock_table_info.columns = None
        mock_client.tables.get.return_value = mock_table_info
        
        # Should fall back to Information Schema
        mock_result = Mock()
        mock_result.result.data_array = [["id", "LONG"], ["data", "STRING"]]
        mock_client.statement_execution.execute_statement.return_value = mock_result
        
        result = detector.get_table_schema("workspace.test.table")
        
        assert result == [("id", "LONG"), ("data", "STRING")]
    
    def test_information_schema_success(self, detector, mock_client):
        """Test successful fallback to Information Schema."""
        # Make native SDK fail
        mock_client.tables.get.side_effect = Exception("SDK failed")
        
        # Setup Information Schema success
        mock_result = Mock()
        mock_result.result = Mock()
        mock_result.result.data_array = [["id", "BIGINT"], ["name", "STRING"]]
        mock_client.statement_execution.execute_statement.return_value = mock_result
        
        result = detector.get_table_schema("workspace.test.table")
        
        assert result == [("id", "BIGINT"), ("name", "STRING")]
        
        # Verify SQL query
        call_args = mock_client.statement_execution.execute_statement.call_args
        assert "information_schema.columns" in call_args[1]["statement"]
        assert "WHERE table_catalog = 'workspace'" in call_args[1]["statement"]
    
    def test_describe_table_success(self, detector, mock_client):
        """Test successful fallback to DESCRIBE TABLE."""
        # Make both native SDK and Information Schema fail
        mock_client.tables.get.side_effect = Exception("SDK failed")
        
        # First call (Information Schema) fails, second call (DESCRIBE) succeeds
        mock_result = Mock()
        mock_result.result.data_array = [["id", "BIGINT"], ["data", "STRING"], ["# Partition Info", ""]]
        
        mock_client.statement_execution.execute_statement.side_effect = [
            Exception("Info schema failed"),  # Information Schema fails
            mock_result  # DESCRIBE TABLE succeeds
        ]
        
        result = detector.get_table_schema("workspace.test.table")
        
        # Should stop at partition info and only return real columns
        assert result == [("id", "BIGINT"), ("data", "STRING")]
    
    def test_describe_table_clustering_metadata_filtering(self, detector, mock_client):
        """Test that DESCRIBE TABLE properly filters clustering metadata."""
        mock_client.tables.get.side_effect = Exception("SDK failed")
        
        mock_result = Mock()
        # Simulate DESCRIBE output with clustering metadata
        mock_result.result.data_array = [
            ["id", "BIGINT"],
            ["category", "STRING"],
            ["data", "STRING"],
            ["Clustering Information", ""],  # Should stop here
            ["category", "STRING"]  # Duplicate from clustering section
        ]
        
        mock_client.statement_execution.execute_statement.side_effect = [
            Exception("Info schema failed"),
            mock_result
        ]
        
        result = detector.get_table_schema("workspace.test.table")
        
        # Should not include duplicates or metadata
        assert result == [("id", "BIGINT"), ("category", "STRING"), ("data", "STRING")]
    
    def test_all_methods_fail(self, detector, mock_client):
        """Test SchemaDetectionError when all methods fail."""
        # Make all methods fail
        mock_client.tables.get.side_effect = Exception("SDK failed")
        mock_client.statement_execution.execute_statement.side_effect = Exception("SQL failed")
        
        with pytest.raises(SchemaDetectionError) as exc_info:
            detector.get_table_schema("workspace.test.table")
        
        assert "Could not determine schema" in str(exc_info.value)
    
    def test_no_warehouse_id_fallback_limitation(self, mock_client):
        """Test behavior when no warehouse_id is provided."""
        detector = SchemaDetector(mock_client, warehouse_id=None)
        mock_client.tables.get.side_effect = Exception("SDK failed")
        
        with pytest.raises(SchemaDetectionError):
            detector.get_table_schema("workspace.test.table")
        
        # Should not attempt SQL methods without warehouse_id
        mock_client.statement_execution.execute_statement.assert_not_called()
    
    def test_invalid_table_name_format(self, detector, mock_client):
        """Test error handling for invalid table name format."""
        mock_client.tables.get.side_effect = Exception("SDK failed")
        
        # Information Schema should fail on invalid table name format
        mock_client.statement_execution.execute_statement.side_effect = ValueError("Invalid format")
        
        with pytest.raises(SchemaDetectionError):
            detector.get_table_schema("invalid_table_name")
    
    @pytest.mark.parametrize("table_name", [
        "catalog.schema.table",
        "workspace.pytest_test_data.size_exemption_test_small_table"
    ])
    def test_valid_table_name_formats(self, detector, mock_client, table_name):
        """Test that valid table name formats are handled correctly."""
        mock_table_info = Mock()
        mock_table_info.columns = [ColumnInfo(name="id", type_name=ColumnTypeName.LONG)]
        mock_client.tables.get.return_value = mock_table_info
        
        result = detector.get_table_schema(table_name)
        
        assert result == [("id", "LONG")]
        mock_client.tables.get.assert_called_once_with(table_name)
    
    def test_enum_to_string_conversion(self, detector, mock_client):
        """Test proper conversion of ColumnTypeName enums to strings."""
        mock_table_info = Mock()
        mock_table_info.columns = [
            ColumnInfo(name="id", type_name=ColumnTypeName.LONG),
            ColumnInfo(name="name", type_name=ColumnTypeName.STRING),
            ColumnInfo(name="price", type_name=ColumnTypeName.DOUBLE),
            ColumnInfo(name="created_at", type_name=ColumnTypeName.TIMESTAMP),
        ]
        mock_client.tables.get.return_value = mock_table_info
        
        result = detector.get_table_schema("workspace.test.table")
        
        expected = [
            ("id", "LONG"),
            ("name", "STRING"), 
            ("price", "DOUBLE"),
            ("created_at", "TIMESTAMP")
        ]
        assert result == expected
    
    def test_empty_columns_handling(self, detector, mock_client):
        """Test handling of tables with empty column lists from various methods."""
        mock_client.tables.get.side_effect = Exception("SDK failed")
        
        # Information Schema returns empty result
        mock_result = Mock()
        mock_result.result.data_array = []
        
        mock_client.statement_execution.execute_statement.side_effect = [
            mock_result,  # Empty Information Schema result
            Exception("DESCRIBE failed")  # DESCRIBE also fails
        ]
        
        with pytest.raises(SchemaDetectionError):
            detector.get_table_schema("workspace.test.table")