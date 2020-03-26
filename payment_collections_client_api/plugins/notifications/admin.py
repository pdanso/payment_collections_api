from django.contrib import admin

# Register your models here.
from plugins.notifications.models import Channel
from plugins.notifications.models import Messages

admin.site.register(Channel)
admin.site.register(Messages)


