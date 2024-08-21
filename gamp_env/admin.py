from django.contrib import admin
from .models import GampArbitraryUser, GampArbitraryClaim, GampArbitraryDevice, GampArbitraryPolicy

admin.site.register(GampArbitraryUser)
admin.site.register(GampArbitraryPolicy)
admin.site.register(GampArbitraryDevice)
admin.site.register(GampArbitraryClaim)


# Register your models here.
