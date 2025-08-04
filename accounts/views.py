from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import login, logout
from django.views.generic import FormView, RedirectView
from django.contrib.auth.views import LoginView
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from .forms import RegisterForm


class RegisterView(FormView):
    template_name = "accounts/register.html"
    form_class = RegisterForm
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Account created! Please log in.")
        return super().form_valid(form)


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password.")
        return super().form_invalid(form)


@method_decorator(csrf_protect, name="dispatch")
@method_decorator(require_POST, name="dispatch")
class LogoutView(RedirectView):
    pattern_name = "accounts:login"

    def post(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, "You have been logged out.")
        return super().post(request, *args, **kwargs)
