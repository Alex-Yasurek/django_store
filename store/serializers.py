from rest_framework import serializers

from store.models import Product, ShoppingCartItem


class CartItemSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(min_value=1, max_value=100)

    class Meta:
        model = ShoppingCartItem
        fields = ('product', 'quantity')


class ProductSerializer(serializers.ModelSerializer):
    # These fields will determine the validation that needs to be done on each before saving
    is_on_sale = serializers.BooleanField(read_only=True)
    current_price = serializers.FloatField(read_only=True)
    # this field needs a min of 2 chars and max of 200 or error is thrown in api
    description = serializers.CharField(max_length=200, min_length=2)

    # price = serializers.FloatField(min_value=1.00, max_value=100000)
    price = serializers.DecimalField(
        min_value=1.00, max_value=100000,
        max_digits=None, decimal_places=2)

    sale_start = serializers.DateTimeField(
        required=False,
        input_formats=['%I:%M %p %d %B %Y'], format=None, allow_null=True,
        help_text='Accepted form is "12:10 PM 16 August 2022"',
        style={'input_type': 'text', 'placeholder': '12:01 AM 28 October 2021'}
    )
    sale_end = serializers.DateTimeField(
        required=False,
        input_formats=['%I:%M %p %d %B %Y'], format=None, allow_null=True,
        help_text='Accepted form is "12:10 PM 16 August 2022"',
        style={'input_type': 'text', 'placeholder': '12:01 AM 28 October 2021'}
    )

    photo = serializers.ImageField(default=None)
    # product model does NOT have a warranty file field, so we set write_only to true
    warranty = serializers.FileField(write_only=True, default=None)

    # this will look for a function that starts with get_ and name of field
    cart_items = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'description',
                  'price', 'sale_start', 'sale_end', 'is_on_sale',
                  'current_price', 'cart_items', 'photo', 'warranty')

    # function serializerMethodField will look for
    def get_cart_items(self, instance):
        #
        items = ShoppingCartItem.objects.filter(product=instance)
        return CartItemSerializer(items, many=True).data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['is_on_sale'] = instance.is_on_sale()
        data['current_price'] = instance.current_price()
        return data

    def update(self, instance, validated_data):
        """Overwrite update method to work with warranty file"""
        if validated_data.get('warranty', None):
            instance.description += '\n\nWarranty Information:\n'
            instance.description += b'; '.join(
                validated_data['warranty'].readlines()
            ).decode()
        return super().update(instance, validated_data)

    def create(self, validated_data):
        """Remove warranty when created product since
        its not a field in the model"""
        validated_data.pop('warranty')
        return Product.objects.create(**validated_data)

class ProductStatSerializer(serializers.Serializer):
    # serializer will be a dict that contains a list of ints
    stats = serializers.DictField(
        child=serializers.ListField(
            child=serializers.IntegerField(),
        )
    )
