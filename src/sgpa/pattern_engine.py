"""
Sacred Geometry Pattern Recognition Engine

Detects sacred geometry patterns in code, data structures, and systems.
"""

import ast
import json
import math
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np

from .calculators import FibonacciCalculator, GoldenRatioCalculator, PHI


@dataclass
class PatternMatch:
    """A detected pattern match"""
    pattern_type: str
    location: str
    confidence: float  # 0.0 to 1.0
    details: Dict
    symbolic_meaning: str


@dataclass
class StructureAnalysis:
    """Analysis of structure"""
    total_elements: int
    depth: int
    branching_factors: List[int]
    symmetry_detected: bool
    ratios: List[float]
    patterns: List[PatternMatch]


class PatternRecognitionEngine:
    """Detect sacred geometry patterns in various contexts"""

    def __init__(self):
        self.golden_calc = GoldenRatioCalculator()
        self.fib_calc = FibonacciCalculator()
        self.patterns_detected: List[PatternMatch] = []

    def analyze_code_structure(self, code: str, language: str = "python") -> StructureAnalysis:
        """
        Analyze code structure for sacred geometry patterns
        """
        if language == "python":
            return self._analyze_python_code(code)
        else:
            return self._analyze_generic_code(code)

    def _analyze_python_code(self, code: str) -> StructureAnalysis:
        """Analyze Python code structure"""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return StructureAnalysis(0, 0, [], False, [], [])

        # Analyze AST structure
        total_elements = sum(1 for _ in ast.walk(tree))
        depth = self._calculate_ast_depth(tree)
        branching_factors = self._calculate_branching_factors(tree)

        # Extract numeric values
        numbers = self._extract_numbers_from_ast(tree)

        # Calculate ratios between elements
        ratios = self._calculate_ratios(branching_factors)

        # Detect patterns
        patterns = []

        # Check for Fibonacci in numbers
        fib_pattern = self._detect_fibonacci_sequence(numbers)
        if fib_pattern:
            patterns.append(fib_pattern)

        # Check for golden ratio in ratios
        golden_pattern = self._detect_golden_ratio(ratios, "code_structure")
        if golden_pattern:
            patterns.append(golden_pattern)

        # Check for symmetry in structure
        symmetry_detected = self._detect_structural_symmetry(tree)

        # Check for sacred numbers in sizes
        sacred_pattern = self._detect_sacred_numbers(branching_factors)
        if sacred_pattern:
            patterns.append(sacred_pattern)

        return StructureAnalysis(
            total_elements=total_elements,
            depth=depth,
            branching_factors=branching_factors,
            symmetry_detected=symmetry_detected,
            ratios=ratios,
            patterns=patterns,
        )

    def _analyze_generic_code(self, code: str) -> StructureAnalysis:
        """Analyze generic code structure"""
        lines = code.split("\n")
        total_elements = len(lines)

        # Calculate indentation depth as proxy for structure depth
        depths = []
        for line in lines:
            if line.strip():
                leading_spaces = len(line) - len(line.lstrip())
                depths.append(leading_spaces // 2)  # Assume 2-space indents

        depth = max(depths) if depths else 0

        # Extract numbers from code
        numbers = []
        for match in re.finditer(r'\b\d+\b', code):
            numbers.append(int(match.group()))

        # Detect patterns
        patterns = []
        fib_pattern = self._detect_fibonacci_sequence(numbers)
        if fib_pattern:
            patterns.append(fib_pattern)

        return StructureAnalysis(
            total_elements=total_elements,
            depth=depth,
            branching_factors=[],
            symmetry_detected=False,
            ratios=[],
            patterns=patterns,
        )

    def _calculate_ast_depth(self, node: ast.AST, current_depth: int = 0) -> int:
        """Calculate maximum depth of AST"""
        max_depth = current_depth
        for child in ast.iter_child_nodes(node):
            child_depth = self._calculate_ast_depth(child, current_depth + 1)
            max_depth = max(max_depth, child_depth)
        return max_depth

    def _calculate_branching_factors(self, node: ast.AST) -> List[int]:
        """Calculate branching factors at each level"""
        branching = []
        for child in ast.walk(node):
            child_count = sum(1 for _ in ast.iter_child_nodes(child))
            if child_count > 0:
                branching.append(child_count)
        return branching

    def _extract_numbers_from_ast(self, tree: ast.AST) -> List[int]:
        """Extract numeric constants from AST"""
        numbers = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                if isinstance(node.value, float):
                    numbers.append(int(node.value))
                else:
                    numbers.append(node.value)
        return numbers

    def _calculate_ratios(self, values: List[int]) -> List[float]:
        """Calculate ratios between consecutive values"""
        if len(values) < 2:
            return []

        ratios = []
        for i in range(len(values) - 1):
            if values[i] != 0:
                ratio = values[i + 1] / values[i]
                ratios.append(ratio)
        return ratios

    def _detect_fibonacci_sequence(self, numbers: List[int]) -> Optional[PatternMatch]:
        """Detect Fibonacci sequence in numbers"""
        if len(numbers) < 3:
            return None

        # Check for consecutive Fibonacci numbers
        fib_matches = []
        for i in range(len(numbers) - 2):
            if self.fib_calc.is_fibonacci_number(numbers[i]):
                # Check if next numbers also form Fibonacci sequence
                if (
                    self.fib_calc.is_fibonacci_number(numbers[i + 1])
                    and self.fib_calc.is_fibonacci_number(numbers[i + 2])
                ):
                    # Check if they're consecutive in the sequence
                    if numbers[i] + numbers[i + 1] == numbers[i + 2]:
                        fib_matches.append((i, numbers[i : i + 3]))

        if fib_matches:
            confidence = min(len(fib_matches) / (len(numbers) / 3), 1.0)
            return PatternMatch(
                pattern_type="fibonacci_sequence",
                location="numeric_constants",
                confidence=confidence,
                details={"matches": fib_matches, "total_numbers": len(numbers)},
                symbolic_meaning="Natural growth and expansion pattern detected",
            )

        return None

    def _detect_golden_ratio(self, ratios: List[float], location: str) -> Optional[PatternMatch]:
        """Detect golden ratio in ratios"""
        if not ratios:
            return None

        golden_matches = sum(1 for r in ratios if self.golden_calc.is_golden_ratio(r, tolerance=0.1))

        if golden_matches > 0:
            confidence = golden_matches / len(ratios)
            avg_ratio = np.mean(ratios)

            return PatternMatch(
                pattern_type="golden_ratio",
                location=location,
                confidence=confidence,
                details={
                    "matches": golden_matches,
                    "total_ratios": len(ratios),
                    "average_ratio": avg_ratio,
                    "phi": PHI,
                },
                symbolic_meaning="Divine proportion detected - indicates optimal balance and harmony",
            )

        return None

    def _detect_structural_symmetry(self, tree: ast.AST) -> bool:
        """Detect structural symmetry in AST"""
        # Simple heuristic: check if function definitions have similar structures
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

        if len(functions) < 2:
            return False

        # Check if functions have similar number of statements
        statement_counts = [len(node.body) for node in functions]
        if len(set(statement_counts)) == 1:  # All same length
            return True

        # Check for symmetry in counts
        if len(statement_counts) >= 2:
            return statement_counts == statement_counts[::-1]  # Palindromic

        return False

    def _detect_sacred_numbers(self, numbers: List[int]) -> Optional[PatternMatch]:
        """Detect sacred numbers (3, 6, 9, 12, etc.)"""
        sacred = {3, 6, 9, 12, 24, 36, 72, 108, 144, 216, 432, 528, 1080}

        if not numbers:
            return None

        matches = sum(1 for n in numbers if n in sacred)

        if matches > 0:
            confidence = matches / len(numbers)
            matched_numbers = [n for n in numbers if n in sacred]

            return PatternMatch(
                pattern_type="sacred_numbers",
                location="structure_sizes",
                confidence=confidence,
                details={"matched_numbers": matched_numbers, "sacred_set": list(sacred)},
                symbolic_meaning="Sacred numbers detected - represents divine proportions and cosmic harmony",
            )

        return None

    def analyze_data_structure(self, data: Any) -> StructureAnalysis:
        """
        Analyze data structure (dict, list, nested structures)
        """
        if isinstance(data, dict):
            return self._analyze_dict_structure(data)
        elif isinstance(data, list):
            return self._analyze_list_structure(data)
        else:
            return StructureAnalysis(1, 0, [], False, [], [])

    def _analyze_dict_structure(self, data: Dict) -> StructureAnalysis:
        """Analyze dictionary structure"""
        total_elements = self._count_elements(data)
        depth = self._calculate_depth(data)
        branching = self._extract_branching_factors(data)

        ratios = self._calculate_ratios(branching)

        patterns = []

        # Check for golden ratio
        golden_pattern = self._detect_golden_ratio(ratios, "data_structure")
        if golden_pattern:
            patterns.append(golden_pattern)

        # Check for Fibonacci in sizes
        fib_pattern = self._detect_fibonacci_sequence(branching)
        if fib_pattern:
            patterns.append(fib_pattern)

        # Check for symmetry
        symmetry_detected = self._detect_dict_symmetry(data)

        return StructureAnalysis(
            total_elements=total_elements,
            depth=depth,
            branching_factors=branching,
            symmetry_detected=symmetry_detected,
            ratios=ratios,
            patterns=patterns,
        )

    def _analyze_list_structure(self, data: List) -> StructureAnalysis:
        """Analyze list structure"""
        total_elements = len(data)
        depth = self._calculate_depth(data)

        # Extract sizes if nested
        sizes = []
        for item in data:
            if isinstance(item, (list, dict)):
                sizes.append(self._count_elements(item))

        patterns = []

        # Check if list length is Fibonacci
        if self.fib_calc.is_fibonacci_number(len(data)):
            patterns.append(
                PatternMatch(
                    pattern_type="fibonacci_length",
                    location="list_size",
                    confidence=1.0,
                    details={"length": len(data)},
                    symbolic_meaning="List length follows Fibonacci - natural growth pattern",
                )
            )

        # Check for Fibonacci in sizes
        if sizes:
            fib_pattern = self._detect_fibonacci_sequence(sizes)
            if fib_pattern:
                patterns.append(fib_pattern)

        return StructureAnalysis(
            total_elements=total_elements,
            depth=depth,
            branching_factors=sizes,
            symmetry_detected=False,
            ratios=self._calculate_ratios(sizes),
            patterns=patterns,
        )

    def _count_elements(self, obj: Any, visited: Optional[Set] = None) -> int:
        """Count total elements in nested structure"""
        if visited is None:
            visited = set()

        obj_id = id(obj)
        if obj_id in visited:
            return 0

        visited.add(obj_id)
        count = 1

        if isinstance(obj, dict):
            for value in obj.values():
                count += self._count_elements(value, visited)
        elif isinstance(obj, list):
            for item in obj:
                count += self._count_elements(item, visited)

        return count

    def _calculate_depth(self, obj: Any, current_depth: int = 0) -> int:
        """Calculate depth of nested structure"""
        if isinstance(obj, dict):
            if not obj:
                return current_depth
            return max(self._calculate_depth(v, current_depth + 1) for v in obj.values())
        elif isinstance(obj, list):
            if not obj:
                return current_depth
            return max(self._calculate_depth(item, current_depth + 1) for item in obj)
        else:
            return current_depth

    def _extract_branching_factors(self, obj: Any) -> List[int]:
        """Extract branching factors from nested structure"""
        branching = []

        if isinstance(obj, dict):
            branching.append(len(obj))
            for value in obj.values():
                branching.extend(self._extract_branching_factors(value))
        elif isinstance(obj, list):
            branching.append(len(obj))
            for item in obj:
                branching.extend(self._extract_branching_factors(item))

        return [b for b in branching if b > 0]

    def _detect_dict_symmetry(self, data: Dict) -> bool:
        """Detect symmetry in dictionary structure"""
        if not data:
            return False

        # Check if key-value pairs have symmetric properties
        keys = list(data.keys())
        if len(keys) < 2:
            return False

        # Check for palindromic keys
        if keys == keys[::-1]:
            return True

        # Check for symmetric values
        values = list(data.values())
        if isinstance(values[0], (int, float)):
            return values == values[::-1]

        return False

    def detect_patterns_in_metrics(self, metrics: Dict[str, float]) -> List[PatternMatch]:
        """
        Detect sacred geometry patterns in metrics
        """
        patterns = []

        # Extract values
        values = [int(v) if isinstance(v, (int, float)) else 0 for v in metrics.values()]
        ratios = self._calculate_ratios(values)

        # Check for golden ratio
        golden_pattern = self._detect_golden_ratio(ratios, "metrics")
        if golden_pattern:
            patterns.append(golden_pattern)

        # Check for Fibonacci
        fib_pattern = self._detect_fibonacci_sequence(values)
        if fib_pattern:
            patterns.append(fib_pattern)

        # Check for sacred numbers
        sacred_pattern = self._detect_sacred_numbers(values)
        if sacred_pattern:
            patterns.append(sacred_pattern)

        return patterns

    def suggest_optimizations(self, analysis: StructureAnalysis) -> List[Dict]:
        """
        Suggest optimizations based on pattern analysis
        """
        suggestions = []

        # If no golden ratio detected, suggest restructuring
        golden_detected = any(p.pattern_type == "golden_ratio" for p in analysis.patterns)
        if not golden_detected and analysis.branching_factors:
            suggestions.append(
                {
                    "type": "golden_ratio_optimization",
                    "priority": "high",
                    "description": "Restructure to align with golden ratio proportions",
                    "target_ratio": PHI,
                    "current_ratios": analysis.ratios,
                }
            )

        # If no Fibonacci detected, suggest sizes
        fib_detected = any("fibonacci" in p.pattern_type for p in analysis.patterns)
        if not fib_detected and analysis.branching_factors:
            fib_sequence = self.fib_calc.fibonacci_sequence(10)
            suggestions.append(
                {
                    "type": "fibonacci_optimization",
                    "priority": "medium",
                    "description": "Align element counts with Fibonacci sequence",
                    "recommended_sizes": fib_sequence,
                    "current_sizes": analysis.branching_factors,
                }
            )

        # If no symmetry, suggest adding it
        if not analysis.symmetry_detected:
            suggestions.append(
                {
                    "type": "symmetry_optimization",
                    "priority": "medium",
                    "description": "Add structural symmetry for better balance",
                    "symmetry_types": ["rotational", "reflective", "bilateral"],
                }
            )

        return suggestions
