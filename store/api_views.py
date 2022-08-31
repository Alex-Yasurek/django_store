from rest_framework.generics import ListAPIView, CreateAPIView, GenericAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from store.serializers import ProductSerializer, ProductStatSerializer
from store.models import Product

from django.utils import timezone
from django.core.cache import cache


class ProductsPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100


class ProductList(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # add pagination to api: ?limit=1&offset=2
    pagination_class = ProductsPagination
    # enable filtering for api
    filter_backends = (DjangoFilterBackend, SearchFilter)
    # only filter on id field: ?id=1
    filter_fields = ('id',)
    # only enable text seraching on these fields: ?search=word
    search_fields = ('name', 'description')

    def get_queryset(self):
        # return only on_sale items if on_sale is pass in as a query param
        # ?on_sale=true
        on_sale = self.request.query_params.get('on_sale', None)
        if on_sale is None:
            return super().get_queryset()
        queryset = Product.objects.all()
        if on_sale.lower() == 'true':
            now = timezone.now()
            return queryset.filter(
                sale_start__lte=now,
                sale_end__gte=now,
            )
        return queryset


class ProductCreate(CreateAPIView):
    serializer_class = ProductSerializer

    def create(self, request, *args, **kwargs):
        try:
            # stops people from creating product that are free
            price = request.data.get('price')
            if price is not None and float(price) <= 0.0:
                raise ValidationError({'price': 'Must be above $0.0'})
        except ValueError:
            raise ValidationError({'price': 'A valid number is required'})
        return super().create(request, *args, **kwargs)


class ProductRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    # one url can be used to delete and update: api/v1/products/<int:id>/
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    lookup_field = 'id'

    # above two params is all that would be needed but function below
    # let us add extra functionality to delete call
    def delete(self, request, *args, **kwargs):
        # remove item from cache when deleted
        product_id = request.data.get('id')
        response = super().delete(request, *args, **kwargs)
        if response.status_code == 204:
            cache.delete('product_data_{}'.format(product_id))
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        if response.status_code == 200:
            product = response.data
            cache.set('product_data_{}'.format(product['id']), {
                'name': product['name'],
                'description': product['description'],
                'price': product['price']
            })
        return response


class ProductStats(GenericAPIView):
    lookup_field = 'id'
    serializer_class = ProductStatSerializer
    queryset = Product.objects.all()

    def get(self, request, format=None, id=None):
        obj = self.get_objects()
        serializer = ProductStatSerializer({
            'stat': {
                '2019-01-01': [5, 10, 15],
                '2019-01-02': [20, 1, 1]
            }
        })
        return Response(serializer.data)
