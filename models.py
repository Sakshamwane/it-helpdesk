"""
Ticket model and data structures for IT Helpdesk System.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class Priority(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

    @classmethod
    def from_string(cls, value: str) -> "Priority":
        """Parse priority from string, case-insensitive."""
        for p in cls:
            if p.value.lower() == value.strip().lower():
                return p
        raise ValueError(f"Invalid priority: {value}. Must be one of: {[p.value for p in cls]}")


class Status(Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    CLOSED = "Closed"

    @classmethod
    def from_string(cls, value: str) -> "Status":
        """Parse status from string, case-insensitive."""
        for s in cls:
            if s.value.lower() == value.strip().lower():
                return s
        raise ValueError(f"Invalid status: {value}. Must be one of: {[s.value for s in cls]}")


# Valid status transitions: current -> allowed next statuses
VALID_TRANSITIONS = {
    Status.OPEN: {Status.IN_PROGRESS},
    Status.IN_PROGRESS: {Status.RESOLVED, Status.OPEN},  # Can reopen
    Status.RESOLVED: {Status.CLOSED, Status.IN_PROGRESS},  # Can reopen
    Status.CLOSED: set(),  # Terminal state
}


@dataclass
class Ticket:
    """Represents an IT support ticket."""
    ticket_id: str
    category: str
    priority: Priority
    requester_name: str
    description: str
    created_at: datetime = field(default_factory=datetime.now)
    status: Status = field(default=Status.OPEN)
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate ticket data after initialization."""
        if not self.ticket_id:
            raise ValueError("Ticket ID cannot be empty")
        if not self.category:
            raise ValueError("Category cannot be empty")
        if not self.requester_name or not self.requester_name.strip():
            raise ValueError("Requester name cannot be empty")
        if not self.description or not self.description.strip():
            raise ValueError("Description cannot be empty")
        if not isinstance(self.priority, Priority):
            raise TypeError("Priority must be a Priority enum")
        if not isinstance(self.status, Status):
            raise TypeError("Status must be a Status enum")

    def update_status(self, new_status: Status) -> None:
        """Update ticket status with transition validation."""
        if new_status not in VALID_TRANSITIONS.get(self.status, set()):
            raise ValueError(
                f"Invalid status transition: {self.status.value} → {new_status.value}. "
                f"Allowed: {[s.value for s in VALID_TRANSITIONS.get(self.status, set())]}"
            )
        self.status = new_status
        self.updated_at = datetime.now()

    def is_sla_breached(self, sla_hours: int) -> bool:
        """Check if ticket has breached its SLA."""
        if self.status in (Status.RESOLVED, Status.CLOSED):
            return False
        elapsed_hours = (datetime.now() - self.created_at).total_seconds() / 3600
        return elapsed_hours > sla_hours

    def hours_elapsed(self) -> float:
        """Return hours elapsed since creation."""
        return (datetime.now() - self.created_at).total_seconds() / 3600

    def to_dict(self) -> dict:
        """Convert ticket to dictionary for serialization."""
        return {
            "ticket_id": self.ticket_id,
            "category": self.category,
            "priority": self.priority.value,
            "requester_name": self.requester_name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "status": self.status.value,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Ticket":
        """Create ticket from dictionary."""
        return cls(
            ticket_id=data["ticket_id"],
            category=data["category"],
            priority=Priority.from_string(data["priority"]),
            requester_name=data["requester_name"],
            description=data["description"],
            created_at=datetime.fromisoformat(data["created_at"]),
            status=Status.from_string(data["status"]),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
        )

    def __str__(self) -> str:
        """Human-readable ticket display."""
        return (
            f"{'='*60}\n"
            f"Ticket ID:     {self.ticket_id}\n"
            f"Category:      {self.category}\n"
            f"Priority:      {self.priority.value}\n"
            f"Requester:     {self.requester_name}\n"
            f"Description:   {self.description}\n"
            f"Status:        {self.status.value}\n"
            f"Created:       {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Updated:       {self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else 'N/A'}\n"
            f"Hours Elapsed: {self.hours_elapsed():.1f}h\n"
            f"{'='*60}"
        )

    def short_str(self) -> str:
        """Compact one-line representation."""
        return f"[{self.ticket_id}] {self.category} | {self.priority.value:8} | {self.status.value:12} | {self.requester_name}"