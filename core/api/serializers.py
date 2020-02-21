from rest_framework import serializers
from core.models import Item, OrderItem


class CartItemSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(min_value=1, max_value=100)

    class Meta:
        model = OrderItem
        fields = ('item', 'quantity')


class ItemSerializer(serializers.ModelSerializer):
    cart_items = serializers.SerializerMethodField()
    price = serializers.DecimalField(
        min_value=1.00, max_value=10000.00, max_digits=None, decimal_places=2,)
    created_date = serializers.DateTimeField(
        input_formats=['%I:%M %p %d %B %Y'], format=None, allow_null=True,
        help_text='Accepted format is "12:01 PM 16 April 2020"',
        style={'input_type': 'text', 'placeholder': '12:01 AM 28 July 2019'},
    )

    image = serializers.ImageField(default=None)

    class Meta:
        model = Item
        fields = ('title', 'price', 'description',
                  'discount_price', 'created_date', 'id', 'cart_items', 'image')

    def get_cart_items(self, instance):
        items = OrderItem.objects.filter(item=instance)
        return CartItemSerializer(items, many=True).data

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     data['discount_price'] = instance.discount_price()
    #     return data


class ItemStatSerializer(serializers.Serializer):
    stats = serializers.DictField(
        child=serializers.ListField(
            child=serializers.IntegerField(),
        )
    )
