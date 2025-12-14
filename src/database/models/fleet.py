from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.database.models.base import Base

class AircraftType(Base):
    __tablename__ = "aircraft_type"
    
    id = Column(Integer, primary_key=True)
    model_name = Column(String, unique=True, nullable=False)
    max_cargo_weight_kg = Column(Integer, nullable=False)
    passenger_capacity = Column(Integer, nullable=False)
    
    aircrafts = relationship("Aircraft", back_populates="aircraft_type")

class Aircraft(Base):
    __tablename__ = "aircraft"
    
    id = Column(Integer, primary_key=True)
    registration_number = Column(String, unique=True, nullable=False)
    aircraft_type_id = Column(Integer, ForeignKey("aircraft_type.id"), nullable=False)
    photo_url = Column(String, nullable=True)
    
    aircraft_type = relationship("AircraftType", back_populates="aircrafts")
    seats = relationship("Seat", back_populates="aircraft")

class SeatType(Base):
    __tablename__ = "seat_type"
    
    id = Column(Integer, primary_key=True)
    seat_type_name = Column(String, unique=True, nullable=False)
    
    seats = relationship("Seat", back_populates="seat_type")

class Seat(Base):
    __tablename__ = "seat"
    
    id = Column(Integer, primary_key=True)
    seat_number = Column(String, nullable=False)
    seat_type_id = Column(Integer, ForeignKey("seat_type.id"), nullable=False)
    aircraft_id = Column(Integer, ForeignKey("aircraft.id"), nullable=False)
    
    seat_type = relationship("SeatType", back_populates="seats")
    aircraft = relationship("Aircraft", back_populates="seats")