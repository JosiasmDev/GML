from django.contrib import admin
from .models import JobOffer


@admin.register(JobOffer)
class JobOfferAdmin(admin.ModelAdmin):
    list_display = ('position', 'company', 'city', 'contract_type', 'created_at')
    list_filter = ('city', 'company', 'contract_type', 'created_at')
    search_fields = ('position', 'company', 'city', 'country')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',) 