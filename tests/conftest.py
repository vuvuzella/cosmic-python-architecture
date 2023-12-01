from settings import global_settings
from sqlalchemy.engine import create_engine, Engine
from sqlalchemy.orm import Session
from typing import Generator
from infrastructure.orm import start_mappers, order_lines

import pytest

# code mostly from https://gist.github.com/kissgyorgy/e2365f25a213de44b9a2
# Do not rename file. pytest requires the filename to be conftest when fixtures reside in different file


@pytest.fixture(scope="session")
def engine() -> Engine:
    return create_engine(
        global_settings.DB_DSN
    )  # TODO: curate special DSN for test database


@pytest.fixture(scope="session")
def tables(engine: Engine) -> Generator[None, None, None]:
    order_lines.metadata.create_all(engine)
    start_mappers()
    yield
    order_lines.metadata.drop_all(engine)


@pytest.fixture(scope="session")
def session(engine: Engine, tables) -> Generator[Session, None, None]:
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()

    transaction.rollback()

    connection.close


# Scope controls the level at which the decorated function will execute
# 4 scopes: function, class, module, session
# The number of times a fixture gets executed depends on the scope
# The default scope is function, hence every function that has the fixture as its dependency, it will be executeddef
# A scope of "session" will only run the fixture once, every time "pytest" is executed
@pytest.fixture(scope="session")
def some_fixture():
    print("executing a session scoped fixture...")


@pytest.fixture(scope="session")
def add_stock():
    # TODO: manually insert rows into database using SQL
    raise NotImplementedError


# TODO: implement restarting the api for tests
@pytest.fixture(scope="session")
def restart_api():
    return "from restart_api"
