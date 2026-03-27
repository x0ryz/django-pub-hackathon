from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("users.urls")),
    path("ecp/", include("ecp_auth.urls")),
    path('admin/', admin.site.urls),
]
