"""Add uploader ownership to transcripts and vector indices.

Revision ID: 20261126_owner_scope
Revises:
Create Date: 2026-11-26
"""

from alembic import op
import sqlalchemy as sa

revision = "20261126_owner_scope"
down_revision = None
branch_labels = None
depends_on = None

_NAMING_CONVENTION = {
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
}


def _column_names(constraint: dict) -> set[str]:
    return set(constraint.get("column_names") or ())


def _upgrade_owner_scope(
    table_name: str,
    old_unique_columns: list[str],
    new_unique_columns: list[str],
    new_unique_name: str,
) -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if table_name not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns(table_name)}
    foreign_keys = inspector.get_foreign_keys(table_name)
    unique_constraints = inspector.get_unique_constraints(table_name)
    target_exists = any(
        _column_names(constraint) == set(new_unique_columns)
        for constraint in unique_constraints
    )
    owner_fk_exists = any(
        foreign_key.get("referred_table") == "users"
        and foreign_key.get("constrained_columns") == ["owner_user_id"]
        for foreign_key in foreign_keys
    )
    old_constraints = [
        constraint
        for constraint in unique_constraints
        if _column_names(constraint) == set(old_unique_columns)
    ]

    if "owner_user_id" in columns and target_exists and owner_fk_exists and not old_constraints:
        return
    if "users" not in inspector.get_table_names():
        raise RuntimeError(f"Cannot add owner scope to {table_name}: users table is missing")

    with op.batch_alter_table(
        table_name,
        naming_convention=_NAMING_CONVENTION,
    ) as batch_op:
        if "owner_user_id" not in columns:
            batch_op.add_column(sa.Column("owner_user_id", sa.Integer(), nullable=True))
        if not owner_fk_exists:
            batch_op.create_foreign_key(
                f"fk_{table_name}_owner_user_id_users",
                "users",
                ["owner_user_id"],
                ["id"],
            )
        for constraint in old_constraints:
            name = constraint.get("name") or f"uq_{table_name}_{old_unique_columns[0]}"
            batch_op.drop_constraint(name, type_="unique")
        if not target_exists:
            batch_op.create_unique_constraint(new_unique_name, new_unique_columns)


def _downgrade_owner_scope(
    table_name: str,
    old_unique_columns: list[str],
    new_unique_columns: set[str],
) -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if table_name not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns(table_name)}
    if "owner_user_id" not in columns:
        return

    owned_rows = bind.execute(
        sa.text(f"SELECT COUNT(*) FROM {table_name} WHERE owner_user_id IS NOT NULL")
    ).scalar_one()
    if owned_rows:
        raise RuntimeError(
            f"Cannot remove owner scope from {table_name} while user-owned rows exist"
        )

    foreign_keys = inspector.get_foreign_keys(table_name)
    unique_constraints = inspector.get_unique_constraints(table_name)
    scoped_constraints = [
        constraint
        for constraint in unique_constraints
        if _column_names(constraint) == new_unique_columns
    ]
    old_constraint_exists = any(
        _column_names(constraint) == set(old_unique_columns)
        for constraint in unique_constraints
    )

    with op.batch_alter_table(
        table_name,
        naming_convention=_NAMING_CONVENTION,
    ) as batch_op:
        for constraint in scoped_constraints:
            name = constraint.get("name") or f"uq_{table_name}_owner_user_id"
            batch_op.drop_constraint(name, type_="unique")
        for foreign_key in foreign_keys:
            if (
                foreign_key.get("referred_table") == "users"
                and foreign_key.get("constrained_columns") == ["owner_user_id"]
            ):
                name = foreign_key.get("name") or f"fk_{table_name}_owner_user_id_users"
                batch_op.drop_constraint(name, type_="foreignkey")
        batch_op.drop_column("owner_user_id")
        if not old_constraint_exists:
            batch_op.create_unique_constraint(
                f"uq_{table_name}_{old_unique_columns[0]}",
                old_unique_columns,
            )


def upgrade() -> None:
    _upgrade_owner_scope(
        "transcripts",
        ["company_id", "quarter", "year"],
        ["owner_user_id", "company_id", "quarter", "year"],
        "uq_owner_company_quarter_year",
    )
    _upgrade_owner_scope(
        "vector_indices",
        ["company_id"],
        ["owner_user_id", "company_id"],
        "uq_owner_company_vector_index",
    )


def downgrade() -> None:
    _downgrade_owner_scope(
        "vector_indices",
        ["company_id"],
        {"owner_user_id", "company_id"},
    )
    _downgrade_owner_scope(
        "transcripts",
        ["company_id", "quarter", "year"],
        {"owner_user_id", "company_id", "quarter", "year"},
    )
