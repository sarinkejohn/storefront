import django_filters
from ..models import Product
from django_filters import rest_framework as filters


class ProductsFilters(filters.FilterSet):
    keyword = filters.CharFilter(field_name="name", lookup_expr="icontains")
    min_price = filters.NumberFilter(
        field_name="price" or 0, lookup_expr="gte")
    max_price = filters.NumberFilter(
        field_name="price" or 1000000, lookup_expr="lte")

    class Meta:
        model = Product
        fields = ('max_price', 'min_price', 'keyword', 'category', 'brand')
