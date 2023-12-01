from https://www.cosmicpython.com/book/preface.html

1. install pipx
2. using pipx, install poetry
3. Optional: set poetry config to create venv folder within the project directory
4. run `poetry install` to install dev dependencies
5. run `poetry run pytest` to run the tests
6. run `poetry python [python file]` to run a specific python script
7. In the root directory, create a foleder named `persistent_store/db_volume` which will serve as the database persistence storage

Do not forget to set the python environment library in vscode so the libraries get referenced correctly

To run the docker compose version:
run `docker compose up -d`
The db is accessible thru `localhost:5435` and the flask api app is accessible thru `localhost:5000`

Current endpoints:

/allocate - POST only works, accepts json body with the following structure:
{
    "orderid": str,
    "sku": str,
    "qty": int
}

# TODO:
1. ~~ Dockerize the whole app ~~
2. ~~ Dockerize the data store ~~
3. Create multiple containers of different data store
4. ~~ Use Docker compose to orchestrate launching of the app and making containers access other containers ~~
5. Create multiple containers of different application api
6. ~~ Organize monorepo into sensible folder structure ~~
7. Finish up integration and e2e testing
