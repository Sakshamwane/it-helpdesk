"""
Core helpdesk business logic: ticket operations, SLA, reports.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from models import Ticket, Priority, Status, VALID_TRANSITIONS
from config import CONFIG
from storage import TicketStorage
from exceptions import (
    ValidationError, InvalidCategoryError, InvalidPriorityError,
    InvalidStatusError, InvalidStatusTransitionError, TicketNotFoundError,
    EmptyInputError
)


class Helpdesk:
    """Main helpdesk controller."""

    def __init__(self, storage: TicketStorage = None):
        self.storage = storage or TicketStorage()
        self.tickets: List[Ticket] = []
        self._ticket_counter = 0
        self._load_tickets()

    # ──────────────────────────────────────────────────────────────────
    # Ticket ID Generation
    # ──────────────────────────────────────────────────────────────────
    def _generate_ticket_id(self) -> str:
        """Generate next ticket ID with zero-padded sequence."""
        self._ticket_counter += 1
        return f"{CONFIG.ticket_prefix}-{self._ticket_counter:04d}"

    def _update_counter_from_existing(self) -> None:
        """Sync counter with highest existing ticket number."""
        prefix = CONFIG.ticket_prefix + "-"
        max_num = 0
        for ticket in self.tickets:
            if ticket.ticket_id.startswith(prefix):
                try:
                    num = int(ticket.ticket_id[len(prefix):])
                    max_num = max(max_num, num)
                except ValueError:
                    pass
        self._ticket_counter = max_num

    # ──────────────────────────────────────────────────────────────────
    # Persistence
    # ──────────────────────────────────────────────────────────────────
    def _load_tickets(self) -> None:
        """Load tickets from storage and sync counter."""
        self.tickets = self.storage.load()
        self._update_counter_from_existing()

    def _save_tickets(self) -> None:
        """Save tickets to storage."""
        self.storage.save(self.tickets)

    # ──────────────────────────────────────────────────────────────────
    # Validation Helpers
    # ──────────────────────────────────────────────────────────────────
    def _validate_category(self, category: str) -> str:
        """Validate and normalize category."""
        if not category or not category.strip():
            raise EmptyInputError("Category")
        category = category.strip()
        # Case-insensitive match against allowed categories
        for allowed in CONFIG.categories:
            if allowed.lower() == category.lower():
                return allowed
        raise InvalidCategoryError(category, CONFIG.categories)

    def _validate_priority(self, priority: str) -> Priority:
        """Validate and parse priority."""
        if not priority or not priority.strip():
            raise EmptyInputError("Priority")
        try:
            return Priority.from_string(priority)
        except ValueError as e:
            raise InvalidPriorityError(priority) from e

    def _validate_status(self, status: str) -> Status:
        """Validate and parse status."""
        if not status or not status.strip():
            raise EmptyInputError("Status")
        try:
            return Status.from_string(status)
        except ValueError as e:
            raise InvalidStatusError(status) from e

    def _validate_description(self, description: str) -> str:
        """Validate description."""
        if not description or not description.strip():
            raise EmptyInputError("Description")
        return description.strip()

    def _validate_requester_name(self, name: str) -> str:
        """Validate requester name."""
        if not name or not name.strip():
            raise EmptyInputError("Requester name")
        return name.strip()

    # ──────────────────────────────────────────────────────────────────
    # Core Operations
    # ──────────────────────────────────────────────────────────────────
    def raise_ticket(
        self,
        category: str,
        priority: str,
        requester_name: str,
        description: str
    ) -> Ticket:
        """Create a new ticket with validation."""
        # Validate all inputs
        category = self._validate_category(category)
        priority = self._validate_priority(priority)
        requester_name = self._validate_requester_name(requester_name)
        description = self._validate_description(description)

        # Create ticket
        ticket_id = self._generate_ticket_id()
        ticket = Ticket(
            ticket_id=ticket_id,
            category=category,
            priority=priority,
            requester_name=requester_name,
            description=description,
        )

        self.tickets.append(ticket)
        self._save_tickets()
        return ticket

    def get_ticket(self, ticket_id: str) -> Ticket:
        """Get ticket by ID (case-insensitive), raise if not found."""
        ticket_id_normalized = ticket_id.strip().upper()
        for ticket in self.tickets:
            if ticket.ticket_id.upper() == ticket_id_normalized:
                return ticket
        raise TicketNotFoundError(ticket_id)

    def update_ticket_status(self, ticket_id: str, new_status: str) -> Ticket:
        """Update ticket status with transition validation."""
        ticket = self.get_ticket(ticket_id)
        target_status = self._validate_status(new_status)

        # Check valid transition
        allowed = VALID_TRANSITIONS.get(ticket.status, set())
        if target_status not in allowed:
            allowed_str = [s.value for s in allowed] if allowed else ["(none - terminal state)"]
            raise InvalidStatusTransitionError(
                ticket.status.value, target_status.value, allowed_str
            )

        ticket.update_status(target_status)
        self._save_tickets()
        return ticket

    def list_tickets(
        self,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Ticket]:
        """List tickets with optional filters."""
        filtered = self.tickets

        if category:
            cat_lower = category.lower()
            filtered = [t for t in filtered if t.category.lower() == cat_lower]

        if priority:
            pri = self._validate_priority(priority)
            filtered = [t for t in filtered if t.priority == pri]

        if status:
            stat = self._validate_status(status)
            filtered = [t for t in filtered if t.status == stat]

        # Sort by creation time (newest first)
        return sorted(filtered, key=lambda t: t.created_at, reverse=True)

    # ──────────────────────────────────────────────────────────────────
    # SLA & Reports
    # ──────────────────────────────────────────────────────────────────
    def get_sla_hours(self, priority: Priority) -> int:
        """Get SLA hours for a priority level."""
        return CONFIG.sla_hours.get(priority.value, 0)

    def check_sla_breach(self, ticket: Ticket) -> bool:
        """Check if a ticket has breached its SLA."""
        sla_hours = self.get_sla_hours(ticket.priority)
        return ticket.is_sla_breached(sla_hours)

    def get_sla_breached_tickets(self) -> List[Ticket]:
        """Get all open tickets that have breached SLA."""
        return [
            t for t in self.tickets
            if t.status not in (Status.RESOLVED, Status.CLOSED)
            and self.check_sla_breach(t)
        ]

    def get_summary(self) -> Dict[str, Any]:
        """Generate summary report using comprehensions."""
        # Counts by status
        by_status = {
            status.value: sum(1 for t in self.tickets if t.status == status)
            for status in Status
        }

        # Counts by category
        categories = sorted(set(t.category for t in self.tickets))
        by_category = {
            cat: sum(1 for t in self.tickets if t.category == cat)
            for cat in categories
        }

        # Counts by priority
        by_priority = {
            priority.value: sum(1 for t in self.tickets if t.priority == priority)
            for priority in Priority
        }

        # SLA breached tickets
        breached = self.get_sla_breached_tickets()

        return {
            "total_tickets": len(self.tickets),
            "by_status": by_status,
            "by_category": by_category,
            "by_priority": by_priority,
            "sla_breached_count": len(breached),
            "sla_breached_tickets": breached,
        }

    def print_summary(self) -> None:
        """Print formatted summary report."""
        summary = self.get_summary()

        print("\n" + "=" * 50)
        print("📊  SUMMARY REPORT")
        print("=" * 50)
        print(f"Total Tickets: {summary['total_tickets']}")

        print("\n📋 By Status:")
        for status, count in summary["by_status"].items():
            print(f"  {status:12}: {count}")

        print("\n🏷️  By Category:")
        for cat, count in summary["by_category"].items():
            print(f"  {cat:20}: {count}")

        print("\n⚡ By Priority:")
        for priority, count in summary["by_priority"].items():
            print(f"  {priority:8}: {count}")

        print(f"\n🚨 SLA Breached: {summary['sla_breached_count']}")
        if summary["sla_breached_tickets"]:
            print("   Breached Tickets:")
            for t in summary["sla_breached_tickets"]:
                sla_hours = self.get_sla_hours(t.priority)
                elapsed = t.hours_elapsed()
                print(f"   • {t.ticket_id} | {t.category} | {t.priority.value} | "
                      f"{elapsed:.1f}h elapsed (SLA: {sla_hours}h)")

    # ──────────────────────────────────────────────────────────────────
    # Utility
    # ──────────────────────────────────────────────────────────────────
    def get_config_info(self) -> Dict[str, Any]:
        """Get current configuration info."""
        return {
            "employee_id": "EMP1042",  # Hardcoded for display
            "ticket_prefix": CONFIG.ticket_prefix,
            "categories": CONFIG.categories,
            "sla_hours": CONFIG.sla_hours,
            "storage_format": CONFIG.storage_format,
            "storage_file": CONFIG.storage_file,
        }