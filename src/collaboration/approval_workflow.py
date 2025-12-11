"""
Approval Workflow

Manages the approval and handoff process for collaboration results.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import structlog

logger = structlog.get_logger(__name__)


class ApprovalStatus(str, Enum):
    """Status of an approval request."""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    CHANGES_REQUESTED = "changes_requested"
    CANCELLED = "cancelled"


class ApprovalDecision(str, Enum):
    """Individual approval decision."""
    APPROVE = "approve"
    REJECT = "reject"
    REQUEST_CHANGES = "request_changes"
    ABSTAIN = "abstain"


class ApproverResponse(BaseModel):
    """Response from an approver."""
    approver_id: str
    decision: ApprovalDecision
    comments: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ApprovalRequest(BaseModel):
    """Represents an approval request."""
    approval_id: str = Field(default_factory=lambda: str(__import__('uuid').uuid4()))
    title: str
    description: str
    content: Any
    requester_id: str
    approvers: List[str]
    status: ApprovalStatus = ApprovalStatus.PENDING
    responses: List[ApproverResponse] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    final_decision_at: Optional[datetime] = None
    handoff_completed: bool = False
    handoff_to: Optional[str] = None
    handoff_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ApprovalWorkflow:
    """
    Manages approval workflows for collaboration results.
    
    Handles the approval process including reviews, voting,
    decision-making, and handoff to next stages or teams.
    """
    
    def __init__(self):
        """Initialize the approval workflow manager."""
        self.approvals: Dict[str, ApprovalRequest] = {}
        self.logger = structlog.get_logger(__name__)
    
    def create_approval(
        self,
        title: str,
        description: str,
        content: Any,
        requester_id: str,
        approvers: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new approval request."""
        approval = ApprovalRequest(
            title=title,
            description=description,
            content=content,
            requester_id=requester_id,
            approvers=approvers,
            metadata=metadata or {}
        )
        
        self.approvals[approval.approval_id] = approval
        
        self.logger.info(
            "Approval request created",
            approval_id=approval.approval_id,
            title=title,
            approvers_count=len(approvers)
        )
        
        return approval.approval_id
    
    def submit_approval_response(
        self,
        approval_id: str,
        approver_id: str,
        decision: ApprovalDecision,
        comments: Optional[str] = None
    ) -> None:
        """Submit an approval response."""
        if approval_id not in self.approvals:
            raise ValueError(f"Approval not found: {approval_id}")
        
        approval = self.approvals[approval_id]
        
        # Check if approver is authorized
        if approver_id not in approval.approvers:
            raise ValueError(f"User {approver_id} is not an authorized approver")
        
        # Check if already responded
        for response in approval.responses:
            if response.approver_id == approver_id:
                raise ValueError(f"Approver {approver_id} has already responded")
        
        # Add response
        response = ApproverResponse(
            approver_id=approver_id,
            decision=decision,
            comments=comments
        )
        
        approval.responses.append(response)
        approval.updated_at = datetime.utcnow()
        approval.status = ApprovalStatus.IN_REVIEW
        
        self.logger.info(
            "Approval response submitted",
            approval_id=approval_id,
            approver_id=approver_id,
            decision=decision.value
        )
        
        # Check if decision can be made
        self._evaluate_approval_status(approval)
    
    def _evaluate_approval_status(self, approval: ApprovalRequest) -> None:
        """Evaluate if an approval decision can be made."""
        total_approvers = len(approval.approvers)
        total_responses = len(approval.responses)
        
        # Count decisions
        approves = sum(1 for r in approval.responses if r.decision == ApprovalDecision.APPROVE)
        rejects = sum(1 for r in approval.responses if r.decision == ApprovalDecision.REJECT)
        change_requests = sum(1 for r in approval.responses if r.decision == ApprovalDecision.REQUEST_CHANGES)
        
        # Decision logic
        if rejects > 0:
            # Any rejection leads to rejection
            approval.status = ApprovalStatus.REJECTED
            approval.final_decision_at = datetime.utcnow()
            self.logger.info("Approval rejected", approval_id=approval.approval_id)
        
        elif change_requests > 0:
            # Any change request requires changes
            approval.status = ApprovalStatus.CHANGES_REQUESTED
            approval.final_decision_at = datetime.utcnow()
            self.logger.info("Changes requested", approval_id=approval.approval_id)
        
        elif approves == total_approvers:
            # All approvers approved
            approval.status = ApprovalStatus.APPROVED
            approval.final_decision_at = datetime.utcnow()
            self.logger.info("Approval granted", approval_id=approval.approval_id)
        
        elif total_responses == total_approvers:
            # All responded but not all approved (some abstained)
            # Require majority approval
            if approves > total_approvers / 2:
                approval.status = ApprovalStatus.APPROVED
                approval.final_decision_at = datetime.utcnow()
                self.logger.info("Approval granted (majority)", approval_id=approval.approval_id)
            else:
                approval.status = ApprovalStatus.REJECTED
                approval.final_decision_at = datetime.utcnow()
                self.logger.info("Approval rejected (no majority)", approval_id=approval.approval_id)
    
    def handoff(
        self,
        approval_id: str,
        handoff_to: str,
        handoff_notes: Optional[str] = None
    ) -> None:
        """Perform handoff to next stage or team."""
        if approval_id not in self.approvals:
            raise ValueError(f"Approval not found: {approval_id}")
        
        approval = self.approvals[approval_id]
        
        if approval.status != ApprovalStatus.APPROVED:
            raise ValueError(f"Cannot handoff non-approved request. Status: {approval.status.value}")
        
        approval.handoff_to = handoff_to
        approval.handoff_at = datetime.utcnow()
        approval.handoff_completed = True
        
        if handoff_notes:
            approval.metadata["handoff_notes"] = handoff_notes
        
        self.logger.info(
            "Handoff completed",
            approval_id=approval_id,
            handoff_to=handoff_to
        )
    
    def get_approval_status(self, approval_id: str) -> Dict[str, Any]:
        """Get the status of an approval request."""
        if approval_id not in self.approvals:
            raise ValueError(f"Approval not found: {approval_id}")
        
        approval = self.approvals[approval_id]
        
        return {
            "approval_id": approval.approval_id,
            "title": approval.title,
            "status": approval.status.value,
            "requester_id": approval.requester_id,
            "total_approvers": len(approval.approvers),
            "responses_received": len(approval.responses),
            "created_at": approval.created_at.isoformat(),
            "updated_at": approval.updated_at.isoformat(),
            "final_decision_at": approval.final_decision_at.isoformat() if approval.final_decision_at else None,
            "handoff_completed": approval.handoff_completed,
            "handoff_to": approval.handoff_to,
            "responses": [
                {
                    "approver_id": r.approver_id,
                    "decision": r.decision.value,
                    "comments": r.comments,
                    "timestamp": r.timestamp.isoformat()
                }
                for r in approval.responses
            ]
        }
    
    def list_pending_approvals(self, approver_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List pending approval requests."""
        pending = [
            a for a in self.approvals.values()
            if a.status in [ApprovalStatus.PENDING, ApprovalStatus.IN_REVIEW]
        ]
        
        if approver_id:
            pending = [
                a for a in pending
                if approver_id in a.approvers and
                not any(r.approver_id == approver_id for r in a.responses)
            ]
        
        return [
            {
                "approval_id": a.approval_id,
                "title": a.title,
                "status": a.status.value,
                "created_at": a.created_at.isoformat()
            }
            for a in pending
        ]
