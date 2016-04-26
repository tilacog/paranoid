from django.contrib import admin

from squeeze.models import SqueezeJob


class SqueezejobAdmin(admin.ModelAdmin):
    list_display = (
        'created_at',
        'real_user_name',
        'real_user_email',
        'notified_at',
        'get_job_state',
        'get_audit_name',
    )
    date_hierarchy = 'created_at'


    # Job state info
    def get_job_state(self, obj):
        state = obj.job.state
        text = dict(obj.job.STATE_CHOICES)[state]
        return '{} - {}'.format(state, text)

    get_job_state.short_description = 'Job State'
    get_job_state.admin_order_field = 'job__state'


    # Audit info
    def get_audit_name(self, obj):
        return obj.job.audit.name
    get_audit_name.short_description = 'Audit'
    get_audit_name.admin_order_field = 'job__audit__name'

admin.site.register(SqueezeJob, SqueezejobAdmin)
