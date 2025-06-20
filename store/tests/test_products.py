import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from model_bakery import baker
from store.models import Product, Collection, Promotion


@pytest.mark.django_db
class TestProductModel:

    def test_product_creation_success(self):
        collection = baker.make(Collection)
        product = Product.objects.create(
            title='Test Product',
            slug='test-product',
            unit_price=Decimal('9.99'),
            inventory=10,
            collection=collection
        )
        assert product.id is not None
        assert product.title == 'Test Product'

    def test_invalid_unit_price_raises_validation_error(self):
        collection = baker.make(Collection)
        product = Product(
            title='Cheap',
            slug='cheap',
            unit_price=Decimal('0.99'),  # below min
            inventory=10,
            collection=collection
        )

        with pytest.raises(ValidationError):
            product.full_clean()

    def test_invalid_inventory_raises_validation_error(self):
        collection = baker.make(Collection)
        product = Product(
            title='Stockless',
            slug='stockless',
            unit_price=Decimal('10.00'),
            inventory=0,  # below min
            collection=collection
        )

        with pytest.raises(ValidationError):
            product.full_clean()

    def test_product_allows_blank_description(self):
        collection = baker.make(Collection)
        product = Product(
            title='No Description',
            slug='no-desc',
            unit_price=Decimal('15.00'),
            inventory=5,
            collection=collection,
            description=''
        )
        product.full_clean()  # Should pass

    def test_can_assign_promotions(self):
        collection = baker.make(Collection)
        promo1 = baker.make(Promotion)
        promo2 = baker.make(Promotion)

        product = Product.objects.create(
            title='Promo Product',
            slug='promo-product',
            unit_price=Decimal('20.00'),
            inventory=15,
            collection=collection
        )
        product.promotions.set([promo1, promo2])
        assert product.promotions.count() == 2

    def test_str_method_returns_title(self):
        product = baker.make(Product, title='Dope Product')
        assert str(product) == 'Dope Product'

    def test_foreign_key_protects_collection_deletion(self):
        collection = baker.make(Collection)
        product = baker.make(Product, collection=collection)

        with pytest.raises(Exception):  # Could be ProtectedError
            collection.delete()
