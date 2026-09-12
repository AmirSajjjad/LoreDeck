"""add users and card history

Revision ID: 002
Revises: 001
Create Date: 2026-09-12 12:10:06.979809
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: str | Sequence[str] | None = "001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Apply the migration."""
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("phone_number", sa.String(length=255), nullable=True),
        sa.Column("profile_pic", sa.String(length=500), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
        sa.UniqueConstraint("phone_number", name=op.f("uq_users_phone_number")),
        sa.UniqueConstraint("telegram_id", name=op.f("uq_users_telegram_id")),
        sa.UniqueConstraint("username", name=op.f("uq_users_username")),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=False)
    op.create_index(op.f("ix_users_phone_number"), "users", ["phone_number"], unique=False)
    op.create_index(op.f("ix_users_telegram_id"), "users", ["telegram_id"], unique=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=False)
    op.create_table(
        "user_card_histories",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("question", sa.Text(), nullable=True),
        sa.Column("deck_id", sa.Integer(), nullable=False),
        sa.Column("first_card_id", sa.Integer(), nullable=False),
        sa.Column("first_story", sa.Text(), nullable=True),
        sa.Column("second_card_id", sa.Integer(), nullable=True),
        sa.Column("second_story", sa.Text(), nullable=True),
        sa.Column("third_card_id", sa.Integer(), nullable=True),
        sa.Column("third_story", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "first_card_id <> second_card_id",
            name=op.f("ck_user_card_histories_first_second_cards_differ"),
        ),
        sa.CheckConstraint(
            "first_card_id <> third_card_id",
            name=op.f("ck_user_card_histories_first_third_cards_differ"),
        ),
        sa.CheckConstraint(
            "second_card_id <> third_card_id",
            name=op.f("ck_user_card_histories_second_third_cards_differ"),
        ),
        sa.CheckConstraint(
            "second_card_id IS NOT NULL OR third_card_id IS NULL",
            name=op.f("ck_user_card_histories_card_sequence"),
        ),
        sa.ForeignKeyConstraint(
            ["deck_id"],
            ["decks.id"],
            name=op.f("fk_user_card_histories_deck_id_decks"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["first_card_id"],
            ["cards.id"],
            name=op.f("fk_user_card_histories_first_card_id_cards"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["second_card_id"],
            ["cards.id"],
            name=op.f("fk_user_card_histories_second_card_id_cards"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["third_card_id"],
            ["cards.id"],
            name=op.f("fk_user_card_histories_third_card_id_cards"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_user_card_histories_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_card_histories")),
    )
    op.create_index(
        op.f("ix_user_card_histories_deck_id"),
        "user_card_histories",
        ["deck_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_card_histories_first_card_id"),
        "user_card_histories",
        ["first_card_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_card_histories_second_card_id"),
        "user_card_histories",
        ["second_card_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_card_histories_third_card_id"),
        "user_card_histories",
        ["third_card_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_card_histories_user_id"),
        "user_card_histories",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    """Revert the migration."""
    op.drop_index(op.f("ix_user_card_histories_user_id"), table_name="user_card_histories")
    op.drop_index(op.f("ix_user_card_histories_third_card_id"), table_name="user_card_histories")
    op.drop_index(op.f("ix_user_card_histories_second_card_id"), table_name="user_card_histories")
    op.drop_index(op.f("ix_user_card_histories_first_card_id"), table_name="user_card_histories")
    op.drop_index(op.f("ix_user_card_histories_deck_id"), table_name="user_card_histories")
    op.drop_table("user_card_histories")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_telegram_id"), table_name="users")
    op.drop_index(op.f("ix_users_phone_number"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
