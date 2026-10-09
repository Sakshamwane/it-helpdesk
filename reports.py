"""
SLA breach detection and summary reports.
"""
from datetime import datetime
from typing import List, Dict, Any
from models import Ticket, Priority, Status
from config import CONFIG

class ReportGenerator:
    """Generates summary reports and SLA breach detection."""
    
    def __init__(self, sla_hours: dict = None):
        self.sla_hours = sla_hours or CONFIG.sla_hours
    
    def get_sla_hours(self, priority: Priority) -> int:
        return self.sla_hours.get(priority.value, 0)
    
    def check_sla_breach(self, ticket: Ticket) -> bool:
        if ticket.status in (Status.RESOLVED, Status.CLOSED):
            return False
        elapsed_hours = (datetime.now() - ticket.created_at).total_seconds() / 3600
        return elapsed_hours > self.get_sla_hours(ticket.priority)
    
    def get_breached_tickets(self, tickets: List[Ticket]) -> List[Ticket]:
        return [t for t in tickets 
                if t.status not in (Status.RESOLVED, Status.CLOSED)
                and self.check_sla_breach(t)]
    
    def generate_summary(self, tickets: List[Ticket]) -> Dict[str, Any]:
        """Generate summary using comprehensions."""
        by_status = {s.value: sum(1 for t in tickets if t.status == s) for s in Status}
        by_category = {cat: sum(1 for t in tickets if t.category == cat) 
                       for cat in sorted(set(t.category for t in tickets))}
        by_priority = {p.value: sum(1 for t in tickets if t.priority == p) for p in Priority}
        breached = self.get_breached_tickets(tickets)
        
        return {
            "total": len(tickets),
            "by_status": by_status,
            "by_category": by_category,
            "by_priority": by_priority,
            "sla_breached": breached,
        }
