#!/usr/bin/env python3
"""
IT Helpdesk Ticket Management System - Main Entry Point
"""
import sys
from helpdesk import Helpdesk
from cli import CLI
from storage import TicketStorage
from config import CONFIG


def main():
    """Application entry point."""
    try:
        # Initialize storage and helpdesk
        storage = TicketStorage()
        helpdesk = Helpdesk(storage)
        cli = CLI(helpdesk)

        # Run CLI
        cli.run()

    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()