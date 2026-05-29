from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from exercise_info.models import ExerciseGoal


def cover(request):
    return render(request, 'cover.html')


def about(request):
    return render(request, 'about.html')


def contact_us(request):
    return render(request, 'contact_us.html')


@login_required
def index(request):
    return render(request, 'index.html')


@login_required
def get_exercise_goals(request):
    goals = ExerciseGoal.objects.filter(user_id=request.user.id)
    events = []
    for goal in goals:
        events.append({
            "id": goal.exercise_goal_id,
            "title": f"{goal.type} - {goal.reminder_text or '心理放松提醒'}",
            "start": goal.start_time.isoformat(),
            "end": goal.end_time.isoformat(),
            "className": "success",
        })
    return JsonResponse(events, safe=False)
