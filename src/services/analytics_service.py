from sqlalchemy import func
from src.database.db_connection import SessionLocal
from src.database.models.business import Ticket, Flight, Organization

class AnalyticsService:
    def get_airline_revenue_stats(self):
        session = SessionLocal()
        try:
            results = session.query(
                Organization.organization_name,
                func.count(Ticket.id).label("tickets_sold"),
                func.sum(Ticket.price).label("total_revenue")
            ).join(Flight, Flight.organization_id == Organization.id)\
             .join(Ticket, Ticket.flight_id == Flight.id)\
             .group_by(Organization.organization_name)\
             .all()
            
            return results
        finally:
            session.close()