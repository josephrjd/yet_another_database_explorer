from django.contrib import admin
from .models import DimUserType, UserMapping

# Registering model for easy debugging

admin.site.register(DimUserType)

admin.site.register(UserMapping)
