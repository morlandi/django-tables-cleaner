from django.contrib import admin
from .models import Sample


@admin.register(Sample)
class SampleAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    list_display = ['id', 'created', ]

