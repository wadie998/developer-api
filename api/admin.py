from django.contrib import admin

from api.models.models import JhiAuthority, JhiUser, JhiUserAuthority

admin.site.register(JhiAuthority)
admin.site.register(JhiUser)
admin.site.register(JhiUserAuthority)
