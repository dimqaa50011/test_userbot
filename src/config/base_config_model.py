import os


class BaseConfigModel:
    def __new__(cls, *args, **kwargs):
        for field_name, field_type in cls.__annotations__.items():
            field_value = field_type(os.getenv(field_name))
            setattr(cls, field_name, field_value)
        return super().__new__(cls, *args, **kwargs)
