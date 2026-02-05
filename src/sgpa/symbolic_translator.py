"""
Symbolic Translator

Translates data patterns into symbolic meanings based on sacred geometry.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

from .calculators import PHI


class ArchetypalPattern(str, Enum):
    """Archetypal patterns in sacred geometry"""
    CREATION = "creation"
    UNITY = "unity"
    DUALITY = "duality"
    TRINITY = "trinity"
    FOUNDATION = "foundation"
    HARMONY = "harmony"
    TRANSFORMATION = "transformation"
    COMPLETION = "completion"
    EXPANSION = "expansion"
    CONTRACTION = "contraction"
    BALANCE = "balance"
    FLOW = "flow"


@dataclass
class SymbolicInterpretation:
    """Symbolic interpretation of a pattern"""
    primary_symbol: str
    archetypal_pattern: ArchetypalPattern
    meaning: str
    qualities: List[str]
    energetic_signature: str
    transformation_potential: str
    practical_application: str


class SymbolicTranslator:
    """Translate data patterns to symbolic meanings"""

    def __init__(self):
        self.symbol_library = self._initialize_symbol_library()

    def _initialize_symbol_library(self) -> Dict:
        """Initialize library of symbolic meanings"""
        return {
            "golden_ratio": SymbolicInterpretation(
                primary_symbol="Divine Proportion (φ)",
                archetypal_pattern=ArchetypalPattern.HARMONY,
                meaning="The divine proportion represents the perfect balance between expansion and contraction, "
                "growth and decay, giving and receiving. It is the fundamental ratio of beauty and harmony.",
                qualities=["balance", "beauty", "growth", "harmony", "perfection", "divine"],
                energetic_signature="Balanced expansion - neither too fast nor too slow, perfectly sustainable",
                transformation_potential="Optimize all ratios to approach φ for maximum efficiency and aesthetic appeal",
                practical_application="Apply to UI proportions, data structures, scaling factors, and resource allocation",
            ),
            "fibonacci": SymbolicInterpretation(
                primary_symbol="Natural Growth Spiral",
                archetypal_pattern=ArchetypalPattern.EXPANSION,
                meaning="The Fibonacci sequence represents natural, organic growth patterns found throughout nature. "
                "Each step builds upon the previous, creating sustainable expansion.",
                qualities=["growth", "evolution", "spiral", "natural", "building", "accumulation"],
                energetic_signature="Organic expansion - building momentum while staying grounded in foundation",
                transformation_potential="Use Fibonacci sizing for progressive enhancement and scalable architecture",
                practical_application="Apply to data chunking, pagination, caching layers, and progressive loading",
            ),
            "flower_of_life": SymbolicInterpretation(
                primary_symbol="Sacred Flower",
                archetypal_pattern=ArchetypalPattern.CREATION,
                meaning="The Flower of Life represents the blueprint of creation, showing how all things are "
                "interconnected through sacred geometric patterns.",
                qualities=["unity", "creation", "interconnection", "wholeness", "sacred"],
                energetic_signature="Creative unity - all parts working as harmonious whole",
                transformation_potential="Design systems where all components are interconnected and interdependent",
                practical_application="Apply to microservices architecture, API design, and data relationship modeling",
            ),
            "vesica_piscis": SymbolicInterpretation(
                primary_symbol="Sacred Vesica",
                archetypal_pattern=ArchetypalPattern.DUALITY,
                meaning="The intersection of two circles represents the birth of form from unity, "
                "the bridge between dualities, and the space where creation happens.",
                qualities=["duality", "union", "bridge", "creation", "intersection"],
                energetic_signature="Creative tension - the productive space between opposites",
                transformation_potential="Create interfaces and bridges between different systems or paradigms",
                practical_application="Apply to API gateways, integration layers, and middleware design",
            ),
            "triangle": SymbolicInterpretation(
                primary_symbol="Trinity",
                archetypal_pattern=ArchetypalPattern.TRINITY,
                meaning="The triangle represents the trinity principle - three points creating stability, "
                "the first stable structure, combining duality into unified purpose.",
                qualities=["stability", "trinity", "foundation", "purpose", "direction"],
                energetic_signature="Stable foundation - minimum viable structure with direction",
                transformation_potential="Establish three-pillar architectures for stability and clarity",
                practical_application="Apply to three-tier architecture, MVC pattern, and triangular redundancy",
            ),
            "square": SymbolicInterpretation(
                primary_symbol="Foundation",
                archetypal_pattern=ArchetypalPattern.FOUNDATION,
                meaning="The square represents solidity, foundation, and the material world. "
                "Four corners create stability and grounding.",
                qualities=["stability", "foundation", "material", "grounding", "structure"],
                energetic_signature="Solid foundation - stable, grounded, reliable",
                transformation_potential="Build robust, stable foundations that can support growth",
                practical_application="Apply to database schemas, core infrastructure, and foundational services",
            ),
            "pentagon": SymbolicInterpretation(
                primary_symbol="Human Expression",
                archetypal_pattern=ArchetypalPattern.HARMONY,
                meaning="The pentagon, with its connection to the golden ratio, represents human proportions "
                "and the balance of material and spiritual.",
                qualities=["human", "balance", "expression", "integration", "harmony"],
                energetic_signature="Human-centered harmony - balancing needs with capabilities",
                transformation_potential="Design systems that honor human needs and natural workflows",
                practical_application="Apply to user experience, human-computer interaction, and workflow design",
            ),
            "hexagon": SymbolicInterpretation(
                primary_symbol="Efficiency",
                archetypal_pattern=ArchetypalPattern.HARMONY,
                meaning="The hexagon represents maximum efficiency and harmony, as seen in honeycombs. "
                "Six-fold symmetry creates optimal space utilization.",
                qualities=["efficiency", "harmony", "optimization", "community", "collaboration"],
                energetic_signature="Efficient harmony - maximum output with minimum waste",
                transformation_potential="Optimize for efficiency while maintaining harmony and balance",
                practical_application="Apply to data storage, caching strategies, and resource management",
            ),
            "circle": SymbolicInterpretation(
                primary_symbol="Unity/Completion",
                archetypal_pattern=ArchetypalPattern.COMPLETION,
                meaning="The circle represents wholeness, completion, and the infinite. "
                "No beginning, no end, perfect unity.",
                qualities=["unity", "wholeness", "infinite", "complete", "eternal"],
                energetic_signature="Complete unity - self-contained and whole",
                transformation_potential="Create complete, self-contained systems with clear boundaries",
                practical_application="Apply to encapsulation, modularity, and circular processes",
            ),
            "spiral": SymbolicInterpretation(
                primary_symbol="Evolution",
                archetypal_pattern=ArchetypalPattern.TRANSFORMATION,
                meaning="The spiral represents evolution, transformation, and cyclical growth. "
                "Each cycle returns to similar place but at a higher level.",
                qualities=["evolution", "transformation", "cycle", "growth", "journey"],
                energetic_signature="Evolutionary transformation - progressive development through cycles",
                transformation_potential="Implement iterative development with progressive enhancement",
                practical_application="Apply to agile development, versioning, and continuous improvement",
            ),
        }

    def translate_pattern(self, pattern_type: str) -> Optional[SymbolicInterpretation]:
        """Get symbolic interpretation for a pattern type"""
        return self.symbol_library.get(pattern_type.lower())

    def translate_number(self, number: int) -> SymbolicInterpretation:
        """Translate number to symbolic meaning"""
        # Sacred number meanings
        meanings = {
            1: ("Unity", ArchetypalPattern.UNITY, "The source, beginning, unity of all things"),
            2: ("Duality", ArchetypalPattern.DUALITY, "Polarity, reflection, balance of opposites"),
            3: ("Trinity", ArchetypalPattern.TRINITY, "Creation, expression, manifestation"),
            4: ("Foundation", ArchetypalPattern.FOUNDATION, "Structure, stability, material world"),
            5: ("Change", ArchetypalPattern.TRANSFORMATION, "Transformation, humanity, life force"),
            6: ("Harmony", ArchetypalPattern.HARMONY, "Balance, beauty, cosmic order"),
            7: ("Mysticism", ArchetypalPattern.COMPLETION, "Spiritual completion, inner wisdom"),
            8: ("Infinity", ArchetypalPattern.FLOW, "Infinite flow, abundance, cycles"),
            9: ("Completion", ArchetypalPattern.COMPLETION, "Ending, fulfillment, universal love"),
            12: ("Cosmic Order", ArchetypalPattern.COMPLETION, "Universal structure, time, zodiac"),
        }

        if number in meanings:
            symbol, archetype, meaning = meanings[number]
            return SymbolicInterpretation(
                primary_symbol=f"{symbol} ({number})",
                archetypal_pattern=archetype,
                meaning=meaning,
                qualities=[symbol.lower(), "sacred"],
                energetic_signature=f"Frequency of {symbol}",
                transformation_potential=f"Leverage the power of {number} for {symbol.lower()}",
                practical_application=f"Use {number} as a guiding principle in design",
            )

        # Default interpretation
        return SymbolicInterpretation(
            primary_symbol=f"Number {number}",
            archetypal_pattern=ArchetypalPattern.FOUNDATION,
            meaning=f"The specific number {number} in your system",
            qualities=["specific", "unique"],
            energetic_signature="Unique frequency",
            transformation_potential="Consider optimizing to nearby sacred numbers",
            practical_application="Evaluate if this number serves the design",
        )

    def translate_ratio(self, ratio: float) -> SymbolicInterpretation:
        """Translate ratio to symbolic meaning"""
        # Check if it's close to golden ratio
        if abs(ratio - PHI) / PHI < 0.05:
            return self.symbol_library["golden_ratio"]

        # Check if it's close to √2 (Vesica Piscis ratio)
        if abs(ratio - 1.414) / 1.414 < 0.05:
            return SymbolicInterpretation(
                primary_symbol="Square Root of 2",
                archetypal_pattern=ArchetypalPattern.DUALITY,
                meaning="The ratio of diagonal to side of a square, representing balanced duality",
                qualities=["balance", "duality", "geometry"],
                energetic_signature="Balanced expansion in two dimensions",
                transformation_potential="Use for balanced scaling in multiple dimensions",
                practical_application="Apply to aspect ratios and proportional scaling",
            )

        # Check if it's close to √3 (Vesica Piscis exact)
        if abs(ratio - 1.732) / 1.732 < 0.05:
            return self.symbol_library["vesica_piscis"]

        # Default
        return SymbolicInterpretation(
            primary_symbol=f"Ratio {ratio:.3f}",
            archetypal_pattern=ArchetypalPattern.FOUNDATION,
            meaning=f"A specific ratio of {ratio:.3f} in your system",
            qualities=["proportion", "relationship"],
            energetic_signature="Unique proportional relationship",
            transformation_potential=f"Consider adjusting toward sacred ratios (φ={PHI:.3f})",
            practical_application="Evaluate if this ratio serves the design optimally",
        )

    def translate_structure(self, structure_type: str, properties: Dict) -> SymbolicInterpretation:
        """
        Translate structural patterns to symbolic meaning
        """
        depth = properties.get("depth", 0)
        branching = properties.get("branching_factor", 1)
        symmetry = properties.get("has_symmetry", False)

        # Determine archetypal pattern based on structure
        if symmetry and branching >= 3:
            archetype = ArchetypalPattern.HARMONY
            symbol = "Harmonious Structure"
            meaning = "A well-balanced, symmetric structure representing harmony and order"
        elif depth > 5:
            archetype = ArchetypalPattern.EXPANSION
            symbol = "Deep Hierarchy"
            meaning = "A deep, layered structure representing complexity and evolution"
        elif branching > 10:
            archetype = ArchetypalPattern.CREATION
            symbol = "Abundant Branching"
            meaning = "Rich branching structure representing creativity and abundance"
        else:
            archetype = ArchetypalPattern.FOUNDATION
            symbol = "Simple Structure"
            meaning = "A foundational structure representing clarity and simplicity"

        return SymbolicInterpretation(
            primary_symbol=symbol,
            archetypal_pattern=archetype,
            meaning=meaning,
            qualities=["structural", "organizational"],
            energetic_signature=f"Depth {depth}, Branching {branching}",
            transformation_potential="Optimize structure to align with sacred geometric principles",
            practical_application=f"Current {structure_type} can be optimized for better flow",
        )

    def translate_alignment_score(self, score: float) -> SymbolicInterpretation:
        """Translate alignment score to symbolic meaning"""
        if score >= 0.9:
            return SymbolicInterpretation(
                primary_symbol="Sacred Alignment",
                archetypal_pattern=ArchetypalPattern.COMPLETION,
                meaning="Exceptional alignment with sacred geometric principles - operating in divine flow",
                qualities=["excellence", "mastery", "divine", "optimal"],
                energetic_signature="High frequency - optimal resonance",
                transformation_potential="Maintain this alignment and share knowledge with others",
                practical_application="Document and replicate these patterns across systems",
            )
        elif score >= 0.7:
            return SymbolicInterpretation(
                primary_symbol="Good Alignment",
                archetypal_pattern=ArchetypalPattern.HARMONY,
                meaning="Strong alignment with sacred principles - on the right path",
                qualities=["good", "balanced", "harmonious"],
                energetic_signature="Positive resonance - flowing well",
                transformation_potential="Fine-tune remaining elements for optimal alignment",
                practical_application="Identify and optimize low-scoring areas",
            )
        elif score >= 0.5:
            return SymbolicInterpretation(
                primary_symbol="Partial Alignment",
                archetypal_pattern=ArchetypalPattern.TRANSFORMATION,
                meaning="Some alignment present - system in transformation toward optimization",
                qualities=["developing", "transforming", "potential"],
                energetic_signature="Mixed frequencies - some resonance, some dissonance",
                transformation_potential="Significant optimization opportunities available",
                practical_application="Prioritize golden ratio and Fibonacci optimizations",
            )
        else:
            return SymbolicInterpretation(
                primary_symbol="Misalignment",
                archetypal_pattern=ArchetypalPattern.FOUNDATION,
                meaning="Limited alignment - foundation needs restructuring for optimization",
                qualities=["challenged", "opportunity", "potential"],
                energetic_signature="Low frequency - significant dissonance",
                transformation_potential="Major optimization potential - transformative changes recommended",
                practical_application="Complete restructuring recommended to align with sacred geometry",
            )

    def create_transformation_path(
        self, current_state: str, optimal_state: str, alignment_score: float
    ) -> List[Dict]:
        """
        Create a transformation path from current to optimal state
        """
        steps = []

        # Step 1: Foundation
        steps.append(
            {
                "phase": 1,
                "name": "Foundation",
                "archetypal_pattern": ArchetypalPattern.FOUNDATION.value,
                "description": "Establish stable foundation aligned with sacred geometry",
                "actions": [
                    "Audit current structure and identify misalignments",
                    "Document baseline metrics and measurements",
                    "Identify quick wins for immediate improvement",
                ],
                "expected_improvement": 0.15,
            }
        )

        # Step 2: Alignment
        if alignment_score < 0.6:
            steps.append(
                {
                    "phase": 2,
                    "name": "Core Alignment",
                    "archetypal_pattern": ArchetypalPattern.HARMONY.value,
                    "description": "Align core structures with golden ratio and Fibonacci",
                    "actions": [
                        "Restructure proportions to golden ratio (φ)",
                        "Optimize sizes to Fibonacci sequence",
                        "Implement symmetry where appropriate",
                    ],
                    "expected_improvement": 0.25,
                }
            )

        # Step 3: Optimization
        steps.append(
            {
                "phase": 3,
                "name": "Optimization",
                "archetypal_pattern": ArchetypalPattern.EXPANSION.value,
                "description": "Optimize all aspects for maximum efficiency and flow",
                "actions": [
                    "Fine-tune all ratios and proportions",
                    "Optimize workflows for natural flow",
                    "Implement sacred harmonic frequencies",
                ],
                "expected_improvement": 0.20,
            }
        )

        # Step 4: Integration
        steps.append(
            {
                "phase": 4,
                "name": "Integration",
                "archetypal_pattern": ArchetypalPattern.UNITY.value,
                "description": "Integrate all optimizations into unified whole",
                "actions": [
                    "Ensure all components work harmoniously",
                    "Balance competing optimizations",
                    "Create feedback loops for continuous alignment",
                ],
                "expected_improvement": 0.15,
            }
        )

        # Step 5: Transcendence (if aiming for excellence)
        if optimal_state == "transcendent":
            steps.append(
                {
                    "phase": 5,
                    "name": "Transcendence",
                    "archetypal_pattern": ArchetypalPattern.COMPLETION.value,
                    "description": "Achieve mastery and transcendent alignment",
                    "actions": [
                        "Implement advanced sacred geometry patterns",
                        "Create self-optimizing systems",
                        "Share knowledge and elevate entire ecosystem",
                    ],
                    "expected_improvement": 0.10,
                }
            )

        return steps

    def get_symbolic_report(self, analysis_results: Dict) -> Dict:
        """
        Create comprehensive symbolic report from analysis
        """
        alignment_score = analysis_results.get("alignment_score", 0.5)
        patterns_detected = analysis_results.get("patterns", [])

        # Translate alignment score
        alignment_interpretation = self.translate_alignment_score(alignment_score)

        # Translate detected patterns
        pattern_interpretations = []
        for pattern in patterns_detected:
            interp = self.translate_pattern(pattern.get("type", ""))
            if interp:
                pattern_interpretations.append(
                    {
                        "pattern": pattern.get("type"),
                        "interpretation": interp,
                        "confidence": pattern.get("confidence", 0.0),
                    }
                )

        # Overall symbolic meaning
        if alignment_score >= 0.8:
            overall_meaning = "Your system resonates with divine proportions and sacred patterns"
        elif alignment_score >= 0.6:
            overall_meaning = "Your system shows harmony and is on the path to sacred alignment"
        elif alignment_score >= 0.4:
            overall_meaning = "Your system has potential waiting to be unlocked through sacred geometry"
        else:
            overall_meaning = "Your system is seeking alignment - transformative opportunity awaits"

        return {
            "overall_meaning": overall_meaning,
            "alignment_interpretation": alignment_interpretation,
            "pattern_interpretations": pattern_interpretations,
            "energetic_signature": alignment_interpretation.energetic_signature,
            "transformation_potential": alignment_interpretation.transformation_potential,
        }
