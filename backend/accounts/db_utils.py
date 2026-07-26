"""Production database repair helpers.

These helpers are PostgreSQL-safe and become no-ops on SQLite where
appropriate. They are used after Railway migrations and when a restored
legacy database has stale serial sequences.
"""

from __future__ import annotations

from collections.abc import Iterable

from django.db import connection
from django.db.models import Model


def reset_model_sequences(models: Iterable[type[Model]]) -> int:
    """Reset PostgreSQL serial sequences for tables that actually exist.

    A partially migrated Railway database can have Django model state for a
    table whose physical table has not been created yet. Calling
    ``pg_get_serial_sequence`` for such a table aborts the whole transaction.
    We therefore introspect once and skip absent/unmanaged tables safely.
    """

    if connection.vendor != "postgresql":
        return 0

    updated = 0
    quote = connection.ops.quote_name

    with connection.cursor() as cursor:
        existing_tables = set(connection.introspection.table_names(cursor))

        for model in models:
            if not model._meta.managed:
                continue

            table = model._meta.db_table
            if table not in existing_tables:
                continue

            pk_column = model._meta.pk.column
            cursor.execute(
                "SELECT pg_get_serial_sequence(%s, %s)",
                [f"public.{table}", pk_column],
            )
            row = cursor.fetchone()
            sequence_name = row[0] if row else None
            if not sequence_name:
                continue

            cursor.execute(
                f"SELECT COALESCE(MAX({quote(pk_column)}), 0) FROM {quote(table)}"
            )
            max_pk = int(cursor.fetchone()[0] or 0)

            if max_pk > 0:
                cursor.execute("SELECT setval(%s, %s, true)", [sequence_name, max_pk])
            else:
                cursor.execute("SELECT setval(%s, 1, false)", [sequence_name])
            updated += 1

    return updated


def is_primary_key_collision(exc: Exception) -> bool:
    """Return True for PostgreSQL duplicate-primary-key style errors."""

    message = str(exc).lower()
    return (
        "duplicate key value violates unique constraint" in message
        and ("_pkey" in message or "primary key" in message)
    )
