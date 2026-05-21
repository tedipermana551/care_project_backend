from django.urls import path
from .views import DailyLogListCreateView, TodayLogView, DailyLogDetailView, PartnerLogsView, PartnerMessagesView

urlpatterns = [
    path('', DailyLogListCreateView.as_view(), name='log-list-create'),
    path('today/', TodayLogView.as_view(), name='log-today'),
    path('partner/', PartnerLogsView.as_view(), name='log-partner'),
    path('partner/messages/', PartnerMessagesView.as_view(), name='log-partner-messages'),
    path('<str:log_date>/', DailyLogDetailView.as_view(), name='log-detail'),
]