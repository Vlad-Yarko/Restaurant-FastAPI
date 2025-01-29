from fastapi_mail import ConnectionConfig, MessageSchema, FastMail

import os

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


config_mail = ConnectionConfig(
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    MAIL_FROM=os.getenv('MAIL_FROM'),
    MAIL_FROM_NAME=os.getenv('MAIL_FROM_NAME'),
    MAIL_PORT=587,
    MAIL_SERVER="in-v3.mailjet.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)


mail = FastMail(
    config=config_mail
)


async def custom_email(
        recipients: list[str],
        subject: str,
        body: str
) -> None:
    schema = MessageSchema(
        recipients=recipients,
        subject=subject,
        body=body,
        subtype='html'
    )
    await mail.send_message(schema)
