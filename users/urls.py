from django.urls import path



from .views import (
    CertificateDownloadView,
    DashboardView,
    KeyDownloadView,
    LoginView,
    LogoutView,
    PrivateKeyDownloadView,
    RegisterView,
)

urlpatterns = [
    path("", LoginView.as_view()),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("keys/", KeyDownloadView.as_view(), name="key-download"),
    path("keys/download/private_key/", PrivateKeyDownloadView.as_view(), name="download-private-key"),
    path("keys/download/certificate/", CertificateDownloadView.as_view(), name="download-certificate"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
