from django.contrib import admin
from .models import Policies, AgentPolicy, InsurerPolicy

admin.site.register(Policies)
admin.site.register(AgentPolicy)
admin.site.register(InsurerPolicy)
