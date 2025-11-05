from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.utils.db_connection import Base

class Country(Base):
    __tablename__ = "country"

    id = Column(Integer, primary_key=True, index=True)
    country_name = Column(String, unique=True, nullable=False)

    cities = relationship("City", back_populates="country")

    def __repr__(self):
        return f"<Country(id={self.id}, name='{self.country_name}')>"

class City(Base):
    __tablename__ = "city"

    id = Column(Integer, primary_key=True, index=True)
    city_name = Column(String, unique=True, nullable=False)
    country_id = Column(Integer, ForeignKey("country.id"), nullable=False)

    country = relationship("Country", back_populates="cities")

    def __repr__(self):
        return f"<City(id={self.id}, name='{self.city_name}', country_id={self.country_id})>"