from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render

import exercise_info
import health_profile


def get_user_info(request):
    if request.user.is_authenticated:
        list(messages.get_messages(request))
        current_user = request.user
        user_info = {
            'username': current_user.username,
            'user_id': current_user.id,
            'join_date': current_user.date_joined,
        }

        journals = exercise_info.models.ExerciseRecord.objects.filter(user_id=current_user.id)
        journal_count = journals.count()

        goals = exercise_info.models.ExerciseGoal.objects.filter(user_id=current_user.id)
        completed_goals = 0
        for goal in goals:
            completed_sessions = exercise_info.models.ExerciseRecord.objects.filter(
                user_id=current_user.id,
                start_time__gte=goal.start_time,
                start_time__lte=goal.end_time,
            ).count()
            if goal.target_calorie_cost and completed_sessions >= goal.target_calorie_cost:
                completed_goals += 1

        profiles = health_profile.models.HealthProfile.objects.filter(user=request.user)
        profile_count = profiles.count()
        return render(request, 'user_center/user_center.html', {
            'user_info': user_info,
            'exercises_count': journal_count,
            'complete_count': completed_goals,
            'health_profile_count': profile_count,
        })

    messages.error(request, '请先登录')
    return redirect('login')


from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required


@login_required
def change_password(request):
    if request.method == 'POST':
        new_password = request.POST.get('newPassword')
        confirm_new_password = request.POST.get('confirmNewPassword')
        list(messages.get_messages(request))

        if new_password != confirm_new_password:
            messages.error(request, "新密码和确认新密码不一致，请重新验证")
            return render(request, 'user_center/reset_password.html')

        if len(new_password) < 6 or len(new_password) > 10:
            messages.error(request, "密码长度必须在 6 到 10 位之间")
            return render(request, 'user_center/reset_password.html')

        request.user.set_password(new_password)
        request.user.save()

    return render(request, 'user_center/reset_password.html')


@login_required
def validate_current_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('currentPassword')
        user = authenticate(username=request.user.username, password=current_password)
        list(messages.get_messages(request))
        if user is not None:
            request.session['current_password_valid'] = True
            return JsonResponse({'valid': True})
        messages.error(request, " ")
        return JsonResponse({'valid': False})
