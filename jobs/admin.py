from django.contrib import admin
from .models import JobOffer, SearchHistory

@admin.register(JobOffer)
class JobOfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'location', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'company', 'description')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('keywords', 'location', 'source', 'created_at', 'results_count')
    list_filter = ('source', 'created_at')
    search_fields = ('keywords', 'location')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
