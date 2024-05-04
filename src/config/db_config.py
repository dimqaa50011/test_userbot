from .base_config_model import BaseConfigModel


class DbConfig(BaseConfigModel):
    DB_SCHEMA: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str

    def get_uri(self) -> str:
        return "%(schema)s://%(user)s:%(password)s@%(host)s:%(port)s/%(name)s" % {
            "schema": self.DB_SCHEMA,
            "user": self.DB_USER,
            "password": self.DB_PASSWORD,
            "host": self.DB_HOST,
            "port": self.DB_PORT,
            "name": self.DB_NAME
        }
