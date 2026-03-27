

from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, FormView, TemplateView

from ecp_auth.generator import generate_key_and_certificate, private_key_to_pem
from ecp_auth.mixins import ECPLoginMixin
from ecp_auth.models import ECPCertificate

from ecp_auth.forms import ECPLoginForm, ECPRegisterForm


class RegisterView(CreateView):
    form_class = ECPRegisterForm
    template_name = "auth/register.html"
    success_url = reverse_lazy("key-download")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)  # saves user → form.instance gets PK
        user = form.instance
        key_password = form.cleaned_data.get("key_password")

        private_key, cert_pem = generate_key_and_certificate(user.username)
        ECPCertificate.objects.update_or_create(
            user=user,
            defaults={"certificate_pem": cert_pem.decode()},
        )
        self.request.session["ecp_key_pem"] = private_key_to_pem(private_key, key_password)
        self.request.session["ecp_cert_pem"] = cert_pem.decode()

        login(self.request, user, backend="django.contrib.auth.backends.ModelBackend")
        return response


class KeyDownloadView(LoginRequiredMixin, TemplateView):
    template_name = "auth/keys.html"
    login_url = "login"


class PrivateKeyDownloadView(LoginRequiredMixin, View):
    login_url = "login"

    def get(self, request: HttpRequest) -> HttpResponse:
        key_pem = request.session.pop("ecp_key_pem", None)
        if key_pem is None:
            return HttpResponse("Приватний ключ вже завантажено або сесія закінчилась.", status=404)
        response = HttpResponse(key_pem, content_type="application/x-pem-file")
        response["Content-Disposition"] = 'attachment; filename="private_key.pem"'
        return response


class CertificateDownloadView(LoginRequiredMixin, View):
    login_url = "login"

    def get(self, request: HttpRequest) -> HttpResponse:
        from ecp_auth.models import ECPCertificate
        try:
            cert = ECPCertificate.objects.get(user=request.user)
        except ECPCertificate.DoesNotExist:
            return HttpResponse("Сертифікат не знайдено.", status=404)
        request.session.pop("ecp_cert_pem", None)
        response = HttpResponse(cert.certificate_pem, content_type="application/x-pem-file")
        response["Content-Disposition"] = 'attachment; filename="certificate.pem"'
        return response


class LoginView(ECPLoginMixin, FormView):
    form_class = ECPLoginForm
    template_name = "auth/login.html"
    success_url = reverse_lazy("dashboard")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard")
        return super().dispatch(request, *args, **kwargs)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"
    login_url = "login"


class LogoutView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        logout(request)
        return redirect("login")
