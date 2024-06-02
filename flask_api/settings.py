from settings import BaseSettings


class FlaskApiSettings(BaseSettings):
    API_URL: str = ""


flask_api_setting = FlaskApiSettings()
