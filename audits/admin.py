from django.contrib import admin

from audits.models import Audit, Doctype, Document, Package

admin.site.register(Audit)
admin.site.register(Doctype)
admin.site.register(Document)
admin.site.register(Package)
