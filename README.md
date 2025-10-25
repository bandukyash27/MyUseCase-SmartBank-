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



## APIs

### 1. Upload KYC Document

- **Endpoint:** `/upload/kyc/`  
- **Method:** `POST`  
- **Authentication:** JWT  
- **Description:**  
  Allows authenticated customers to upload KYC documents. Only supports document types: `aadhaar`, `pan`, `passport`.

---

### 2. Verify Customer KYC

- **Endpoint:** `/verify/kyc/`  
- **Method:** `POST`  
- **Authentication:** JWT  
- **Description:**  
  Performs rule-based verification of all uploaded KYC documents for a given customer. Marks the customer profile as verified only if all documents pass validation.

---

## Verification Rules

1. Document file must exist.  
2. Document type must be one of `aadhaar`, `pan`, or `passport`.  
3. Customer is marked verified only if all uploaded documents are valid.

---

## Notes

- JWT authentication is required for both APIs.  
- Audit logs track all KYC upload actions.  
- Designed to integrate with a frontend or third-party system for managing KYC workflows.

---

## Author

**Yaswanth Banduku**




