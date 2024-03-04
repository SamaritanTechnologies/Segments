from django.contrib import admin

from dashboard.models import Traits, Segment, AnalyzeReport, Questions, Answers


@admin.register(Traits)
class TraitsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    search_fields = ('title',)


@admin.register(Segment)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'sample_size')


@admin.register(AnalyzeReport)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'audience', 'trait'   )


admin.site.register(Questions)
admin.site.register(Answers)
