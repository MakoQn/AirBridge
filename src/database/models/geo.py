from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.database.models.base import Base

class Country(Base):
    __tablename__ = "country"

    id = Column(Integer, primary_key=True, index=True)
    country_name = Column(String, unique=True, nullable=False)

    cities = relationship("City", back_populates="country")

class City(Base):
    __tablename__ = "city"

    id = Column(Integer, primary_key=True, index=True)
    city_name = Column(String, unique=True, nullable=False)
    country_id = Column(Integer, ForeignKey("country.id"), nullable=False)

    country = relationship("Country", back_populates="cities")
    airports = relationship("Airport", back_populates="city")

class Airport(Base):
    __tablename__ = "airport"
    
    id = Column(Integer, primary_key=True)
    airport_name = Column(String, unique=True, nullable=False)
    city_id = Column(Integer, ForeignKey("city.id"), nullable=False)
    
    city = relationship("City", back_populates="airports")