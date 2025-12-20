import csv
import json
import os
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

    def export_stats_csv(self, filename="analytics_export.csv"):
        data = self.get_airline_revenue_stats()
        try:
            with open(filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Airline", "Tickets Sold", "Total Revenue"])
                for row in data:
                    writer.writerow(row)
            return os.path.abspath(filename)
        except Exception:
            return None

    def export_stats_json(self, filename="analytics_export.json"):
        data = self.get_airline_revenue_stats()
        json_data = []
        for row in data:
            json_data.append({
                "airline": row[0],
                "tickets_sold": row[1],
                "total_revenue": float(row[2]) if row[2] else 0.0 
            })
            
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                json.dump(json_data, file, indent=4)
            return os.path.abspath(filename)
        except Exception:
            return None

    def export_bookings_csv(self, filename="bookings_export.csv"):
        session = SessionLocal()
        try:
            tickets = session.query(Ticket).all()
            with open(filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Ticket Number", "Flight", "Passenger", "Price", "Buyer"])
                for t in tickets:
                    buyer_name = t.buyer.username if t.buyer else "N/A"
                    writer.writerow([
                        t.ticket_number,
                        t.flight.flight_number,
                        f"{t.passenger.last_name} {t.passenger.first_name}",
                        t.price,
                        buyer_name
                    ])
            return os.path.abspath(filename)
        except Exception as e:
            print(f"Export error: {e}")
            return None
        finally:
            session.close()