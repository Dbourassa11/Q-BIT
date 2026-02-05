"""
Data Integrity Scanner Agent

Specialized agent for scanning and validating data integrity.
"""

import asyncio
import hashlib
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

import structlog

from ..core.agent import AgentCapability, BaseAgent, Task, TaskResult
from ..database.models import DataIntegrityLevel

logger = structlog.get_logger(__name__)


class DataIntegrityScannerAgent(BaseAgent):
    """Agent specialized in data integrity scanning and validation"""

    def __init__(self, config: Optional[Dict] = None):
        capabilities = {
            AgentCapability.CODE_ANALYSIS,
            AgentCapability.OPTIMIZATION,
            AgentCapability.MONITORING,
        }

        if config is None:
            config = {}

        config.setdefault("capabilities", list(capabilities))
        config.setdefault("max_concurrent_tasks", 5)
        config.setdefault("timeout", 600)  # 10 minutes for large scans

        super().__init__(config)

        logger.info(
            "data_integrity_scanner_initialized",
            agent_id=self.agent_id,
            capabilities=list(capabilities),
        )

    async def _setup(self) -> None:
        """Setup data integrity scanner"""
        logger.info("data_integrity_scanner_setup", agent_id=self.agent_id)
        await asyncio.sleep(0.1)

    async def _cleanup(self) -> None:
        """Cleanup data integrity scanner"""
        logger.info("data_integrity_scanner_cleanup", agent_id=self.agent_id)
        await asyncio.sleep(0.1)

    async def execute_task(self, task: Task) -> TaskResult:
        """
        Execute data integrity scanning task

        Supported task types:
        - scan_completeness: Check data completeness
        - scan_consistency: Check data consistency
        - scan_accuracy: Validate data accuracy
        - scan_full: Comprehensive integrity scan
        - validate_schema: Validate against schema
        """
        logger.info(
            "executing_integrity_scan",
            agent_id=self.agent_id,
            task_id=task.task_id,
        )

        try:
            task_type = task.metadata.get("task_type", "scan_full")

            if task_type == "scan_completeness":
                result = await self._scan_completeness(task)
            elif task_type == "scan_consistency":
                result = await self._scan_consistency(task)
            elif task_type == "scan_accuracy":
                result = await self._scan_accuracy(task)
            elif task_type == "scan_full":
                result = await self._scan_full(task)
            elif task_type == "validate_schema":
                result = await self._validate_schema(task)
            else:
                result = TaskResult(
                    task_id=task.task_id,
                    success=False,
                    error=f"Unknown task type: {task_type}",
                    metadata={"agent_id": self.agent_id},
                )

            logger.info(
                "integrity_scan_completed",
                agent_id=self.agent_id,
                task_id=task.task_id,
                success=result.success,
            )

            return result

        except Exception as e:
            logger.error(
                "integrity_scan_failed",
                agent_id=self.agent_id,
                task_id=task.task_id,
                error=str(e),
            )
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error=str(e),
                metadata={"agent_id": self.agent_id},
            )

    async def _scan_completeness(self, task: Task) -> TaskResult:
        """Scan data for completeness"""
        data = task.metadata.get("data", {})
        required_fields = task.metadata.get("required_fields", [])

        total_records = len(data) if isinstance(data, list) else 1
        issues = []
        missing_field_counts = {}

        if isinstance(data, list):
            for idx, record in enumerate(data):
                for field in required_fields:
                    if field not in record or record[field] is None or record[field] == "":
                        issues.append(
                            {
                                "type": "missing_field",
                                "field": field,
                                "record_index": idx,
                                "severity": "high",
                            }
                        )
                        missing_field_counts[field] = missing_field_counts.get(field, 0) + 1

        # Calculate completeness score
        if required_fields and total_records > 0:
            total_required = len(required_fields) * total_records
            total_missing = sum(missing_field_counts.values())
            completeness_score = 1.0 - (total_missing / total_required)
        else:
            completeness_score = 1.0

        return TaskResult(
            task_id=task.task_id,
            success=True,
            result={
                "completeness_score": completeness_score,
                "total_records": total_records,
                "issues_found": len(issues),
                "issues": issues[:100],  # Limit to first 100
                "missing_field_summary": missing_field_counts,
            },
            metadata={"agent_id": self.agent_id, "scan_type": "completeness"},
        )

    async def _scan_consistency(self, task: Task) -> TaskResult:
        """Scan data for consistency"""
        data = task.metadata.get("data", {})
        consistency_rules = task.metadata.get("consistency_rules", {})

        issues = []
        total_records = len(data) if isinstance(data, list) else 1

        if isinstance(data, list):
            # Check for duplicate records
            seen_hashes = set()
            for idx, record in enumerate(data):
                # Create hash of record
                record_str = json.dumps(record, sort_keys=True)
                record_hash = hashlib.md5(record_str.encode()).hexdigest()

                if record_hash in seen_hashes:
                    issues.append(
                        {
                            "type": "duplicate_record",
                            "record_index": idx,
                            "severity": "medium",
                        }
                    )
                seen_hashes.add(record_hash)

            # Check for data type consistency
            if data:
                first_record = data[0]
                for field in first_record:
                    expected_type = type(first_record[field])
                    for idx, record in enumerate(data[1:], 1):
                        if field in record and not isinstance(record[field], expected_type):
                            issues.append(
                                {
                                    "type": "type_inconsistency",
                                    "field": field,
                                    "record_index": idx,
                                    "expected_type": expected_type.__name__,
                                    "actual_type": type(record[field]).__name__,
                                    "severity": "high",
                                }
                            )

        # Calculate consistency score
        if total_records > 0:
            consistency_score = 1.0 - min(len(issues) / total_records, 1.0)
        else:
            consistency_score = 1.0

        return TaskResult(
            task_id=task.task_id,
            success=True,
            result={
                "consistency_score": consistency_score,
                "total_records": total_records,
                "issues_found": len(issues),
                "issues": issues[:100],
                "duplicates_found": sum(1 for i in issues if i["type"] == "duplicate_record"),
            },
            metadata={"agent_id": self.agent_id, "scan_type": "consistency"},
        )

    async def _scan_accuracy(self, task: Task) -> TaskResult:
        """Scan data for accuracy"""
        data = task.metadata.get("data", {})
        validation_rules = task.metadata.get("validation_rules", {})

        issues = []
        total_records = len(data) if isinstance(data, list) else 1

        if isinstance(data, list):
            for idx, record in enumerate(data):
                for field, rules in validation_rules.items():
                    if field not in record:
                        continue

                    value = record[field]

                    # Check range
                    if "min" in rules and value < rules["min"]:
                        issues.append(
                            {
                                "type": "value_below_minimum",
                                "field": field,
                                "record_index": idx,
                                "value": value,
                                "min": rules["min"],
                                "severity": "high",
                            }
                        )

                    if "max" in rules and value > rules["max"]:
                        issues.append(
                            {
                                "type": "value_above_maximum",
                                "field": field,
                                "record_index": idx,
                                "value": value,
                                "max": rules["max"],
                                "severity": "high",
                            }
                        )

                    # Check pattern
                    if "pattern" in rules and isinstance(value, str):
                        import re

                        if not re.match(rules["pattern"], value):
                            issues.append(
                                {
                                    "type": "pattern_mismatch",
                                    "field": field,
                                    "record_index": idx,
                                    "value": value,
                                    "pattern": rules["pattern"],
                                    "severity": "medium",
                                }
                            )

        # Calculate accuracy score
        if total_records > 0:
            accuracy_score = 1.0 - min(len(issues) / total_records, 1.0)
        else:
            accuracy_score = 1.0

        return TaskResult(
            task_id=task.task_id,
            success=True,
            result={
                "accuracy_score": accuracy_score,
                "total_records": total_records,
                "issues_found": len(issues),
                "issues": issues[:100],
            },
            metadata={"agent_id": self.agent_id, "scan_type": "accuracy"},
        )

    async def _scan_full(self, task: Task) -> TaskResult:
        """Comprehensive integrity scan"""
        # Run all scans
        completeness_result = await self._scan_completeness(task)
        consistency_result = await self._scan_consistency(task)
        accuracy_result = await self._scan_accuracy(task)

        # Aggregate results
        completeness_score = completeness_result.result["completeness_score"]
        consistency_score = consistency_result.result["consistency_score"]
        accuracy_score = accuracy_result.result["accuracy_score"]

        # Overall integrity score (weighted average)
        integrity_score = (
            completeness_score * 0.4 + consistency_score * 0.3 + accuracy_score * 0.3
        )

        # Determine integrity level
        if integrity_score >= 0.9:
            integrity_level = DataIntegrityLevel.EXCELLENT
        elif integrity_score >= 0.75:
            integrity_level = DataIntegrityLevel.GOOD
        elif integrity_score >= 0.6:
            integrity_level = DataIntegrityLevel.FAIR
        elif integrity_score >= 0.4:
            integrity_level = DataIntegrityLevel.POOR
        else:
            integrity_level = DataIntegrityLevel.CRITICAL

        # Aggregate issues
        all_issues = (
            completeness_result.result["issues"]
            + consistency_result.result["issues"]
            + accuracy_result.result["issues"]
        )

        critical_issues = sum(1 for i in all_issues if i.get("severity") == "high")
        warnings = sum(1 for i in all_issues if i.get("severity") == "medium")

        # Generate recommendations
        recommendations = []
        if completeness_score < 0.7:
            recommendations.append("Implement data validation to ensure all required fields are populated")
        if consistency_score < 0.7:
            recommendations.append("Add uniqueness constraints and type validation")
        if accuracy_score < 0.7:
            recommendations.append("Implement range and pattern validation rules")

        # Sacred geometry alignment for data structure
        from ..sgpa.pattern_engine import PatternRecognitionEngine

        pattern_engine = PatternRecognitionEngine()
        data = task.metadata.get("data", {})
        structure_analysis = pattern_engine.analyze_data_structure(data)

        structural_alignment = (
            structure_analysis.patterns[0].confidence if structure_analysis.patterns else 0.5
        )

        return TaskResult(
            task_id=task.task_id,
            success=True,
            result={
                "integrity_level": integrity_level.value,
                "integrity_score": integrity_score,
                "completeness_score": completeness_score,
                "consistency_score": consistency_score,
                "accuracy_score": accuracy_score,
                "total_records_scanned": completeness_result.result["total_records"],
                "total_issues": len(all_issues),
                "critical_issues": critical_issues,
                "warnings": warnings,
                "issues": all_issues[:100],
                "recommendations": recommendations,
                "structural_alignment": structural_alignment,
                "sacred_geometry_patterns": [
                    {"type": p.pattern_type, "confidence": p.confidence}
                    for p in structure_analysis.patterns
                ],
            },
            metadata={"agent_id": self.agent_id, "scan_type": "full"},
        )

    async def _validate_schema(self, task: Task) -> TaskResult:
        """Validate data against schema"""
        data = task.metadata.get("data", {})
        schema = task.metadata.get("schema", {})

        issues = []

        # Simple schema validation
        if isinstance(data, dict) and isinstance(schema, dict):
            for field, field_schema in schema.items():
                if field_schema.get("required", False) and field not in data:
                    issues.append(
                        {
                            "type": "missing_required_field",
                            "field": field,
                            "severity": "high",
                        }
                    )

                if field in data:
                    expected_type = field_schema.get("type")
                    actual_type = type(data[field]).__name__

                    if expected_type and expected_type != actual_type:
                        issues.append(
                            {
                                "type": "type_mismatch",
                                "field": field,
                                "expected": expected_type,
                                "actual": actual_type,
                                "severity": "high",
                            }
                        )

        validation_score = 1.0 if not issues else 0.0

        return TaskResult(
            task_id=task.task_id,
            success=True,
            result={
                "validation_score": validation_score,
                "issues_found": len(issues),
                "issues": issues,
                "schema_valid": len(issues) == 0,
            },
            metadata={"agent_id": self.agent_id, "scan_type": "schema_validation"},
        )
