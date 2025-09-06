from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.db.session import engine  # Your SQLModel engine
from app.models import ticket      # Import models so Alembic can detect them

# Alembic Config object
config = context.config

# If you want to load DB URL from your engine instead of alembic.ini:
# This ensures we always use the same DB URL as the app
config.set_main_option("sqlalchemy.url", str(engine.url))

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for 'autogenerate'
target_metadata = ticket.SQLModel.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
