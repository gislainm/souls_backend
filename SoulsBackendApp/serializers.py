from rest_framework import serializers

from . import models


class UserSerializer(serializers.ModelSerializer):
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
    class Meta(object):
        model = models.SmallGroup
        fields = [
            "id",
            "name",
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
