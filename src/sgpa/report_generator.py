"""
SGPA Report Generator

Generates comprehensive client reports with visualizations and recommendations.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional

from .calculators import AlignmentScore, ValueMetrics
from .optimizer import OptimizationPlan
from .symbolic_translator import SymbolicTranslator
from .templates import SGPATemplateLibrary
from .visualizer import SGPAVisualizer


class SGPAReportGenerator:
    """Generate comprehensive SGPA reports for clients"""

    def __init__(self):
        self.visualizer = SGPAVisualizer()
        self.symbolic_translator = SymbolicTranslator()
        self.template_library = SGPATemplateLibrary()

    def generate_executive_summary(
        self, alignment_score: AlignmentScore, value_metrics: ValueMetrics
    ) -> Dict:
        """Generate executive summary"""
        # Get symbolic interpretation
        interpretation = self.symbolic_translator.translate_alignment_score(
            alignment_score.overall_score
        )

        summary = {
            "overall_assessment": interpretation.meaning,
            "sacred_alignment_score": round(alignment_score.overall_score * 100, 1),
            "alignment_grade": self._get_alignment_grade(alignment_score.overall_score),
            "key_strengths": self._identify_strengths(alignment_score),
            "key_opportunities": self._identify_opportunities(alignment_score),
            "estimated_value": {
                "annual_benefit": round(value_metrics.cost_savings, 2),
                "roi_percentage": round(value_metrics.roi_percentage, 1),
                "payback_months": round(value_metrics.payback_period_months, 1),
            },
            "primary_recommendation": interpretation.transformation_potential,
        }

        return summary

    def _get_alignment_grade(self, score: float) -> str:
        """Get letter grade for alignment score"""
        if score >= 0.9:
            return "A+ (Sacred)"
        elif score >= 0.8:
            return "A (Excellent)"
        elif score >= 0.7:
            return "B+ (Very Good)"
        elif score >= 0.6:
            return "B (Good)"
        elif score >= 0.5:
            return "C+ (Fair)"
        elif score >= 0.4:
            return "C (Needs Improvement)"
        else:
            return "D (Critical)"

    def _identify_strengths(self, alignment: AlignmentScore) -> List[str]:
        """Identify key strengths from alignment scores"""
        strengths = []

        if alignment.golden_ratio_alignment >= 0.7:
            strengths.append(
                f"Strong golden ratio alignment ({alignment.golden_ratio_alignment:.1%}) - "
                "demonstrates natural harmony and balance"
            )

        if alignment.fibonacci_alignment >= 0.7:
            strengths.append(
                f"Good Fibonacci sequence alignment ({alignment.fibonacci_alignment:.1%}) - "
                "shows organic growth patterns"
            )

        if alignment.symmetry_alignment >= 0.7:
            strengths.append(
                f"Excellent structural symmetry ({alignment.symmetry_alignment:.1%}) - "
                "indicates balanced design"
            )

        if alignment.harmonic_alignment >= 0.7:
            strengths.append(
                f"Strong harmonic resonance ({alignment.harmonic_alignment:.1%}) - "
                "aligned with sacred frequencies"
            )

        if alignment.flow_alignment >= 0.7:
            strengths.append(
                f"Optimal flow characteristics ({alignment.flow_alignment:.1%}) - "
                "efficient and coherent operations"
            )

        if not strengths:
            strengths.append("Foundation established - ready for sacred geometry optimization")

        return strengths

    def _identify_opportunities(self, alignment: AlignmentScore) -> List[str]:
        """Identify key improvement opportunities"""
        opportunities = []

        if alignment.golden_ratio_alignment < 0.6:
            opportunities.append(
                f"Golden ratio optimization ({alignment.golden_ratio_alignment:.1%} → 90%+) - "
                "highest impact opportunity"
            )

        if alignment.fibonacci_alignment < 0.6:
            opportunities.append(
                f"Fibonacci sequence alignment ({alignment.fibonacci_alignment:.1%} → 85%+) - "
                "natural scaling improvements"
            )

        if alignment.symmetry_alignment < 0.6:
            opportunities.append(
                f"Structural symmetry enhancement ({alignment.symmetry_alignment:.1%} → 80%+) - "
                "balance and coherence"
            )

        if alignment.flow_alignment < 0.6:
            opportunities.append(
                f"Flow optimization ({alignment.flow_alignment:.1%} → 90%+) - "
                "efficiency and performance gains"
            )

        return opportunities[:3]  # Top 3 opportunities

    def generate_detailed_findings(
        self, alignment: AlignmentScore, patterns_detected: List[Dict]
    ) -> Dict:
        """Generate detailed findings section"""
        findings = {
            "sacred_geometry_alignment": {
                "overall_score": round(alignment.overall_score, 3),
                "dimension_scores": {
                    "golden_ratio": round(alignment.golden_ratio_alignment, 3),
                    "fibonacci_sequence": round(alignment.fibonacci_alignment, 3),
                    "symmetry": round(alignment.symmetry_alignment, 3),
                    "harmonic_resonance": round(alignment.harmonic_alignment, 3),
                    "flow_optimization": round(alignment.flow_alignment, 3),
                },
                "interpretation": self.symbolic_translator.translate_alignment_score(
                    alignment.overall_score
                ).__dict__,
            },
            "patterns_detected": [
                {
                    "pattern": p.get("type"),
                    "confidence": round(p.get("confidence", 0), 2),
                    "location": p.get("location"),
                    "interpretation": self.symbolic_translator.translate_pattern(
                        p.get("type", "")
                    ).__dict__
                    if self.symbolic_translator.translate_pattern(p.get("type", ""))
                    else None,
                }
                for p in patterns_detected
            ],
            "analysis_methodology": {
                "approach": "Sacred Geometric Principles of Alignment (SGPA)",
                "frameworks_used": [
                    "Golden Ratio (φ ≈ 1.618) Analysis",
                    "Fibonacci Sequence Pattern Recognition",
                    "Sacred Symmetry Detection",
                    "Harmonic Frequency Alignment",
                    "Flow Optimization Metrics",
                ],
                "data_sources_analyzed": "System architecture, data structures, workflows, and metrics",
            },
        }

        return findings

    def generate_implementation_roadmap(
        self, optimization_plan: OptimizationPlan
    ) -> Dict:
        """Generate implementation roadmap"""
        # Organize by phase
        roadmap = {
            "overview": {
                "current_alignment": round(optimization_plan.current_alignment_score * 100, 1),
                "target_alignment": round(optimization_plan.projected_alignment_score * 100, 1),
                "total_improvement": round(optimization_plan.total_improvement_potential, 1),
                "recommended_approach": "Phased implementation following sacred geometry principles",
            },
            "phases": [],
        }

        # Phase 1: Quick Wins
        if optimization_plan.quick_wins:
            roadmap["phases"].append(
                {
                    "phase": 1,
                    "name": "Foundation - Quick Wins",
                    "duration": "2-3 weeks",
                    "sacred_principle": "Begin with foundation (4-fold stability)",
                    "initiatives": [
                        {
                            "title": rec.title,
                            "expected_improvement": f"{rec.expected_improvement}%",
                            "steps": rec.implementation_steps,
                        }
                        for rec in optimization_plan.quick_wins
                    ],
                    "expected_alignment_gain": sum(
                        r.expected_improvement for r in optimization_plan.quick_wins
                    )
                    / 100,
                }
            )

        # Phase 2: Core Optimizations
        core_recommendations = [
            r
            for r in optimization_plan.recommendations
            if r.priority == 1 and r not in optimization_plan.quick_wins
        ]
        if core_recommendations:
            roadmap["phases"].append(
                {
                    "phase": 2,
                    "name": "Core Alignment",
                    "duration": "4-5 weeks",
                    "sacred_principle": "Build harmonious structure (6-fold efficiency)",
                    "initiatives": [
                        {
                            "title": rec.title,
                            "expected_improvement": f"{rec.expected_improvement}%",
                            "steps": rec.implementation_steps,
                        }
                        for rec in core_recommendations
                    ],
                }
            )

        # Phase 3: Strategic Initiatives
        if optimization_plan.strategic_initiatives:
            roadmap["phases"].append(
                {
                    "phase": 3,
                    "name": "Strategic Optimization",
                    "duration": "5-8 weeks",
                    "sacred_principle": "Achieve sacred completion (7-fold mastery)",
                    "initiatives": [
                        {
                            "title": rec.title,
                            "expected_improvement": f"{rec.expected_improvement}%",
                            "steps": rec.implementation_steps,
                        }
                        for rec in optimization_plan.strategic_initiatives
                    ],
                }
            )

        # Phase 4: Integration
        roadmap["phases"].append(
            {
                "phase": 4,
                "name": "Integration & Transcendence",
                "duration": "2-3 weeks",
                "sacred_principle": "Unify all elements (return to unity)",
                "initiatives": [
                    {
                        "title": "System Integration",
                        "description": "Integrate all optimizations into unified whole",
                        "steps": [
                            "Test all optimizations together",
                            "Balance competing priorities",
                            "Fine-tune for optimal harmony",
                            "Implement continuous alignment monitoring",
                        ],
                    }
                ],
            }
        )

        # Timeline
        total_weeks = sum(
            int(phase.get("duration", "0 weeks").split("-")[0]) for phase in roadmap["phases"]
        )
        roadmap["total_duration"] = f"{total_weeks} weeks (approximately {total_weeks // 4} months)"

        return roadmap

    def generate_value_assessment(
        self, value_metrics: ValueMetrics, optimization_plan: OptimizationPlan
    ) -> Dict:
        """Generate value assessment section"""
        # Calculate pricing using value formula
        service_price = self._calculate_service_price(
            value_metrics, optimization_plan.current_alignment_score
        )

        assessment = {
            "value_delivered": {
                "total_annual_benefit": round(
                    value_metrics.cost_savings + value_metrics.efficiency_gain_value, 2
                ),
                "data_integrity_value": round(value_metrics.data_integrity_value, 2),
                "optimization_value": round(value_metrics.optimization_value, 2),
                "alignment_value": round(value_metrics.alignment_value, 2),
                "efficiency_gains": round(value_metrics.efficiency_gain_value, 2),
            },
            "time_savings": {
                "hours_per_month": round(value_metrics.time_savings_hours, 1),
                "annual_hours": round(value_metrics.time_savings_hours * 12, 1),
                "equivalent_fte": round(value_metrics.time_savings_hours * 12 / 2080, 2),
            },
            "roi_analysis": {
                "service_investment": round(service_price, 2),
                "first_year_benefit": round(
                    value_metrics.cost_savings + value_metrics.efficiency_gain_value, 2
                ),
                "roi_percentage": round(value_metrics.roi_percentage, 1),
                "payback_period_months": round(value_metrics.payback_period_months, 1),
                "3_year_net_benefit": round(
                    (value_metrics.cost_savings + value_metrics.efficiency_gain_value) * 3
                    - service_price,
                    2,
                ),
            },
            "service_pricing": {
                "total_price": round(service_price, 2),
                "pricing_model": "Value-based pricing aligned with sacred geometry principles",
                "value_capture_ratio": "25-35% of value delivered",
                "payment_terms": "Payment aligned with value realization milestones",
            },
        }

        return assessment

    def _calculate_service_price(self, value_metrics: ValueMetrics, alignment_score: float) -> float:
        """Calculate service price using sacred geometry value formula"""
        total_value = (
            value_metrics.data_integrity_value
            + value_metrics.optimization_value
            + value_metrics.alignment_value
            + value_metrics.efficiency_gain_value
        )

        # Value capture ratio based on alignment tier
        if alignment_score >= 0.85:
            value_capture = 0.45  # Transcendent
        elif alignment_score >= 0.7:
            value_capture = 0.35  # Sacred
        elif alignment_score >= 0.5:
            value_capture = 0.25  # Harmony
        else:
            value_capture = 0.15  # Foundation

        # Alignment multiplier
        alignment_multiplier = 1 + max(0, (alignment_score - 0.5) * 0.5)

        service_price = total_value * value_capture * alignment_multiplier

        return service_price

    def generate_complete_report(
        self,
        client_info: Dict,
        alignment: AlignmentScore,
        value_metrics: ValueMetrics,
        optimization_plan: OptimizationPlan,
        patterns_detected: List[Dict],
        additional_data: Optional[Dict] = None,
    ) -> Dict:
        """Generate complete SGPA report"""
        additional_data = additional_data or {}

        report = {
            "metadata": {
                "report_type": "Comprehensive SGPA Analysis & Optimization Report",
                "client": client_info,
                "generated_at": datetime.utcnow().isoformat(),
                "report_version": "1.0",
                "sacred_geometry_framework": "SGPA v1.0",
            },
            "executive_summary": self.generate_executive_summary(alignment, value_metrics),
            "detailed_findings": self.generate_detailed_findings(alignment, patterns_detected),
            "optimization_recommendations": {
                "overview": {
                    "total_recommendations": len(optimization_plan.recommendations),
                    "quick_wins": len(optimization_plan.quick_wins),
                    "strategic_initiatives": len(optimization_plan.strategic_initiatives),
                },
                "recommendations": [
                    {
                        "category": rec.category,
                        "priority": rec.priority,
                        "title": rec.title,
                        "description": rec.description,
                        "current_value": rec.current_value,
                        "optimal_value": rec.optimal_value,
                        "expected_improvement": f"{rec.expected_improvement}%",
                        "implementation_steps": rec.implementation_steps,
                        "sacred_principle": rec.sacred_principle,
                    }
                    for rec in optimization_plan.recommendations
                ],
            },
            "implementation_roadmap": self.generate_implementation_roadmap(optimization_plan),
            "value_assessment": self.generate_value_assessment(value_metrics, optimization_plan),
            "templates_and_protocols": {
                "included_templates": list(self.template_library.get_all_templates().keys()),
                "access": "All templates and protocols provided as part of engagement",
            },
            "appendix": {
                "sacred_geometry_primer": {
                    "golden_ratio": "φ ≈ 1.618 - The divine proportion found throughout nature",
                    "fibonacci_sequence": "1, 1, 2, 3, 5, 8, 13, 21... - Natural growth pattern",
                    "sacred_symmetry": "Balance and harmony through geometric patterns",
                    "harmonic_resonance": "Alignment with natural frequencies",
                },
                "methodology": "Comprehensive analysis using sacred geometric principles",
                "tools_used": [
                    "SGPA Calculator",
                    "Pattern Recognition Engine",
                    "Symbolic Translator",
                    "Optimization Engine",
                    "Value Calculator",
                ],
            },
        }

        return report

    def export_to_json(self, report: Dict, output_path: str):
        """Export report to JSON file"""
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2, default=str)

    def export_to_html(self, report: Dict, output_path: str):
        """Export report to HTML file"""
        html_content = self._generate_html_report(report)
        with open(output_path, "w") as f:
            f.write(html_content)

    def _generate_html_report(self, report: Dict) -> str:
        """Generate HTML formatted report"""
        exec_summary = report["executive_summary"]
        value_assessment = report["value_assessment"]

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset='utf-8'>
    <title>SGPA Report - {report["metadata"]["client"]["name"]}</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        h1 {{ color: #2C3E50; border-bottom: 4px solid #3498DB; padding-bottom: 10px; }}
        h2 {{ color: #34495E; margin-top: 40px; }}
        h3 {{ color: #7F8C8D; }}
        .metric {{ display: inline-block; margin: 20px; padding: 20px; background: #ECF0F1; border-radius: 8px; min-width: 200px; }}
        .metric-value {{ font-size: 32px; font-weight: bold; color: #27AE60; }}
        .metric-label {{ font-size: 14px; color: #7F8C8D; margin-top: 5px; }}
        .grade {{ font-size: 48px; font-weight: bold; color: #3498DB; display: inline-block; }}
        .recommendation {{ background: #FFF9E6; padding: 15px; margin: 10px 0; border-left: 4px solid #F39C12; border-radius: 4px; }}
        .strength {{ color: #27AE60; }}
        .opportunity {{ color: #E67E22; }}
        ul {{ line-height: 1.8; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Sacred Geometric Principles of Alignment Report</h1>
        <p><strong>Client:</strong> {report["metadata"]["client"].get("name", "N/A")}</p>
        <p><strong>Generated:</strong> {report["metadata"]["generated_at"]}</p>

        <h2>Executive Summary</h2>
        <div class="grade">{exec_summary["alignment_grade"]}</div>
        <p><strong>Overall Assessment:</strong> {exec_summary["overall_assessment"]}</p>

        <div class="metric">
            <div class="metric-value">{exec_summary["sacred_alignment_score"]}%</div>
            <div class="metric-label">Sacred Alignment Score</div>
        </div>

        <div class="metric">
            <div class="metric-value">${value_assessment["roi_analysis"]["first_year_benefit"]:,.0f}</div>
            <div class="metric-label">First Year Benefit</div>
        </div>

        <div class="metric">
            <div class="metric-value">{value_assessment["roi_analysis"]["roi_percentage"]}%</div>
            <div class="metric-label">ROI</div>
        </div>

        <h3>Key Strengths</h3>
        <ul>
            {"".join(f'<li class="strength">{s}</li>' for s in exec_summary["key_strengths"])}
        </ul>

        <h3>Key Opportunities</h3>
        <ul>
            {"".join(f'<li class="opportunity">{o}</li>' for o in exec_summary["key_opportunities"])}
        </ul>

        <h2>Value Assessment</h2>
        <p><strong>Total Annual Benefit:</strong> ${value_assessment["value_delivered"]["total_annual_benefit"]:,.2f}</p>
        <p><strong>Service Investment:</strong> ${value_assessment["service_pricing"]["total_price"]:,.2f}</p>
        <p><strong>Payback Period:</strong> {value_assessment["roi_analysis"]["payback_period_months"]} months</p>
        <p><strong>3-Year Net Benefit:</strong> ${value_assessment["roi_analysis"]["3_year_net_benefit"]:,.2f}</p>

        <h2>Recommendations</h2>
        {self._generate_recommendations_html(report["optimization_recommendations"]["recommendations"])}

        <h2>Implementation Roadmap</h2>
        {self._generate_roadmap_html(report["implementation_roadmap"])}

        <p style="margin-top: 60px; padding-top: 20px; border-top: 1px solid #ddd; color: #7F8C8D; font-size: 12px;">
            Generated by SGPA Framework | Sacred Geometric Principles of Alignment
        </p>
    </div>
</body>
</html>
"""
        return html

    def _generate_recommendations_html(self, recommendations: List[Dict]) -> str:
        """Generate HTML for recommendations"""
        html_parts = []
        for rec in recommendations[:5]:  # Top 5
            html_parts.append(f"""
            <div class="recommendation">
                <h3>{rec["title"]}</h3>
                <p>{rec["description"]}</p>
                <p><strong>Expected Improvement:</strong> {rec["expected_improvement"]}</p>
                <p><strong>Sacred Principle:</strong> {rec["sacred_principle"]}</p>
            </div>
            """)
        return "\n".join(html_parts)

    def _generate_roadmap_html(self, roadmap: Dict) -> str:
        """Generate HTML for roadmap"""
        html_parts = []
        for phase in roadmap["phases"]:
            html_parts.append(f"""
            <h3>Phase {phase["phase"]}: {phase["name"]}</h3>
            <p><strong>Duration:</strong> {phase["duration"]}</p>
            <p><strong>Sacred Principle:</strong> {phase["sacred_principle"]}</p>
            """)
        return "\n".join(html_parts)
