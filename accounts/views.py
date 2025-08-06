from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import login, logout
from django.views.generic import FormView, RedirectView
from django.contrib.auth.views import LoginView
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from .forms import RegisterForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from interactions.models import Bookmark, Visited
from content.models import Review, Photo

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

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        sections = {
            'bookmarks': self._get_bookmarks(user),
            'visited': self._get_visited(user),
            'photos': self._get_photos(user),
            'reviews': self._get_reviews(user),
        }

        for name, qs in sections.items():
            context[f"{name}_count"] = qs.count()
            context[name] = qs[:5]

        return context
    
    def _get_bookmarks(self, user):
        return Bookmark.objects.filter(user=user) \
            .select_related('restaurant') \
            .order_by('-created_at')

    def _get_visited(self, user):
        return Visited.objects.filter(user=user) \
            .select_related('restaurant') \
            .order_by('-visited_on')

    def _get_photos(self, user):
        return Photo.objects.filter(uploaded_by=user) \
            .order_by('-uploaded_at')

    def _get_reviews(self, user):
        return Review.objects.filter(user=user) \
            .select_related('user') \
            .order_by('-created_at')
