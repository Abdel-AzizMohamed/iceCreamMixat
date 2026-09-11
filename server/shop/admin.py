from django.contrib import admin
from .models import Category, Extra, Flavor, Product, Order, OrderItem, Language

admin.site.register(Language)
admin.site.register(Category)
admin.site.register(Extra)
admin.site.register(Flavor)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
