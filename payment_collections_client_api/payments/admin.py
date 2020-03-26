from django.contrib import admin

# Register your models here.
from .models import Transactions
from .models import ExtraDetails


admin.site.register(Transactions)
admin.site.register(ExtraDetails)

