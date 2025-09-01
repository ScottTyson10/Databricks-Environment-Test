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
        return SchemaDetector(mock_client)
    
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
        
        with pytest.raises(SchemaDetectionError) as exc_info:
            detector.get_table_schema("workspace.test.table")
        
        assert "has no columns metadata" in str(exc_info.value)
    
    def test_sdk_failure(self, detector, mock_client):
        """Test SchemaDetectionError when SDK fails."""
        mock_client.tables.get.side_effect = Exception("SDK connection failed")
        
        with pytest.raises(SchemaDetectionError) as exc_info:
            detector.get_table_schema("workspace.test.table")
        
        assert "Could not determine schema" in str(exc_info.value)
        assert "SDK connection failed" in str(exc_info.value)
    
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
        """Test handling of tables with empty column lists."""
        mock_table_info = Mock()
        mock_table_info.columns = []
        mock_client.tables.get.return_value = mock_table_info
        
        with pytest.raises(SchemaDetectionError) as exc_info:
            detector.get_table_schema("workspace.test.table")
            
        assert "has no columns metadata" in str(exc_info.value)