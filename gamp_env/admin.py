from django.contrib import admin
from .models import GampArbitraryUser, GampArbitraryClaim, GampArbitraryDevice, GampArbitraryPolicy, \
    GampArbitraryProduct, GampPolicyProducts

admin.site.register(GampArbitraryUser)
admin.site.register(GampArbitraryPolicy)
admin.site.register(GampArbitraryDevice)
admin.site.register(GampArbitraryClaim)
admin.site.register(GampArbitraryProduct)
admin.site.register(GampPolicyProducts)
