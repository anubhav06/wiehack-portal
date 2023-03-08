from django.contrib import admin
from .models import User, Round, FormRequirements, SubmissionForm

# Register your models here.
admin.site.register(User)
admin.site.register(Round)
admin.site.register(FormRequirements)
admin.site.register(SubmissionForm)