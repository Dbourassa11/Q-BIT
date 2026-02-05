"""
SGPA Core Calculators

Mathematical calculators for sacred geometry, alignment scores,
optimization metrics, and value assessments.
"""

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np


# Constants
PHI = (1 + math.sqrt(5)) / 2  # Golden ratio: ~1.618033988749895
PHI_INVERSE = 1 / PHI  # ~0.618033988749895
EULER = math.e
PI = math.pi


@dataclass
class AlignmentScore:
    """Alignment score with detailed breakdown"""
    overall_score: float  # 0.0 to 1.0
    golden_ratio_alignment: float
    fibonacci_alignment: float
    symmetry_alignment: float
    harmonic_alignment: float
    flow_alignment: float
    details: Dict


@dataclass
class OptimizationResult:
    """Optimization calculation result"""
    current_value: float
    optimal_value: float
    improvement_potential: float  # Percentage
    alignment_gain: float
    recommendations: List[str]


@dataclass
class ValueMetrics:
    """Comprehensive value metrics"""
    total_value_score: float
    data_integrity_value: float
    optimization_value: float
    alignment_value: float
    efficiency_gain_value: float
    time_savings_hours: float
    cost_savings: float
    roi_percentage: float
    payback_period_months: float


class GoldenRatioCalculator:
    """Calculator for golden ratio analysis and optimization"""

    @staticmethod
    def calculate_phi_power(n: int) -> float:
        """Calculate phi raised to power n"""
        return PHI ** n

    @staticmethod
    def is_golden_ratio(ratio: float, tolerance: float = 0.01) -> bool:
        """Check if a ratio approximates the golden ratio"""
        return abs(ratio - PHI) / PHI < tolerance

    @staticmethod
    def golden_ratio_proximity(ratio: float) -> float:
        """Calculate proximity to golden ratio (0.0 = exact, 1.0 = far)"""
        if ratio <= 0:
            return 1.0
        deviation = abs(ratio - PHI) / PHI
        return min(deviation, 1.0)

    @staticmethod
    def optimize_to_golden_ratio(value: float) -> Tuple[float, float]:
        """
        Optimize a value to golden ratio proportions
        Returns: (optimized_value, golden_ratio_complement)
        """
        optimized = value * PHI
        complement = value * PHI_INVERSE
        return optimized, complement

    @staticmethod
    def golden_rectangle_dimensions(area: float) -> Tuple[float, float]:
        """Calculate golden rectangle dimensions for given area"""
        # For a golden rectangle: width/height = phi
        # area = width * height = phi * height^2
        height = math.sqrt(area / PHI)
        width = height * PHI
        return width, height

    @staticmethod
    def golden_spiral_point(theta: float, a: float = 1.0) -> Tuple[float, float]:
        """
        Calculate point on golden spiral
        theta: angle in radians
        a: scaling factor
        """
        r = a * math.exp(PHI_INVERSE * theta)
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        return x, y

    @staticmethod
    def analyze_ratio_distribution(values: List[float]) -> Dict:
        """Analyze how well a distribution follows golden ratio"""
        if len(values) < 2:
            return {"error": "Need at least 2 values"}

        ratios = []
        for i in range(len(values) - 1):
            if values[i] != 0:
                ratio = values[i + 1] / values[i]
                ratios.append(ratio)

        if not ratios:
            return {"error": "No valid ratios"}

        avg_ratio = np.mean(ratios)
        proximity = GoldenRatioCalculator.golden_ratio_proximity(avg_ratio)

        return {
            "average_ratio": avg_ratio,
            "golden_ratio": PHI,
            "proximity_to_golden": 1.0 - proximity,
            "alignment_score": max(0, 1.0 - proximity),
            "ratios": ratios,
        }


class FibonacciCalculator:
    """Calculator for Fibonacci sequence analysis"""

    _cache = {0: 0, 1: 1}

    @classmethod
    def fibonacci(cls, n: int) -> int:
        """Calculate nth Fibonacci number with caching"""
        if n in cls._cache:
            return cls._cache[n]

        if n < 0:
            raise ValueError("n must be non-negative")

        # Calculate using iterative approach for efficiency
        a, b = 0, 1
        for _ in range(n):
            a, b = b, a + b

        cls._cache[n] = a
        return a

    @classmethod
    def fibonacci_sequence(cls, count: int) -> List[int]:
        """Generate Fibonacci sequence up to count numbers"""
        return [cls.fibonacci(i) for i in range(count)]

    @staticmethod
    def is_fibonacci_number(n: int) -> bool:
        """Check if a number is in Fibonacci sequence"""
        # A number is Fibonacci if one of (5*n^2 + 4) or (5*n^2 - 4) is a perfect square
        def is_perfect_square(x):
            s = int(math.sqrt(x))
            return s * s == x

        return is_perfect_square(5 * n * n + 4) or is_perfect_square(5 * n * n - 4)

    @staticmethod
    def closest_fibonacci(n: int) -> Tuple[int, int]:
        """Find closest Fibonacci number to n (returns number and its index)"""
        if n <= 0:
            return 0, 0

        fib_prev, fib_curr = 0, 1
        index = 1

        while fib_curr < n:
            fib_prev, fib_curr = fib_curr, fib_prev + fib_curr
            index += 1

        # Return the closest one
        if abs(fib_curr - n) < abs(fib_prev - n):
            return fib_curr, index
        else:
            return fib_prev, index - 1

    @staticmethod
    def fibonacci_alignment_score(values: List[int]) -> float:
        """Calculate how well values align with Fibonacci sequence"""
        if not values:
            return 0.0

        matches = sum(1 for v in values if FibonacciCalculator.is_fibonacci_number(v))
        return matches / len(values)

    @staticmethod
    def optimize_to_fibonacci(value: int) -> Tuple[int, float]:
        """
        Optimize value to nearest Fibonacci number
        Returns: (fibonacci_number, improvement_score)
        """
        closest_fib, index = FibonacciCalculator.closest_fibonacci(value)
        if value == 0:
            improvement = 0.0
        else:
            improvement = 1.0 - abs(closest_fib - value) / value

        return closest_fib, improvement


class AlignmentCalculator:
    """Calculate alignment scores based on sacred geometry principles"""

    def __init__(self):
        self.golden_calc = GoldenRatioCalculator()
        self.fib_calc = FibonacciCalculator()

    def calculate_symmetry_score(self, structure: Dict) -> float:
        """
        Calculate symmetry alignment score
        Structure should contain symmetry information
        """
        if not structure:
            return 0.0

        # Check for various types of symmetry
        symmetry_types = structure.get("symmetry_types", [])
        symmetry_score = len(symmetry_types) * 0.2  # Base score for having symmetry

        # Check rotational symmetry order
        rotation_order = structure.get("rotation_order", 1)
        if rotation_order in [2, 3, 4, 5, 6, 8, 12]:  # Sacred numbers
            symmetry_score += 0.3

        # Check for reflective symmetry
        if structure.get("has_reflection", False):
            symmetry_score += 0.2

        # Check for bilateral symmetry
        if structure.get("has_bilateral", False):
            symmetry_score += 0.3

        return min(symmetry_score, 1.0)

    def calculate_harmonic_score(self, frequencies: List[float]) -> float:
        """
        Calculate harmonic alignment score
        Sacred frequencies: 432 Hz, 528 Hz, etc.
        """
        if not frequencies:
            return 0.0

        sacred_frequencies = [432, 528, 396, 417, 639, 741, 852, 963]
        tolerance = 0.05  # 5% tolerance

        matches = 0
        for freq in frequencies:
            for sacred in sacred_frequencies:
                if abs(freq - sacred) / sacred < tolerance:
                    matches += 1
                    break

        return min(matches / len(frequencies), 1.0)

    def calculate_flow_score(self, metrics: Dict) -> float:
        """
        Calculate flow alignment score based on efficiency and coherence
        """
        efficiency = metrics.get("efficiency", 0.5)
        coherence = metrics.get("coherence", 0.5)
        balance = metrics.get("balance", 0.5)

        # Flow is optimal when all three are high and balanced
        flow_score = (efficiency + coherence + balance) / 3

        # Bonus for balance (all three similar)
        variance = np.var([efficiency, coherence, balance])
        if variance < 0.05:  # Low variance means good balance
            flow_score = min(flow_score * 1.2, 1.0)

        return flow_score

    def calculate_overall_alignment(
        self,
        ratios: List[float],
        values: List[int],
        structure: Dict,
        frequencies: Optional[List[float]] = None,
        metrics: Optional[Dict] = None,
    ) -> AlignmentScore:
        """
        Calculate comprehensive alignment score
        """
        # Golden ratio alignment
        ratio_analysis = self.golden_calc.analyze_ratio_distribution(ratios) if ratios else {}
        golden_alignment = ratio_analysis.get("alignment_score", 0.0)

        # Fibonacci alignment
        fib_alignment = self.fib_calc.fibonacci_alignment_score(values) if values else 0.0

        # Symmetry alignment
        symmetry_alignment = self.calculate_symmetry_score(structure)

        # Harmonic alignment
        harmonic_alignment = self.calculate_harmonic_score(frequencies) if frequencies else 0.5

        # Flow alignment
        flow_alignment = self.calculate_flow_score(metrics) if metrics else 0.5

        # Calculate weighted overall score
        weights = {
            "golden": 0.25,
            "fibonacci": 0.20,
            "symmetry": 0.20,
            "harmonic": 0.15,
            "flow": 0.20,
        }

        overall = (
            golden_alignment * weights["golden"]
            + fib_alignment * weights["fibonacci"]
            + symmetry_alignment * weights["symmetry"]
            + harmonic_alignment * weights["harmonic"]
            + flow_alignment * weights["flow"]
        )

        return AlignmentScore(
            overall_score=overall,
            golden_ratio_alignment=golden_alignment,
            fibonacci_alignment=fib_alignment,
            symmetry_alignment=symmetry_alignment,
            harmonic_alignment=harmonic_alignment,
            flow_alignment=flow_alignment,
            details={
                "ratio_analysis": ratio_analysis,
                "weights": weights,
            },
        )


class ValueCalculator:
    """Calculate true value metrics and ROI"""

    def calculate_data_integrity_value(
        self,
        integrity_score: float,
        data_volume: int,
        error_cost_per_record: float = 10.0,
    ) -> float:
        """
        Calculate value of data integrity improvements
        """
        # Value = (improvement in integrity) * volume * cost per error
        integrity_improvement = max(0, integrity_score - 0.5)  # Above baseline
        error_reduction = integrity_improvement * data_volume
        value = error_reduction * error_cost_per_record
        return value

    def calculate_optimization_value(
        self,
        baseline_efficiency: float,
        optimized_efficiency: float,
        annual_operations: int,
        cost_per_operation: float,
    ) -> float:
        """
        Calculate value of optimization improvements
        """
        efficiency_gain = optimized_efficiency - baseline_efficiency
        operations_saved = annual_operations * efficiency_gain
        value = operations_saved * cost_per_operation
        return value

    def calculate_alignment_value(
        self,
        alignment_score: float,
        team_size: int,
        avg_salary: float,
        productivity_multiplier: float = 0.15,
    ) -> float:
        """
        Calculate value of sacred geometry alignment
        Better alignment = better flow = higher productivity
        """
        # Alignment above 0.7 provides productivity benefits
        if alignment_score < 0.7:
            return 0.0

        alignment_benefit = (alignment_score - 0.7) / 0.3  # Normalize to 0-1
        productivity_gain = alignment_benefit * productivity_multiplier
        annual_value = team_size * avg_salary * productivity_gain
        return annual_value

    def calculate_time_savings(
        self,
        baseline_time: float,
        optimized_time: float,
        frequency_per_month: int,
    ) -> float:
        """
        Calculate time savings in hours per month
        """
        time_saved_per_operation = baseline_time - optimized_time
        monthly_savings = time_saved_per_operation * frequency_per_month
        return monthly_savings

    def calculate_roi(
        self,
        implementation_cost: float,
        annual_benefit: float,
    ) -> Tuple[float, float]:
        """
        Calculate ROI and payback period
        Returns: (roi_percentage, payback_period_months)
        """
        if implementation_cost == 0:
            return 0.0, 0.0

        roi_percentage = (annual_benefit / implementation_cost) * 100
        payback_period_months = (implementation_cost / annual_benefit) * 12 if annual_benefit > 0 else float("inf")

        return roi_percentage, payback_period_months

    def calculate_comprehensive_value(
        self,
        integrity_score: float,
        alignment_score: float,
        efficiency_gain: float,
        data_volume: int,
        team_size: int,
        avg_salary: float,
        annual_operations: int,
        cost_per_operation: float,
        implementation_cost: float,
    ) -> ValueMetrics:
        """
        Calculate comprehensive value metrics
        """
        # Individual value components
        integrity_value = self.calculate_data_integrity_value(integrity_score, data_volume)

        alignment_value = self.calculate_alignment_value(alignment_score, team_size, avg_salary)

        optimization_value = self.calculate_optimization_value(
            baseline_efficiency=0.7,  # Assume baseline
            optimized_efficiency=0.7 + efficiency_gain,
            annual_operations=annual_operations,
            cost_per_operation=cost_per_operation,
        )

        # Efficiency gain value (time savings converted to cost)
        time_savings = efficiency_gain * annual_operations
        efficiency_value = time_savings * cost_per_operation

        # Total annual benefit
        annual_benefit = integrity_value + alignment_value + optimization_value + efficiency_value

        # Cost savings (sum of tangible savings)
        cost_savings = integrity_value + optimization_value

        # ROI calculation
        roi_percentage, payback_months = self.calculate_roi(implementation_cost, annual_benefit)

        # Total value score (normalized 0-1)
        # Scale based on implementation cost as baseline
        if implementation_cost > 0:
            value_score = min(annual_benefit / (implementation_cost * 2), 1.0)
        else:
            value_score = 0.8  # Default good score if no cost

        return ValueMetrics(
            total_value_score=value_score,
            data_integrity_value=integrity_value,
            optimization_value=optimization_value,
            alignment_value=alignment_value,
            efficiency_gain_value=efficiency_value,
            time_savings_hours=time_savings,
            cost_savings=cost_savings,
            roi_percentage=roi_percentage,
            payback_period_months=payback_months,
        )


class SGPACalculator:
    """Main SGPA calculator combining all calculation capabilities"""

    def __init__(self):
        self.golden_calc = GoldenRatioCalculator()
        self.fibonacci_calc = FibonacciCalculator()
        self.alignment_calc = AlignmentCalculator()
        self.value_calc = ValueCalculator()

    def analyze_system(self, system_data: Dict) -> Dict:
        """
        Comprehensive system analysis
        """
        # Extract data from system
        ratios = system_data.get("ratios", [])
        values = system_data.get("values", [])
        structure = system_data.get("structure", {})
        frequencies = system_data.get("frequencies")
        metrics = system_data.get("metrics")

        # Calculate alignment
        alignment = self.alignment_calc.calculate_overall_alignment(
            ratios, values, structure, frequencies, metrics
        )

        # Optimize to sacred geometry
        optimizations = []
        for value in values[:10]:  # Limit to first 10 for performance
            opt_fib, improvement = self.fibonacci_calc.optimize_to_fibonacci(value)
            optimizations.append(
                {"original": value, "optimized": opt_fib, "improvement": improvement}
            )

        return {
            "alignment_score": alignment,
            "optimizations": optimizations,
            "recommendations": self._generate_recommendations(alignment),
        }

    def _generate_recommendations(self, alignment: AlignmentScore) -> List[str]:
        """Generate recommendations based on alignment scores"""
        recommendations = []

        if alignment.golden_ratio_alignment < 0.5:
            recommendations.append(
                "Consider restructuring proportions to align with golden ratio (φ ≈ 1.618)"
            )

        if alignment.fibonacci_alignment < 0.5:
            recommendations.append(
                "Optimize sizing and scaling to Fibonacci sequence numbers (1, 2, 3, 5, 8, 13, 21...)"
            )

        if alignment.symmetry_alignment < 0.5:
            recommendations.append("Increase structural symmetry for better balance and coherence")

        if alignment.harmonic_alignment < 0.5:
            recommendations.append(
                "Align frequencies and rhythms with sacred harmonic ratios (432Hz, 528Hz)"
            )

        if alignment.flow_alignment < 0.5:
            recommendations.append(
                "Improve flow by balancing efficiency, coherence, and structural balance"
            )

        if alignment.overall_score > 0.8:
            recommendations.append("Excellent sacred geometry alignment! Maintain current patterns.")

        return recommendations
