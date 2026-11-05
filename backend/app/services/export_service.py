"""
Export Service - Convert extracted data to various formats
Handles JSON, CSV, and Excel (XLSX) exports
"""

import json
import csv
import io
from typing import List, Dict, Any, BinaryIO
from datetime import datetime
import pandas as pd
from app.core.exceptions import ExportError
import logging

logger = logging.getLogger(__name__)


class ExportService:
    """
    Service for exporting extracted data to various formats
    """
    
    @staticmethod
    def export_to_json(
        records: List[Dict[str, Any]],
        pretty: bool = True,
    ) -> str:
        """
        Export data to JSON string
        
        Args:
            records: List of extracted records
            pretty: Whether to use pretty formatting
            
        Returns:
            JSON string
            
        Raises:
            ExportError: If export fails
        """
        logger.info(f"Exporting {len(records)} records to JSON...")
        
        try:
            if pretty:
                json_str = json.dumps(records, indent=2, ensure_ascii=False)
            else:
                json_str = json.dumps(records, ensure_ascii=False)
            
            logger.info(f"Successfully exported to JSON ({len(json_str)} bytes)")
            return json_str
            
        except Exception as e:
            logger.error(f"JSON export failed: {e}")
            raise ExportError(f"Failed to export to JSON: {str(e)}")
    
    @staticmethod
    def export_to_csv(
        records: List[Dict[str, Any]],
    ) -> str:
        """
        Export data to CSV string
        
        Args:
            records: List of extracted records
            
        Returns:
            CSV string
            
        Raises:
            ExportError: If export fails
        """
        logger.info(f"Exporting {len(records)} records to CSV...")
        
        if not records:
            return ""
        
        try:
            # Get all field names (union of all record keys)
            fieldnames = list(records[0].keys()) if records else []
            
            # Create CSV in memory
            output = io.StringIO()
            writer = csv.DictWriter(
                output,
                fieldnames=fieldnames,
                extrasaction='ignore',
            )
            
            writer.writeheader()
            writer.writerows(records)
            
            csv_str = output.getvalue()
            logger.info(f"Successfully exported to CSV ({len(csv_str)} bytes)")
            return csv_str
            
        except Exception as e:
            logger.error(f"CSV export failed: {e}")
            raise ExportError(f"Failed to export to CSV: {str(e)}")
    
    @staticmethod
    def export_to_excel(
        records: List[Dict[str, Any]],
    ) -> bytes:
        """
        Export data to Excel (XLSX) bytes
        
        Args:
            records: List of extracted records
            
        Returns:
            Excel file as bytes
            
        Raises:
            ExportError: If export fails
        """
        logger.info(f"Exporting {len(records)} records to Excel...")
        
        if not records:
            # Create empty workbook
            df = pd.DataFrame()
        else:
            # Create DataFrame from records
            df = pd.DataFrame(records)
        
        try:
            # Write to bytes buffer
            output = io.BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(
                    writer,
                    sheet_name='Extracted Data',
                    index=False,
                )
            
            excel_bytes = output.getvalue()
            logger.info(f"Successfully exported to Excel ({len(excel_bytes)} bytes)")
            return excel_bytes
            
        except Exception as e:
            logger.error(f"Excel export failed: {e}")
            raise ExportError(f"Failed to export to Excel: {str(e)}")
    
    @staticmethod
    def create_export_filename(
        format: str,
        url: str = "",
        timestamp: datetime = None,
    ) -> str:
        """
        Create filename for export
        
        Args:
            format: Export format (json, csv, xlsx)
            url: Optional source URL for naming
            timestamp: Optional timestamp (uses current time if not provided)
            
        Returns:
            Suggested filename
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # Clean URL for filename
        if url:
            # Extract domain
            from urllib.parse import urlparse
            domain = urlparse(url).netloc.replace('www.', '')
            if domain:
                base_name = f"extraction_{domain}"
            else:
                base_name = "extraction"
        else:
            base_name = "extraction"
        
        # Add timestamp
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        
        # Add extension
        extension_map = {
            'json': '.json',
            'csv': '.csv',
            'xlsx': '.xlsx',
            'excel': '.xlsx',
        }
        
        extension = extension_map.get(format.lower(), '.txt')
        
        return f"{base_name}_{timestamp_str}{extension}"
    
    @staticmethod
    def get_content_type(format: str) -> str:
        """
        Get HTTP content type for format
        
        Args:
            format: Export format
            
        Returns:
            Content-Type header value
        """
        content_types = {
            'json': 'application/json',
            'csv': 'text/csv',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        }
        
        return content_types.get(format.lower(), 'application/octet-stream')
    
    @staticmethod
    async def export_data(
        records: List[Dict[str, Any]],
        format: str,
    ) -> tuple[bytes | str, str, str]:
        """
        Export data to specified format
        
        Args:
            records: List of extracted records
            format: Export format (json, csv, xlsx)
            
        Returns:
            Tuple of (data, content_type, filename)
            
        Raises:
            ExportError: If export fails
        """
        format_lower = format.lower()
        
        if format_lower == 'json':
            data = ExportService.export_to_json(records)
            content_type = ExportService.get_content_type('json')
            filename = ExportService.create_export_filename('json')
            
        elif format_lower == 'csv':
            data = ExportService.export_to_csv(records)
            content_type = ExportService.get_content_type('csv')
            filename = ExportService.create_export_filename('csv')
            
        elif format_lower in ['xlsx', 'excel']:
            data = ExportService.export_to_excel(records)
            content_type = ExportService.get_content_type('xlsx')
            filename = ExportService.create_export_filename('xlsx')
            
        else:
            raise ExportError(f"Unsupported export format: {format}")
        
        return data, content_type, filename


# Create singleton instance
export_service = ExportService()
