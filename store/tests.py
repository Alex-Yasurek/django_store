from decimal import Decimal
from itertools import product
from rest_framework.test import APITestCase

from store.models import Product


class ProductApiTestCase(APITestCase):
    def test_create_product(self):
        initial_product_count = Product.objects.count()
        product_attrs = {
            'name': 'New product',
            'description': 'New awesome product',
            'price': '123.45',
        }
        response = self.client.post('/api/v1/products/new', product_attrs)
        if response.status_code != 200:
            print(response.data)
        self.assertEqual(
            Product.objects.count(),
            initial_product_count + 1,
        )
        for attr, expected_value in product_attrs.items():
            self.assertEqual(response.data[attr], expected_value)
        self.assertEqual(response.data['is_on_sale'], False)
        self.assertEqual(response.data['current_price'],
                         Decimal(product_attrs['price']))

    # def test_delete_product(self):
    #     initial_product_count = Product.objects.count()
    #     product_id = Product.objects.first().id
    #     self.client.delete('/api/v1/products/{}'.format(product_id))
    #     self.assertEqual(
    #         Product.objects.count(),
    #         initial_product_count - 1,
    #     )
    #     self.assertRaises(Product.DoesNotExist,
    #                       Product.objects.get, id=product_id,)

    # def test_list_products(self):
    #     product_count = Product.objects.count()
    #     response = self.client.get('api/v1/products/')
    #     self.assertIsNone(response.data['next'])
    #     self.assertIsNone(response.data['previous'])
    #     self.assertEqual(response.data['count'], product_count)
    #     self.assertEqual(len(response.data['results']), product_count)

    # def test_updating_product(self):
    #     product_id = Product.objects.first().id
    #     self.client.patch('/api/v1/products/{}'.format(product_id), {
    #         'name': 'New product name',
    #         'description': 'new description',
    #         'price': Decimal('45.67'),
    #     }, format='json')
    #     updated = Product.objects.get(id=product_id)
    #     self.assertEqual(updated.name, 'New product name')
