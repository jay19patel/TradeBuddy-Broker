from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from starlette.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import List


conf = ConnectionConfig(
    MAIL_USERNAME="developer.jay19@gmail.com",
    MAIL_PASSWORD="gtlgweqwhtizargb",
    MAIL_FROM="developer.jay19@gmail.com",
    MAIL_PORT=465,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)


async def email_send_access_token(emails: List[str], access_token: str) -> JSONResponse:
    try:
        html = f"""
        <p>Thanks for using Fastapi-mail</p> 
        <a href="http://127.0.0.1:8000/verify_email/verification/{access_token}">Click for Verification</a>
        """
        message = MessageSchema(
            subject="Fastapi-Mail module",
            recipients=emails,
            body=html,
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message)
        print("EMAIL SENT -------------")
    except Exception as e:
        print("Something went wrong", e)
