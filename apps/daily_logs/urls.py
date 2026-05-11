from django.urls import path
from .views import DailyLogListCreateView, TodayLogView, DailyLogDetailView, PartnerLogsView

urlpatterns = [
    path('', DailyLogListCreateView.as_view(), name='log-list-create'),
    path('today/', TodayLogView.as_view(), name='log-today'),
    path('partner/', PartnerLogsView.as_view(), name='log-partner'),
    path('<str:log_date>/', DailyLogDetailView.as_view(), name='log-detail'),
]