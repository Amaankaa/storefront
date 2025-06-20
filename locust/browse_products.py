from locust import HttpUser, task, between
from random import randint

class WebsiteUser(HttpUser):
    #Viewing products
    #Viewing product
    #Add product to cart
    wait_time = between(1, 5)

    @task(2)
    def view_products(self):
        collection_id = randint(3, 6)
        self.client.get(
            f'/store/products/?collection_id={collection_id}', name='/store/products')
    
    @task(4)
    def view_product(self):
        product_id = randint(1, 1000)
        self.client.get(f'/store/products/{product_id}/', 
                        name='/store/products/:id')
    
    @task(1)
    def add_to_cart(self): 
        if not self.cart_id:
            return  # skip if no valid cart
        product_id = randint(1, 10)
        self.client.post(
            f'/store/carts/{self.cart_id}/items/',
            name='/store/carts/items',
            json={'product_id': product_id, 'quantity': 1}
        )

    
    @task
    def say_hello(self):
        self.client.get('/playground/hello/')

    def on_start(self):
        response = self.client.post('/store/carts/')
        if response.status_code == 201:
            self.cart_id = response.json()['id'] 
        else:
            self.cart_id = None