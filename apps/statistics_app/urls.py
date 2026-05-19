from django.urls import path
from .views import (SummaryStatsView, MoodStatsView, SleepStatsView, ExerciseStatsView, StreakStatsView)

urlpatterns = [
    path('summary/', SummaryStatsView.as_view(), name='stats-summary'),
    path('mood/', MoodStatsView.as_view(), name='stats-mood'),
    path('sleep/', SleepStatsView.as_view(), name='stats-sleep'),
    path('exercise/', ExerciseStatsView.as_view(), name='stats-exercise'),
    path('streaks/', StreakStatsView.as_view(), name='stats-streak'),
]