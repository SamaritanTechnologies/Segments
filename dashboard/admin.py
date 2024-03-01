from django.contrib import admin

from dashboard.models import Traits, Segment


@admin.register(Traits)
class TraitsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    search_fields = ('title',)


@admin.register(Segment)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'sample_size')
