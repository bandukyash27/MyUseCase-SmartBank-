from django.test import TestCase
from django.contrib.auth import get_user_model
from ninja.testing import TestClient
from api.api import router  # Your single NinjaAPI instance
from api.models import CustomerProfile

User = get_user_model()
client = TestClient(router)

class CustomerAPITestCase(TestCase):
    def setUp(self):
        # Base user data for signup
        self.user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "phone_number": "9876543210",
            "password": "testpass123",
            "full_name": "Test User",
            "date_of_birth": "2000-01-01",
            "address": "123 Test St",
            "city": "TestCity",
            "state": "TestState",
            "pincode": "123456"
        }

    def test_hello_endpoint(self):
        response = client.get("/hello/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Hello message"})

    def test_customer_signup_success(self):
        response = client.post("/customers/signup/", self.user_data, format="json")
        print("Signup response:", response.json())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["status"])
        self.assertIn("token", response.json())
        self.assertEqual(response.json()["customer"]["full_name"], "Test User")

    def test_customer_signup_duplicate_username(self):
        # First signup
        client.post("/customers/signup/", self.user_data, format="json")
        # Attempt duplicate signup
        response = client.post("/customers/signup/", self.user_data, format="json")
        print("Duplicate signup response:", response.json())
        self.assertEqu
