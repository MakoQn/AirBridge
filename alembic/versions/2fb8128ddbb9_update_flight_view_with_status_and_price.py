"""Update flight view with status and price

Revision ID: 2fb8128ddbb9
Revises: b1903b4ba549
Create Date: 2025-12-21 19:50:28.538349

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2fb8128ddbb9'
down_revision: Union[str, Sequence[str], None] = 'b1903b4ba549'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("DROP VIEW IF EXISTS flight_details_view")
    op.execute("""
    CREATE VIEW flight_details_view AS
    SELECT 
        f.id as flight_id,
        f.flight_number,
        f.departure_datetime,
        f.base_price,
        f.status,
        f.max_tickets,
        dep.airport_name as dep_airport,
        c_dep.city_name as dep_city,
        arr.airport_name as arr_airport,
        c_arr.city_name as arr_city,
        a.registration_number as aircraft_reg,
        o.organization_name as airline_name
    FROM flight f
    JOIN airport dep ON f.departure_airport_id = dep.id
    JOIN city c_dep ON dep.city_id = c_dep.id
    JOIN airport arr ON f.arrival_airport_id = arr.id
    JOIN city c_arr ON arr.city_id = c_arr.id
    JOIN aircraft a ON f.aircraft_id = a.id
    JOIN organization o ON f.organization_id = o.id;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP VIEW IF EXISTS flight_details_view")
