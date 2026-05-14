from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.exceptions import success_response
from core.permissions import IsLinkedPartner
from .models import Appointment
from .serializers import AppointmentSerializer

class AppointmentListCreateView(APIView):
    def get(self,request):
        qs = Appointment.objects.filter(user=request.user)
        return success_response(data=AppointmentSerializer(qs,many=True).data)

    def post(self,request):
        serializer = AppointmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return success_response(data=serializer.data, message="Appointment created successfully",
                                status=201)

class UpcomingAppointmentsView(APIView):
    def get(self,request):
        qs = Appointment.objects.filter(user=request.user, appointment_date__gte=timezone.now(),
                                        is_completed=False,)
        return success_response(data=AppointmentSerializer(qs,many=True).data)

class AppointmentDetailView(APIView):
    def _get_appointment(self,request,pk):
        try:
            return Appointment.objects.get(pk=pk, user=request.user)
        except Appointment.DoesNotExist:
            return None

    def get(self,request,pk):
        appt = self._get_appointment(request,pk)
        if not appt:
            return Response({'success': False, 'message': 'Appointment Not Found', 'errors': {}},
                            status=status.HTTP_404_NOT_FOUND)
        return success_response(data=AppointmentSerializer(appt).data)

    def patch(self,request,pk):
        appt = self._get_appointment(request,pk)
        if not appt:
            return Response({'success': False, 'message': 'Appointment Not Found', 'errors': {}},
                            status=status.HTTP_404_NOT_FOUND)
        serializer = AppointmentSerializer(appt, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=serializer.data, message="Appointment updated successfully",)

    def delete(self,request,pk):
        appt = self._get_appointment(request,pk)
        if not appt:
            return Response({'success': False, 'message': 'Appointment Not Found', 'errors': {}},
                            status=status.HTTP_404_NOT_FOUND)
        appt.delete()
        return success_response(message = 'Appointment deleted successfully')

class CompleteAppointmentView(APIView):
    def patch(self,request,pk):
        try:
            appt = Appointment.objects.get(pk=pk, user=request.user)
        except Appointment.DoesNotExist:
            return Response({'success': False, 'message': 'Appointment Not Found', 'errors': {}},
                            status=status.HTTP_404_NOT_FOUND)
        appt.is_completed = True
        appt.save()
        return success_response(data=AppointmentSerializer(appt).data,
                                message = 'Appointment marked as completed.')

class PartnerAppointmentView(APIView):
    permission_classes = [IsLinkedPartner]

    def get(self, request):
        partner_profile = request.user.userprofile.partner
        qs = Appointment.objects.filter(user=partner_profile.user)
        return success_response(data=AppointmentSerializer(qs,many=True).data)