from django.contrib import admin

from api.models.models import Document, JhiAuthority, JhiUser, JhiUserAuthority, Request

admin.site.register(Request)
admin.site.register(Document)
admin.site.register(JhiAuthority)
admin.site.register(JhiUser)
admin.site.register(JhiUserAuthority)
