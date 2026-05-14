from django.urls import path
from .views import PregnancyStatusView

urlpatterns = [
    path('status/', PregnancyStatusView.as_view(), name='pregnancy_status'),
]