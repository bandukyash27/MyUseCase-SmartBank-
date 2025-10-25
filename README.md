# SmartBank Modular Banking Backend System UseCase-1(Customer SignUp)
---

## Technologies Used

- **Python 3.x**
- **Django**
- **Django-Ninja** (API framework)
- **SQLite 
- **Pydantic** (for request validation in Ninja)
- **JWT Authentication** (custom JWT handler for user authentication)

---

## Models Overview

### 1. **User**
Custom user model extending Django's `AbstractUser` with additional fields:
- `role` (customer, bank admin, auditor)
- `phone_number`
- `is_verified` (set after KYC approval)
- Custom ManyToMany fields for `groups` and `user_permissions` to avoid reverse accessor clash.

### 2. **CustomerProfile**
Stores customer details:
- `full_name`, `date_of_birth`, `address`, `city`, `state`, `pincode`
- Linked to `User` via `OneToOneField`
- `created_at` timestamp

### 3. **KYCDocument**
Stores uploaded KYC documents for customers:
- `document_type` (Aadhaar, PAN, Passport)
- `document_number`
- `document_file`
- `is_verified` (boolean)
- Linked to `CustomerProfile` via `ForeignKey`
- `uploaded_at` timestamp

### 4. **AuditLog**
Tracks all actions by users:
- `actor` (User performing the action)
- `action` (description)
- `timestamp`
- `details` (JSON string for extra info)

---

## API Endpoints

### 1. `GET /hello/`
Simple hello message for testing API connectivity.

### 2. `POST /customers/signup/`
Registers a new customer.

**Request Schema:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "phone_number": "9876543210",
  "password": "securepassword",
  "full_name": "John Doe",
  "date_of_birth": "1990-01-01",
  "address": "123 Main St",
  "city": "CityName",
  "state": "StateName",
  "pincode": "123456"
}




