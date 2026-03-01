import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hospital_project.settings")

import django

django.setup()

from django.contrib.auth import get_user_model


def create_superuser():
    username = os.getenv("DJANGO_SUPERUSER_USERNAME", "kitwana")
    email = os.getenv("DJANGO_SUPERUSER_EMAIL", "alymaulidkitwana068@gmail.com")
    password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "kitwana26 ")

    user_model = get_user_model()

    if user_model.objects.filter(username=username).exists():
        print(f"Superuser '{username}' already exists.")
        return

    user_model.objects.create_superuser(
        username=username,
        email=email,
        password=password,
    )
    print(f"Superuser '{username}' created successfully.")


if __name__ == "__main__":
    create_superuser()
