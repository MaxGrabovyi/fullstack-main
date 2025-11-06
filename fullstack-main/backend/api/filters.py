import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    price_min = django_filters.NumberFilter(field_name="new_price", lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name="new_price", lookup_expr='lte')
    category = django_filters.CharFilter(field_name="category__name", lookup_expr='iexact')

    class Meta:
        model = Product
        fields = ['price_min', 'price_max', 'category']
