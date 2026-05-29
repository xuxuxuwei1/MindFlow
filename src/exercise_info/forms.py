from django import forms
from django.utils import timezone

from .models import ExerciseGoal, ExerciseRecord


class ExerciseRecordForm(forms.ModelForm):
    class Meta:
        model = ExerciseRecord
        fields = ['type', 'start_time', 'end_time', 'calorie_cost', 'stress_source', 'coping_action', 'note']
        widgets = {
            'type': forms.Select(choices=[
                ('', '请选择情绪类型'),
                ('开心', '开心'),
                ('平静', '平静'),
                ('焦虑', '焦虑'),
                ('疲惫', '疲惫'),
                ('难过', '难过'),
                ('生气', '生气'),
            ]),
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'calorie_cost': forms.NumberInput(attrs={'min': 1, 'max': 10}),
            'stress_source': forms.TextInput(attrs={'placeholder': '例如：课程压力、人际关系、实习面试'}),
            'coping_action': forms.TextInput(attrs={'placeholder': '例如：散步、听歌、和朋友聊天'}),
            'note': forms.Textarea(attrs={'rows': 4, 'placeholder': '记录当时发生了什么，以及你的感受'}),
        }
        labels = {
            'type': '情绪类型',
            'start_time': '记录时间',
            'end_time': '情绪缓解时间',
            'calorie_cost': '情绪强度（1-10）',
            'stress_source': '压力来源',
            'coping_action': '缓解方式',
            'note': '情绪日记',
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        intensity = cleaned_data.get('calorie_cost')
        current_time = timezone.now()

        if start_time and start_time > current_time:
            self.add_error('start_time', '记录时间不能晚于当前时间。')
        if end_time and end_time > current_time:
            self.add_error('end_time', '缓解时间不能晚于当前时间。')
        if start_time and end_time and end_time < start_time:
            self.add_error('end_time', '缓解时间不能早于记录时间。')
        if intensity is None or intensity < 1 or intensity > 10:
            self.add_error('calorie_cost', '情绪强度请填写 1 到 10 之间的整数。')
        return cleaned_data


class ExerciseGoalForm(forms.ModelForm):
    class Meta:
        model = ExerciseGoal
        fields = ['type', 'start_time', 'end_time', 'target_calorie_cost', 'reminder_text', 'support_quote']
        widgets = {
            'type': forms.Select(choices=[
                ('', '请选择计划主题'),
                ('正念呼吸', '正念呼吸'),
                ('情绪复盘', '情绪复盘'),
                ('运动放松', '运动放松'),
                ('睡前整理', '睡前整理'),
                ('社交连接', '社交连接'),
            ]),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'target_calorie_cost': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'reminder_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '例如：晚上 10 点前做 10 分钟呼吸放松'}),
            'support_quote': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '例如：允许自己慢一点，也是在前进'}),
        }
        labels = {
            'type': '计划主题',
            'start_time': '开始时间',
            'end_time': '结束时间',
            'target_calorie_cost': '计划执行次数',
            'reminder_text': '提醒语',
            'support_quote': '鼓励语录',
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        target_count = cleaned_data.get('target_calorie_cost')
        if start_time and end_time and end_time < start_time:
            self.add_error('end_time', '结束时间不能早于开始时间。')
        if target_count is None or target_count < 1:
            self.add_error('target_calorie_cost', '计划执行次数至少为 1。')
        return cleaned_data
