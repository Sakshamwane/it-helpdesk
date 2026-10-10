"""
CLI helpers for the IT Helpdesk System.
"""
from typing import List, Optional
from models import Ticket, Priority, Status, VALID_TRANSITIONS
from helpdesk import Helpdesk
from exceptions import HelpdeskError, ValidationError, TicketNotFoundError, InvalidStatusTransitionError


class CLI:
    """Command-line interface handler."""

    def __init__(self, helpdesk: Helpdesk):
        self.helpdesk = helpdesk

    # ──────────────────────────────────────────────────────────────────
    # Input Helpers
    # ──────────────────────────────────────────────────────────────────
    def prompt(self, message: str, default: str = None) -> str:
        """Prompt user for input with optional default."""
        if default:
            msg = f"{message} [{default}]: "
        else:
            msg = f"{message}: "
        value = input(msg).strip()
        return value if value else (default or "")

    def prompt_required(self, message: str) -> str:
        """Prompt for required input (loops until non-empty)."""
        while True:
            value = self.prompt(message)
            if value:
                return value
            print("❌ This field is required. Please enter a value.")

    def prompt_choice(self, message: str, choices: List[str], default: str = None) -> str:
        """Prompt for a choice from a list (case-insensitive)."""
        choices_lower = [c.lower() for c in choices]
        while True:
            value = self.prompt(message, default)
            if value.lower() in choices_lower:
                # Return the original case version
                return choices[choices_lower.index(value.lower())]
            print(f"❌ Invalid choice. Options: {', '.join(choices)}")

    def confirm(self, message: str, default: bool = False) -> bool:
        """Yes/No confirmation prompt."""
        suffix = " [Y/n]: " if default else " [y/N]: "
        while True:
            response = input(message + suffix).strip().lower()
            if not response:
                return default
            if response in ("y", "yes"):
                return True
            if response in ("n", "no"):
                return False
            print("Please enter 'y' or 'n'.")

    # ──────────────────────────────────────────────────────────────────
    # Menu Actions
    # ──────────────────────────────────────────────────────────────────
    def action_raise_ticket(self) -> None:
        """Raise a new ticket."""
        print("\n--- Raise New Ticket ---")
        print(f"Categories: {', '.join(self.helpdesk.helpdesk_config.categories) if hasattr(self.helpdesk, 'helpdesk_config') else 'See config'}")
        # Get config from helpdesk
        from config import CONFIG
        print(f"Categories: {', '.join(CONFIG.categories)}")
        print("Priorities: Low, Medium, High, Critical")

        try:
            category = self.prompt_required("Category")
            priority = self.prompt_choice("Priority", ["Low", "Medium", "High", "Critical"])
            requester = self.prompt_required("Requester Name")
            description = self.prompt_required("Description")

            ticket = self.helpdesk.raise_ticket(category, priority, requester, description)
            print(f"\n✅ Ticket {ticket.ticket_id} created successfully!")
            print(ticket.short_str())

        except ValidationError as e:
            print(f"❌ Validation Error: {e}")
        except HelpdeskError as e:
            print(f"❌ Error: {e}")

    def action_update_status(self) -> None:
        """Update ticket status."""
        print("\n--- Update Ticket Status ---")
        ticket_id = self.prompt_required("Ticket ID")

        try:
            ticket = self.helpdesk.get_ticket(ticket_id)
            print(f"Current status: {ticket.status.value}")
            print(f"Allowed transitions: {[s.value for s in VALID_TRANSITIONS.get(ticket.status, set())]}")

            if ticket.status == Status.CLOSED:
                print("❌ Cannot update closed ticket.")
                return

            new_status = self.prompt_choice(
                "New Status",
                [s.value for s in VALID_TRANSITIONS.get(ticket.status, set())]
            )

            updated = self.helpdesk.update_ticket_status(ticket_id, new_status)
            print(f"✅ Status updated: {ticket.status.value} → {updated.status.value}")

        except TicketNotFoundError as e:
            print(f"❌ {e}")
        except InvalidStatusTransitionError as e:
            print(f"❌ {e}")
        except HelpdeskError as e:
            print(f"❌ Error: {e}")

    def action_view_ticket(self) -> None:
        """View ticket details."""
        print("\n--- View Ticket Details ---")
        ticket_id = self.prompt_required("Ticket ID")

        try:
            ticket = self.helpdesk.get_ticket(ticket_id)
            print(ticket)

        except TicketNotFoundError as e:
            print(f"❌ {e}")

    def action_summary(self) -> None:
        """View summary report."""
        self.helpdesk.print_summary()

    def action_filter_tickets(self) -> None:
        """Filter/search tickets."""
        print("\n--- Filter Tickets ---")
        print("Leave blank to skip filter.")

        category = self.prompt("Category (optional)")
        priority = self.prompt("Priority (optional)")
        status = self.prompt("Status (optional)")

        tickets = self.helpdesk.list_tickets(
            category=category if category else None,
            priority=priority if priority else None,
            status=status if status else None,
        )

        print(f"\nFound {len(tickets)} ticket(s):")
        if tickets:
            for t in tickets:
                print(f"  {t.short_str()}")
        else:
            print("  (no tickets match the filters)")

    def action_list_all(self) -> None:
        """List all tickets."""
        tickets = self.helpdesk.list_tickets()
        print(f"\n--- All Tickets ({len(tickets)}) ---")
        if tickets:
            for t in tickets:
                print(f"  {t.short_str()}")
        else:
            print("  (no tickets)")

    # ──────────────────────────────────────────────────────────────────
    # Main Menu
    # ──────────────────────────────────────────────────────────────────
    def print_header(self) -> None:
        """Print program header."""
        from config import CONFIG
        print("\n" + "═" * 60)
        print("     IT HELPDESK TICKET MANAGEMENT SYSTEM")
        print(f"     Employee: EMP1042  |  Prefix: {CONFIG.ticket_prefix}  |  Format: {CONFIG.storage_format.upper()}")
        print("═" * 60)

    def print_menu(self) -> None:
        """Print main menu."""
        print("\n1. Raise Ticket")
        print("2. Update Ticket Status")
        print("3. View Ticket Details")
        print("4. View Summary Report")
        print("5. Filter/Search Tickets")
        print("6. List All Tickets")
        print("7. Exit")

    def run(self) -> None:
        """Main CLI loop."""
        self.print_header()

        while True:
            self.print_menu()
            choice = input("\nChoose an option (1-7): ").strip()

            try:
                if choice == "1":
                    self.action_raise_ticket()
                elif choice == "2":
                    self.action_update_status()
                elif choice == "3":
                    self.action_view_ticket()
                elif choice == "4":
                    self.action_summary()
                elif choice == "5":
                    self.action_filter_tickets()
                elif choice == "6":
                    self.action_list_all()
                elif choice == "7":
                    print("\n👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid option. Please choose 1-7.")

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")