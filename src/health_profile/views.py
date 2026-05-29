import json
from statistics import mean

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views import View

from .models import HealthProfile


@method_decorator(login_required, name='dispatch')
class add_health_profile(View):
    def get(self, request):
        return render(request, 'health_profile/add_health_profile.html')

    def post(self, request):
        mood_score = request.POST.get('mood_score', None)
        stress_level = request.POST.get('stress_level', None)
        energy_level = request.POST.get('energy_level', None)
        sleep_hours = request.POST.get('sleep_hours', None)
        reflection = request.POST.get('reflection', '').strip()

        if not any([mood_score, stress_level, energy_level, sleep_hours, reflection]):
            messages.error(request, "请至少填写一项心理状态信息。")
            return redirect('add_health_profile')

        errors = []
        mood_score = float(mood_score) if mood_score else None
        stress_level = float(stress_level) if stress_level else None
        energy_level = float(energy_level) if energy_level else None
        sleep_hours = float(sleep_hours) if sleep_hours else None

        for label, value in [('情绪评分', mood_score), ('压力等级', stress_level), ('精力水平', energy_level)]:
            if value is not None and not 1 <= value <= 10:
                errors.append(f"{label}应在 1 到 10 之间。")
        if sleep_hours is not None and not 0 <= sleep_hours <= 24:
            errors.append("睡眠时长应在 0 到 24 小时之间。")

        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect('add_health_profile')

        HealthProfile.objects.create(
            user=request.user,
            mood_score=mood_score,
            stress_level=stress_level,
            energy_level=energy_level,
            sleep_hours=sleep_hours,
            reflection=reflection,
        )
        messages.success(request, "心理状态评估已保存。")
        return redirect('add_health_profile')


@method_decorator(login_required, name='dispatch')
class health_profile_list(View):
    def get(self, request):
        health_profiles = HealthProfile.objects.filter(user=request.user).order_by('-timestamp')
        mood_data = [{'date': profile.timestamp.strftime('%Y-%m-%d %H:%M'), 'value': float(profile.mood_score)}
                     for profile in health_profiles if profile.mood_score is not None]
        stress_data = [{'date': profile.timestamp.strftime('%Y-%m-%d %H:%M'), 'value': float(profile.stress_level)}
                       for profile in health_profiles if profile.stress_level is not None]
        energy_data = [{'date': profile.timestamp.strftime('%Y-%m-%d %H:%M'), 'value': float(profile.energy_level)}
                       for profile in health_profiles if profile.energy_level is not None]
        sleep_data = [{'date': profile.timestamp.strftime('%Y-%m-%d %H:%M'), 'value': float(profile.sleep_hours)}
                      for profile in health_profiles if profile.sleep_hours is not None]

        return render(request, 'health_profile/health_profile_list.html', {
            'health_profiles': health_profiles,
            'mood_data': json.dumps(mood_data),
            'stress_data': json.dumps(stress_data),
            'energy_data': json.dumps(energy_data),
            'sleep_data': json.dumps(sleep_data),
        })


@method_decorator(login_required, name='dispatch')
class delete_health_profile(View):
    def post(self, request, health_profile_id):
        health_profile = get_object_or_404(HealthProfile, id=health_profile_id, user=request.user)
        health_profile.delete()
        return redirect('health_profile_list')


@method_decorator(login_required, name='dispatch')
class health_profile_analysis(View):
    def get(self, request):
        profiles = list(HealthProfile.objects.filter(user=request.user).order_by('-timestamp')[:7])
        latest = profiles[0] if profiles else None

        mood_values = [float(profile.mood_score) for profile in profiles if profile.mood_score is not None]
        stress_values = [float(profile.stress_level) for profile in profiles if profile.stress_level is not None]
        energy_values = [float(profile.energy_level) for profile in profiles if profile.energy_level is not None]
        sleep_values = [float(profile.sleep_hours) for profile in profiles if profile.sleep_hours is not None]

        avg_mood = round(mean(mood_values), 1) if mood_values else None
        avg_stress = round(mean(stress_values), 1) if stress_values else None
        avg_energy = round(mean(energy_values), 1) if energy_values else None
        avg_sleep = round(mean(sleep_values), 1) if sleep_values else None

        status_title = "继续保持"
        status_desc = "你的近期状态整体平稳，可以继续维持当前节奏。"
        quote = "每一次认真感受自己的情绪，都是在照顾内心。"
        tip = "今天给自己留 10 分钟，做一次不被打扰的深呼吸。"

        if avg_stress is not None and avg_stress >= 7:
            status_title = "压力偏高"
            status_desc = "最近压力水平较高，建议优先处理最耗神的一件事，并适度降低额外任务。"
            quote = "先把呼吸放慢，答案通常会跟着变清楚。"
            tip = "试试 4-6 呼吸法：吸气 4 秒，呼气 6 秒，连续 5 轮。"
        elif avg_mood is not None and avg_mood <= 4:
            status_title = "情绪需要被照顾"
            status_desc = "近期情绪评分偏低，适合通过倾诉、运动或短时休息给自己做一点修复。"
            quote = "低落不是失败，它只是提醒你需要更多照顾。"
            tip = "联系一个让你安心的人，或者写下今天最困扰你的三件事。"
        elif avg_energy is not None and avg_energy <= 4:
            status_title = "精力不足"
            status_desc = "你的精力水平偏低，先保证睡眠和基本作息，比强行赶进度更重要。"
            quote = "休息不是停下，而是在为下一次出发蓄力。"
            tip = "今晚尽量提前半小时休息，睡前减少刷手机。"

        return render(request, 'health_profile/health_profile_analysis.html', {
            'latest': latest,
            'avg_mood': avg_mood,
            'avg_stress': avg_stress,
            'avg_energy': avg_energy,
            'avg_sleep': avg_sleep,
            'status_title': status_title,
            'status_desc': status_desc,
            'quote': quote,
            'tip': tip,
        })
