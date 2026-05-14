from django.urls import path
from .views import (AppointmentListCreateView, UpcomingAppointmentsView, AppointmentDetailView,
                    CompleteAppointmentView, PartnerAppointmentView,)

urlpatterns = [
    path('', AppointmentListCreateView.as_view(), name='appointment-liat-create'),
    path('upcoming/', UpcomingAppointmentsView.as_view(), name='appointment-upcoming'),
    path('partner/', PartnerAppointmentView.as_view(), name='appointment-partner'),
    path('<int:pk>/', AppointmentDetailView.as_view(), name='appointment-detail'),
    path('<int:pk>/complete/', CompleteAppointmentView.as_view(), name='appointment-complete'),
]