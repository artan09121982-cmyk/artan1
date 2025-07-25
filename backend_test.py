#!/usr/bin/env python3
"""
Property Management API Testing Suite
Tests all backend endpoints for the property management application
"""

import requests
import json
import sys
from datetime import datetime, date
from typing import Dict, Any, Optional

class PropertyManagementAPITester:
    def __init__(self, base_url: str = "https://18ddf004-c98d-4856-a941-a3c58613f316.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.created_resources = {
            'apartments': [],
            'tenants': [],
            'expenses': [],
            'rent_payments': []
        }

    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED {details}")
        else:
            print(f"❌ {name} - FAILED {details}")

    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> tuple[bool, Dict[str, Any], int]:
        """Make HTTP request and return success, response data, status code"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                return False, {}, 0

            try:
                response_data = response.json() if response.content else {}
            except json.JSONDecodeError:
                response_data = {"raw_response": response.text}

            return response.status_code < 400, response_data, response.status_code

        except requests.exceptions.RequestException as e:
            return False, {"error": str(e)}, 0

    def test_apartment_crud(self):
        """Test apartment CRUD operations"""
        print("\n🏢 Testing Apartment CRUD Operations...")
        
        # Test GET empty apartments
        success, data, status = self.make_request('GET', 'apartments')
        self.log_test("GET /api/apartments (empty)", success, f"Status: {status}")
        
        # Test CREATE apartment
        apartment_data = {
            "unit_number": "101",
            "address": "123 Test Street, Test City",
            "bedrooms": 2,
            "bathrooms": 1.5,
            "square_feet": 1200,
            "monthly_rent": 1500.00,
            "deposit": 1500.00,
            "description": "Test apartment for API testing"
        }
        
        success, data, status = self.make_request('POST', 'apartments', apartment_data)
        if success and 'id' in data:
            apartment_id = data['id']
            self.created_resources['apartments'].append(apartment_id)
            self.log_test("POST /api/apartments", True, f"Created apartment ID: {apartment_id}")
            
            # Test GET specific apartment
            success, data, status = self.make_request('GET', f'apartments/{apartment_id}')
            self.log_test(f"GET /api/apartments/{apartment_id}", success, f"Status: {status}")
            
            # Test UPDATE apartment
            update_data = apartment_data.copy()
            update_data['monthly_rent'] = 1600.00
            success, data, status = self.make_request('PUT', f'apartments/{apartment_id}', update_data)
            self.log_test(f"PUT /api/apartments/{apartment_id}", success, f"Status: {status}")
            
        else:
            self.log_test("POST /api/apartments", False, f"Status: {status}, Response: {data}")
        
        # Test GET all apartments
        success, data, status = self.make_request('GET', 'apartments')
        apartment_count = len(data) if isinstance(data, list) else 0
        self.log_test("GET /api/apartments (with data)", success, f"Found {apartment_count} apartments")

    def test_tenant_crud(self):
        """Test tenant CRUD operations"""
        print("\n👥 Testing Tenant CRUD Operations...")
        
        # Test GET empty tenants
        success, data, status = self.make_request('GET', 'tenants')
        self.log_test("GET /api/tenants (empty)", success, f"Status: {status}")
        
        # Test CREATE tenant
        tenant_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@test.com",
            "phone": "555-0123",
            "apartment_id": self.created_resources['apartments'][0] if self.created_resources['apartments'] else None,
            "lease_start": "2024-01-01",
            "lease_end": "2024-12-31",
            "monthly_rent": 1500.00,
            "deposit_paid": 1500.00,
            "emergency_contact_name": "Jane Doe",
            "emergency_contact_phone": "555-0124"
        }
        
        success, data, status = self.make_request('POST', 'tenants', tenant_data)
        if success and 'id' in data:
            tenant_id = data['id']
            self.created_resources['tenants'].append(tenant_id)
            self.log_test("POST /api/tenants", True, f"Created tenant ID: {tenant_id}")
            
            # Test GET specific tenant
            success, data, status = self.make_request('GET', f'tenants/{tenant_id}')
            self.log_test(f"GET /api/tenants/{tenant_id}", success, f"Status: {status}")
            
            # Test UPDATE tenant
            update_data = tenant_data.copy()
            update_data['phone'] = "555-9999"
            success, data, status = self.make_request('PUT', f'tenants/{tenant_id}', update_data)
            self.log_test(f"PUT /api/tenants/{tenant_id}", success, f"Status: {status}")
            
        else:
            self.log_test("POST /api/tenants", False, f"Status: {status}, Response: {data}")
        
        # Test GET all tenants
        success, data, status = self.make_request('GET', 'tenants')
        tenant_count = len(data) if isinstance(data, list) else 0
        self.log_test("GET /api/tenants (with data)", success, f"Found {tenant_count} tenants")

    def test_expense_crud(self):
        """Test expense CRUD operations"""
        print("\n💰 Testing Expense CRUD Operations...")
        
        # Test GET empty expenses
        success, data, status = self.make_request('GET', 'expenses')
        self.log_test("GET /api/expenses (empty)", success, f"Status: {status}")
        
        # Test CREATE expense
        expense_data = {
            "apartment_id": self.created_resources['apartments'][0] if self.created_resources['apartments'] else None,
            "expense_type": "maintenance",
            "amount": 250.00,
            "description": "Plumbing repair in unit 101",
            "date": "2024-02-15",
            "vendor": "ABC Plumbing Co"
        }
        
        success, data, status = self.make_request('POST', 'expenses', expense_data)
        if success and 'id' in data:
            expense_id = data['id']
            self.created_resources['expenses'].append(expense_id)
            self.log_test("POST /api/expenses", True, f"Created expense ID: {expense_id}")
            
            # Test UPDATE expense
            update_data = expense_data.copy()
            update_data['amount'] = 300.00
            success, data, status = self.make_request('PUT', f'expenses/{expense_id}', update_data)
            self.log_test(f"PUT /api/expenses/{expense_id}", success, f"Status: {status}")
            
        else:
            self.log_test("POST /api/expenses", False, f"Status: {status}, Response: {data}")
        
        # Test GET all expenses
        success, data, status = self.make_request('GET', 'expenses')
        expense_count = len(data) if isinstance(data, list) else 0
        self.log_test("GET /api/expenses (with data)", success, f"Found {expense_count} expenses")

    def test_rent_payment_crud(self):
        """Test rent payment CRUD operations"""
        print("\n🏦 Testing Rent Payment CRUD Operations...")
        
        # Test GET empty rent payments
        success, data, status = self.make_request('GET', 'rent-payments')
        self.log_test("GET /api/rent-payments (empty)", success, f"Status: {status}")
        
        # Test CREATE rent payment
        if self.created_resources['tenants'] and self.created_resources['apartments']:
            payment_data = {
                "tenant_id": self.created_resources['tenants'][0],
                "apartment_id": self.created_resources['apartments'][0],
                "amount": 1500.00,
                "due_date": "2024-02-01",
                "paid_date": "2024-02-01",
                "status": "paid",
                "payment_method": "bank_transfer",
                "notes": "February rent payment"
            }
            
            success, data, status = self.make_request('POST', 'rent-payments', payment_data)
            if success and 'id' in data:
                payment_id = data['id']
                self.created_resources['rent_payments'].append(payment_id)
                self.log_test("POST /api/rent-payments", True, f"Created payment ID: {payment_id}")
                
                # Test UPDATE rent payment
                update_data = payment_data.copy()
                update_data['notes'] = "Updated payment notes"
                success, data, status = self.make_request('PUT', f'rent-payments/{payment_id}', update_data)
                self.log_test(f"PUT /api/rent-payments/{payment_id}", success, f"Status: {status}")
                
            else:
                self.log_test("POST /api/rent-payments", False, f"Status: {status}, Response: {data}")
        else:
            self.log_test("POST /api/rent-payments", False, "No tenants or apartments available for testing")
        
        # Test GET all rent payments
        success, data, status = self.make_request('GET', 'rent-payments')
        payment_count = len(data) if isinstance(data, list) else 0
        self.log_test("GET /api/rent-payments (with data)", success, f"Found {payment_count} payments")

    def test_financial_reports(self):
        """Test financial reporting endpoints"""
        print("\n📊 Testing Financial Reports...")
        
        # Test monthly report
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        success, data, status = self.make_request('GET', f'reports/monthly/{current_year}/{current_month}')
        self.log_test(f"GET /api/reports/monthly/{current_year}/{current_month}", success, f"Status: {status}")
        
        if success and isinstance(data, dict):
            expected_fields = ['total_rental_income', 'total_expenses', 'net_profit', 'occupancy_rate', 'month', 'year']
            has_all_fields = all(field in data for field in expected_fields)
            self.log_test("Monthly report structure", has_all_fields, f"Fields present: {list(data.keys())}")
        
        # Test yearly report
        success, data, status = self.make_request('GET', f'reports/yearly/{current_year}')
        self.log_test(f"GET /api/reports/yearly/{current_year}", success, f"Status: {status}")
        
        if success and isinstance(data, dict):
            expected_fields = ['year', 'total_rental_income', 'total_expenses', 'net_profit', 'average_occupancy_rate', 'monthly_breakdown']
            has_all_fields = all(field in data for field in expected_fields)
            self.log_test("Yearly report structure", has_all_fields, f"Fields present: {list(data.keys())}")

    def test_dashboard(self):
        """Test dashboard endpoint"""
        print("\n📈 Testing Dashboard...")
        
        success, data, status = self.make_request('GET', 'dashboard')
        self.log_test("GET /api/dashboard", success, f"Status: {status}")
        
        if success and isinstance(data, dict):
            expected_fields = ['current_month_report', 'total_apartments', 'total_tenants', 'overdue_payments_count', 'overdue_payments', 'recent_expenses']
            has_all_fields = all(field in data for field in expected_fields)
            self.log_test("Dashboard structure", has_all_fields, f"Fields present: {list(data.keys())}")
            
            # Check if data makes sense
            if 'total_apartments' in data and 'total_tenants' in data:
                apartments_count = data['total_apartments']
                tenants_count = data['total_tenants']
                self.log_test("Dashboard data consistency", True, f"Apartments: {apartments_count}, Tenants: {tenants_count}")

    def test_cleanup(self):
        """Clean up created test resources"""
        print("\n🧹 Cleaning up test resources...")
        
        # Delete expenses
        for expense_id in self.created_resources['expenses']:
            success, _, status = self.make_request('DELETE', f'expenses/{expense_id}')
            self.log_test(f"DELETE expense {expense_id}", success, f"Status: {status}")
        
        # Delete tenants
        for tenant_id in self.created_resources['tenants']:
            success, _, status = self.make_request('DELETE', f'tenants/{tenant_id}')
            self.log_test(f"DELETE tenant {tenant_id}", success, f"Status: {status}")
        
        # Delete apartments
        for apartment_id in self.created_resources['apartments']:
            success, _, status = self.make_request('DELETE', f'apartments/{apartment_id}')
            self.log_test(f"DELETE apartment {apartment_id}", success, f"Status: {status}")

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Property Management API Tests")
        print(f"🌐 Testing against: {self.base_url}")
        print("=" * 60)
        
        try:
            # Test basic connectivity
            success, _, status = self.make_request('GET', 'apartments')
            if not success:
                print(f"❌ Cannot connect to API at {self.api_url}")
                return False
            
            # Run all test suites
            self.test_apartment_crud()
            self.test_tenant_crud()
            self.test_expense_crud()
            self.test_rent_payment_crud()
            self.test_financial_reports()
            self.test_dashboard()
            
            # Cleanup
            self.test_cleanup()
            
            # Print summary
            print("\n" + "=" * 60)
            print(f"📊 TEST SUMMARY")
            print(f"Tests Run: {self.tests_run}")
            print(f"Tests Passed: {self.tests_passed}")
            print(f"Tests Failed: {self.tests_run - self.tests_passed}")
            print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
            
            return self.tests_passed == self.tests_run
            
        except Exception as e:
            print(f"❌ Test suite failed with error: {str(e)}")
            return False

def main():
    """Main test runner"""
    tester = PropertyManagementAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())