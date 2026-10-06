"""
Custom exceptions for the IT Helpdesk System.
"""


class HelpdeskError(Exception):
    """Base exception for helpdesk errors."""
    pass


class ValidationError(HelpdeskError):
    """Raised when input validation fails."""
    pass


class InvalidCategoryError(ValidationError):
    """Raised when category is not in allowed list."""
    def __init__(self, category: str, allowed: list):
        self.category = category
        self.allowed = allowed
        super().__init__(
            f"Invalid category: '{category}'. Allowed: {', '.join(allowed)}"
        )


class InvalidPriorityError(ValidationError):
    """Raised when priority is not valid."""
    def __init__(self, priority: str):
        self.priority = priority
        super().__init__(
            f"Invalid priority: '{priority}'. Must be: Low, Medium, High, Critical"
        )


class InvalidStatusError(ValidationError):
    """Raised when status is not valid."""
    def __init__(self, status: str):
        self.status = status
        super().__init__(
            f"Invalid status: '{status}'. Must be: Open, In Progress, Resolved, Closed"
        )


class InvalidStatusTransitionError(ValidationError):
    """Raised when status transition is not allowed."""
    def __init__(self, current: str, target: str, allowed: list):
        self.current = current
        self.target = target
        self.allowed = allowed
        super().__init__(
            f"Invalid transition: {current} → {target}. Allowed: {', '.join(allowed)}"
        )


class TicketNotFoundError(HelpdeskError):
    """Raised when ticket ID is not found."""
    def __init__(self, ticket_id: str):
        self.ticket_id = ticket_id
        super().__init__(f"Ticket not found: {ticket_id}")


class StorageError(HelpdeskError):
    """Raised when storage operations fail."""
    pass


class EmptyInputError(ValidationError):
    """Raised when required input is empty."""
    def __init__(self, field: str):
        self.field = field
        super().__init__(f"{field} cannot be empty")