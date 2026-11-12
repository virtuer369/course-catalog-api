
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '08d83362f614'
down_revision: Union[str, Sequence[str], None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add the column as nullable.
    op.add_column(
        'courses',
        sa.Column('level', sa.String(), nullable=True)
    )

    # 2. Populate existing courses.
    op.execute(
        """
        UPDATE courses
        SET level = CASE
            WHEN is_elective = TRUE THEN 'beginner'
            ELSE 'intermediate'
        END
        """
    )

    # 3. Make the column required.
    op.alter_column(
        'courses',
        'level',
        existing_type=sa.String(),
        nullable=False
    )


def downgrade() -> None:
    op.drop_column('courses', 'level')
