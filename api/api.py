from ninja import NinjaAPI
from ninja import ModelSchema,Schema
from pydantic import EmailStr
from api.models import *
from typing import Optional
from datetime import date
import re
from ninja import UploadedFile,File,Form
from SmartAppBackend.utils import *
import json
from django.contrib.auth import get_user_model
User = get_user_model()
router=NinjaAPI()




@router.get('/hello/')
def get_hello_message(request):
    return{
        "message":"Hello message"
    }

class CustomerSignupSchema(Schema):
    username: str
    email: str
    phone_number: str
    password: str
    
    full_name: str
    date_of_birth: date
    address: str
    city: str
    state: str
    pincode: str

@router.post('/customers/signup/')
def customer_register(request,data:CustomerSignupSchema):
    username=data.username
    existence_of_user=User.objects.filter(username=username).exists()
    if existence_of_user:
        return {"status":False,"message":"User is already Exists"}
    
    email_regex = r"[^@]+@[^@]+\.[^@]+"
    if not re.match(email_regex, data.email):
        return {"status": False, "message": "Invalid email format"}

    if len(data.phone_number)!=10 and not data.phone_number.isdigit():
        return {"status":False,"message":"Phone Number should contain only digits and  should not exceed 10 characters"}
    
    phone_no_existence=User.objects.filter(phone_number=data.phone_number).exists()
    if phone_no_existence:
        return {"status":False,'message':"Phone number is already exists"}
    user_object = User.objects.create_user(
        username=data.username,
        email=data.email,
        password=data.password,
        phone_number=data.phone_number,
        role='customer'
    )
    
    customer_object=CustomerProfile.objects.create(
        user=user_object,
        full_name=data.full_name,
        date_of_birth=data.date_of_birth,
        address=data.address,
        city=data.city,
        state=data.state,
        pincode=data.pincode,
    )
    token=JWTHandler.generate_token(user_object)
    return {
        "status":True,
        "message":"Customer Registered Successfully",
        "token":token,
        "customer":{
            "id":customer_object.id,
            "customer full name":customer_object.full_name,
        }
    }




class UploadKYCSchema(Schema):
    customer_id: int
    document_type: str
    document_number: str

@router.post('/upload/kyc/', auth=JWTAuth())
def upload_kyc(
    request,
    document_type: str = Form(...),
    document_number: str = Form(...),
    document_file: UploadedFile = File(...)
):
    user = request.auth
    print("user:--",user)
    customer = CustomerProfile.objects.filter(user=user).first()
    if not customer:
        return {"status": False, "message": "Customer doesn't exist"}

    if document_type not in ['aadhaar', 'pan', 'passport']:
        return {"status": False, "message": "Invalid document type"}

    kyc_record = KYCDocument.objects.create(
        customer=customer,
        document_type=document_type,
        document_number=document_number,
        document_file=document_file
    )

    AuditLog.objects.create(
        actor=user,
        action="Upload KYC Document",
        details=json.dumps({
            "customer_id": customer.id,
            "kyc_id": kyc_record.id,
            "document_type": document_type
        })
    )

    return {
        "status": True,
        "message": "KYC document uploaded successfully",
    }



def rule_based_kyc_check(document):

    if not document.document_file:
        document.is_verified = False
    elif document.document_type.lower() not in ['aadhaar', 'pan', 'passport']:
        document.is_verified = False
    else:
        document.is_verified = True

    document.save()
    return document.is_verified

@router.post('/verify/kyc/', auth=JWTAuth())
def verify_customer_kyc(request, customer_id: int):
    try:
        customer = CustomerProfile.objects.get(id=customer_id)
    except CustomerProfile.DoesNotExist:
        return {"status": False, "message": "Customer doesn't exist"}

    kyc_documents = KYCDocument.objects.filter(customer=customer)
    if not kyc_documents.exists():
        return {"status": False, "message": "No KYC document uploaded to customer"}

    all_verified = True
    for doc in kyc_documents:
        if not doc.is_verified:
            if not rule_based_kyc_check(doc):
                all_verified = False

    if all_verified:
        customer.is_verified = True
        customer.save()
        return {"status": True, "message": "Customer profile validated and verified"}

    return {"status": False, "message": "KYC validation failed for some documents"}





