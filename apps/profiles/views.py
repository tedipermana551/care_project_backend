from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from core.exceptions import success_response
from core.permissions import IsLinkedPartner
from .models import UserProfile
from .serializers import (UserProfileSerializer, ProfileSetupSerializer, ProfileUpdateSerializer, LinkPartnerSerializer)

def _get_or_create_profile(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile

class ProfileSetupView(APIView):
    def post(self, request):
        profile = _get_or_create_profile(request.user)
        serializer = ProfileSetupSerializer(profile, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=UserProfileSerializer(profile).data,
                                message='Profile set up successfully.',
                                status=status.HTTP_201_CREATED)

class ProfileMeView(APIView):
    def get(self, request):
        profile = _get_or_create_profile(request.user)
        return success_response(data=UserProfileSerializer(profile).data)

    def patch(self, request):
        profile = _get_or_create_profile(request.user)
        serializer = ProfileUpdateSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=UserProfileSerializer(profile).data, message='Profile successfully updated.')

class MyCodeView(APIView):
    def get(self, request):
        profile = _get_or_create_profile(request.user)
        return success_response(data={'unique_code': profile.unique_code})

class LinkPartnerView(APIView):
    def post(self, request):
        from rest_framework import status
        from rest_framework.response import Response

        serializer = LinkPartnerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code'].upper()

        my_profile = _get_or_create_profile(request.user)

        if my_profile.unique_code == code:
            return Response({'success':False, 'message': 'You cannot link with yourself.', 'errors': {}},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            target = UserProfile.objects.get(unique_code=code)
        except UserProfile.DoesNotExist:
            return Response({'success':False, 'message': 'User does not exist.', 'errors': {}},
                            status=status.HTTP_404_NOT_FOUND)

        if my_profile.partner is not None:
            return Response({'success':False, 'message': 'You already linked to a partner', 'errors': {}},
                            status=status.HTTP_400_BAD_REQUEST)

        if my_profile.role and target.role and my_profile.role == target.role:
            return Response({'success':False, 'message': 'Partner must have complementary roles (mother or husband)', 'errors': {}},
                            status=status.HTTP_400_BAD_REQUEST)

        if not my_profile.role or not target.role:
            return Response({'success': False,
                             'message': 'Both users must set their role before linking.',
                             'errors': {}}, status=400)
        if my_profile.role == target.role:
            return Response({'success': False,
                             'message': 'Partner must have a complementary role.',
                             'errors': {}}, status=400)

        my_profile.partner = target
        target.partner = my_profile
        my_profile.save()
        target.save()

        return success_response(data=UserProfileSerializer(my_profile).data, message='Partner Linked successfully.')

class UnlinkPartnerView(APIView):
    permission_classes = [IsAuthenticated, IsLinkedPartner]

    def delete(self, request):
        my_profile = _get_or_create_profile(request.user)
        partner = my_profile.partner

        my_profile.partner = None
        my_profile.save()

        if partner:
            partner.partner = None
            partner.save()

        return success_response(message='Partner unlinked successfully.')

#pregnancy Status
class PregnancyStatusView(APIView):
    def get(self, request):
        from rest_framework import status
        from rest_framework.response import Response

        profile = _get_or_create_profile(request.user)
        mother = profile.mother_profile

        if mother is None:
            return Response({'success':False, 'message': 'No pregnancy data found. Link to a mother profile', 'errors': {}},
                            status=status.HTTP_404_NOT_FOUND)

        today = timezone.now().date()
        due_date = mother.due_date
        start_date = mother.pregnancy_start_date

        if not due_date:
            return Response({'success': False, 'message': 'Due date is not set', 'errors': {}},
                            status=status.HTTP_404_NOT_FOUND)

        if not start_date:
            return Response({'success': False,
                             'message': 'Pregnancy start date is not set.', 'errors': {}},
                            status=status.HTTP_404_NOT_FOUND)

        days_pregnant = (today - start_date).days if start_date else None
        weeks_pregnant = days_pregnant // 7 if days_pregnant is not None else None

        if weeks_pregnant is not None:
            if weeks_pregnant <= 12:
                trimester = 1
            elif weeks_pregnant <= 26:
                trimester = 2
            else:
                trimester = 3
        else:
            trimester = None

        is_overdue = today > due_date
        days_until_due = max((due_date - today).days, 0)
        weeks_until_due = days_until_due // 7

        total_days = (due_date - start_date).days if start_date else None
        progress = round((days_pregnant / total_days) * 100, 1) if (days_pregnant and total_days) else None

        return success_response(data={
            'due_date': due_date,
            'pregnancy_start_date': start_date,
            'days_pregnant': days_pregnant,
            'weeks_pregnant': weeks_pregnant,
            'trimester': trimester,
            'days_until_due': days_until_due,
            'weeks_until_due': weeks_until_due,
            'progress_percentage': progress,
            'is_overdue': is_overdue,
        })