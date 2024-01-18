from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user_leader(self, name: str, email: str, telephone: str, **extra_fields):
        if not name:
            raise ValueError("User must have a name")
        if not email:
            raise ValueError("User must have an email")
        user = self.model(
            name=name,
            email=email,
            telephone=telephone,
            is_group_leader=True,
            **extra_fields,
        )
        user.save()
        return user

    def create_user_admin(
        self, name: str, email: str, password: str, telephone: str, **extra_fields
    ):
        if not name:
            raise ValueError("User must have a name")
        if not email:
            raise ValueError("User must have an email")
        if not telephone:
            raise ValueError("User must have a phone number")
        if not password:
            print("password missing")
            raise TypeError("User must have a password")
        email = self.normalize_email(email)
        user = self.model(
            name=name, email=email, telephone=telephone, is_admin=True, **extra_fields
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email: str, password: str, **extra_fields):
        if not email:
            raise ValueError("User must have an email")
        user = self.model(
            email=email,
            is_staff=True,
            is_superuser=True,
            **extra_fields,
        )
        user.set_password(password)
        user.save()
