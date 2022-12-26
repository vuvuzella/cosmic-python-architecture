from https://www.cosmicpython.com/book/preface.html

1. install pipx
2. using pipx, install poetry
3. Optional: set poetry config to create venv folder within the project directory
4. run `poetry install` to install dev dependencies
5. run `poetry run pytest` to run the tests
6. run `poetry python [python file]` to run a specific python script

Do not forget to set the python environment library in vscode so the libraries get referenced correctly

# TODO:
1. Dockerize the whole app
2. ~~ Dockerize the data store ~~
3. Create multiple containers of different data store
4. Use Docker compose to orchestrate launching of the app and making containers access other containers
