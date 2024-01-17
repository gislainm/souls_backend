from django.core.exceptions import ValidationError

from ..models import CustomUser


def user_email_exists(email: str):
    if not CustomUser.objects.filter(email=email).exists():
        raise ValidationError(
            f"No user with associated email",
            params={"email": email},
        )


def user_id_exists(id: str):
    if not CustomUser.objects.filter(id=id).exists():
        raise ValidationError(
            f"No user with associated id",
            params={"id": id},
        )
