from django.contrib import admin

from .models import ReputationScore, Review


@admin.register(ReputationScore)
class ReputationScoreAdmin(admin.ModelAdmin):
    list_display = ("user_profile", "score", "reviews_count")
    ordering = ("-score",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("target_user", "author", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("comment",)
