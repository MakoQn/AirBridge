"""Create flight details view

Revision ID: 906492423f39
Revises: 4608a0adf195
Create Date: 2025-12-15 19:48:35.027960

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '906492423f39'
down_revision: Union[str, Sequence[str], None] = '4608a0adf195'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    
    op.execute("""
    CREATE OR REPLACE VIEW flight_details_view AS
    SELECT 
        f.id as flight_id,
        f.flight_number,
        c_dep.city_name as departure_city,
        c_arr.city_name as arrival_city,
        o.organization_name as airline_name,
        f.departure_datetime
    FROM flight f
    JOIN airport dep ON f.departure_airport_id = dep.id
    JOIN city c_dep ON dep.city_id = c_dep.id
    JOIN airport arr ON f.arrival_airport_id = arr.id
    JOIN city c_arr ON arr.city_id = c_arr.id
    JOIN organization o ON f.organization_id = o.id;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    
    op.execute("DROP VIEW IF EXISTS flight_details_view")
