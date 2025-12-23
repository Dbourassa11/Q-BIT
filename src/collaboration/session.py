"""
Collaboration Session

Manages the complete lifecycle of a collaboration from conception to approval.
"""

import asyncio
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import structlog

from src.collaboration.recipe import CollaborationRecipe, RecipeManager, RecipePhase, RecipeIngredient
from src.collaboration.expert_system import ExpertSystem, ExpertDomain, ExpertInsight
from src.collaboration.formula_engine import FormulaEngine, Formula
from src.collaboration.approval_workflow import ApprovalWorkflow, ApprovalStatus
import uuid

logger = structlog.get_logger(__name__)


class SessionPhase(str, Enum):
    """Phases in a collaboration session."""
    INITIALIZATION = "initialization"
    INGREDIENT_GATHERING = "ingredient_gathering"
    MIXING = "mixing"
    EXPERT_COLLABORATION = "expert_collaboration"
    FORMULA_GENERATION = "formula_generation"
    REVIEW = "review"
    APPROVAL = "approval"
    HANDOFF = "handoff"
    COMPLETED = "completed"


class CollaborationSession(BaseModel):
    """
    Complete collaboration session managing the entire lifecycle.
    
    This is the main orchestrator that ties together recipes, experts,
    formulas, and approval workflows.
    """
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    phase: SessionPhase = SessionPhase.INITIALIZATION
    
    recipe_id: Optional[str] = None
    approval_id: Optional[str] = None
    
    # Collected results
    expert_insights: List[Dict[str, Any]] = Field(default_factory=list)
    suggested_formulas: List[Dict[str, Any]] = Field(default_factory=list)
    final_solution: Optional[Dict[str, Any]] = None
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CollaborationOrchestrator:
    """
    Orchestrates the complete collaboration lifecycle.
    
    This is the "cook button" system that activates cross-domain
    expert collaboration, formula generation, and approval workflows.
    """
    
    # Configuration constants
    MAX_EXPERT_DOMAINS = 5  # Maximum number of expert domains to consult
    
    def __init__(self):
        """Initialize the collaboration orchestrator."""
        self.sessions: Dict[str, CollaborationSession] = {}
        self.recipe_manager = RecipeManager()
        self.expert_system = ExpertSystem()
        self.formula_engine = FormulaEngine()
        self.approval_workflow = ApprovalWorkflow()
        
        self.logger = structlog.get_logger(__name__)
    
    def create_session(
        self,
        name: str,
        description: str,
        created_by: str,
        tags: Optional[List[str]] = None
    ) -> CollaborationSession:
        """Create a new collaboration session."""
        session = CollaborationSession(
            name=name,
            description=description,
            created_by=created_by,
            tags=tags or []
        )
        
        self.sessions[session.session_id] = session
        
        # Create associated recipe
        recipe = self.recipe_manager.create_recipe(
            name=f"Recipe for {name}",
            description=description,
            created_by=created_by
        )
        session.recipe_id = recipe.recipe_id
        session.phase = SessionPhase.INGREDIENT_GATHERING
        
        self.logger.info(
            "Collaboration session created",
            session_id=session.session_id,
            name=name
        )
        
        return session
    
    def add_ingredient(
        self,
        session_id: str,
        ingredient: RecipeIngredient
    ) -> None:
        """Add an ingredient to the session's recipe."""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        if session.phase not in [SessionPhase.INGREDIENT_GATHERING]:
            raise ValueError(f"Cannot add ingredients in phase: {session.phase.value}")
        
        self.recipe_manager.add_ingredient(session.recipe_id, ingredient)
        
        self.logger.info(
            "Ingredient added to session",
            session_id=session_id,
            ingredient_type=ingredient.type.value
        )
    
    async def press_cook_button(self, session_id: str) -> Dict[str, Any]:
        """
        Press the "cook button" to activate cross-domain collaboration.
        
        This is the main action that triggers:
        1. Recipe mixing
        2. Expert consultation across domains
        3. Formula and schema generation
        4. Result synthesis
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        self.logger.info("🔥 COOK BUTTON PRESSED", session_id=session_id)
        
        # Phase 1: Mix ingredients
        session.phase = SessionPhase.MIXING
        self.recipe_manager.transition_to_mixing(session.recipe_id)
        mixed_results = await self.recipe_manager.mix_ingredients(session.recipe_id)
        
        self.logger.info("✅ Ingredients mixed", complexity=mixed_results.get("complexity_score"))
        
        # Phase 2: Consult experts (cross-domain collaboration)
        session.phase = SessionPhase.EXPERT_COLLABORATION
        recipe = self.recipe_manager.get_recipe(session.recipe_id)
        
        problem_description = f"{session.description}. Ingredients: {len(recipe.ingredients)}"
        
        # Determine relevant domains based on ingredients
        relevant_domains = self._determine_relevant_domains(recipe)
        
        self.logger.info(
            "🧠 Consulting experts across domains",
            domains=[d.value for d in relevant_domains]
        )
        
        expert_insights = await self.expert_system.consult_all_experts(
            problem=problem_description,
            context={"recipe": recipe.model_dump()},
            domains=relevant_domains
        )
        
        # Store insights in session
        session.expert_insights = [insight.model_dump() for insight in expert_insights]
        
        self.logger.info(
            "✅ Expert consultation completed",
            insights_count=len(expert_insights)
        )
        
        # Phase 3: Generate formulas and schemas
        session.phase = SessionPhase.FORMULA_GENERATION
        
        suggested_formulas = self.formula_engine.suggest_formulas_for_problem(
            problem_description
        )
        
        session.suggested_formulas = [formula.model_dump() for formula in suggested_formulas]
        
        self.logger.info(
            "✅ Formulas suggested",
            formula_count=len(suggested_formulas)
        )
        
        # Phase 4: Synthesize results
        final_solution = self._synthesize_solution(
            recipe=recipe,
            insights=expert_insights,
            formulas=suggested_formulas
        )
        
        session.final_solution = final_solution
        session.phase = SessionPhase.REVIEW
        
        self.logger.info("🎉 Cooking completed - solution ready for review")
        
        return {
            "status": "success",
            "phase": session.phase.value,
            "mixed_results": mixed_results,
            "expert_insights_count": len(expert_insights),
            "suggested_formulas_count": len(suggested_formulas),
            "final_solution": final_solution
        }
    
    def _determine_relevant_domains(
        self,
        recipe: CollaborationRecipe
    ) -> List[ExpertDomain]:
        """Determine which expert domains are relevant to the recipe."""
        domains = set()
        
        # Default core domains
        domains.add(ExpertDomain.MATHEMATICS)
        domains.add(ExpertDomain.ALGORITHMS)
        
        # Analyze ingredients to determine additional domains
        for ingredient in recipe.ingredients:
            content_lower = str(ingredient.content).lower()
            
            if any(word in content_lower for word in ["optimize", "maximum", "minimum"]):
                domains.add(ExpertDomain.OPTIMIZATION)
            
            if any(word in content_lower for word in ["learn", "predict", "train", "model"]):
                domains.add(ExpertDomain.MACHINE_LEARNING)
                domains.add(ExpertDomain.DATA_SCIENCE)
            
            if any(word in content_lower for word in ["security", "encrypt", "secure"]):
                domains.add(ExpertDomain.SECURITY)
                domains.add(ExpertDomain.CRYPTOGRAPHY)
            
            if any(word in content_lower for word in ["system", "architecture", "design"]):
                domains.add(ExpertDomain.ARCHITECTURE)
                domains.add(ExpertDomain.SYSTEMS_DESIGN)
        
        return list(domains)[:self.MAX_EXPERT_DOMAINS]
    
    def _synthesize_solution(
        self,
        recipe: CollaborationRecipe,
        insights: List[ExpertInsight],
        formulas: List[Formula]
    ) -> Dict[str, Any]:
        """Synthesize all inputs into a cohesive solution."""
        solution = {
            "recipe_summary": {
                "name": recipe.name,
                "ingredients_count": len(recipe.ingredients),
                "complexity_score": recipe.complexity_score
            },
            "expert_contributions": {
                "total_insights": len(insights),
                "domains_consulted": list(set(i.expert_domain.value for i in insights)),
                "average_confidence": sum(i.confidence for i in insights) / len(insights) if insights else 0,
                "key_recommendations": [
                    {
                        "domain": i.expert_domain.value,
                        "insight": i.insight[:200],
                        "algorithms": i.suggested_algorithms[:3]
                    }
                    for i in insights[:3]
                ]
            },
            "mathematical_foundations": {
                "formulas_suggested": len(formulas),
                "categories": list(set(f.category.value for f in formulas)),
                "key_formulas": [
                    {
                        "name": f.name,
                        "notation": f.formula_notation,
                        "complexity": f.complexity
                    }
                    for f in formulas[:5]
                ]
            },
            "implementation_guide": {
                "recommended_approach": "Multi-phase implementation",
                "phases": ["design", "prototype", "validate", "optimize", "deploy"],
                "estimated_complexity": "Medium to High"
            }
        }
        
        return solution
    
    async def request_approval(
        self,
        session_id: str,
        approvers: List[str]
    ) -> str:
        """Request approval for the collaboration results."""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        if session.phase != SessionPhase.REVIEW:
            raise ValueError(f"Session must be in review phase, currently: {session.phase.value}")
        
        # Create approval request
        approval_id = self.approval_workflow.create_approval(
            title=f"Approval for {session.name}",
            description=f"Collaboration session results for approval",
            content=session.final_solution,
            requester_id=session.created_by,
            approvers=approvers
        )
        
        session.approval_id = approval_id
        session.phase = SessionPhase.APPROVAL
        
        self.logger.info(
            "Approval requested",
            session_id=session_id,
            approval_id=approval_id
        )
        
        return approval_id
    
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get the current status of a collaboration session."""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        recipe = self.recipe_manager.get_recipe(session.recipe_id)
        
        status = {
            "session_id": session.session_id,
            "name": session.name,
            "phase": session.phase.value,
            "created_at": session.created_at.isoformat(),
            "recipe": {
                "ingredient_count": len(recipe.ingredients),
                "phase": recipe.phase.value,
                "complexity_score": recipe.complexity_score
            },
            "results": {
                "expert_insights": len(session.expert_insights),
                "suggested_formulas": len(session.suggested_formulas),
                "has_final_solution": session.final_solution is not None
            }
        }
        
        if session.approval_id:
            approval_status = self.approval_workflow.get_approval_status(session.approval_id)
            status["approval"] = approval_status
        
        return status
