import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .managers import CustomUserManager, num_week_of_the_year


class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(
        default=uuid.uuid4, unique=True, primary_key=True, editable=False
    )
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=200, unique=True)
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


class AttendingUser(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4, unique=True, primary_key=True, editable=False
    )
    name = models.CharField(max_length=200)
    is_deleted = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name


class Organization(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4, unique=True, primary_key=True, editable=False
    )
    name = models.CharField(max_length=200)
    admin = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="admin_of_organization"
    )
    registration_date = models.DateField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name


class SmallGroup(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4, unique=True, primary_key=True, editable=False
    )
    name = models.CharField(max_length=200)
    leader = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="led_groups",
    )
    members = models.ManyToManyField(
        AttendingUser, related_name="small_groups", blank=True
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
    week_number = models.IntegerField()
    members_present = models.ManyToManyField(
        AttendingUser, related_name="attendances", blank=True
    )
    is_deleted = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"Attendance for {self.group.name} on {self.meeting_date}"
