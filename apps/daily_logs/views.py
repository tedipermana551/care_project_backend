from datetime import date
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.exceptions import success_response
from core.permissions import IsLinkedPartner
from .models import DailyLog
from .serializers import DailyLogSerializer

def _filter_logs(qs, params):
    start = params.get('start_date')
    end = params.get('end_date')
    mood = params.get('mood')
    month = params.get('month')

    if start:
        qs = qs.filter(date__gte=start)
    if end:
        qs = qs.filter(date__lte=end)
    if mood:
        qs = qs.filter(mood=mood)
    if month:
        try:
            years, mon = month.split('-')
            qs = qs.filter(date__year=int(year), date__month=int(mon))
        except (ValueError, AttributeError):
            pass
    return qs

class DailyLogListCreateView(APIView):
    def get(self, request):
        qs = DailyLog.objects.get(user=request.user)
        qs = _filter_logs(qs, request.query_params)
        return success_response(data=DailyLogSerializer(qs, many=True).data)

    def post(self, request):
        serializer = DailyLogSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        log_date = serializer.validated_data.get('date', timezone.now().date())

        if DailyLog.objects.filter(user=request.user, date=log_date).exists():
            return Response({'success': False, 'message': f'A log for {log_date} already exists.', 'errors': {}},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer.save(user=request.user)
        return success_response(data=serializer.data, message='Log created successfully.', status=status.HTTP_201_CREATED)

class TodayLogView(APIView):
    def get(self, request):
        today = timezone.now().date()
        try:
            log = DailyLog.objects.get(user=request.user, date=today)
            return success_response(data=DailyLogSerializer(log).data)
        except DailyLog.DoesNotExist:
            return Response({'success': False, 'message': 'No log found for today.', 'errors': {}},
                            status=status.HTTP_404_NOT_FOUND)

class DailyLogDetailView(APIView):
    def _get_log(self, request, log_date):
        try:
            return DailyLog.objects.get(user=request.user, date=log_date)
        except DailyLog.DoesNotExist:
            return None

    def get(self, request, log_date):
        log = self._get_log(request, log_date)
        if not log:
            return Response({'success': False, 'message': 'Log not found.', 'errors': {}},
                            status=status.HTTP_404_NOT_FOUND)
        return success_response(data=DailyLogSerializer(log).data)

    def patch(self, request, log_date):
        log = self._get_log(request, log_date)
        if not log:
            return Response({'success': False, 'message': 'Log not found.', 'errors': {}},
                            status=status.HTTP_404_NOT_FOUND)
        serializer = DailyLogSerializer(log, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=serializer.data, message='Log updated successfully.')

    def delete(self, request, log_date):
        log = self._get_log(request, log_date)
        if not log:
            return Response({'success': False, 'message': 'Log not found.', 'errors': {}},
                            status=status.HTTP_404_NOT_FOUND)
        log.delete()
        return success_response(message='Log deleted successfully.')

class PartnerLogsView(APIView):
    permission_classes = [IsLinkedPartner]

    def get(self, request):
        from rest_framework.permissions import IsAuthenticated
        partner_profile = request.user.userprofile.partner
        qs = DailyLog.objects.filter(user=partner_profile.user)
        qs = _filter_logs(qs, request.query_params)
        return success_response(data=DailyLogSerializer(qs, many=True).data)
