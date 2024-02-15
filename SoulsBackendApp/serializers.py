from rest_framework import serializers

from . import models
from .managers import num_week_of_the_year


class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = models.CustomUser
        fields = [
            "id",
            "name",
            "email",
            "password",
            "telephone",
            "is_admin",
            "is_group_leader",
            "is_deleted",
        ]


class AttendingUserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = models.AttendingUser
        fields = [
            "id",
            "name",
            "is_deleted",
        ]


class UserResponseSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = models.CustomUser
        fields = [
            "id",
            "name",
            "email",
            "telephone",
            "is_admin",
            "is_group_leader",
            "is_deleted",
        ]


class organizationSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = models.Organization
        fields = ["id", "name", "admin"]


class smallGroupSerializer(serializers.ModelSerializer):
    leader = UserResponseSerializer("leader", read_only=True)
    class Meta(object):
        model = models.SmallGroup
        fields = [
            "id",
            "name",
            "leader",
            "members",
            "organization",
            "meet_day",
            "meet_time",
            "is_deleted",
        ]

    def create(self, validated_data):
        members_data = validated_data.pop("members", [])
        small_group = models.SmallGroup.objects.create(**validated_data)
        small_group.members.set(members_data)
        return small_group


class AttendanceSerializer(serializers.ModelSerializer):
    week_number = serializers.SerializerMethodField()

    class Meta(object):
        model = models.Attendance
        fields = ["id", "meeting_date", "week_number", "members_present"]

    def create(self, validated_data):
        members_present = validated_data.pop("members_present", [])
        is_saved = models.Attendance.objects.filter(
            group=self.context["group"],
            meeting_date__year=validated_data["meeting_date"].year,
            week_number=num_week_of_the_year(validated_data["meeting_date"]),
        )
        if is_saved:
            raise ValueError("Attendance for this week has already been saved")
        else:
            attendance = models.Attendance.objects.create(
                group=self.context["group"],
                week_number=num_week_of_the_year(validated_data["meeting_date"]),
                meeting_date=validated_data["meeting_date"],
            )
            attendance.members_present.set(members_present)
            return attendance

    def get_week_number(self, obj):
        return obj.week_number
