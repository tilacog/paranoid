from django.contrib import admin

from jobs.models import Job


class JobAdmin(admin.ModelAdmin):
    list_display = ('user', 'audit', 'created_at', 'state')
    list_display_links = ('user', 'audit')
    list_filter = ('state', 'audit')
    date_hierarchy = 'created_at'

    readonly_fields = ('audit', 'user', 'documents')

    fieldsets = (
        ('Job info', {
            'fields': readonly_fields
        }),
        ('Results', {
            'fields': ('state', 'report_file')
        })

    )

    search_fields = ('user__email',)

admin.site.register(Job, JobAdmin)
