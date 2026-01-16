from django.db import models
from mod_authentication.models import UserProfile


class ReputationScore(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)  # 0 to 100 gauge
    reviews_count = models.IntegerField(default=0)


class Review(models.Model):
    target_user = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="reviews_received"
    )
    author = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="reviews_written"
    )
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
