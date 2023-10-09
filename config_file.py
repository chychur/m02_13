from dataclasses import dataclass
from pathlib import Path
from ipaddress import ip_address

from pydantic import BaseSettings, EmailStr
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).parent

BANNED_IPS = [
    ip_address("192.168.1.1"), ip_address("192.168.1.2"),
]

ORIGINS = [
    "http://localhost:3000",
]


@dataclass(frozen=True)
class Template:
    emails: Path = BASE_DIR / 'src' / 'templates' / 'emails'
    html_response: Jinja2Templates = Jinja2Templates(directory=BASE_DIR / 'src' / 'templates' / 'response')


class Settings(BaseSettings):
    db_url: str = 'DB_URL'

    secret_key_jwt: str = 'SECRET_KEY'
    algorithm: str = 'ALGORITHM'

    mail_username: EmailStr = 'MAIL_USERNAME'
    mail_password: str = 'MAIL_PASSWORD'
    mail_from: EmailStr = 'MAIL_FROM'
    mail_port: int = 'MAIL_PORT'
    mail_server: str = 'MAIL_SERVER'
    mail_from_name: str = 'MAIL_FROM_NAME'

    redis_host: str = 'REDIS_HOST'
    redis_port: int = 'REDIS_PORT'
    redis_password: str = 'REDIS_PASSWORD'

    cloudinary_name: str = 'CLOUDINARY_NAME'
    cloudinary_api_key: int = 'CLOUDINARY_API_KEY'
    cloudinary_api_secret: str = 'CLOUDINARY_SECRET'
    cloudinary_folder: str = 'CLOUDINARY_FOLDER'

    class Config:
        env_file = BASE_DIR / '.env'


settings = Settings()

#print(settings.db_url)
