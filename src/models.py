from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from src.utils.db_connection import Base
class Country(Base):
    __tablename__ = "country"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    cities = relationship("City", back_populates="country")

    def __repr__(self):
        return f"<Country(id={self.id}, name='{self.name}')>"
    
class City(Base):
    __tablename__ = "city"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    country_id = Column(Integer, ForeignKey("country.id"), nullable=False)

    country = relationship("Country", back_populates="city")

    def __repr__(self):
        return f"<City(id={self.id}, name='{self.name}', country_id={self.country_id})>"
    
class Airport(Base):
    __tablename__ = "airport"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    city_id = Column(Integer, ForeignKey("cities.id", ondelete="CASCADE"), nullable=False)
    
    city = relationship("City", back_populates="airport")
    
    def __repr__(self):
        return f"<Airport(id={self.id}, name='{self.name}', city_id={self.city_id})>"
    
class AircraftType(Base):
    __tablename__ = "aircraft_type"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    max_cargo_weight_kg = Column(Integer, nullable=False)
    passenger_capacity = Column(Integer, nullable=False)
    
    aircraft = relationship("Aircraft", back_populates="aircraft_type")
    
    def __repr__(self):
        return f"<Aircraft type(id={self.id}, name='{self.name}', max_cargo_weight_kg={self.max_cargo_weight_kg}, passenger_capacity={self.passenger_capacity})>"
    
class Aircraft(Base):
    __tablename__ = "aircraft"
    
    registration_number = Column(String(10), primary_key=True)
    aircraft_type_id = Column(Integer, ForeignKey("aircraft_type.id", ondelete="RESTRICT"), nullable=False)
    photo_path = Column(String(255), nullable=True)
    
    aircraft_type = relationship("AircraftType", back_populates="aircraft")
    
    def __repr__(self):
        return f"<Aircraft(registration_number={self.registration_number}, aircraft_type_id={self.aircraft_type_id})>"
    
class SeatType(Base):
    __tablename__ = "seat_types"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(20), unique=True, nullable=False)
    
    seats = relationship("Seat", back_populates="seat_type")

    def __repr__(self):
        return f"<Seat type(id={self.id}, name={self.name})>"
    
class Seat(Base):
    __tablename__ = "seats"
    
    id = Column(Integer, primary_key=True)
    aircraft_registration = Column(String(10), ForeignKey("aircraft.registration_number", ondelete="CASCADE"), nullable=False)
    seat_number = Column(String(5), nullable=False)
    seat_type_id = Column(Integer, ForeignKey("seat_types.id", ondelete="RESTRICT"), nullable=False)
    
    aircraft = relationship("Aircraft", back_populates="seats")
    seat_type = relationship("SeatType", back_populates="seats")