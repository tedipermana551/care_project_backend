from collections import Counter
from datetime import timedelta

from django.db.models import Avg, Count
from django.utils import timezone
from rest_framework.views import APIView

from core.exceptions import success_response
from apps.daily_logs.models import DailyLog

MOOD_ORDER = ['great', 'good', 'neutral', 'bad', 'terrible']

def _parse_date_params(params):
    start = params.get('start_date')
    end = params.get('end_date')
    period = params.get('period', 'all')

    today = timezone.now().date()

    if not start and not end:
        if period == 'weekly' :
            start = (today - timedelta(days=6)).isoformat()
            end = today.isoformat()
        elif period == 'monthly' :
            start = today.replace(day=1).isoformat()
            end = today.isoformat()
    return start, end, today

def _apply_date_filters(qs, start, end):
    if start:
        qs = qs.filter(date__gte=start)
    if end:
        qs = qs.filter(date__lte=end)
    return qs

def _compute_streak(qs, today):
    dates = set(qs.values_list('date', flat=True))
    streak = 0
    current = today
    while current in dates:
        streak += 1
        current -= timedelta(days=1)
    return streak

class SummaryStatsView(APIView):
    def get(self, request):
        start, end, today = _parse_date_params(request.query_params)
        qs = DailyLog.objects.filter(user=request.user)
        qs = _apply_date_filters(qs, start, end)

        total_logs = qs.count()
        streak = _compute_streak(DailyLog.objects.filter(user=request.user), today)

        agg = qs.aggregate(
            avg_sleep = Avg('sleep_duration'),
            avg_exercise = Avg('exercise_duration'),
        )

        mood_counts = dict(Counter(qs.values_list('mood', flat=True)))
        most_common = max(mood_counts, key=mood_counts.get) if mood_counts else None

        distribution = {m: mood_counts.get(m, 0) for m in MOOD_ORDER}

        return success_response(data={
            'total_logs': total_logs,
            'logging_streak_days': streak,
            'average_sleep_hours': round(float(agg['avg_sleep'] or 0), 1),
            'average_exercise_minutes': round(float(agg['avg_exercise'] or 0), 1),
            'most_common_mood': most_common,
            'mood_distribution': distribution,
            'period':{
                'start': start or (qs.order_by('date').values_list('date', flat=True).first()),
                'end': end or today.isoformat(),
            }
        })

class MoodStatsView(APIView):
    def get(self, request):
        start, end, today = _parse_date_params(request.query_params)
        qs = DailyLog.objects.filter(user=request.user)
        qs = _apply_date_filters(qs, start, end)

        mood_counts = (
            qs.values('mood')
            .annotate(count=Count('mood'))
            .order_by('mood')
        )

        raw = {item['mood']: item['count'] for item in mood_counts}
        distribution = {m: raw.get(m,0) for m in MOOD_ORDER}

        timeline = list(qs.order_by('date').values('date', 'mood'))

        return success_response(data={
            'mood_distribution': distribution,
            'timeline': timeline,
            'period':{'start': start, 'end': end or today.isoformat()}
        })

class SleepStatsView(APIView):
    def get(self, request):
        start, end, today = _parse_date_params(request.query_params)
        qs = DailyLog.objects.filter(user=request.user)
        qs = _apply_date_filters(qs, start, end)

        agg = qs.aggregate(avg=Avg('sleep_duration'))
        timeline = list(qs.order_by('date').values('date', 'sleep_duration'))

        return success_response(data={
            'average_sleep_hours': round(float(agg['avg'] or 0), 1),
            'timeline': timeline,
            'period': {'start':start, 'end':end or today.isoformat()}
        })

class ExerciseStatsView(APIView):
    def get(self, request):
        start, end, today = _parse_date_params(request.query_params)
        qs = DailyLog.objects.filter(user=request.user)
        qs = _apply_date_filters(qs, start, end)

        agg = qs.aggregate(avg=Avg('exercise_duration'))
        timeline = list(qs.order_by('date').values('date', 'exercise_duration'))

        return success_response(data={
            'average_exercise_minutes': round(float(agg['avg'] or 0), 1),
            'timeline': timeline,
            'period': {'start':start, 'end':end or today.isoformat()}
        })

class StreakStatsView(APIView):
    def get(self, request):
        today = timezone.now().date()
        all_logs = DailyLog.objects.filter(user=request.user)
        dates = sorted(set(all_logs.values_list('date', flat=True)),reverse=True)

        current_streak = _compute_streak(all_logs, today)
        longest_streak = 0
        run = 0
        prev = None
        for d in sorted(dates):
            if prev is None or (d - prev).days == 1:
                run += 1
            else:
                run = 1
            longest_streak = max(longest_streak, run)
            prev = d

        return success_response(data={
            'current_streak': current_streak,
            'longest_streak_days': longest_streak,
            'total_logged_days': len(dates),
            'last_logged_date': dates[0] if dates else None,
        })