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
    status = Column(String, default="Check-in")
    
    departure_airport_id = Column(Integer, ForeignKey("airport.id"), nullable=False)
    arrival_airport_id = Column(Integer, ForeignKey("airport.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organization.id"), nullable=False)
    aircraft_id = Column(Integer, ForeignKey("aircraft.id"), nullable=False)

    tickets = relationship("Ticket", back_populates="flight")
    organization = relationship("Organization")
    aircraft = relationship("src.database.models.fleet.Aircraft")

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
    seat_id = Column(Integer, ForeignKey("seat.id"), nullable=True)
    buyer_id = Column(Integer, ForeignKey("app_user.id"), nullable=True)

    flight = relationship("Flight", back_populates="tickets")
    passenger = relationship("Passenger")
    buyer = relationship("src.database.models.auth.AppUser")
    
    __table_args__ = (UniqueConstraint('flight_id', 'seat_id', name='uq_flight_seat_ticket'),)

class CargoType(Base):
    __tablename__ = "cargo_type"

    id = Column(Integer, primary_key=True)
    cargo_type_name = Column(String, unique=True, nullable=False)

class TransportFeature(Base):
    __tablename__ = "transport_feature"

    id = Column(Integer, primary_key=True)
    feature_name = Column(String, unique=True, nullable=False)
    description = Column(String)

class Cargo(Base):
    __tablename__ = "cargo"

    id = Column(Integer, primary_key=True)
    mass = Column(DECIMAL(10, 2), nullable=False)
    cargo_type_id = Column(Integer, ForeignKey("cargo_type.id"), nullable=False)
    transport_feature_id = Column(Integer, ForeignKey("transport_feature.id"), nullable=True)
    passenger_id = Column(Integer, ForeignKey("passenger.id"), nullable=True)
    flight_id = Column(Integer, ForeignKey("flight.id"), nullable=True)