from datetime import date, datetime, timedelta

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


def num_week_of_the_year(provided_date=None):
    """
    used to determine which week of the year a specific record is created
    """
    if provided_date is None:
        today = datetime.now().date()
    else:
        # date_format = "%Y-%m-%d"
        # today = datetime.strptime(provided_date, date_format).date()
        today = provided_date
    start_year = today.year
    start_date = date(start_year, 1, 1)
    end_date = today  # date we want to determine which week of the year it belongs to
    num_of_weeks = 0
    current_date = start_date

    while current_date <= end_date:
        if (
            current_date.weekday() == 0
        ):  # every monday we start a new week.adding to the number of weeks that have already passed
            num_of_weeks += 1
        current_date += timedelta(days=1)

    return num_of_weeks
