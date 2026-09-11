from modeltranslation.translator import TranslationOptions, register
from .models import Category, Extra, Flavor, Product


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ("name", "description")


@register(Flavor)
class FlavorTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(Extra)
class ExtraTranslationOptions(TranslationOptions):
    fields = ("name",)
