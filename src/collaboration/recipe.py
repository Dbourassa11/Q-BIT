"""
Collaboration Recipe System

Implements the recipe metaphor for collaborative idea development.
Users add "ingredients" (concepts, requirements, ideas) which are mixed
together to create a comprehensive solution.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel, Field
import structlog

logger = structlog.get_logger(__name__)


class IngredientType(str, Enum):
    """Types of ingredients that can be added to a recipe."""
    IDEA = "idea"
    REQUIREMENT = "requirement"
    CONSTRAINT = "constraint"
    RESOURCE = "resource"
    SPECIFICATION = "specification"
    DATA = "data"
    ALGORITHM = "algorithm"
    FORMULA = "formula"
    SCHEMA = "schema"


class IngredientQuality(str, Enum):
    """Quality assessment for ingredients."""
    RAW = "raw"
    REFINED = "refined"
    VALIDATED = "validated"
    APPROVED = "approved"


class RecipeIngredient(BaseModel):
    """Represents a single ingredient in the collaboration recipe."""
    ingredient_id: str = Field(default_factory=lambda: str(__import__('uuid').uuid4()))
    type: IngredientType
    name: str
    description: str
    content: Any
    quality: IngredientQuality = IngredientQuality.RAW
    added_by: str
    added_at: datetime = Field(default_factory=datetime.utcnow)
    tags: Set[str] = Field(default_factory=set)
    dependencies: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    validation_scores: Dict[str, float] = Field(default_factory=dict)


class RecipePhase(str, Enum):
    """Phases in the recipe development lifecycle."""
    CONCEPTION = "conception"  # Initial idea gathering
    MIXING = "mixing"  # Combining ingredients
    COOKING = "cooking"  # Cross-domain collaboration and processing
    TASTING = "tasting"  # Review and evaluation
    SERVING = "serving"  # Ready for approval
    COMPLETED = "completed"  # Approved and finalized


class CollaborationRecipe(BaseModel):
    """
    Collaboration Recipe - the complete mix of ideas and requirements.
    
    Implements a recipe metaphor where users add ingredients (ideas, requirements)
    that are mixed together and processed by expert agents to create solutions.
    """
    recipe_id: str = Field(default_factory=lambda: str(__import__('uuid').uuid4()))
    name: str
    description: str
    phase: RecipePhase = RecipePhase.CONCEPTION
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # The ingredients
    ingredients: List[RecipeIngredient] = Field(default_factory=list)
    
    # Processing results
    mixed_results: Dict[str, Any] = Field(default_factory=dict)
    expert_insights: List[Dict[str, Any]] = Field(default_factory=list)
    suggested_formulas: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Metadata
    tags: Set[str] = Field(default_factory=set)
    complexity_score: float = 0.0
    quality_score: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RecipeManager:
    """
    Manages collaboration recipes throughout their lifecycle.
    
    Handles ingredient addition, mixing, cooking (expert processing),
    and final approval.
    """
    
    def __init__(self):
        """Initialize the recipe manager."""
        self.recipes: Dict[str, CollaborationRecipe] = {}
        self.logger = structlog.get_logger(__name__)
    
    def create_recipe(
        self,
        name: str,
        description: str,
        created_by: str,
        tags: Optional[Set[str]] = None
    ) -> CollaborationRecipe:
        """Create a new collaboration recipe."""
        recipe = CollaborationRecipe(
            name=name,
            description=description,
            created_by=created_by,
            tags=tags or set()
        )
        
        self.recipes[recipe.recipe_id] = recipe
        
        self.logger.info(
            "Recipe created",
            recipe_id=recipe.recipe_id,
            name=name,
            created_by=created_by
        )
        
        return recipe
    
    def add_ingredient(
        self,
        recipe_id: str,
        ingredient: RecipeIngredient
    ) -> None:
        """Add an ingredient to a recipe."""
        if recipe_id not in self.recipes:
            raise ValueError(f"Recipe not found: {recipe_id}")
        
        recipe = self.recipes[recipe_id]
        
        if recipe.phase not in [RecipePhase.CONCEPTION, RecipePhase.MIXING]:
            raise ValueError(
                f"Cannot add ingredients in phase: {recipe.phase.value}"
            )
        
        recipe.ingredients.append(ingredient)
        
        self.logger.info(
            "Ingredient added",
            recipe_id=recipe_id,
            ingredient_type=ingredient.type.value,
            ingredient_name=ingredient.name
        )
    
    def remove_ingredient(
        self,
        recipe_id: str,
        ingredient_id: str
    ) -> None:
        """Remove an ingredient from a recipe."""
        if recipe_id not in self.recipes:
            raise ValueError(f"Recipe not found: {recipe_id}")
        
        recipe = self.recipes[recipe_id]
        
        recipe.ingredients = [
            ing for ing in recipe.ingredients
            if ing.ingredient_id != ingredient_id
        ]
        
        self.logger.info(
            "Ingredient removed",
            recipe_id=recipe_id,
            ingredient_id=ingredient_id
        )
    
    def transition_to_mixing(self, recipe_id: str) -> None:
        """Transition recipe to mixing phase."""
        if recipe_id not in self.recipes:
            raise ValueError(f"Recipe not found: {recipe_id}")
        
        recipe = self.recipes[recipe_id]
        
        if recipe.phase != RecipePhase.CONCEPTION:
            raise ValueError(
                f"Cannot transition to mixing from phase: {recipe.phase.value}"
            )
        
        recipe.phase = RecipePhase.MIXING
        
        self.logger.info("Recipe transitioned to mixing", recipe_id=recipe_id)
    
    async def mix_ingredients(self, recipe_id: str) -> Dict[str, Any]:
        """
        Mix the ingredients together to prepare for cooking.
        
        This analyzes the ingredients and determines what processing is needed.
        """
        if recipe_id not in self.recipes:
            raise ValueError(f"Recipe not found: {recipe_id}")
        
        recipe = self.recipes[recipe_id]
        
        if recipe.phase != RecipePhase.MIXING:
            raise ValueError(f"Recipe is not in mixing phase: {recipe.phase.value}")
        
        # Analyze ingredients
        ingredient_types = {}
        for ingredient in recipe.ingredients:
            ingredient_types[ingredient.type.value] = ingredient_types.get(
                ingredient.type.value, 0
            ) + 1
        
        # Calculate complexity
        recipe.complexity_score = len(recipe.ingredients) * 0.1
        if len(ingredient_types) > 3:
            recipe.complexity_score += 0.3
        
        # Prepare mixed results
        mixed_results = {
            "total_ingredients": len(recipe.ingredients),
            "ingredient_types": ingredient_types,
            "complexity_score": recipe.complexity_score,
            "ready_for_cooking": True,
            "mixed_at": datetime.utcnow().isoformat()
        }
        
        recipe.mixed_results = mixed_results
        
        self.logger.info(
            "Ingredients mixed",
            recipe_id=recipe_id,
            complexity=recipe.complexity_score
        )
        
        return mixed_results
    
    def get_recipe(self, recipe_id: str) -> Optional[CollaborationRecipe]:
        """Get a recipe by ID."""
        return self.recipes.get(recipe_id)
    
    def list_recipes(
        self,
        phase: Optional[RecipePhase] = None,
        created_by: Optional[str] = None
    ) -> List[CollaborationRecipe]:
        """List recipes with optional filtering."""
        recipes = list(self.recipes.values())
        
        if phase:
            recipes = [r for r in recipes if r.phase == phase]
        
        if created_by:
            recipes = [r for r in recipes if r.created_by == created_by]
        
        return recipes
    
    def get_recipe_summary(self, recipe_id: str) -> Dict[str, Any]:
        """Get a summary of a recipe."""
        recipe = self.get_recipe(recipe_id)
        if not recipe:
            raise ValueError(f"Recipe not found: {recipe_id}")
        
        return {
            "recipe_id": recipe.recipe_id,
            "name": recipe.name,
            "phase": recipe.phase.value,
            "created_by": recipe.created_by,
            "created_at": recipe.created_at.isoformat(),
            "ingredient_count": len(recipe.ingredients),
            "complexity_score": recipe.complexity_score,
            "quality_score": recipe.quality_score,
            "has_expert_insights": len(recipe.expert_insights) > 0,
            "has_formulas": len(recipe.suggested_formulas) > 0
        }
