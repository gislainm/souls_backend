import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(
        default=uuid.uuid4, unique=True, primary_key=True, editable=False
    )
    name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(max_length=200, unique=True, blank=True)
    password = models.CharField(max_length=100, blank=True)
    telephone = models.CharField(max_length=100, blank=True)
    is_admin = models.BooleanField(default=False)
    is_group_leader = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name + " " + self.email

    USERNAME_FIELD = "email"

    objects = CustomUserManager()


class Organization(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4, unique=True, primary_key=True, editable=False
    )
    name = models.CharField(max_length=200)
    admin = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="admin_of_organization"
    )
    is_deleted = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name


class SmallGroup(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4, unique=True, primary_key=True, editable=False
    )
    name = models.CharField(max_length=200)
    members = models.ManyToManyField(
        CustomUser, related_name="small_groups", blank=True
    )
    organization = models.ForeignKey(
        "Organization", on_delete=models.CASCADE, related_name="small_groups"
    )

    # group meeting days options
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"

    MEET_DAY_CHOICES = [
        (MONDAY, "Monday"),
        (TUESDAY, "Tuesday"),
        (WEDNESDAY, "Wednesday"),
        (THURSDAY, "Thursday"),
        (FRIDAY, "Friday"),
        (SATURDAY, "Saturday"),
        (SUNDAY, "Sunday"),
    ]
    meet_day = models.CharField(
        max_length=20, choices=MEET_DAY_CHOICES, null=True, blank=True
    )
    meet_time = models.TimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Attendance(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4, unique=True, primary_key=True, editable=False
    )
    group = models.ForeignKey(
        SmallGroup, on_delete=models.CASCADE, related_name="attendances"
    )
    meeting_date = models.DateField()
    members_present = models.ManyToManyField(
        CustomUser, related_name="attendances", blank=True
    )
    id_deleted = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"Attendance for {self.group.name} on {self.meeting_date}"
