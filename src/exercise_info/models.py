from django.db import models


class ExerciseRecord(models.Model):
    exercise_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    type = models.CharField(max_length=30)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    calorie_cost = models.IntegerField()
    stress_source = models.CharField(max_length=100, blank=True)
    coping_action = models.CharField(max_length=100, blank=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.type} ({self.calorie_cost})"


class ExerciseGoal(models.Model):
    exercise_goal_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    type = models.CharField(max_length=30)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    target_calorie_cost = models.IntegerField()
    reminder_text = models.CharField(max_length=200, blank=True)
    support_quote = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.type
