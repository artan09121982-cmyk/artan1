from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, date
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums
class RentStatus(str, Enum):
    PAID = "paid"
    UNPAID = "unpaid"
    OVERDUE = "overdue"
    PARTIAL = "partial"

class ExpenseType(str, Enum):
    MAINTENANCE = "maintenance"
    UTILITIES = "utilities"
    INSURANCE = "insurance"
    TAXES = "taxes"
    FAMILY = "family"
    OTHER = "other"

# Models
class Apartment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    unit_number: str
    address: str
    bedrooms: int
    bathrooms: float
    square_feet: Optional[int] = None
    monthly_rent: float
    deposit: float
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ApartmentCreate(BaseModel):
    unit_number: str
    address: str
    bedrooms: int
    bathrooms: float
    square_feet: Optional[int] = None
    monthly_rent: float
    deposit: float
    description: Optional[str] = None

class Tenant(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    first_name: str
    last_name: str
    email: str
    phone: str
    apartment_id: Optional[str] = None
    lease_start: str  # Changed from date to str for MongoDB compatibility
    lease_end: str    # Changed from date to str for MongoDB compatibility
    monthly_rent: float
    deposit_paid: float
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TenantCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    apartment_id: Optional[str] = None
    lease_start: date
    lease_end: date
    monthly_rent: float
    deposit_paid: float
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None

class RentPayment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    apartment_id: str
    amount: float
    due_date: date
    paid_date: Optional[date] = None
    status: RentStatus
    payment_method: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RentPaymentCreate(BaseModel):
    tenant_id: str
    apartment_id: str
    amount: float
    due_date: date
    paid_date: Optional[date] = None
    status: RentStatus = RentStatus.UNPAID
    payment_method: Optional[str] = None
    notes: Optional[str] = None

class Expense(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    apartment_id: Optional[str] = None
    expense_type: ExpenseType
    amount: float
    description: str
    date: date
    vendor: Optional[str] = None
    receipt_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ExpenseCreate(BaseModel):
    apartment_id: Optional[str] = None
    expense_type: ExpenseType
    amount: float
    description: str
    date: date
    vendor: Optional[str] = None
    receipt_url: Optional[str] = None

class FinancialSummary(BaseModel):
    total_rental_income: float
    total_expenses: float
    net_profit: float
    occupancy_rate: float
    month: str
    year: int

# Apartment CRUD
@api_router.post("/apartments", response_model=Apartment)
async def create_apartment(apartment: ApartmentCreate):
    apartment_dict = apartment.dict()
    apartment_obj = Apartment(**apartment_dict)
    await db.apartments.insert_one(apartment_obj.dict())
    return apartment_obj

@api_router.get("/apartments", response_model=List[Apartment])
async def get_apartments():
    apartments = await db.apartments.find().to_list(1000)
    return [Apartment(**apt) for apt in apartments]

@api_router.get("/apartments/{apartment_id}", response_model=Apartment)
async def get_apartment(apartment_id: str):
    apartment = await db.apartments.find_one({"id": apartment_id})
    if not apartment:
        raise HTTPException(status_code=404, detail="Apartment not found")
    return Apartment(**apartment)

@api_router.put("/apartments/{apartment_id}", response_model=Apartment)
async def update_apartment(apartment_id: str, apartment_update: ApartmentCreate):
    existing = await db.apartments.find_one({"id": apartment_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Apartment not found")
    
    update_dict = apartment_update.dict()
    await db.apartments.update_one({"id": apartment_id}, {"$set": update_dict})
    
    updated_apartment = await db.apartments.find_one({"id": apartment_id})
    return Apartment(**updated_apartment)

@api_router.delete("/apartments/{apartment_id}")
async def delete_apartment(apartment_id: str):
    result = await db.apartments.delete_one({"id": apartment_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Apartment not found")
    return {"message": "Apartment deleted successfully"}

# Tenant CRUD
@api_router.post("/tenants", response_model=Tenant)
async def create_tenant(tenant: TenantCreate):
    tenant_dict = tenant.dict()
    tenant_obj = Tenant(**tenant_dict)
    await db.tenants.insert_one(tenant_obj.dict())
    return tenant_obj

@api_router.get("/tenants", response_model=List[Tenant])
async def get_tenants():
    tenants = await db.tenants.find().to_list(1000)
    return [Tenant(**tenant) for tenant in tenants]

@api_router.get("/tenants/{tenant_id}", response_model=Tenant)
async def get_tenant(tenant_id: str):
    tenant = await db.tenants.find_one({"id": tenant_id})
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return Tenant(**tenant)

@api_router.put("/tenants/{tenant_id}", response_model=Tenant)
async def update_tenant(tenant_id: str, tenant_update: TenantCreate):
    existing = await db.tenants.find_one({"id": tenant_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    update_dict = tenant_update.dict()
    await db.tenants.update_one({"id": tenant_id}, {"$set": update_dict})
    
    updated_tenant = await db.tenants.find_one({"id": tenant_id})
    return Tenant(**updated_tenant)

@api_router.delete("/tenants/{tenant_id}")
async def delete_tenant(tenant_id: str):
    result = await db.tenants.delete_one({"id": tenant_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return {"message": "Tenant deleted successfully"}

# Rent Payment CRUD
@api_router.post("/rent-payments", response_model=RentPayment)
async def create_rent_payment(payment: RentPaymentCreate):
    payment_dict = payment.dict()
    payment_obj = RentPayment(**payment_dict)
    await db.rent_payments.insert_one(payment_obj.dict())
    return payment_obj

@api_router.get("/rent-payments", response_model=List[RentPayment])
async def get_rent_payments():
    payments = await db.rent_payments.find().to_list(1000)
    return [RentPayment(**payment) for payment in payments]

@api_router.put("/rent-payments/{payment_id}", response_model=RentPayment)
async def update_rent_payment(payment_id: str, payment_update: RentPaymentCreate):
    existing = await db.rent_payments.find_one({"id": payment_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    update_dict = payment_update.dict()
    await db.rent_payments.update_one({"id": payment_id}, {"$set": update_dict})
    
    updated_payment = await db.rent_payments.find_one({"id": payment_id})
    return RentPayment(**updated_payment)

# Expense CRUD
@api_router.post("/expenses", response_model=Expense)
async def create_expense(expense: ExpenseCreate):
    expense_dict = expense.dict()
    expense_obj = Expense(**expense_dict)
    await db.expenses.insert_one(expense_obj.dict())
    return expense_obj

@api_router.get("/expenses", response_model=List[Expense])
async def get_expenses():
    expenses = await db.expenses.find().to_list(1000)
    return [Expense(**expense) for expense in expenses]

@api_router.put("/expenses/{expense_id}", response_model=Expense)
async def update_expense(expense_id: str, expense_update: ExpenseCreate):
    existing = await db.expenses.find_one({"id": expense_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    update_dict = expense_update.dict()
    await db.expenses.update_one({"id": expense_id}, {"$set": update_dict})
    
    updated_expense = await db.expenses.find_one({"id": expense_id})
    return Expense(**updated_expense)

@api_router.delete("/expenses/{expense_id}")
async def delete_expense(expense_id: str):
    result = await db.expenses.delete_one({"id": expense_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"message": "Expense deleted successfully"}

# Financial Reports
@api_router.get("/reports/monthly/{year}/{month}", response_model=FinancialSummary)
async def get_monthly_report(year: int, month: int):
    # Calculate date range
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)
    
    # Get rent payments for the month
    rent_payments = await db.rent_payments.find({
        "paid_date": {
            "$gte": start_date.date(),
            "$lt": end_date.date()
        },
        "status": "paid"
    }).to_list(1000)
    
    # Get expenses for the month
    expenses = await db.expenses.find({
        "date": {
            "$gte": start_date.date(),
            "$lt": end_date.date()
        }
    }).to_list(1000)
    
    # Calculate totals
    total_rental_income = sum(payment["amount"] for payment in rent_payments)
    total_expenses = sum(expense["amount"] for expense in expenses)
    net_profit = total_rental_income - total_expenses
    
    # Calculate occupancy rate (simplified)
    total_apartments = await db.apartments.count_documents({})
    occupied_apartments = await db.tenants.count_documents({
        "lease_start": {"$lte": end_date.date()},
        "lease_end": {"$gte": start_date.date()}
    })
    
    occupancy_rate = (occupied_apartments / total_apartments * 100) if total_apartments > 0 else 0
    
    return FinancialSummary(
        total_rental_income=total_rental_income,
        total_expenses=total_expenses,
        net_profit=net_profit,
        occupancy_rate=occupancy_rate,
        month=start_date.strftime("%B"),
        year=year
    )

@api_router.get("/reports/yearly/{year}")
async def get_yearly_report(year: int):
    yearly_data = []
    for month in range(1, 13):
        monthly_report = await get_monthly_report(year, month)
        yearly_data.append(monthly_report)
    
    # Calculate yearly totals
    total_yearly_income = sum(report.total_rental_income for report in yearly_data)
    total_yearly_expenses = sum(report.total_expenses for report in yearly_data)
    yearly_net_profit = total_yearly_income - total_yearly_expenses
    avg_occupancy = sum(report.occupancy_rate for report in yearly_data) / 12
    
    return {
        "year": year,
        "total_rental_income": total_yearly_income,
        "total_expenses": total_yearly_expenses,
        "net_profit": yearly_net_profit,
        "average_occupancy_rate": avg_occupancy,
        "monthly_breakdown": yearly_data
    }

@api_router.get("/dashboard")
async def get_dashboard():
    # Get current month/year
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    
    # Get current month report
    current_report = await get_monthly_report(current_year, current_month)
    
    # Get total counts
    total_apartments = await db.apartments.count_documents({})
    total_tenants = await db.tenants.count_documents({})
    
    # Get overdue payments
    today = datetime.now().date()
    overdue_payments = await db.rent_payments.find({
        "due_date": {"$lt": today},
        "status": {"$in": ["unpaid", "partial"]}
    }).to_list(100)
    
    # Get recent expenses
    recent_expenses = await db.expenses.find().sort("date", -1).limit(5).to_list(5)
    
    return {
        "current_month_report": current_report,
        "total_apartments": total_apartments,
        "total_tenants": total_tenants,
        "overdue_payments_count": len(overdue_payments),
        "overdue_payments": [RentPayment(**payment) for payment in overdue_payments],
        "recent_expenses": [Expense(**expense) for expense in recent_expenses]
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()