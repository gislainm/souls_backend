import uuid

from django.db import models


class User(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4, unique=True, primary_key=True, editable=False
    )
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=200, unique=True, blank=True)
    password = models.CharField(max_length=100, blank=True)
    telephone = models.CharField(max_length=100, blank=True)
    is_admin = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name + "" + self.email


class Organization(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4, unique=True, primary_key=True, editable=False
    )
    name = models.CharField(max_length=200)
    admin = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="admin_of_organizations"
    )
    is_deleted = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name


class Group(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4, unique=True, primary_key=True, editable=False
    )
    name = models.CharField(max_length=200)
    members = models.ManyToManyField(User, related_name="groups")
    organization = models.ForeignKey(
        "Organization", on_delete=models.CASCADE, related_name="groups"
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
        Group, on_delete=models.CASCADE, related_name="attendances"
    )
    meeting_date = models.DateField()
    members_present = models.ManyToManyField(
        User, related_name="attendances", blank=True
    )
    id_deleted = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"Attendance for {self.group.name} on {self.meeting_date}"
