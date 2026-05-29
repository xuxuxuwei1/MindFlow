from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import ExerciseGoalForm, ExerciseRecordForm
from .models import ExerciseGoal, ExerciseRecord


def exercise_record_list(request):
    records = ExerciseRecord.objects.filter(user_id=request.user.id).order_by('-start_time')
    records_with_meta = []
    for index, record in enumerate(records, start=1):
        duration_text = '未记录'
        if record.end_time:
            duration = record.end_time - record.start_time
            total_minutes = max(int(duration.total_seconds() // 60), 0)
            duration_text = f"{total_minutes} 分钟"
        records_with_meta.append({
            'index': index,
            'record': record,
            'duration_text': duration_text,
        })
    return render(request, "exercise_info/exercise_record_list.html", {"records": records_with_meta})


def add_exercise_record(request):
    if request.method == 'POST':
        form = ExerciseRecordForm(request.POST)
        if form.is_valid():
            emotion_record = form.save(commit=False)
            emotion_record.user_id = request.user.id
            emotion_record.save()
            messages.success(request, '情绪日志已保存。')
            return redirect('exercise_record_list')
    else:
        form = ExerciseRecordForm()
    return render(request, 'exercise_info/add_exercise_record.html', {'form': form})


def delete_exercise_record(request, exerciseid):
    record = get_object_or_404(ExerciseRecord, exercise_id=exerciseid, user_id=request.user.id)
    record.delete()
    return redirect('exercise_record_list')


def exercise_goal_list(request):
    goals = ExerciseGoal.objects.filter(user_id=request.user.id).order_by('start_time')
    goals_with_progress = []
    complete_cnt = 0
    uncompleted_cnt = 0
    for goal in goals:
        completed_sessions = ExerciseRecord.objects.filter(
            user_id=request.user.id,
            start_time__gte=goal.start_time,
            start_time__lte=goal.end_time,
        ).count()
        progress = (completed_sessions / goal.target_calorie_cost) * 100 if goal.target_calorie_cost else 0
        timeout = timezone.now() > goal.end_time
        if progress >= 100:
            complete_cnt += 1
        elif timeout:
            uncompleted_cnt += 1
        goals_with_progress.append({
            'goal': goal,
            'completed_sessions': completed_sessions,
            'progress': progress,
            'is_completed': progress >= 100,
            'timeout': timeout,
        })

    total_cnt = len(goals_with_progress)
    doing_cnt = total_cnt - uncompleted_cnt - complete_cnt
    return render(request, 'exercise_info/exercise_goal_list.html', {
        'goals': goals_with_progress,
        'total_count': total_cnt,
        'complete_count': complete_cnt,
        'uncomplete_count': uncompleted_cnt,
        'doing_count': doing_cnt,
    })


def add_exercise_goal(request):
    if request.method == 'POST':
        form = ExerciseGoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user_id = request.user.id
            goal.save()
            messages.success(request, '放松计划已创建。')
            return redirect('exercise_goal_list')
    else:
        form = ExerciseGoalForm()
    return render(request, 'exercise_info/add_exercise_goal.html', {'form': form})


def exercise_goal_update(request, exerciseGoal_id):
    goal = get_object_or_404(ExerciseGoal, exercise_goal_id=exerciseGoal_id, user_id=request.user.id)
    if request.method == 'POST':
        form = ExerciseGoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            return redirect('exercise_goal_list')
    else:
        form = ExerciseGoalForm(instance=goal)
    return render(request, 'exercise_info/add_exercise_goal.html', {'form': form})


def exercise_goal_delete(request, exerciseGoal_id):
    goal = get_object_or_404(ExerciseGoal, exercise_goal_id=exerciseGoal_id, user_id=request.user.id)
    if request.method == 'POST':
        goal.delete()
        return redirect('exercise_goal_list')
    return render(request, 'exercise_info/exercise_goal_list.html', {'goal': goal})
