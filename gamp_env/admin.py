from django.contrib import admin
from .models import GampArbitraryUser, GampArbitraryClaim, GampArbitraryDevice, GampArbitraryPolicy, \
    GampArbitraryProduct, Product, ProductType, UserPolicy

admin.site.register(GampArbitraryUser)
admin.site.register(GampArbitraryPolicy)
admin.site.register(GampArbitraryDevice)
admin.site.register(GampArbitraryClaim)
admin.site.register(GampArbitraryProduct)
admin.site.register(UserPolicy)
admin.site.register(Product)
admin.site.register(ProductType)

