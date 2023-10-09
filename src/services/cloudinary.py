from typing import BinaryIO

import cloudinary
from cloudinary.api import resource
from cloudinary.uploader import upload

from config_file import settings

cloudinary.config(
    cloud_name=settings.cloudinary_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
    secure=True
)


def upload_image(file: BinaryIO, user_id: int, return_size: tuple[int, int] = (250, 250)) -> str:
    file_id = settings.cloudinary_folder + f'avatar_{user_id}'
    upload(file, public_id=file_id, owerwrite=True)

    return cloudinary.CloudinaryImage(file_id).build_url(
        width=return_size[0], height=return_size[1], crop='fill', version=resource(file_id)['version']
    )
