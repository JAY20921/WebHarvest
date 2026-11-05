"""
Validation Service - Validate extracted data quality
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, ValidationError, create_model
import logging

logger = logging.getLogger(__name__)


class ValidationResult:
    """
    Result of data validation
    """
    
    def __init__(self):
        self.is_valid = True
        self.total_records = 0
        self.valid_records = 0
        self.invalid_records = 0
        self.errors = []
        self.warnings = []
        self.field_stats = {}
    
    def add_error(self, record_idx: int, field: str, error: str):
        """Add validation error"""
        self.errors.append({
            'record_index': record_idx,
            'field': field,
            'error': error,
        })
        self.is_valid = False
    
    def add_warning(self, record_idx: int, field: str, warning: str):
        """Add validation warning"""
        self.warnings.append({
            'record_index': record_idx,
            'field': field,
            'warning': warning,
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'is_valid': self.is_valid,
            'total_records': self.total_records,
            'valid_records': self.valid_records,
            'invalid_records': self.invalid_records,
            'error_count': len(self.errors),
            'warning_count': len(self.warnings),
            'errors': self.errors[:10],  # First 10 errors
            'warnings': self.warnings[:10],  # First 10 warnings
            'field_stats': self.field_stats,
        }


class ValidationService:
    """
    Service for validating extracted data quality
    """
    
    @staticmethod
    def validate_extracted_data(
        records: List[Dict[str, Any]],
        schema: Dict[str, Any],
    ) -> ValidationResult:
        """
        Validate extracted data against schema
        
        Args:
            records: List of extracted records
            schema: Extraction schema with field types
            
        Returns:
            ValidationResult with detailed validation info
        """
        logger.info(f"Validating {len(records)} records...")
        
        result = ValidationResult()
        result.total_records = len(records)
        
        field_types = schema.get('fields', {})
        
        # Initialize field statistics
        for field_name in field_types.keys():
            result.field_stats[field_name] = {
                'present': 0,
                'missing': 0,
                'null': 0,
                'empty': 0,
            }
        
        # Validate each record
        for idx, record in enumerate(records):
            record_valid = True
            
            # Check each field
            for field_name, field_type in field_types.items():
                # Update statistics
                if field_name not in record:
                    result.field_stats[field_name]['missing'] += 1
                    result.add_warning(idx, field_name, "Field missing from record")
                    continue
                
                value = record[field_name]
                
                if value is None:
                    result.field_stats[field_name]['null'] += 1
                    result.add_warning(idx, field_name, "Field value is null")
                    continue
                
                if isinstance(value, str) and not value.strip():
                    result.field_stats[field_name]['empty'] += 1
                    result.add_warning(idx, field_name, "Field value is empty")
                    continue
                
                result.field_stats[field_name]['present'] += 1
                
                # Type validation
                expected_type = ValidationService._get_python_type(field_type)
                if expected_type and not isinstance(value, expected_type):
                    result.add_error(
                        idx,
                        field_name,
                        f"Expected {expected_type.__name__}, got {type(value).__name__}"
                    )
                    record_valid = False
            
            if record_valid:
                result.valid_records += 1
            else:
                result.invalid_records += 1
        
        logger.info(
            f"Validation complete: {result.valid_records} valid, "
            f"{result.invalid_records} invalid, "
            f"{len(result.warnings)} warnings"
        )
        
        return result
    
    @staticmethod
    def _get_python_type(field_type: str) -> Optional[type]:
        """
        Map field type string to Python type
        
        Args:
            field_type: Type string from schema
            
        Returns:
            Python type or None
        """
        type_mapping = {
            'string': str,
            'text': str,
            'number': (int, float),
            'int': int,
            'integer': int,
            'float': float,
            'boolean': bool,
            'bool': bool,
            'url': str,
            'link': str,
            'price': (int, float),
            'currency': (int, float),
        }
        
        return type_mapping.get(field_type.lower())
    
    @staticmethod
    def calculate_quality_score(validation_result: ValidationResult) -> float:
        """
        Calculate overall data quality score (0.0 - 1.0)
        
        Args:
            validation_result: Validation result
            
        Returns:
            Quality score between 0.0 and 1.0
        """
        if validation_result.total_records == 0:
            return 0.0
        
        # Base score from valid records
        validity_score = validation_result.valid_records / validation_result.total_records
        
        # Penalty for missing/null/empty fields
        total_fields = sum(
            stats['present'] + stats['missing'] + stats['null'] + stats['empty']
            for stats in validation_result.field_stats.values()
        )
        
        if total_fields == 0:
            completeness_score = 0.0
        else:
            present_fields = sum(
                stats['present']
                for stats in validation_result.field_stats.values()
            )
            completeness_score = present_fields / total_fields
        
        # Weighted average
        quality_score = (validity_score * 0.6) + (completeness_score * 0.4)
        
        return round(quality_score, 3)
    
    @staticmethod
    def get_recommendations(validation_result: ValidationResult) -> List[str]:
        """
        Get recommendations for improving extraction
        
        Args:
            validation_result: Validation result
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Check for high error rate
        if validation_result.invalid_records > validation_result.valid_records:
            recommendations.append(
                "High error rate detected. Consider refining the extraction schema or selectors."
            )
        
        # Check for missing fields
        for field_name, stats in validation_result.field_stats.items():
            missing_rate = stats['missing'] / validation_result.total_records if validation_result.total_records > 0 else 0
            
            if missing_rate > 0.5:
                recommendations.append(
                    f"Field '{field_name}' is missing in {missing_rate*100:.0f}% of records. "
                    f"Check if the selector is correct."
                )
            
            null_rate = stats['null'] / validation_result.total_records if validation_result.total_records > 0 else 0
            
            if null_rate > 0.3:
                recommendations.append(
                    f"Field '{field_name}' has null values in {null_rate*100:.0f}% of records. "
                    f"The selector might be targeting the wrong elements."
                )
        
        # Check for low record count
        if validation_result.total_records < 3:
            recommendations.append(
                "Very few records extracted. The container selector might be too specific or incorrect."
            )
        
        return recommendations
