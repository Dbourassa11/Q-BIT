"""
SGPA Visualizer

Generate visualizations for sacred geometry patterns and analysis results.
"""

import json
import math
from typing import Dict, List, Optional, Tuple

import numpy as np

from .calculators import PHI


class SGPAVisualizer:
    """Generate visual representations of SGPA analysis"""

    def __init__(self, width: int = 800, height: int = 600):
        self.width = width
        self.height = height
        self.center_x = width / 2
        self.center_y = height / 2

    def generate_golden_spiral(self, scale: float = 50) -> str:
        """Generate SVG for golden spiral"""
        svg_parts = [
            f'<svg width="{self.width}" height="{self.height}" xmlns="http://www.w3.org/2000/svg">',
            '<defs>',
            '<style>',
            '.spiral { fill: none; stroke: #FFD700; stroke-width: 2; }',
            '.golden-rect { fill: none; stroke: #DAA520; stroke-width: 1; opacity: 0.5; }',
            '</style>',
            '</defs>',
        ]

        # Generate golden rectangles
        x, y = self.center_x - scale, self.center_y - scale
        w, h = scale * 2, scale * 2

        for i in range(8):  # 8 iterations of golden rectangle
            svg_parts.append(
                f'<rect x="{x}" y="{y}" width="{w}" height="{h}" class="golden-rect"/>'
            )

            # Next rectangle follows golden ratio
            if i % 4 == 0:  # Right
                new_w = h / PHI
                x = x + w
                w = new_w
            elif i % 4 == 1:  # Down
                new_h = w / PHI
                y = y + h
                h = new_h
            elif i % 4 == 2:  # Left
                new_w = h / PHI
                x = x
                w = new_w
            else:  # Up
                new_h = w / PHI
                y = y
                h = new_h

        # Generate spiral curve
        points = []
        for theta in np.linspace(0, 4 * np.pi, 200):
            r = scale * np.exp(theta / (2 * np.pi / np.log(PHI)))
            px = self.center_x + r * np.cos(theta)
            py = self.center_y + r * np.sin(theta)
            points.append(f"{px},{py}")

        spiral_path = "M " + " L ".join(points)
        svg_parts.append(f'<path d="{spiral_path}" class="spiral"/>')

        svg_parts.append("</svg>")
        return "\n".join(svg_parts)

    def generate_flower_of_life(self, radius: float = 60) -> str:
        """Generate SVG for Flower of Life pattern"""
        svg_parts = [
            f'<svg width="{self.width}" height="{self.height}" xmlns="http://www.w3.org/2000/svg">',
            '<defs>',
            '<style>',
            '.flower-circle { fill: none; stroke: #9370DB; stroke-width: 1.5; }',
            '</style>',
            '</defs>',
        ]

        # Central circle
        svg_parts.append(
            f'<circle cx="{self.center_x}" cy="{self.center_y}" r="{radius}" class="flower-circle"/>'
        )

        # Six surrounding circles
        for i in range(6):
            angle = i * (np.pi / 3)
            cx = self.center_x + radius * np.cos(angle)
            cy = self.center_y + radius * np.sin(angle)
            svg_parts.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" class="flower-circle"/>')

        # Outer ring of 12 circles
        for i in range(12):
            angle = i * (np.pi / 6)
            distance = radius * np.sqrt(3)
            cx = self.center_x + distance * np.cos(angle)
            cy = self.center_y + distance * np.sin(angle)
            svg_parts.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" class="flower-circle"/>')

        svg_parts.append("</svg>")
        return "\n".join(svg_parts)

    def generate_metatrons_cube(self, radius: float = 80) -> str:
        """Generate SVG for Metatron's Cube"""
        svg_parts = [
            f'<svg width="{self.width}" height="{self.height}" xmlns="http://www.w3.org/2000/svg">',
            '<defs>',
            '<style>',
            '.meta-circle { fill: none; stroke: #4169E1; stroke-width: 1; }',
            '.meta-line { stroke: #4169E1; stroke-width: 0.5; opacity: 0.6; }',
            '</style>',
            '</defs>',
        ]

        # 13 circles (1 center + 6 inner + 6 outer)
        circles = [(self.center_x, self.center_y)]  # Center

        # Inner ring
        for i in range(6):
            angle = i * (np.pi / 3)
            cx = self.center_x + radius * 0.6 * np.cos(angle)
            cy = self.center_y + radius * 0.6 * np.sin(angle)
            circles.append((cx, cy))

        # Outer ring
        for i in range(6):
            angle = i * (np.pi / 3) + (np.pi / 6)
            cx = self.center_x + radius * np.cos(angle)
            cy = self.center_y + radius * np.sin(angle)
            circles.append((cx, cy))

        # Draw connecting lines
        for i, (x1, y1) in enumerate(circles):
            for j, (x2, y2) in enumerate(circles):
                if i < j:
                    svg_parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="meta-line"/>')

        # Draw circles
        for cx, cy in circles:
            svg_parts.append(f'<circle cx="{cx}" cy="{cy}" r="5" class="meta-circle"/>')

        svg_parts.append("</svg>")
        return "\n".join(svg_parts)

    def generate_alignment_gauge(self, score: float, label: str = "Alignment Score") -> str:
        """Generate SVG gauge for alignment score"""
        svg_parts = [
            f'<svg width="{self.width}" height="{300}" xmlns="http://www.w3.org/2000/svg">',
            '<defs>',
            '<style>',
            '.gauge-bg { fill: none; stroke: #E0E0E0; stroke-width: 20; }',
            '.gauge-fill { fill: none; stroke-width: 20; stroke-linecap: round; }',
            '.gauge-text { font-family: Arial; font-size: 48px; font-weight: bold; text-anchor: middle; }',
            '.gauge-label { font-family: Arial; font-size: 18px; text-anchor: middle; fill: #666; }',
            '</style>',
            '<linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">',
            '<stop offset="0%" style="stop-color:#FF6B6B;stop-opacity:1" />',
            '<stop offset="50%" style="stop-color:#FFD93D;stop-opacity:1" />',
            '<stop offset="100%" style="stop-color:#6BCB77;stop-opacity:1" />',
            '</linearGradient>',
            '</defs>',
        ]

        # Gauge parameters
        cx, cy = self.width / 2, 150
        radius = 100
        start_angle = -np.pi * 0.75
        end_angle = np.pi * 0.75
        angle_range = end_angle - start_angle

        # Background arc
        bg_path = self._create_arc_path(cx, cy, radius, start_angle, end_angle)
        svg_parts.append(f'<path d="{bg_path}" class="gauge-bg"/>')

        # Filled arc based on score
        score_angle = start_angle + (angle_range * score)
        fill_path = self._create_arc_path(cx, cy, radius, start_angle, score_angle)

        # Color based on score
        if score >= 0.8:
            color = "#6BCB77"
        elif score >= 0.6:
            color = "#FFD93D"
        elif score >= 0.4:
            color = "#FFA500"
        else:
            color = "#FF6B6B"

        svg_parts.append(f'<path d="{fill_path}" class="gauge-fill" stroke="{color}"/>')

        # Score text
        score_percent = int(score * 100)
        svg_parts.append(
            f'<text x="{cx}" y="{cy + 15}" class="gauge-text" fill="{color}">{score_percent}%</text>'
        )

        # Label
        svg_parts.append(f'<text x="{cx}" y="{cy + 50}" class="gauge-label">{label}</text>')

        svg_parts.append("</svg>")
        return "\n".join(svg_parts)

    def _create_arc_path(
        self, cx: float, cy: float, radius: float, start_angle: float, end_angle: float
    ) -> str:
        """Create SVG arc path"""
        start_x = cx + radius * np.cos(start_angle)
        start_y = cy + radius * np.sin(start_angle)
        end_x = cx + radius * np.cos(end_angle)
        end_y = cy + radius * np.sin(end_angle)

        large_arc = 1 if (end_angle - start_angle) > np.pi else 0

        return f"M {start_x} {start_y} A {radius} {radius} 0 {large_arc} 1 {end_x} {end_y}"

    def generate_matrix_view(self, matrix_data: List[List[Dict]]) -> str:
        """Generate matrix visualization for optimization recommendations"""
        cell_width = 150
        cell_height = 100
        total_width = len(matrix_data[0]) * cell_width + 200
        total_height = len(matrix_data) * cell_height + 100

        svg_parts = [
            f'<svg width="{total_width}" height="{total_height}" xmlns="http://www.w3.org/2000/svg">',
            '<defs>',
            '<style>',
            '.matrix-cell { stroke: #CCC; stroke-width: 1; }',
            '.cell-empty { fill: #F5F5F5; }',
            '.cell-low { fill: #FFE5E5; }',
            '.cell-medium { fill: #FFF4E5; }',
            '.cell-high { fill: #E5F5E5; }',
            '.cell-text { font-family: Arial; font-size: 12px; text-anchor: middle; }',
            '.axis-label { font-family: Arial; font-size: 14px; font-weight: bold; }',
            '</style>',
            '</defs>',
        ]

        # Column headers (priorities)
        headers = ["High Priority", "Medium Priority", "Low Priority"]
        for i, header in enumerate(headers):
            x = 150 + i * cell_width + cell_width / 2
            svg_parts.append(f'<text x="{x}" y="30" class="axis-label" text-anchor="middle">{header}</text>')

        # Row labels (categories)
        categories = ["Proportions", "Sizing", "Structure", "Timing", "Workflow"]
        for i, category in enumerate(categories):
            y = 60 + i * cell_height + cell_height / 2
            svg_parts.append(f'<text x="10" y="{y}" class="axis-label">{category}</text>')

        # Matrix cells
        for row_idx, row in enumerate(matrix_data):
            for col_idx, cell in enumerate(row):
                x = 150 + col_idx * cell_width
                y = 60 + row_idx * cell_height

                # Determine cell color
                if not cell.get("has_recommendation", False):
                    cell_class = "cell-empty"
                else:
                    improvement = cell.get("total_improvement", 0)
                    if improvement >= 30:
                        cell_class = "cell-high"
                    elif improvement >= 15:
                        cell_class = "cell-medium"
                    else:
                        cell_class = "cell-low"

                svg_parts.append(
                    f'<rect x="{x}" y="{y}" width="{cell_width}" height="{cell_height}" '
                    f'class="matrix-cell {cell_class}"/>'
                )

                # Cell content
                if cell.get("has_recommendation", False):
                    count = cell.get("count", 0)
                    improvement = cell.get("total_improvement", 0)
                    svg_parts.append(
                        f'<text x="{x + cell_width/2}" y="{y + cell_height/2 - 5}" class="cell-text">'
                        f'{count} item{"s" if count > 1 else ""}</text>'
                    )
                    svg_parts.append(
                        f'<text x="{x + cell_width/2}" y="{y + cell_height/2 + 15}" class="cell-text">'
                        f'+{improvement:.0f}%</text>'
                    )

        svg_parts.append("</svg>")
        return "\n".join(svg_parts)

    def generate_radar_chart(self, scores: Dict[str, float]) -> str:
        """Generate radar chart for multi-dimensional scores"""
        svg_parts = [
            f'<svg width="{self.width}" height="{self.height}" xmlns="http://www.w3.org/2000/svg">',
            '<defs>',
            '<style>',
            '.radar-grid { fill: none; stroke: #CCC; stroke-width: 1; }',
            '.radar-axis { stroke: #999; stroke-width: 1; }',
            '.radar-fill { fill: #4169E1; fill-opacity: 0.3; stroke: #4169E1; stroke-width: 2; }',
            '.radar-label { font-family: Arial; font-size: 12px; text-anchor: middle; }',
            '</style>',
            '</defs>',
        ]

        # Radar parameters
        cx, cy = self.width / 2, self.height / 2
        max_radius = min(self.width, self.height) / 2 - 80
        num_axes = len(scores)
        angle_step = (2 * np.pi) / num_axes

        # Draw concentric circles (grid)
        for i in range(1, 6):
            radius = (max_radius / 5) * i
            svg_parts.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" class="radar-grid"/>')

        # Draw axes and labels
        axes_points = []
        for i, (label, score) in enumerate(scores.items()):
            angle = i * angle_step - (np.pi / 2)  # Start from top

            # Axis line
            end_x = cx + max_radius * np.cos(angle)
            end_y = cy + max_radius * np.sin(angle)
            svg_parts.append(f'<line x1="{cx}" y1="{cy}" x2="{end_x}" y2="{end_y}" class="radar-axis"/>')

            # Label
            label_distance = max_radius + 30
            label_x = cx + label_distance * np.cos(angle)
            label_y = cy + label_distance * np.sin(angle)
            svg_parts.append(f'<text x="{label_x}" y="{label_y}" class="radar-label">{label}</text>')

            # Data point
            data_radius = max_radius * score
            point_x = cx + data_radius * np.cos(angle)
            point_y = cy + data_radius * np.sin(angle)
            axes_points.append((point_x, point_y))

        # Draw filled polygon
        polygon_points = " ".join([f"{x},{y}" for x, y in axes_points])
        svg_parts.append(f'<polygon points="{polygon_points}" class="radar-fill"/>')

        svg_parts.append("</svg>")
        return "\n".join(svg_parts)

    def generate_comprehensive_dashboard(self, analysis_results: Dict) -> Dict[str, str]:
        """
        Generate complete dashboard with multiple visualizations
        Returns dict of visualization name -> SVG string
        """
        dashboard = {}

        # 1. Overall alignment gauge
        overall_score = analysis_results.get("overall_alignment_score", 0.5)
        dashboard["alignment_gauge"] = self.generate_alignment_gauge(
            overall_score, "Overall Sacred Alignment"
        )

        # 2. Radar chart for dimension scores
        dimension_scores = {
            "Golden Ratio": analysis_results.get("golden_ratio_alignment", 0.5),
            "Fibonacci": analysis_results.get("fibonacci_alignment", 0.5),
            "Symmetry": analysis_results.get("symmetry_alignment", 0.5),
            "Harmonic": analysis_results.get("harmonic_alignment", 0.5),
            "Flow": analysis_results.get("flow_alignment", 0.5),
        }
        dashboard["dimension_radar"] = self.generate_radar_chart(dimension_scores)

        # 3. Sacred geometry patterns
        dashboard["golden_spiral"] = self.generate_golden_spiral()
        dashboard["flower_of_life"] = self.generate_flower_of_life()
        dashboard["metatrons_cube"] = self.generate_metatrons_cube()

        # 4. Matrix view if available
        if "optimization_matrix" in analysis_results:
            dashboard["optimization_matrix"] = self.generate_matrix_view(
                analysis_results["optimization_matrix"]
            )

        return dashboard

    def export_to_html(self, dashboard: Dict[str, str], output_path: str):
        """Export dashboard visualizations to HTML file"""
        html_parts = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "<meta charset='utf-8'>",
            "<title>SGPA Analysis Dashboard</title>",
            "<style>",
            "body { font-family: Arial, sans-serif; margin: 20px; background: #F5F5F5; }",
            "h1 { color: #333; text-align: center; }",
            "h2 { color: #666; margin-top: 40px; }",
            ".viz-container { background: white; padding: 20px; margin: 20px 0; "
            "border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }",
            ".grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; }",
            "</style>",
            "</head>",
            "<body>",
            "<h1>Sacred Geometric Principles of Alignment Dashboard</h1>",
        ]

        # Add visualizations
        for name, svg in dashboard.items():
            title = name.replace("_", " ").title()
            html_parts.append(f"<div class='viz-container'>")
            html_parts.append(f"<h2>{title}</h2>")
            html_parts.append(svg)
            html_parts.append("</div>")

        html_parts.append("</body>")
        html_parts.append("</html>")

        with open(output_path, "w") as f:
            f.write("\n".join(html_parts))
