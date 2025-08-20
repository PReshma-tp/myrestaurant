from django.shortcuts import redirect
from django.views.generic import ListView, DetailView
from django.db.models import Avg, Prefetch
from django.db.models.functions import Coalesce
from .models import Restaurant, Photo, MenuItem
from interactions.views import BookmarkAnnotationMixin, VisitedAnnotationMixin
from content.forms import ReviewForm
from django.contrib.contenttypes.models import ContentType
from content.models import Review
from django.db import IntegrityError
from django.urls import reverse
from django.contrib import messages
from .filters import RestaurantFilter

# Create your views here.
class ReviewHandleMixin:
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        content_type = ContentType.objects.get_for_model(self.object)
        object_id = self.object.pk

        existing_review = Review.objects.filter(
            user=self.request.user,
            content_type=content_type,
            object_id=object_id
        ).first()

        form = ReviewForm(request.POST, instance=existing_review)

        if form.is_valid():
            try:
                review = form.save(commit=False)
                review.user = request.user
                review.content_type = content_type
                review.object_id = object_id
                review.save()
                return redirect(self.object.get_absolute_url())
            except IntegrityError:
                messages.warning(self.request, "You have already submitted a review for this item.")
                return redirect(self.object.get_absolute_url())

        return self.render_to_response(self.get_context_data(form=form))


class UserReviewFormMixin:
    def get_review_form(self, obj):
        if not self.request.user.is_authenticated:
            return None
        user_review = obj.reviews.filter(user=self.request.user).first()
        return ReviewForm(instance=user_review) if user_review else ReviewForm()


class BaseDetailView(UserReviewFormMixin, DetailView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.object

        if 'form' in kwargs:
            context["review_form"] = kwargs['form']
        else:
            context["review_form"] = self.get_review_form(obj)

        context["latest_reviews"] = obj.reviews.all()[:3]
        return context

class RestaurantListView(BookmarkAnnotationMixin, ListView):
    model = Restaurant
    template_name = 'restaurants/restaurant_list.html'
    context_object_name = 'restaurants'

    def get_queryset(self):
        queryset= (
            Restaurant.objects
            .prefetch_related('cuisines', 'photos')
            .annotate(avg_rating=Coalesce(Avg('reviews__rating'), 0.0))
        )
        queryset = self.annotate_with_bookmarks(queryset)

        self.filterset = RestaurantFilter(self.request.GET, queryset=queryset)

        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['filter'] = self.filterset
        
        context['spotlight_restaurants'] = [
            restaurant for restaurant in self.object_list if restaurant.spotlight
        ]

        return context

class RestaurantDetailView(BookmarkAnnotationMixin,VisitedAnnotationMixin, BaseDetailView, ReviewHandleMixin):
    model = Restaurant
    template_name = "restaurants/restaurant_detail.html"
    context_object_name = "restaurant"

    def get_queryset(self):
        queryset = (Restaurant.objects
            .prefetch_related(
                "cuisines",
                self._prefetch_photos(),
                self._prefetch_menu_items(),
            )
            .annotate(avg_rating=Coalesce(Avg('reviews__rating'), 0.0))
        )
        queryset = self.annotate_with_bookmarks(queryset)

        return self.annotate_with_visited(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        photos = list(self.object.photos.order_by('id'))
        context["main_photo"] = photos[0] if photos else None
        context["extra_photos"] = photos[1:] if len(photos) > 1 else []
        context["menu_items"] = self.object.menu_items.all()
        return context

    def _prefetch_photos(self):
        return Prefetch(
            "photos",
            queryset=Photo.objects.only("id", "image", "object_id")
        )

    def _prefetch_menu_items(self):
        return Prefetch(
            "menu_items",
            queryset=MenuItem.objects.prefetch_related(
                self._prefetch_photos()
            ).annotate(avg_rating=Coalesce(Avg('reviews__rating'), 0.0))
        )

class MenuItemDetailView(BaseDetailView, ReviewHandleMixin):
    model = MenuItem
    template_name = 'restaurants/menu_item_detail.html'
    context_object_name = 'menu_item'
    pk_url_kwarg = "menu_id"

    def get_object(self, queryset=None):
        menu_id = self.kwargs.get('menu_id')
        return self.get_queryset().get(pk=menu_id)

    def get_queryset(self):
        return self._menuitem_with_details()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        menu_item = self.object

        context.update({
            "restaurant": menu_item.restaurant,
            "menu_photo": menu_item.photos.all().first(),
            "related_items": self._get_related_items(menu_item),
            "avg_rating": menu_item.avg_rating,
    })
        return context

    def _get_related_items(self, menu_item):
        return (
            self._menuitem_with_details()
            .filter(
                cuisine=menu_item.cuisine,
                restaurant=menu_item.restaurant
            )
            .exclude(id=menu_item.id)
        )
    
    def _menuitem_with_details(self):
        return (
            MenuItem.objects
            .select_related('restaurant', 'cuisine')
            .annotate(avg_rating=Avg('reviews__rating'))
            .prefetch_related(
                Prefetch(
                    'photos',
                    queryset=Photo.objects.only('id', 'image', 'object_id').order_by('id')
                )
            )
        )
