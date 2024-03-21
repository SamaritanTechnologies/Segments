from django.contrib import admin

from dashboard.models import Traits, Segment, AnalyzeReport, Questions, Answers, Audience


@admin.register(Traits)
class TraitsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    search_fields = ('title',)


@admin.register(Segment)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'sample_size')


@admin.register(AnalyzeReport)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'audience', 'trait', 'loop')


@admin.register(Audience)
class AudienceAdmin(admin.ModelAdmin):
    list_display = ('id', 'prompt', 'email', 'process_completed')


admin.site.register(Questions)
admin.site.register(Answers)
