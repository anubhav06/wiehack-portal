from django.contrib import admin
from .models import User, Round, FormRequirements, SubmissionForm, GradingSheet
from django.contrib.auth.admin import UserAdmin
from django.contrib.sessions.models import Session


class MyUserAdmin(UserAdmin):
    model = User

    fieldsets = UserAdmin.fieldsets + (
            (None, {'fields': ('teamID','team_type_offline', 'team_number')}),
    )

# Register your models here.
admin.site.register(User, MyUserAdmin)
admin.site.register(Round)
admin.site.register(FormRequirements)
admin.site.register(SubmissionForm)
admin.site.register(GradingSheet)
admin.site.register(Session)