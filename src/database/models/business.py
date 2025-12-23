from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, DECIMAL, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.database.models.base import Base

class Organization(Base):
    __tablename__ = "organization"

    id = Column(Integer, primary_key=True)
    organization_name = Column(String, unique=True, nullable=False)
    phone_number = Column(String)
    email = Column(String)
    address = Column(String)

class Flight(Base):
    __tablename__ = "flight"

    id = Column(Integer, primary_key=True)
    flight_number = Column(String, unique=True, nullable=False)
    departure_datetime = Column(DateTime, nullable=False)
    arrival_datetime = Column(DateTime, nullable=False)
    base_price = Column(DECIMAL(10, 2), nullable=False, default=0.0)
    status = Column(String, default="Registration")
    max_tickets = Column(Integer, nullable=False, default=100)
    
    departure_airport_id = Column(Integer, ForeignKey("airport.id"), nullable=False)
    arrival_airport_id = Column(Integer, ForeignKey("airport.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organization.id"), nullable=False)
    aircraft_id = Column(Integer, ForeignKey("aircraft.id"), nullable=False)

    tickets = relationship("Ticket", back_populates="flight")
    organization = relationship("Organization")
    aircraft = relationship("src.database.models.fleet.Aircraft")
    departure_airport = relationship("src.database.models.geo.Airport", foreign_keys=[departure_airport_id])
    arrival_airport = relationship("src.database.models.geo.Airport", foreign_keys=[arrival_airport_id])

class Passenger(Base):
    __tablename__ = "passenger"

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    middle_name = Column(String)
    date_of_birth = Column(DateTime)
    passport_series_number = Column(String, unique=True, nullable=False)
    phone_number = Column(String)
    email = Column(String)

class Ticket(Base):
    __tablename__ = "ticket"

    id = Column(Integer, primary_key=True)
    ticket_number = Column(String, unique=True, nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    booking_datetime = Column(DateTime, server_default=func.now())
    
    passenger_id = Column(Integer, ForeignKey("passenger.id"), nullable=False)
    flight_id = Column(Integer, ForeignKey("flight.id"), nullable=False)
    buyer_id = Column(Integer, ForeignKey("app_user.id"), nullable=True)

    flight = relationship("Flight", back_populates="tickets")
    passenger = relationship("Passenger")
    buyer = relationship("src.database.models.auth.AppUser")