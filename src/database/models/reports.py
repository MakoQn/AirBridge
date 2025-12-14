from sqlalchemy import Column, Integer, String, DateTime
from src.database.models.base import Base

class FlightDetailsView(Base):
    __tablename__ = "flight_details_view"
    __table_args__ = {"info": dict(is_view=True)}

    flight_id = Column(Integer, primary_key=True)
    flight_number = Column(String)
    departure_city = Column(String)
    arrival_city = Column(String)
    airline_name = Column(String)
    departure_datetime = Column(DateTime)