from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class ReviewManager(models.Manager):
    def for_instance(self, instance):
        ct = ContentType.objects.get_for_model(instance)
        return self.filter(content_type=ct, object_id=instance.pk)


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ReviewManager()

    class Meta:
        ordering = ['-created_at']

    def clean(self):
        if Review.objects.exclude(pk=self.pk).filter(
            user=self.user,
            content_type=self.content_type,
            object_id=self.object_id
        ).exists():
            raise ValidationError("You have already reviewed this item.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} ({self.rating}★) on {self.content_object}"


class PhotoManager(models.Manager):
    def for_instance(self, instance):
        ct = ContentType.objects.get_for_model(instance)
        return self.filter(content_type=ct, object_id=instance.pk)


class Photo(models.Model):
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    image = models.ImageField(upload_to='photos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    objects = PhotoManager()

    class Meta:
        ordering = ['-uploaded_at']

    def clean(self):
        if not self.content_object:
            raise ValidationError("Photo must be linked to an object.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Photo for {self.content_object}"
