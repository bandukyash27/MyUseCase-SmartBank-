from django.test import TestCase
from django.contrib.auth import get_user_model
from ninja.testing import TestClient
from api.models import CustomerProfile, KYCDocument, AuditLog
from api.api import router  # import your Ninja router
from datetime import date
from io import BytesIO

User = get_user_model()

client = TestClient(router)

class CustomerAPITestCase(TestCase):
    def setUp(self):
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
        response = client.post("/customers/signup/", self.user_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["status"])
        self.assertIn("token", response.json())
        self.assertEqual(response.json()["customer"]["customer full name"], "Test User")

    def test_customer_signup_duplicate_username(self):
        User.objects.create_user(
            username="testuser",
            email="other@example.com",
            password="pass123",
            phone_number="1234567890",
            role="customer"
        )
        response = client.post("/customers/signup/", self.user_data)
        self.assertFalse(response.json()["status"])
        self.assertEqual(response.json()["message"], "User is already Exists")

    def test_customer_signup_invalid_email(self):
        self.user_data["email"] = "invalidemail"
        response = client.post("/customers/signup/", self.user_data)
        self.assertFalse(response.json()["status"])
        self.assertEqual(response.json()["message"], "Invalid email format")

    def test_customer_signup_invalid_phone(self):
        self.user_data["phone_number"] = "12345abcde"
        response = client.post("/customers/signup/", self.user_data)
        self.assertFalse(response.json()["status"])

class KYCUploadTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="kycuser",
            email="kycuser@example.com",
            password="pass123",
            phone_number="9876543210",
            role="customer"
        )
        self.customer = CustomerProfile.objects.create(
            user=self.user,
            full_name="KYC User",
            date_of_birth=date(2000, 1, 1),
            address="123 Test St",
            city="City",
            state="State",
            pincode="123456"
        )
        self.token = "dummy-token"  # Normally you generate JWT
        self.client = TestClient(router)

    def test_upload_kyc_success(self):
        file_content = BytesIO(b"dummy data")
        file_content.name = "test_aadhaar.pdf"

        response = self.client.post(
            "/upload/kyc/",
            data={
                "document_type": "aadhaar",
                "document_number": "123456789012",
                "document_file": file_content
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertTrue(response.json()["status"])
        self.assertEqual(response.json()["message"], "KYC document uploaded successfully")
        self.assertEqual(KYCDocument.objects.count(), 1)
        self.assertEqual(AuditLog.objects.count(), 1)

    def test_upload_invalid_document_type(self):
        file_content = BytesIO(b"dummy data")
        file_content.name = "test.docx"
        response = self.client.post(
            "/upload/kyc/",
            data={
                "document_type": "driver_license",
                "document_number": "123456",
                "document_file": file_content
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertFalse(response.json()["status"])
        self.assertEqual(response.json()["message"], "Invalid document type")

class KYCVerificationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="verifyuser",
            email="verifyuser@example.com",
            password="pass123",
            phone_number="9876543210",
            role="customer"
        )
        self.customer = CustomerProfile.objects.create(
            user=self.user,
            full_name="Verify User",
            date_of_birth=date(2000, 1, 1),
            address="123 Test St",
            city="City",
            state="State",
            pincode="123456"
        )
        self.kyc_doc = KYCDocument.objects.create(
            customer=self.customer,
            document_type="aadhaar",
            document_number="123456789012"
        )
        self.client = TestClient(router)
        self.token = "dummy-token"

    def test_verify_customer_kyc_success(self):
        response = self.client.post(
            f"/verify/kyc/?customer_id={self.customer.id}",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertFalse(response.json()["status"])  # Because is_verified=False initially
        self.kyc_doc.refresh_from_db()
        self.assertTrue(self.kyc_doc.is_verified)

    def test_verify_customer_no_docs(self):
        KYCDocument.objects.all().delete()
        response = self.client.post(
            f"/verify/kyc/?customer_id={self.customer.id}",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertFalse(response.json()["status"])
        self.assertEqual(response.json()["message"], "No KYC document uploaded to customer")
