"""
Collaboration Lifecycle Demo

Demonstrates the complete lifecycle of collaboration from conception to approval.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.collaboration.session import CollaborationOrchestrator
from src.collaboration.recipe import RecipeIngredient, IngredientType
from src.collaboration.approval_workflow import ApprovalDecision


async def demo_collaboration_lifecycle():
    """
    Demo the complete collaboration lifecycle:
    1. Create session
    2. Add ingredients (ideas, requirements)
    3. Press "cook button" for expert collaboration
    4. Review results
    5. Request approval
    6. Handoff
    """
    
    print("=" * 80)
    print("🚀 Q-BIT Collaboration Lifecycle Demo")
    print("=" * 80)
    print()
    
    # Create the orchestrator
    orchestrator = CollaborationOrchestrator()
    
    # Step 1: Create a collaboration session
    print("📝 Step 1: Creating collaboration session...")
    session = orchestrator.create_session(
        name="Optimize Machine Learning Model",
        description="Develop an advanced optimization algorithm for deep learning models",
        created_by="user_alice",
        tags=["machine-learning", "optimization", "algorithms"]
    )
    print(f"   ✓ Session created: {session.session_id}")
    print(f"   ✓ Phase: {session.phase.value}")
    print()
    
    # Step 2: Add ingredients (ideas, requirements, constraints)
    print("🥘 Step 2: Adding ingredients to the recipe...")
    
    ingredients = [
        RecipeIngredient(
            type=IngredientType.IDEA,
            name="Adaptive Learning Rate",
            description="Use an adaptive learning rate that adjusts based on gradient magnitude",
            content="Implement dynamic learning rate adjustment using gradient statistics",
            added_by="user_alice"
        ),
        RecipeIngredient(
            type=IngredientType.REQUIREMENT,
            name="Fast Convergence",
            description="Model must converge in less than 100 epochs",
            content="Target convergence: < 100 epochs",
            added_by="user_alice"
        ),
        RecipeIngredient(
            type=IngredientType.CONSTRAINT,
            name="Memory Efficient",
            description="Must work within 8GB GPU memory",
            content="Max memory: 8GB GPU RAM",
            added_by="user_alice"
        ),
        RecipeIngredient(
            type=IngredientType.ALGORITHM,
            name="Momentum-based Optimization",
            description="Consider momentum for smoother convergence",
            content="Use momentum coefficient β=0.9",
            added_by="user_alice"
        ),
        RecipeIngredient(
            type=IngredientType.FORMULA,
            name="Loss Function",
            description="Cross-entropy loss for classification",
            content="L = -Σ y*log(ŷ)",
            added_by="user_alice"
        )
    ]
    
    for ingredient in ingredients:
        orchestrator.add_ingredient(session.session_id, ingredient)
        print(f"   ✓ Added {ingredient.type.value}: {ingredient.name}")
    print()
    
    # Step 3: Press the "COOK BUTTON" 🔥
    print("🔥 Step 3: Pressing the COOK BUTTON!")
    print("   (Activating cross-domain expert collaboration...)")
    print()
    
    cook_results = await orchestrator.press_cook_button(session.session_id)
    
    print("   ✅ COOKING COMPLETED!")
    print(f"   • Phase: {cook_results['phase']}")
    print(f"   • Expert insights received: {cook_results['expert_insights_count']}")
    print(f"   • Formulas suggested: {cook_results['suggested_formulas_count']}")
    print()
    
    # Step 4: Review the results
    print("📊 Step 4: Reviewing collaboration results...")
    print()
    
    status = orchestrator.get_session_status(session.session_id)
    
    print("   Expert Contributions:")
    if session.final_solution and "expert_contributions" in session.final_solution:
        expert_contrib = session.final_solution["expert_contributions"]
        print(f"   • Domains consulted: {', '.join(expert_contrib['domains_consulted'])}")
        print(f"   • Average confidence: {expert_contrib['average_confidence']:.2%}")
        print()
        print("   Key Recommendations:")
        for rec in expert_contrib['key_recommendations']:
            print(f"   • [{rec['domain']}] {rec['insight'][:80]}...")
            if rec['algorithms']:
                print(f"     Suggested algorithms: {', '.join(rec['algorithms'])}")
    print()
    
    print("   Mathematical Foundations:")
    if session.final_solution and "mathematical_foundations" in session.final_solution:
        math_found = session.final_solution["mathematical_foundations"]
        print(f"   • Formulas suggested: {math_found['formulas_suggested']}")
        print(f"   • Categories: {', '.join(math_found['categories'])}")
        print()
        print("   Key Formulas:")
        for formula in math_found['key_formulas']:
            print(f"   • {formula['name']}")
            print(f"     Formula: {formula['notation']}")
            print(f"     Complexity: {formula['complexity']}")
        print()
    
    # Step 5: Request approval
    print("✋ Step 5: Requesting approval...")
    approvers = ["manager_bob", "tech_lead_carol", "architect_dave"]
    approval_id = await orchestrator.request_approval(
        session.session_id,
        approvers=approvers
    )
    print(f"   ✓ Approval request created: {approval_id}")
    print(f"   ✓ Approvers: {', '.join(approvers)}")
    print()
    
    # Simulate approval responses
    print("📝 Step 6: Simulating approval responses...")
    workflow = orchestrator.approval_workflow
    
    # Manager approves
    workflow.submit_approval_response(
        approval_id=approval_id,
        approver_id="manager_bob",
        decision=ApprovalDecision.APPROVE,
        comments="Looks good, the approach is solid."
    )
    print("   ✓ manager_bob: APPROVED")
    
    # Tech lead approves
    workflow.submit_approval_response(
        approval_id=approval_id,
        approver_id="tech_lead_carol",
        decision=ApprovalDecision.APPROVE,
        comments="Technical approach is sound. Ready for implementation."
    )
    print("   ✓ tech_lead_carol: APPROVED")
    
    # Architect approves
    workflow.submit_approval_response(
        approval_id=approval_id,
        approver_id="architect_dave",
        decision=ApprovalDecision.APPROVE,
        comments="Architecture aligns with our standards."
    )
    print("   ✓ architect_dave: APPROVED")
    print()
    
    approval_status = workflow.get_approval_status(approval_id)
    print(f"   🎉 Final Status: {approval_status['status'].upper()}")
    print()
    
    # Step 7: Handoff
    print("🤝 Step 7: Performing handoff...")
    workflow.handoff(
        approval_id=approval_id,
        handoff_to="implementation_team",
        handoff_notes="Approved for implementation. See final solution for details."
    )
    print("   ✓ Handoff completed to: implementation_team")
    print()
    
    # Final summary
    print("=" * 80)
    print("✨ COLLABORATION LIFECYCLE COMPLETED SUCCESSFULLY")
    print("=" * 80)
    print()
    print("Summary:")
    print(f"  • Session: {session.name}")
    print(f"  • Ingredients: {len(ingredients)}")
    print(f"  • Expert insights: {len(session.expert_insights)}")
    print(f"  • Formulas suggested: {len(session.suggested_formulas)}")
    print(f"  • Approval status: {approval_status['status']}")
    print(f"  • Handoff completed: ✓")
    print()
    print("The complete collaboration lifecycle has been demonstrated successfully!")
    print("From conception → mixing → expert collaboration → approval → handoff")
    print()


if __name__ == "__main__":
    asyncio.run(demo_collaboration_lifecycle())
