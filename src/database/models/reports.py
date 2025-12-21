from sqlalchemy import Column, Integer, String, DateTime, DECIMAL
from src.database.models.base import Base

class FlightDetailsView(Base):
    __tablename__ = "flight_details_view"
    __table_args__ = {"info": dict(is_view=True)}

    flight_id = Column(Integer, primary_key=True)
    flight_number = Column(String)
    departure_datetime = Column(DateTime)
    base_price = Column(DECIMAL(10, 2))
    status = Column(String)
    max_tickets = Column(Integer)
    
    dep_airport = Column(String)
    dep_city = Column(String)
    arr_airport = Column(String)
    arr_city = Column(String)
    aircraft_reg = Column(String)
    airline_name = Column(String)