from django.contrib.auth.models import User
from rest_framework import status
import pytest
from model_bakery import baker

from store.models import Collection, Product

@pytest.fixture
def create_collection(api_client):
    def do_create_collection(collection):
        return api_client.post('/store/collections/', collection)
    return do_create_collection


@pytest.mark.django_db
class TestCreateCollection:
    def test_if_user_is_anonymous_returns_401(self,create_collection):
        response = create_collection({'title': 'a'})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_if_user_is_not_admin_returns_403(self, authenticate, create_collection):
        authenticate()

        response = create_collection({'title': 'a'})

        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_if_sata_is_invalid_returns_400(self, authenticate, create_collection):
        authenticate(is_staff=True)

        response = create_collection({'title': ''})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['title'] is not None
    
    def test_if_sata_is_valid_returns_201(self, authenticate, create_collection):
        authenticate(is_staff=True)

        response = create_collection({'title': 'a'})

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0


@pytest.mark.django_db
class TestRetrieveCollection:
    def test_if_collection_exists_returns_200(self, api_client):
        collection = baker.make(Collection)

        response = api_client.get(f'/store/collections/{collection.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            'id': collection.id,
            'title': collection.title,
            'products_count': 0
        }

@pytest.mark.django_db
class TestDeleteCollection:
    def test_if_user_is_not_staff_returns_403(self, api_client, authenticate):
        authenticate()

        collection = baker.make(Collection)

        response = api_client.delete(f'/store/collections/{collection.id}/')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_is_staff_returns_204(self, authenticate, api_client):
        authenticate(is_staff=True)

        collection = baker.make(Collection)

        response = api_client.delete(f'/store/collections/{collection.id}/')

        assert response.status_code == status.HTTP_204_NO_CONTENT
    
    def test_cannot_delete_collection_with_products(self, authenticate, api_client):
        authenticate(is_staff=True)
        
        collection = baker.make(Collection)
        baker.make(Product, collection=collection)  # assuming Product model exists

        response = api_client.delete(f'/store/collections/{collection.id}/')

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED




@pytest.mark.django_db
class TestUpdateCollection:

    def test_if_user_is_not_staff_returns_403(self, api_client, authenticate):
        authenticate(is_staff=False)
        collection = baker.make(Collection, title="Old Title")

        response = api_client.put(
            f'/store/collections/{collection.id}/',
            {'title': 'New Title'}
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_is_staff_can_update_collection(self, api_client, authenticate):
        authenticate(is_staff=True)
        collection = baker.make(Collection, title="Old Title")

        response = api_client.put(
            f'/store/collections/{collection.id}/',
            {'title': 'Updated Title'}
        )

        assert response.status_code == status.HTTP_200_OK
        collection.refresh_from_db()
        assert collection.title == 'Updated Title'

    def test_if_user_is_staff_can_partially_update_collection(self, api_client, authenticate):
        authenticate(is_staff=True)
        collection = baker.make(Collection, title="Partial Old Title")

        response = api_client.patch(
            f'/store/collections/{collection.id}/',
            {'title': 'Patched Title'}
        )

        assert response.status_code == status.HTTP_200_OK
        collection.refresh_from_db()
        assert collection.title == 'Patched Title'

    def test_if_invalid_data_returns_400(self, api_client, authenticate):
        authenticate(is_staff=True)
        collection = baker.make(Collection, title="Still Valid Title")

        # Missing title (assuming it's required)
        response = api_client.put(
            f'/store/collections/{collection.id}/',
            {'title': ''}  # invalid (empty)
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
class TestListCollections:
    def test_returns_200(self, api_client):
        Collection.objects.all().delete() 
        
        baker.make(Collection, _quantity=3)

        response = api_client.get('/store/collections/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3
