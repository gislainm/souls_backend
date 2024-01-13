from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView

from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("register", views.register, name="regist_user"),
    path("organization/add", views.addOrganization, name="organization_add"),
    path(
        "organization/<uuid:organization_id>/add-small-group/",
        views.addSmallGroup,
        name="add_small_group",
    ),
    path("api/", include("SoulsBackendApp.api.urls")),
]
