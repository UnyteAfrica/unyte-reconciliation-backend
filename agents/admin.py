from django.contrib import admin

from .models import Agent, AgentProfile


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'middle_name', 'last_name')


@admin.register(AgentProfile)
class AgentProfileAdmin(admin.ModelAdmin):
    list_display = ('get_agent_first_name', 'get_agent_last_name', 'get_agent_profile_picture_url')

    def get_agent_first_name(self, obj: AgentProfile) -> str:
        return obj.agent.first_name

    def get_agent_last_name(self, obj: AgentProfile) -> str:
        return obj.agent.last_name

    def get_agent_profile_picture_url(self, obj: AgentProfile) -> str:
        return obj.profile_image

    get_agent_profile_picture_url.short_description = 'agent_profile_picture'
    get_agent_first_name.short_description = 'agent_first_name'
    get_agent_last_name.short_description = 'agent_last_name'
