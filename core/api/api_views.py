from rest_framework.exceptions import ValidationError
from core.models import Item
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView, GenericAPIView
from .serializers import ItemSerializer, ItemStatSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class ItemPagination(LimitOffsetPagination):
    default_limit = 2
    max_limit = 100


class ItemList(ListAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filter_fields = ('title', 'discount_price', 'id')
    search_fields = ('title', 'description', 'id')
    pagination_class = ItemPagination

    def get_queryset(self):
        discount_price = self.request.query_params.get('discount_price', None)
        if discount_price is None:
            return super().get_queryset()
        queryset = Item.objects.all()
        if discount_price.lower():
            return queryset.filter(
                discount_price >= 90,
            )
        return queryset


class ItemCreate(CreateAPIView):
    serializer_class = ItemSerializer

    def create(self, request, *args, **kwargs):
        try:
            price = request.data.get('price')
            if price is not None and float(price) <= 0.0:
                raise ValidationError({'price': 'Must be above 0'})

        except ValueError:
            raise ValidationError({'price': 'A valid number is required'})
        return super().create(request, *args, **kwargs)


class ItemRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    queryset = Item.objects.all()
    lookup_field = 'id'
    serializer_class = ItemSerializer

    def delete(self, request, *args, **kwargs):
        item_id = request.data.get('id')
        response = super().delete(request, *args, **kwargs)
        if response.status_code == 204:
            from django.core.cache import cache
            cache.delete('item_data_{}'.format(item_id))
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        if response.status_code == 200:
            from django.core.cache import cache
            item = response.data
            cache.set('item_data_{}'.format(item['id']), {
                      'title': item['title'],
                      'description': item['description'],
                      'price': item['price'],
                      })
        return response


class ItemStats(GenericAPIView):
    lookup_field = 'id'
    serializer_class = ItemStatSerializer
    queryset = Item.objects.all()

    def get(self, request, format=None, id=None):
        obj = self.get_object()
        serializer = ItemStatSerializer({
            'stats': {
                '2019-01-01': [5, 10, 15],
                '2015-01-06': [6, 2, 44],
                '2013-05-01': [7, 6, 9],
            }
        })
        return Response(serializer.data)
