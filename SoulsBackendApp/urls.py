from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView

from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    # path("login", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("login", views.login, name="login_user"),
    path("logout", views.logout, name="logout_user"),
    path("register", views.register, name="regist_user"),
    path("organization/add", views.addOrganization, name="organization_add"),
    path(
        "organization/<uuid:organization_id>/add-small-group",
        views.addSmallGroup,
        name="add_small_group",
    ),
    path(
        "organization/<uuid:organization_id>/add-small-group-eleader",
        views.addSmallGroupWithExistingLeader,
        name="add_small_group_with_existing_leader",
    ),
    path(
        "group/<uuid:group_id>/add-member",
        views.addSmallGroupMember,
        name="add_small_group_member",
    ),
    path(
        "group/<uuid:group_id>/record-attendance",
        views.recordAttendance,
        name="record_attendance",
    ),
    path(
        "organization/<uuid:organization_id>/get-groups",
        views.getSmallGroups,
        name="get_small_groups",
    ),
    path(
        "organization/<uuid:organization_id>/get-leaders",
        views.getOrganizationsGroupLeader,
        name="get_small_group_leaders",
    ),
    path(
        "organization/<uuid:organization_id>/get-attendance-record/<int:year>",
        views.weeklyAttendanceCount,
        name="get_organization_yearly_attendance_record",
    ),
    path(
        "group/<uuid:group_id>/get-members",
        views.getSmallGroupMembers,
        name="get_small_group_members",
    ),
    path("api/", include("SoulsBackendApp.api.urls")),
    path("oauth/", include("SoulsBackendApp.oauth.urls")),
]
