from typing import Generator

import pytest
from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.orm import Session, clear_mappers

from infrastructure.orm import metadata, order_lines, start_mappers
from settings import global_settings

# code mostly from https://gist.github.com/kissgyorgy/e2365f25a213de44b9a2
# Do not rename file. pytest requires the filename to be conftest when fixtures reside in different file


@pytest.fixture(scope="session")
def engine() -> Engine:
    return create_engine(
        global_settings.DB_DSN
    )  # TODO: curate special DSN for test database


@pytest.mark.skip
@pytest.fixture(scope="session")
def tables(engine: Engine) -> Generator[None, None, None]:
    metadata.create_all(engine)
    start_mappers()
    yield
    order_lines.metadata.drop_all(engine)
    clear_mappers()


@pytest.fixture(scope="session")
def session(engine: Engine, tables) -> Generator[Session, None, None]:
    # connection = engine.connect()
    # transaction = connection.begin()
    session = Session(bind=engine)

    yield session

    session.close()
    # transaction.rollback()
    # connection.close


@pytest.fixture(scope="session")
def add_stock():
    # TODO: manually insert rows into database using SQL
    raise NotImplementedError


# TODO: implement restarting the api for tests
@pytest.fixture(scope="session")
def restart_api():
    return "from restart_api"
