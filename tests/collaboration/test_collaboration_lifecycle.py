"""
Tests for the Collaboration Lifecycle System
"""

import pytest
import asyncio
from src.collaboration.session import CollaborationOrchestrator
from src.collaboration.recipe import (
    RecipeIngredient,
    IngredientType,
    RecipePhase,
    RecipeManager
)
from src.collaboration.expert_system import ExpertSystem, ExpertDomain
from src.collaboration.formula_engine import FormulaEngine, FormulaCategory
from src.collaboration.approval_workflow import (
    ApprovalWorkflow,
    ApprovalDecision,
    ApprovalStatus
)


class TestRecipeManager:
    """Test the Recipe Manager functionality."""
    
    def test_create_recipe(self):
        """Test recipe creation."""
        manager = RecipeManager()
        recipe = manager.create_recipe(
            name="Test Recipe",
            description="Test Description",
            created_by="test_user"
        )
        
        assert recipe.name == "Test Recipe"
        assert recipe.phase == RecipePhase.CONCEPTION
        assert len(recipe.ingredients) == 0
    
    def test_add_ingredient(self):
        """Test adding ingredients to a recipe."""
        manager = RecipeManager()
        recipe = manager.create_recipe(
            name="Test Recipe",
            description="Test",
            created_by="test_user"
        )
        
        ingredient = RecipeIngredient(
            type=IngredientType.IDEA,
            name="Test Idea",
            description="Test idea description",
            content="Some content",
            added_by="test_user"
        )
        
        manager.add_ingredient(recipe.recipe_id, ingredient)
        
        assert len(recipe.ingredients) == 1
        assert recipe.ingredients[0].name == "Test Idea"
    
    def test_remove_ingredient(self):
        """Test removing ingredients from a recipe."""
        manager = RecipeManager()
        recipe = manager.create_recipe(
            name="Test Recipe",
            description="Test",
            created_by="test_user"
        )
        
        ingredient = RecipeIngredient(
            type=IngredientType.IDEA,
            name="Test Idea",
            description="Test",
            content="Content",
            added_by="test_user"
        )
        
        manager.add_ingredient(recipe.recipe_id, ingredient)
        assert len(recipe.ingredients) == 1
        
        manager.remove_ingredient(recipe.recipe_id, ingredient.ingredient_id)
        assert len(recipe.ingredients) == 0
    
    @pytest.mark.asyncio
    async def test_mix_ingredients(self):
        """Test mixing ingredients."""
        manager = RecipeManager()
        recipe = manager.create_recipe(
            name="Test Recipe",
            description="Test",
            created_by="test_user"
        )
        
        # Add multiple ingredients
        for i in range(3):
            ingredient = RecipeIngredient(
                type=IngredientType.IDEA,
                name=f"Idea {i}",
                description=f"Description {i}",
                content=f"Content {i}",
                added_by="test_user"
            )
            manager.add_ingredient(recipe.recipe_id, ingredient)
        
        # Transition to mixing
        manager.transition_to_mixing(recipe.recipe_id)
        
        # Mix ingredients
        mixed_results = await manager.mix_ingredients(recipe.recipe_id)
        
        assert mixed_results["total_ingredients"] == 3
        assert mixed_results["ready_for_cooking"] is True
        assert recipe.complexity_score > 0


class TestExpertSystem:
    """Test the Expert System functionality."""
    
    @pytest.mark.asyncio
    async def test_register_expert(self):
        """Test expert registration."""
        system = ExpertSystem()
        expert = await system.register_expert(ExpertDomain.MATHEMATICS)
        
        assert expert is not None
        assert expert.domain == ExpertDomain.MATHEMATICS
        assert ExpertDomain.MATHEMATICS in system.experts
    
    @pytest.mark.asyncio
    async def test_consult_expert(self):
        """Test consulting a single expert."""
        system = ExpertSystem()
        insight = await system.consult_expert(
            domain=ExpertDomain.ALGORITHMS,
            problem="Sort a large dataset efficiently",
            context={}
        )
        
        assert insight is not None
        assert insight.expert_domain == ExpertDomain.ALGORITHMS
        assert insight.confidence > 0
        assert len(insight.suggested_algorithms) > 0
    
    @pytest.mark.asyncio
    async def test_consult_all_experts(self):
        """Test consulting multiple experts."""
        system = ExpertSystem()
        insights = await system.consult_all_experts(
            problem="Optimize machine learning model",
            context={},
            domains=[
                ExpertDomain.MACHINE_LEARNING,
                ExpertDomain.OPTIMIZATION,
                ExpertDomain.MATHEMATICS
            ]
        )
        
        assert len(insights) == 3
        assert all(insight.confidence > 0 for insight in insights)


class TestFormulaEngine:
    """Test the Formula Engine functionality."""
    
    def test_formula_engine_initialization(self):
        """Test that formula engine initializes with formulas."""
        engine = FormulaEngine()
        
        assert len(engine.formulas) > 0
        summary = engine.get_formulas_summary()
        assert summary["total_formulas"] > 0
    
    def test_search_formulas_by_category(self):
        """Test searching formulas by category."""
        engine = FormulaEngine()
        
        ml_formulas = engine.search_formulas(
            category=FormulaCategory.MACHINE_LEARNING
        )
        
        assert len(ml_formulas) > 0
        assert all(f.category == FormulaCategory.MACHINE_LEARNING for f in ml_formulas)
    
    def test_suggest_formulas_for_problem(self):
        """Test formula suggestion for a problem."""
        engine = FormulaEngine()
        
        suggestions = engine.suggest_formulas_for_problem(
            "Optimize a machine learning model using gradient descent"
        )
        
        assert len(suggestions) > 0
    
    def test_generate_computational_schema(self):
        """Test computational schema generation."""
        engine = FormulaEngine()
        
        schema = engine.generate_computational_schema(
            problem="Process large dataset",
            requirements=["scalable", "efficient"]
        )
        
        assert schema is not None
        assert schema.schema_type == "computational"
        assert "input" in schema.structure
        assert "processing" in schema.structure
        assert "output" in schema.structure


class TestApprovalWorkflow:
    """Test the Approval Workflow functionality."""
    
    def test_create_approval(self):
        """Test approval creation."""
        workflow = ApprovalWorkflow()
        
        approval_id = workflow.create_approval(
            title="Test Approval",
            description="Test approval request",
            content={"test": "data"},
            requester_id="user1",
            approvers=["user2", "user3"]
        )
        
        assert approval_id is not None
        approval = workflow.approvals[approval_id]
        assert approval.status == ApprovalStatus.PENDING
        assert len(approval.approvers) == 2
    
    def test_submit_approval_response(self):
        """Test submitting approval responses."""
        workflow = ApprovalWorkflow()
        
        approval_id = workflow.create_approval(
            title="Test",
            description="Test",
            content={},
            requester_id="user1",
            approvers=["user2", "user3"]
        )
        
        # First approval
        workflow.submit_approval_response(
            approval_id=approval_id,
            approver_id="user2",
            decision=ApprovalDecision.APPROVE,
            comments="Looks good"
        )
        
        approval = workflow.approvals[approval_id]
        assert approval.status == ApprovalStatus.IN_REVIEW
        assert len(approval.responses) == 1
    
    def test_approval_granted_all_approve(self):
        """Test that approval is granted when all approve."""
        workflow = ApprovalWorkflow()
        
        approval_id = workflow.create_approval(
            title="Test",
            description="Test",
            content={},
            requester_id="user1",
            approvers=["user2", "user3"]
        )
        
        # All approve
        workflow.submit_approval_response(
            approval_id=approval_id,
            approver_id="user2",
            decision=ApprovalDecision.APPROVE
        )
        workflow.submit_approval_response(
            approval_id=approval_id,
            approver_id="user3",
            decision=ApprovalDecision.APPROVE
        )
        
        approval = workflow.approvals[approval_id]
        assert approval.status == ApprovalStatus.APPROVED
        assert approval.final_decision_at is not None
    
    def test_approval_rejected_on_reject(self):
        """Test that approval is rejected if anyone rejects."""
        workflow = ApprovalWorkflow()
        
        approval_id = workflow.create_approval(
            title="Test",
            description="Test",
            content={},
            requester_id="user1",
            approvers=["user2", "user3"]
        )
        
        # One rejects
        workflow.submit_approval_response(
            approval_id=approval_id,
            approver_id="user2",
            decision=ApprovalDecision.REJECT
        )
        
        approval = workflow.approvals[approval_id]
        assert approval.status == ApprovalStatus.REJECTED
    
    def test_handoff(self):
        """Test handoff functionality."""
        workflow = ApprovalWorkflow()
        
        approval_id = workflow.create_approval(
            title="Test",
            description="Test",
            content={},
            requester_id="user1",
            approvers=["user2"]
        )
        
        # Approve
        workflow.submit_approval_response(
            approval_id=approval_id,
            approver_id="user2",
            decision=ApprovalDecision.APPROVE
        )
        
        # Handoff
        workflow.handoff(
            approval_id=approval_id,
            handoff_to="next_team",
            handoff_notes="Ready for implementation"
        )
        
        approval = workflow.approvals[approval_id]
        assert approval.handoff_completed is True
        assert approval.handoff_to == "next_team"


class TestCollaborationOrchestrator:
    """Test the complete Collaboration Orchestrator."""
    
    def test_create_session(self):
        """Test session creation."""
        orchestrator = CollaborationOrchestrator()
        
        session = orchestrator.create_session(
            name="Test Session",
            description="Test description",
            created_by="test_user"
        )
        
        assert session.name == "Test Session"
        assert session.recipe_id is not None
        assert session.phase.value == "ingredient_gathering"
    
    def test_add_ingredient_to_session(self):
        """Test adding ingredients to a session."""
        orchestrator = CollaborationOrchestrator()
        
        session = orchestrator.create_session(
            name="Test",
            description="Test",
            created_by="user"
        )
        
        ingredient = RecipeIngredient(
            type=IngredientType.REQUIREMENT,
            name="Test Requirement",
            description="Test",
            content="Content",
            added_by="user"
        )
        
        orchestrator.add_ingredient(session.session_id, ingredient)
        
        recipe = orchestrator.recipe_manager.get_recipe(session.recipe_id)
        assert len(recipe.ingredients) == 1
    
    @pytest.mark.asyncio
    async def test_press_cook_button(self):
        """Test pressing the cook button."""
        orchestrator = CollaborationOrchestrator()
        
        session = orchestrator.create_session(
            name="ML Optimization",
            description="Optimize machine learning model",
            created_by="user"
        )
        
        # Add ingredients
        ingredients = [
            RecipeIngredient(
                type=IngredientType.IDEA,
                name="Use adaptive learning rate",
                description="Adjust learning rate dynamically",
                content="Adaptive learning rate based on gradients",
                added_by="user"
            ),
            RecipeIngredient(
                type=IngredientType.REQUIREMENT,
                name="Fast convergence",
                description="Converge in < 100 epochs",
                content="Target: < 100 epochs",
                added_by="user"
            )
        ]
        
        for ingredient in ingredients:
            orchestrator.add_ingredient(session.session_id, ingredient)
        
        # Press cook button
        results = await orchestrator.press_cook_button(session.session_id)
        
        assert results["status"] == "success"
        assert results["phase"] == "review"
        assert results["expert_insights_count"] > 0
        assert results["suggested_formulas_count"] > 0
        assert session.final_solution is not None
    
    @pytest.mark.asyncio
    async def test_full_lifecycle(self):
        """Test the complete lifecycle from creation to handoff."""
        orchestrator = CollaborationOrchestrator()
        
        # Create session
        session = orchestrator.create_session(
            name="Complete Test",
            description="Test full lifecycle",
            created_by="user"
        )
        
        # Add ingredient
        ingredient = RecipeIngredient(
            type=IngredientType.IDEA,
            name="Test Idea",
            description="Test",
            content="Content",
            added_by="user"
        )
        orchestrator.add_ingredient(session.session_id, ingredient)
        
        # Cook
        cook_results = await orchestrator.press_cook_button(session.session_id)
        assert cook_results["status"] == "success"
        
        # Request approval
        approval_id = await orchestrator.request_approval(
            session.session_id,
            approvers=["approver1", "approver2"]
        )
        assert approval_id is not None
        
        # Approve
        workflow = orchestrator.approval_workflow
        workflow.submit_approval_response(
            approval_id=approval_id,
            approver_id="approver1",
            decision=ApprovalDecision.APPROVE
        )
        workflow.submit_approval_response(
            approval_id=approval_id,
            approver_id="approver2",
            decision=ApprovalDecision.APPROVE
        )
        
        # Handoff
        workflow.handoff(
            approval_id=approval_id,
            handoff_to="implementation_team"
        )
        
        # Verify
        approval_status = workflow.get_approval_status(approval_id)
        assert approval_status["status"] == "approved"
        assert approval_status["handoff_completed"] is True
