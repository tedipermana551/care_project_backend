from django.urls import path
from .views import (ProfileSetupView, ProfileMeView, MyCodeView, LinkPartnerView, UnlinkPartnerView)

urlpatterns = [
    path('setup/', ProfileSetupView.as_view(), name='profile-setup'),
    path('me/', ProfileMeView.as_view(), name='profile-me'),
    path('my-code/', MyCodeView.as_view(), name='profile-my-code'),
    path('link-partner/', LinkPartnerView.as_view(), name='profile-link-partner'),
    path('unlink-partner/', UnlinkPartnerView.as_view(), name='profile-unlink-partner'),
]