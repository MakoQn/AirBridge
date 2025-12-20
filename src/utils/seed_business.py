import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.database.db_connection import SessionLocal
from src.database.models.geo import Country, City
from src.database.models.fleet import AircraftType
from src.database.models.business import Organization

def seed_dictionaries():
    session = SessionLocal()
    try:
        if session.query(Country).count() > 0:
            print("Dictionaries already seeded")
            return

        russia = Country(country_name="Russia")
        uae = Country(country_name="UAE")
        turkey = Country(country_name="Turkey")
        session.add_all([russia, uae, turkey])
        session.flush()

        cities = [
            City(city_name="Moscow", country_id=russia.id),
            City(city_name="St. Petersburg", country_id=russia.id),
            City(city_name="Sochi", country_id=russia.id),
            City(city_name="Kazan", country_id=russia.id),
            City(city_name="Dubai", country_id=uae.id),
            City(city_name="Istanbul", country_id=turkey.id)
        ]
        session.add_all(cities)
        
        types = [
            AircraftType(model_name="Boeing 737-800", max_cargo_weight_kg=5000, passenger_capacity=189),
            AircraftType(model_name="Airbus A320", max_cargo_weight_kg=4000, passenger_capacity=150),
            AircraftType(model_name="Sukhoi Superjet 100", max_cargo_weight_kg=3000, passenger_capacity=98),
            AircraftType(model_name="Boeing 777-300ER", max_cargo_weight_kg=20000, passenger_capacity=400)
        ]
        session.add_all(types)

        orgs = [
            Organization(organization_name="AirBridge Airlines", email="hq@airbridge.loc"),
            Organization(organization_name="Emirates", email="partners@emirates.com"),
            Organization(organization_name="Turkish Airlines", email="partners@thy.com")
        ]
        session.add_all(orgs)

        session.commit()
        print("Base dictionaries created")

    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    seed_dictionaries()