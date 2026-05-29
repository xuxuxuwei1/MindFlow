from django.contrib.auth.models import User
from django.db import models


class HealthProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='health_profiles', to_field='id')
    timestamp = models.DateTimeField(auto_now_add=True)
    mood_score = models.DecimalField(null=True, blank=True, max_digits=4, decimal_places=1)
    stress_level = models.DecimalField(null=True, blank=True, max_digits=4, decimal_places=1)
    energy_level = models.DecimalField(null=True, blank=True, max_digits=4, decimal_places=1)
    sleep_hours = models.DecimalField(null=True, blank=True, max_digits=4, decimal_places=1)
    reflection = models.TextField(blank=True)

    def __str__(self):
        return f"Mood profile for {self.user.username} at {self.timestamp}"
