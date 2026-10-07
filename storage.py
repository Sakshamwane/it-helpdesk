"""
Storage layer for ticket persistence (JSON and CSV).
"""
import json
import csv
import os
from pathlib import Path
from typing import List, Dict, Any
from models import Ticket
from config import CONFIG
from exceptions import StorageError


class TicketStorage:
    """Handles loading and saving tickets to file."""

    def __init__(self, filepath: str = None, format: str = None):
        self.filepath = filepath or CONFIG.storage_file
        self.format = (format or CONFIG.storage_format).lower()
        if self.format not in ("json", "csv"):
            raise ValueError(f"Unsupported format: {self.format}. Use 'json' or 'csv'")

    def save(self, tickets: List[Ticket]) -> None:
        """Save tickets to file."""
        try:
            if self.format == "json":
                self._save_json(tickets)
            else:
                self._save_csv(tickets)
        except Exception as e:
            raise StorageError(f"Failed to save tickets: {e}")

    def load(self) -> List[Ticket]:
        """Load tickets from file."""
        if not os.path.exists(self.filepath):
            return []
        try:
            if self.format == "json":
                return self._load_json()
            else:
                return self._load_csv()
        except Exception as e:
            raise StorageError(f"Failed to load tickets: {e}")

    # ──────────────────────────────────────────────────────────────────
    # JSON Implementation
    # ──────────────────────────────────────────────────────────────────
    def _save_json(self, tickets: List[Ticket]) -> None:
        data = [t.to_dict() for t in tickets]
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _load_json(self) -> List[Ticket]:
        with open(self.filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [Ticket.from_dict(item) for item in data]

    # ──────────────────────────────────────────────────────────────────
    # CSV Implementation
    # ──────────────────────────────────────────────────────────────────
    def _save_csv(self, tickets: List[Ticket]) -> None:
        if not tickets:
            # Write header only
            with open(self.filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "ticket_id", "category", "priority", "requester_name",
                    "description", "created_at", "status", "updated_at"
                ])
            return

        fieldnames = [
            "ticket_id", "category", "priority", "requester_name",
            "description", "created_at", "status", "updated_at"
        ]
        with open(self.filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for ticket in tickets:
                row = ticket.to_dict()
                # Convert None to empty string for CSV
                row = {k: (v if v is not None else "") for k, v in row.items()}
                writer.writerow(row)

    def _load_csv(self) -> List[Ticket]:
        tickets = []
        with open(self.filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert empty strings back to None for updated_at
                if row.get("updated_at") == "":
                    row["updated_at"] = None
                tickets.append(Ticket.from_dict(row))
        return tickets

    # ──────────────────────────────────────────────────────────────────
    # Utility Methods
    # ──────────────────────────────────────────────────────────────────
    def backup(self, tickets: List[Ticket]) -> str:
        """Create a timestamped backup."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{self.filepath}.backup_{timestamp}"
        if self.format == "json":
            self._save_json(tickets)
        else:
            self._save_csv(tickets)
        # Copy to backup
        import shutil
        shutil.copy2(self.filepath, backup_path)
        return backup_path

    def get_file_info(self) -> Dict[str, Any]:
        """Get storage file information."""
        if not os.path.exists(self.filepath):
            return {"exists": False, "path": self.filepath, "format": self.format}
        stat = os.stat(self.filepath)
        return {
            "exists": True,
            "path": self.filepath,
            "format": self.format,
            "size_bytes": stat.st_size,
            "modified": stat.st_mtime,
        }