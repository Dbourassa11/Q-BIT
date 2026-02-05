"""
SGPA Optimizer

Optimizes systems based on sacred geometry principles.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .calculators import AlignmentScore, FibonacciCalculator, GoldenRatioCalculator, PHI


@dataclass
class OptimizationRecommendation:
    """A specific optimization recommendation"""
    category: str
    priority: int  # 1 = highest
    title: str
    description: str
    current_value: Any
    optimal_value: Any
    expected_improvement: float  # Percentage
    implementation_steps: List[str]
    sacred_principle: str


@dataclass
class OptimizationPlan:
    """Complete optimization plan"""
    current_alignment_score: float
    projected_alignment_score: float
    total_improvement_potential: float
    recommendations: List[OptimizationRecommendation]
    quick_wins: List[OptimizationRecommendation]
    strategic_initiatives: List[OptimizationRecommendation]


class SGPAOptimizer:
    """Optimize systems using sacred geometry principles"""

    def __init__(self):
        self.golden_calc = GoldenRatioCalculator()
        self.fib_calc = FibonacciCalculator()

    def optimize_value(self, value: float, target_pattern: str = "golden_ratio") -> Tuple[float, str]:
        """
        Optimize a single value to sacred geometry pattern
        Returns: (optimized_value, reasoning)
        """
        if target_pattern == "golden_ratio":
            # Find nearest golden ratio multiple
            multiplier = round(value / PHI)
            if multiplier == 0:
                multiplier = 1
            optimized = multiplier * PHI
            reasoning = f"Optimized to {multiplier}φ ≈ {optimized:.3f} (golden ratio multiple)"
            return optimized, reasoning

        elif target_pattern == "fibonacci":
            # Find nearest Fibonacci number
            int_value = int(value)
            optimized_fib, index = self.fib_calc.closest_fibonacci(int_value)
            reasoning = f"Optimized to Fibonacci F({index}) = {optimized_fib}"
            return float(optimized_fib), reasoning

        elif target_pattern == "sacred_number":
            # Round to nearest sacred number
            sacred_numbers = [3, 5, 7, 8, 12, 13, 21, 24, 33, 34, 55, 89, 144]
            closest = min(sacred_numbers, key=lambda x: abs(x - value))
            reasoning = f"Optimized to sacred number {closest}"
            return float(closest), reasoning

        return value, "No optimization needed"

    def optimize_proportions(
        self, dimensions: List[float], target: str = "golden_ratio"
    ) -> List[float]:
        """
        Optimize proportions to sacred geometry ratios
        """
        if not dimensions or len(dimensions) < 2:
            return dimensions

        optimized = []

        if target == "golden_ratio":
            # Make each dimension relate to previous by golden ratio
            base = dimensions[0]
            optimized.append(base)

            for i in range(1, len(dimensions)):
                # Should be either base * PHI or base / PHI
                if dimensions[i] > base:
                    optimized.append(base * PHI)
                    base = base * PHI
                else:
                    optimized.append(base / PHI)
                    base = base / PHI

        elif target == "fibonacci":
            # Map to Fibonacci sequence
            fib_sequence = self.fib_calc.fibonacci_sequence(len(dimensions))
            # Scale to match approximate magnitude
            scale = dimensions[0] / fib_sequence[0] if fib_sequence[0] != 0 else 1
            optimized = [f * scale for f in fib_sequence]

        return optimized

    def optimize_structure(self, structure: Dict) -> Dict:
        """
        Optimize a dictionary structure for sacred geometry alignment
        """
        optimized = {}

        for key, value in structure.items():
            if isinstance(value, (int, float)):
                # Optimize numeric values
                opt_value, _ = self.optimize_value(value)
                optimized[key] = opt_value
            elif isinstance(value, list):
                # Optimize list lengths to Fibonacci
                if len(value) > 0:
                    target_length, _ = self.fib_calc.closest_fibonacci(len(value))
                    # Don't actually truncate/extend, just recommend
                    optimized[key] = value
                else:
                    optimized[key] = value
            elif isinstance(value, dict):
                # Recursively optimize nested dicts
                optimized[key] = self.optimize_structure(value)
            else:
                optimized[key] = value

        return optimized

    def create_optimization_plan(
        self, current_alignment: AlignmentScore, analysis_data: Dict
    ) -> OptimizationPlan:
        """
        Create comprehensive optimization plan
        """
        recommendations = []

        # 1. Golden Ratio Optimizations
        if current_alignment.golden_ratio_alignment < 0.7:
            recommendations.append(
                OptimizationRecommendation(
                    category="proportions",
                    priority=1,
                    title="Optimize Proportions to Golden Ratio",
                    description="Restructure key proportions to align with the golden ratio (φ ≈ 1.618) "
                    "for optimal balance and aesthetic harmony",
                    current_value=current_alignment.golden_ratio_alignment,
                    optimal_value=0.9,
                    expected_improvement=30.0,
                    implementation_steps=[
                        "Identify all proportion ratios in the system",
                        "Calculate current deviation from golden ratio",
                        "Adjust dimensions to match φ or φ² or φ³",
                        "Test and validate new proportions",
                        "Document golden ratio applications",
                    ],
                    sacred_principle="Golden Ratio - Divine Proportion of perfect balance",
                )
            )

        # 2. Fibonacci Optimizations
        if current_alignment.fibonacci_alignment < 0.7:
            recommendations.append(
                OptimizationRecommendation(
                    category="sizing",
                    priority=1,
                    title="Align Sizes with Fibonacci Sequence",
                    description="Optimize element counts, sizes, and scaling factors to Fibonacci numbers "
                    "for natural, organic growth patterns",
                    current_value=current_alignment.fibonacci_alignment,
                    optimal_value=0.85,
                    expected_improvement=25.0,
                    implementation_steps=[
                        "Audit all size configurations (arrays, chunks, batches, etc.)",
                        "Identify nearest Fibonacci numbers",
                        "Refactor to use Fibonacci sizing: 1, 2, 3, 5, 8, 13, 21, 34, 55, 89...",
                        "Apply to pagination, caching, and data structures",
                        "Measure performance improvements",
                    ],
                    sacred_principle="Fibonacci - Natural growth and sustainable expansion",
                )
            )

        # 3. Symmetry Optimizations
        if current_alignment.symmetry_alignment < 0.6:
            recommendations.append(
                OptimizationRecommendation(
                    category="structure",
                    priority=2,
                    title="Introduce Structural Symmetry",
                    description="Add symmetrical patterns to improve balance, reduce cognitive load, "
                    "and enhance system coherence",
                    current_value=current_alignment.symmetry_alignment,
                    optimal_value=0.8,
                    expected_improvement=20.0,
                    implementation_steps=[
                        "Map current system structure",
                        "Identify asymmetrical components",
                        "Design symmetrical alternatives (bilateral, rotational, or reflective)",
                        "Implement symmetry in APIs, data structures, and workflows",
                        "Validate improved balance and coherence",
                    ],
                    sacred_principle="Symmetry - Universal principle of balance and harmony",
                )
            )

        # 4. Harmonic Optimizations
        if current_alignment.harmonic_alignment < 0.7:
            recommendations.append(
                OptimizationRecommendation(
                    category="timing",
                    priority=3,
                    title="Align Frequencies and Rhythms",
                    description="Synchronize timing, intervals, and frequencies with sacred harmonic ratios",
                    current_value=current_alignment.harmonic_alignment,
                    optimal_value=0.85,
                    expected_improvement=15.0,
                    implementation_steps=[
                        "Identify all timed processes (polling, cron jobs, timeouts)",
                        "Calculate current frequencies",
                        "Adjust to harmonic intervals (multiples of sacred numbers)",
                        "Synchronize related processes",
                        "Monitor for improved flow and reduced conflicts",
                    ],
                    sacred_principle="Harmonic Resonance - Frequencies in sacred alignment",
                )
            )

        # 5. Flow Optimizations
        if current_alignment.flow_alignment < 0.7:
            recommendations.append(
                OptimizationRecommendation(
                    category="workflow",
                    priority=2,
                    title="Optimize System Flow",
                    description="Improve efficiency, coherence, and balance in system workflows",
                    current_value=current_alignment.flow_alignment,
                    optimal_value=0.9,
                    expected_improvement=25.0,
                    implementation_steps=[
                        "Map current workflows and data flows",
                        "Identify bottlenecks and friction points",
                        "Apply sacred geometry to workflow design",
                        "Create balanced, spiral-like progressive flows",
                        "Implement feedback loops for self-optimization",
                    ],
                    sacred_principle="Sacred Flow - Natural, effortless movement like water",
                )
            )

        # Categorize into quick wins vs strategic initiatives
        quick_wins = [r for r in recommendations if r.priority == 1 and r.expected_improvement >= 20]
        strategic = [r for r in recommendations if r.priority >= 2 or r.expected_improvement > 30]

        # Calculate projected improvement
        total_improvement = sum(r.expected_improvement for r in recommendations)
        avg_improvement = total_improvement / len(recommendations) if recommendations else 0

        projected_score = min(current_alignment.overall_score + (avg_improvement / 100), 1.0)

        return OptimizationPlan(
            current_alignment_score=current_alignment.overall_score,
            projected_alignment_score=projected_score,
            total_improvement_potential=avg_improvement,
            recommendations=sorted(recommendations, key=lambda x: x.priority),
            quick_wins=quick_wins,
            strategic_initiatives=strategic,
        )

    def generate_optimization_matrix(self, plan: OptimizationPlan) -> List[List[Dict]]:
        """
        Generate optimization matrix for visualization
        Matrix dimensions: [category][priority]
        """
        categories = ["proportions", "sizing", "structure", "timing", "workflow"]
        priorities = [1, 2, 3]

        matrix = []
        for category in categories:
            row = []
            for priority in priorities:
                # Find recommendations matching this cell
                matching = [
                    r
                    for r in plan.recommendations
                    if r.category == category and r.priority == priority
                ]

                if matching:
                    row.append(
                        {
                            "has_recommendation": True,
                            "count": len(matching),
                            "recommendations": matching,
                            "total_improvement": sum(r.expected_improvement for r in matching),
                        }
                    )
                else:
                    row.append({"has_recommendation": False, "count": 0})

            matrix.append(row)

        return matrix

    def create_swarm_optimization_hierarchy(
        self, optimization_plan: OptimizationPlan
    ) -> Dict[str, List[Dict]]:
        """
        Create hierarchical swarm optimization tasks
        Organizes optimizations for parallel execution by swarm agents
        """
        hierarchy = {
            "foundation": [],  # Must complete first
            "core": [],  # Can run in parallel after foundation
            "enhancement": [],  # Can run after core
            "integration": [],  # Final integration phase
        }

        for rec in optimization_plan.recommendations:
            task = {
                "title": rec.title,
                "category": rec.category,
                "priority": rec.priority,
                "expected_improvement": rec.expected_improvement,
                "steps": rec.implementation_steps,
                "agent_capability_required": self._map_to_agent_capability(rec.category),
            }

            # Categorize by execution phase
            if rec.priority == 1 and rec.category in ["proportions", "sizing"]:
                hierarchy["foundation"].append(task)
            elif rec.priority == 1:
                hierarchy["core"].append(task)
            elif rec.priority == 2:
                hierarchy["enhancement"].append(task)
            else:
                hierarchy["integration"].append(task)

        return hierarchy

    def _map_to_agent_capability(self, category: str) -> str:
        """Map optimization category to agent capability"""
        mapping = {
            "proportions": "ARCHITECTURE",
            "sizing": "OPTIMIZATION",
            "structure": "ARCHITECTURE",
            "timing": "OPTIMIZATION",
            "workflow": "OPTIMIZATION",
        }
        return mapping.get(category, "OPTIMIZATION")

    def calculate_roi_for_optimization(
        self, recommendation: OptimizationRecommendation, system_context: Dict
    ) -> Dict:
        """
        Calculate ROI for a specific optimization
        """
        # Extract context
        team_size = system_context.get("team_size", 5)
        avg_salary = system_context.get("avg_salary", 100000)
        annual_operations = system_context.get("annual_operations", 10000)

        # Estimate implementation cost
        # Based on priority and complexity
        base_hours = {1: 40, 2: 80, 3: 120}  # Hours by priority
        hourly_rate = avg_salary / 2080  # Annual to hourly
        implementation_cost = base_hours.get(recommendation.priority, 80) * hourly_rate

        # Estimate annual benefit
        # Improvement percentage applied to productivity/efficiency
        productivity_gain = recommendation.expected_improvement / 100
        annual_benefit = (
            team_size * avg_salary * productivity_gain * 0.2
        )  # Conservative 20% of productivity

        # Calculate ROI
        if implementation_cost > 0:
            roi_percentage = (annual_benefit / implementation_cost) * 100
            payback_months = (implementation_cost / annual_benefit) * 12 if annual_benefit > 0 else 999
        else:
            roi_percentage = 0
            payback_months = 0

        return {
            "implementation_cost": implementation_cost,
            "annual_benefit": annual_benefit,
            "roi_percentage": roi_percentage,
            "payback_months": payback_months,
            "net_benefit_3_years": (annual_benefit * 3) - implementation_cost,
        }
