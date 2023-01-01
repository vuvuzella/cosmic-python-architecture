from pydantic import BaseConfig


class FlaskApiSettings(BaseConfig):
    API_URL: str = ""


flask_api_setting = FlaskApiSettings()
