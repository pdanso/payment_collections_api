from django.urls import path
from plugins.notifications.api_views.UpdateSmsDlrStatus import update_sms_dlr

urlpatterns = [
    path('updatesmsdlr/', update_sms_dlr, name="update-sms-dlr"),
]
