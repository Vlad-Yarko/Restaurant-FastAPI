from fastapi import UploadFile

from pydantic import BaseModel, Field, field_validator, model_validator, EmailStr
from pydantic_async_validation import async_field_validator, AsyncValidationModelMixin

from bcrypt import checkpw

# from werkzeug.security import check_password_hash

from app.src.databases.requests import orm_find_account
from app.src.databases.engine import main_session


class CreateAccountSchema(AsyncValidationModelMixin, BaseModel):

    username: str = Field(default=None)
    password: str = Field(default=None)
    email: EmailStr

    @async_field_validator('username')
    async def check_username(self, value):
        if not value:
            raise ValueError("Username is required")
        if 2 <= len(value) <= 20:
            async with main_session() as session:
                u = await orm_find_account(value, session=session)
            if not u:
                return value
            raise ValueError('Username is already busy')
        raise ValueError("Username must be about 2 and 20 characters")

    @field_validator('password')
    def check_password(cls, value):
        if not value:
            raise ValueError("Password is required")
        if 8 <= len(value) <= 25:
            return value
        raise ValueError("Password must be about 8 and 25 characters")


class LoginAccountSchema(AsyncValidationModelMixin, BaseModel):

    username: str = Field(default=None)
    password: str = Field(default=None)

    @field_validator('password')
    def check_password(cls, value):
        if not value:
            raise ValueError("Password is required")
        if 8 <= len(value) <= 25:
            return value
        raise ValueError("Password must be about 8 and 25 characters")

    @async_field_validator('username')
    async def check_username(self, value):
        if not value:
            raise ValueError("Username is required")
        if 2 <= len(value) <= 20:
            async with main_session() as session:
                u = await orm_find_account(value, session=session)
                if u:
                    if checkpw(self.password.encode(), u.password):
                        return value
                    raise ValueError('Incorrect password')
                raise ValueError("Username is not found")
        raise ValueError("Username must be about 2 and 20 characters")


class FileSchema(BaseModel):

    file: UploadFile | None = Field(default=None)

    @field_validator('file')
    def check_file(cls, value):
        print(value)
        if not value.filename:
            raise ValueError('File is required')
        extensions = ("jpg", 'png', 'jpeg')
        if value.filename.split('.')[1] in extensions:
            return value
        raise ValueError('Incorrect extension for file')


class MailCodeSchema(AsyncValidationModelMixin, BaseModel):

    code: int | None = Field(default=None)
    sent_code: int

    @async_field_validator('code')
    async def check_code(self, value):
        if value is not None:
            if self.sent_code == value:
                return value
            raise ValueError("Incorrect code")
        raise ValueError("Code is required")
