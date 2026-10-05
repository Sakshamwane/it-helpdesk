"""
Personalized configuration for the IT Helpdesk System.
Run get_my_parameters() with your employee ID to generate your unique config.
"""
import hashlib
import random
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Config:
    """Configuration derived from employee ID."""
    categories: List[str]
    sla_hours: Dict[str, int]
    ticket_prefix: str
    storage_format: str = "json"  # "json" or "csv"
    storage_file: str = "tickets.json"


def get_my_parameters(employee_id: str) -> Config:
    """
    Deterministic, unique parameters derived from the employee ID.
    Every joiner gets a different set of ticket categories, SLA
    thresholds, and a ticket-ID prefix so no two submissions look the same.
    """
    seed = int(hashlib.sha256(employee_id.encode()).hexdigest(), 16) % (2**31)
    rng = random.Random(seed)
    all_categories = [
        'Hardware', 'Software', 'Network', 'Access Request',
        'Email', 'Printer', 'VPN', 'Application Bug',
        'Account Lockout', 'Data Backup'
    ]
    
    categories = rng.sample(all_categories, 5)
    sla_hours = {
        'Critical': rng.randint(2, 4),
        'High': rng.randint(6, 12),
        'Medium': rng.randint(24, 48),
        'Low': rng.randint(72, 120),
    }
    ticket_prefix = rng.choice(['TCK', 'INC', 'REQ', 'SR'])
    
    return Config(
        categories=categories,
        sla_hours=sla_hours,
        ticket_prefix=ticket_prefix,
    )


# ──────────────────────────────────────────────────────────────────────
# 👇 REPLACE 'EMP1042' WITH YOUR ACTUAL EMPLOYEE ID
# ──────────────────────────────────────────────────────────────────────
MY_EMPLOYEE_ID = "56036390"
CONFIG = get_my_parameters(MY_EMPLOYEE_ID)


def print_config() -> None:
    """Print the personalized configuration."""
    print(f"Employee ID: {MY_EMPLOYEE_ID}")
    print(f"Ticket Prefix: {CONFIG.ticket_prefix}")
    print(f"Categories ({len(CONFIG.categories)}): {', '.join(CONFIG.categories)}")
    print("SLA Hours:")
    for priority, hours in CONFIG.sla_hours.items():
        print(f"  {priority:8}: {hours}h")
    print(f"Storage: {CONFIG.storage_format.upper()} ({CONFIG.storage_file})")


if __name__ == "__main__":
    print_config()