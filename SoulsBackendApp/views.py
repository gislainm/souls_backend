from datetime import datetime, time, timedelta

import pytz
from django.db.models import Count
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from .api.serializers import MyTokenObtainPairSerializer
from .models import Attendance, CustomUser, Organization, SmallGroup
from .oauth.utils import token as tokenGenerator
from .serializers import (
    AttendanceSerializer,
    AttendingUserSerializer,
    UserResponseSerializer,
    UserSerializer,
    organizationSerializer,
    smallGroupSerializer,
)


@api_view(["POST"])
def login(request):
    serializer = MyTokenObtainPairSerializer(data=request.data)
    if serializer.is_valid():
        access = serializer.validated_data.get("authToken").get("access")
        refresh = serializer.validated_data.get("authToken").get("refresh")
        user = serializer.validated_data.get("user")
        try:
            organization = Organization.objects.get(admin=user.get("id"))
        except Organization.DoesNotExist:
            organization = None
        response = Response(
            {
                "access": access,
                "user": user,
                "organization": organizationSerializer(organization).data,
            },
            status=status.HTTP_200_OK,
        )
        response.set_cookie(
            key="refresh",
            value=refresh,
            max_age=3 * 24 * 60 * 60,
            httponly=True,
            samesite="None",
            secure=True,
        )
        return response


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    refresh_token = request.COOKIES.get("refresh")
    if refresh_token:
        try:
            RefreshToken(refresh_token).blacklist()
            response = Response(
                {"message": "Logout Successful"}, status=status.HTTP_200_OK
            )
            response.delete_cookie(key="refresh")
            return response
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(
            {"error": "No token provided"}, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["POST"])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user_manager = CustomUser._default_manager
        try:
            user = user_manager.create_user_admin(**serializer.validated_data)
            token = tokenGenerator.get_tokens_for_user(user)
            access = token.get("access")
            refresh = token.get("refresh")
            response = Response(
                {"access": access, "user": UserResponseSerializer(user).data},
                status=status.HTTP_201_CREATED,
            )
            response.set_cookie(
                key="refresh",
                value=refresh,
                max_age=3 * 24 * 60 * 60,
                httponly=True,
                samesite="None",
                secure=True,
            )
            return response
        except (ValueError, TypeError) as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
    return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def addOrganization(request):
    if request.method == "POST":
        user = request.user
        if user.is_admin:
            organization_name = request.data.get("name", "")
            if organization_name:
                organization = Organization.objects.create(
                    name=organization_name, admin=user
                )
                return Response(
                    {
                        "organization": organizationSerializer(organization).data,
                        "message": "Organization created successfully",
                    },
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {"error": "Organization name is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"error": "You do not have permission to create organizations"},
                status=status.HTTP_403_FORBIDDEN,
            )

    return Response(
        {"error": "Invalid HTTP method"}, status=status.HTTP_400_BAD_REQUEST
    )


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def addSmallGroup(request, organization_id):
    """
    - This view create a small group in the organization that is already saved in the database.
    - The view also adds a new user in the database, the user is set to the leader of this small-group
    - The leader added with this small group must be a brand new user on the app with no matching email in the database
    """
    if request.method == "POST":
        user = request.user
        if user.is_admin:
            try:
                Organization.objects.get(id=organization_id)
                small_group_data = request.data.get("small_group")
                small_group_data["organization"] = organization_id
                small_group_serializer = smallGroupSerializer(data=small_group_data)
                group_leader_serializer = UserSerializer(
                    data=request.data.get("group_leader")
                )
                if (
                    group_leader_serializer.is_valid()
                    and not small_group_serializer.is_valid()
                ):
                    return Response(
                        {"error": small_group_serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                elif (
                    small_group_serializer.is_valid()
                    and not group_leader_serializer.is_valid()
                ):
                    return Response(
                        {"error": group_leader_serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                else:
                    user_manager = CustomUser._default_manager
                    group_leader = user_manager.create_user_leader(
                        **group_leader_serializer.validated_data
                    )
                    small_group = SmallGroup.objects.create(
                        **small_group_serializer.validated_data, leader=group_leader
                    )
                    return Response(
                        {
                            "small_group": smallGroupSerializer(small_group).data,
                            "message": "Small group created successfully",
                        }
                    )
            except Organization.DoesNotExist as e:
                return Response(
                    {"error": "Organization not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            return Response(
                {"error": "You do not have permission to create small groups"},
                status=status.HTTP_403_FORBIDDEN,
            )
    return Response(
        {"error": "Invalid HTTP method"}, status=status.HTTP_400_BAD_REQUEST
    )


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def addSmallGroupWithExistingLeader(request, organization_id):
    """
    - This view create a new small-group in the already existing organization, and gives the small-group a leader.
    - The leader given to this small-group has to be an already existing user on the app with the role of small_group_leader
        associated with his/her email
    """
    if request.method == "POST":
        user = request.user
        if user.is_admin:
            try:
                Organization.objects.get(id=organization_id)
                small_group_data = request.data.get("small_group")
                small_group_data["organization"] = organization_id
                small_group_serializer = smallGroupSerializer(data=small_group_data)
                group_leader = CustomUser.objects.filter(
                    id=request.data.get("group_leader").get("id")
                ).first()
                if group_leader is not None and not small_group_serializer.is_valid():
                    return Response(
                        {"error": small_group_serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                elif small_group_serializer.is_valid() and group_leader is None:
                    return Response(
                        {"error": "Group Leader Id is required"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                else:
                    small_group = SmallGroup.objects.create(
                        **small_group_serializer.validated_data, leader=group_leader
                    )
                    return Response(
                        {
                            "small_group": smallGroupSerializer(small_group).data,
                            "message": "Small group created successfully",
                        }
                    )
            except Organization.DoesNotExist as e:
                return Response(
                    {"error": "Organization not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            return Response(
                {"error": "You do not have permission to create small groups"},
                status=status.HTTP_403_FORBIDDEN,
            )
    return Response(
        {"error": "Invalid HTTP method"}, status=status.HTTP_400_BAD_REQUEST
    )


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def addSmallGroupMember(request, group_id):
    if request.method == "POST":
        user = request.user
        if user.is_group_leader:
            try:
                small_group = SmallGroup.objects.get(id=group_id)
                user_serializer = AttendingUserSerializer(data=request.data)
                if user_serializer.is_valid():
                    try:
                        new_user = user_serializer.save()
                        small_group.members.add(new_user)
                        return Response(
                            {
                                "small_group": smallGroupSerializer(small_group).data,
                                "message": "User successfully added to the group",
                            },
                            status=status.HTTP_202_ACCEPTED,
                        )
                    except (ValueError, TypeError) as e:
                        return Response(
                            {"error": str(e)},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                else:
                    return Response(
                        {"error": user_serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            except SmallGroup.DoesNotExist:
                return Response(
                    {"error": "small group not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            return Response(
                {"error": "You do not have permission to create small groups"},
                status=status.HTTP_403_FORBIDDEN,
            )
    return Response(
        {"error": "Invalid HTTP method"}, status=status.HTTP_400_BAD_REQUEST
    )


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def recordAttendance(request, group_id):
    group_leader = request.user
    try:
        group = SmallGroup.objects.get(id=group_id)
    except SmallGroup.DoesNotExist:
        return Response(
            {"error": "Small group requested doesn't exist"},
            status=status.HTTP_404_NOT_FOUND,
        )
    if group_leader.is_group_leader:
        serializer = AttendanceSerializer(data=request.data, context={"group": group})
        try:
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "attendance": serializer.data,
                        "message": "Attendance successfully recorded",
                    },
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
                )
        except ValueError as ve:
            return Response({"error": str(ve)})


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def getOrganizationsGroupLeader(request, organization_id):
    user = request.user
    if user.is_admin:
        try:
            organization = Organization.objects.get(id=organization_id)
            small_groups = organization.small_groups.all()
            leaders = [group.leader for group in small_groups]
            unique_leaders = {leader.email: leader for leader in leaders}.values()
            serializer = UserResponseSerializer(unique_leaders, many=True)
            return Response(
                {"leaders": serializer.data},
            )
        except Organization.DoesNotExist:
            return Response(
                {"error": "Organization requested doesn't exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
    else:
        return Response(
            {"error": "You do not have required permission"},
            status=status.HTTP_403_FORBIDDEN,
        )


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def getSmallGroups(request, organization_id):
    user = request.user
    if user.is_admin:
        try:
            organization = Organization.objects.get(id=organization_id)
            groups = organization.small_groups.all()
            serializer = smallGroupSerializer(groups, many=True)
            return Response({"groups": serializer.data})
        except Organization.DoesNotExist:
            return Response(
                {"error": "Organization requested doesn't exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
    else:
        return Response(
            {"error": "You do not have required permission"},
            status=status.HTTP_403_FORBIDDEN,
        )


def get_week_range(input_date):
    # Calculate the number of days between the input date and the nearest Monday
    days_to_monday = (input_date.weekday() - 0) % 7

    # Calculate the start date (Monday) of the week
    start_date = input_date - timedelta(days=days_to_monday)

    # Calculate the end date (Sunday) of the week
    end_date = start_date + timedelta(days=6)

    # Format the start and end dates in the desired format
    formatted_start_date = start_date.strftime("%m/%d/%Y")
    formatted_end_date = end_date.strftime("%m/%d/%Y")

    # Return the formatted range
    return f"{formatted_start_date}-{formatted_end_date}"


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def weeklyAttendanceCount(request, organization_id, year):
    """
    This view will be used to return the organization data such as: each group's weekly attendance.
    The attendance record for each group will have the following format:
    {"week": 1, "dates": "01/01-01/07", "year": 2023, "total_attending_users": 10},
    """
    user = request.user
    if user.is_admin:
        try:
            organization = Organization.objects.get(id=organization_id)
            groups = organization.small_groups.all()
            requested_year = int(year)
            if groups:
                result = {
                    "attendance_counts": [],
                    "message": "Organization's yearly attendance record on a weekly basis",
                }
                for group in groups:
                    group_weekly_attendance = []
                    queryset = (
                        Attendance.objects.filter(
                            group=group, meeting_date__year=requested_year
                        )
                        .values("week_number", "meeting_date")
                        .annotate(total_attended_members=Count("members_present"))
                    )
                    for entry in queryset:
                        week_data = {
                            "week": entry["week_number"],
                            "dates": get_week_range(entry["meeting_date"]),
                            "total_attendend_members": entry["total_attended_members"],
                        }
                        group_weekly_attendance.append(week_data)
                    group_data = {
                        "group_id": group.id,
                        "group_name": group.name,
                        "weekly_attendance_data": group_weekly_attendance,
                    }
                    result["attendance_counts"].append(group_data)
                return Response(result)
            else:
                return Response(
                    {
                        "attendance_counts": [],
                        "message": "No small-groups in this organization",
                    }
                )
        except Organization.DoesNotExist:
            return Response(
                {"error": "Organization requested doesn't exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
    else:
        return Response(
            {"error": "You do not have required permission"},
            status=status.HTTP_403_FORBIDDEN,
        )


# server_current_time = timezone.now()
# central_timezone = pytz.timezone("America/Chicago")
# current_time_central = timezone.localtime(
#     timezone.now(), timezone=central_timezone
# )
# (
#     current_central_year,
#     current_central_month,
#     current_central_day,
# ) = current_time_central.date().timetuple()[:3]
# send_time = datetime(
#     current_central_year,
#     current_central_month,
#     current_central_day,
#     20,
#     00,
#     00,
# )

# date = current_time_central.date()
# date_time = datetime.combine(date, send_time.time())
# non_naive_time = central_timezone.localize(date_time)
# sender_server_time = timezone.localtime(
#     non_naive_time, timezone=timezone.get_current_timezone()
# )
# current_time_central = timezone.localtime(
#     timezone.now(), timezone=central_timezone
# )
# time_difference = current_time_central.utcoffset().total_seconds()
# execution_time_server = server_current_time + timedelta(
#     seconds=time_difference
# )
# print(f"time at which the server will send message: {sender_server_time}")
