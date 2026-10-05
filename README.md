# IT Helpdesk Ticket Management System (CLI)

A command-line helpdesk system for logging, tracking, updating, and resolving IT support tickets with SLA breach detection.

## Features

- **Raise tickets** with auto-generated IDs, personalized categories, and priorities
- **Update ticket status** through defined flow: Open → In Progress → Resolved → Closed
- **SLA breach detection** based on personalized SLA thresholds per priority
- **View summaries** with ticket counts by status, category, and SLA-breached tickets
- **Filter/search** tickets by category, priority, or status
- **Persistence** to JSON/CSV file (survives program restarts)
- **Personalized configuration** derived from employee ID

## Quick Start

### 1. Configure Your Employee ID

Edit `config.py` and replace `EMP1042` with your employee ID:

```python
MY_EMPLOYEE_ID = "YOUR_EMPLOYEE_ID"
```

Then run to see your personalized config:
```bash
python config.py
```

### 2. Run the Helpdesk

```bash
python main.py
```

## Menu Options

| Option | Description |
|--------|-------------|
| 1 | Raise a new ticket |
| 2 | Update ticket status |
| 3 | View ticket details |
| 4 | View summary report |
| 5 | Filter/Search tickets |
| 6 | List all tickets |
| 7 | Exit |

## Project Structure

```
├── config.py          # Personalized configuration (employee ID → categories, SLA, prefix)
├── models.py          # Ticket class, Priority/Status enums, validation
├── storage.py         # JSON/CSV persistence layer
├── exceptions.py      # Custom exceptions
├── helpdesk.py        # Core business logic (ticket operations, SLA, reports)
├── cli.py             # Command-line interface helpers
├── main.py            # Entry point, main menu loop
├── tickets.json       # Auto-generated ticket storage
└── README.md          # This file
```

## Personalized Parameters

Your unique configuration (derived from employee ID):

- **Ticket Prefix**: e.g., `INC-0001`, `TCK-0001`, `REQ-0001`, `SR-0001`
- **5 Categories**: Randomly selected from 10 possible categories
- **SLA Hours**: Unique thresholds per priority level

Run `python config.py` to see yours.

## Example Usage

```
$ python main.py

╔══════════════════════════════════════════════════════════════╗
║          IT HELPDESK TICKET MANAGEMENT SYSTEM                ║
║                    Employee: EMP1042                         ║
║                    Prefix: INC | Format: JSON                ║
╚══════════════════════════════════════════════════════════════╝

1. Raise Ticket
2. Update Ticket Status
3. View Ticket Details
4. View Summary Report
5. Filter/Search Tickets
6. List All Tickets
7. Exit

Choose an option (1-7): 1

--- Raise New Ticket ---
Categories: Network, Printer, VPN, Email, Data Backup
Priority [Low/Medium/High/Critical]: High
Category: VPN
Requester Name: John Doe
Description: Cannot connect to corporate VPN from home office

✅ Ticket INC-0001 created successfully!

[INC-0001] VPN         | High       | Open          | John Doe
```

## Requirements

- Python 3.8+

## Design Decisions

1. **Dataclasses for Ticket model** - Clean, type-safe, auto-generates `__init__`, `__repr__`
2. **Enum for Priority/Status** - Type safety, prevents invalid values, IDE autocomplete
3. **Config class with deterministic generation** - Reproducible, no external config files needed
4. **Separation of concerns** - Models, storage, business logic, CLI in separate modules
5. **JSON persistence** - Human-readable, easy to debug, standard library support

## Git Workflow (Team of 2)

Each team member makes 3 pushes to the shared repository:

| Push | Branch | Focus |
|------|--------|-------|
| 1 | `phase1-setup` / `phase1-storage` | Models, config, exceptions, storage |
| 2 | `phase2-core` / `phase2-status` | Ticket creation, status transitions |
| 3 | `phase3-sla` / `phase3-cli` | SLA detection, reports, full CLI |

## License

Assessment submission - Educational use.