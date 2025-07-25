import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PropertyManagementApp = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [apartments, setApartments] = useState([]);
  const [tenants, setTenants] = useState([]);
  const [rentPayments, setRentPayments] = useState([]);
  const [expenses, setExpenses] = useState([]);
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(false);

  // Form states
  const [apartmentForm, setApartmentForm] = useState({
    unit_number: '',
    address: '',
    bedrooms: '',
    bathrooms: '',
    square_feet: '',
    monthly_rent: '',
    deposit: '',
    description: ''
  });

  const [tenantForm, setTenantForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    apartment_id: '',
    lease_start: '',
    lease_end: '',
    monthly_rent: '',
    deposit_paid: '',
    emergency_contact_name: '',
    emergency_contact_phone: ''
  });

  const [expenseForm, setExpenseForm] = useState({
    apartment_id: '',
    expense_type: 'maintenance',
    amount: '',
    description: '',
    date: '',
    vendor: ''
  });

  // Fetch data functions
  const fetchApartments = async () => {
    try {
      const response = await axios.get(`${API}/apartments`);
      setApartments(response.data);
    } catch (error) {
      console.error('Error fetching apartments:', error);
    }
  };

  const fetchTenants = async () => {
    try {
      const response = await axios.get(`${API}/tenants`);
      setTenants(response.data);
    } catch (error) {
      console.error('Error fetching tenants:', error);
    }
  };

  const fetchRentPayments = async () => {
    try {
      const response = await axios.get(`${API}/rent-payments`);
      setRentPayments(response.data);
    } catch (error) {
      console.error('Error fetching rent payments:', error);
    }
  };

  const fetchExpenses = async () => {
    try {
      const response = await axios.get(`${API}/expenses`);
      setExpenses(response.data);
    } catch (error) {
      console.error('Error fetching expenses:', error);
    }
  };

  const fetchDashboard = async () => {
    try {
      const response = await axios.get(`${API}/dashboard`);
      setDashboardData(response.data);
    } catch (error) {
      console.error('Error fetching dashboard:', error);
    }
  };

  // Submit functions
  const submitApartment = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await axios.post(`${API}/apartments`, {
        ...apartmentForm,
        bedrooms: parseInt(apartmentForm.bedrooms),
        bathrooms: parseFloat(apartmentForm.bathrooms),
        square_feet: apartmentForm.square_feet ? parseInt(apartmentForm.square_feet) : null,
        monthly_rent: parseFloat(apartmentForm.monthly_rent),
        deposit: parseFloat(apartmentForm.deposit)
      });
      setApartmentForm({
        unit_number: '',
        address: '',
        bedrooms: '',
        bathrooms: '',
        square_feet: '',
        monthly_rent: '',
        deposit: '',
        description: ''
      });
      await fetchApartments();
      alert('Apartment added successfully!');
    } catch (error) {
      console.error('Error creating apartment:', error);
      alert('Error adding apartment');
    }
    setLoading(false);
  };

  const submitTenant = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await axios.post(`${API}/tenants`, {
        ...tenantForm,
        monthly_rent: parseFloat(tenantForm.monthly_rent),
        deposit_paid: parseFloat(tenantForm.deposit_paid)
      });
      setTenantForm({
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
        apartment_id: '',
        lease_start: '',
        lease_end: '',
        monthly_rent: '',
        deposit_paid: '',
        emergency_contact_name: '',
        emergency_contact_phone: ''
      });
      await fetchTenants();
      alert('Tenant added successfully!');
    } catch (error) {
      console.error('Error creating tenant:', error);
      alert('Error adding tenant');
    }
    setLoading(false);
  };

  const submitExpense = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await axios.post(`${API}/expenses`, {
        ...expenseForm,
        amount: parseFloat(expenseForm.amount)
      });
      setExpenseForm({
        apartment_id: '',
        expense_type: 'maintenance',
        amount: '',
        description: '',
        date: '',
        vendor: ''
      });
      await fetchExpenses();
      await fetchDashboard(); // Refresh dashboard
      alert('Expense added successfully!');
    } catch (error) {
      console.error('Error creating expense:', error);
      alert('Error adding expense');
    }
    setLoading(false);
  };

  const markRentPaid = async (paymentId, tenantId, apartmentId, amount) => {
    try {
      await axios.put(`${API}/rent-payments/${paymentId}`, {
        tenant_id: tenantId,
        apartment_id: apartmentId,
        amount: amount,
        due_date: new Date().toISOString().split('T')[0],
        paid_date: new Date().toISOString().split('T')[0],
        status: 'paid'
      });
      await fetchRentPayments();
      await fetchDashboard();
      alert('Rent marked as paid!');
    } catch (error) {
      console.error('Error updating rent payment:', error);
      alert('Error updating payment');
    }
  };

  const deleteApartment = async (id) => {
    if (window.confirm('Are you sure you want to delete this apartment?')) {
      try {
        await axios.delete(`${API}/apartments/${id}`);
        await fetchApartments();
        alert('Apartment deleted successfully!');
      } catch (error) {
        console.error('Error deleting apartment:', error);
        alert('Error deleting apartment');
      }
    }
  };

  const deleteTenant = async (id) => {
    if (window.confirm('Are you sure you want to delete this tenant?')) {
      try {
        await axios.delete(`${API}/tenants/${id}`);
        await fetchTenants();
        alert('Tenant deleted successfully!');
      } catch (error) {
        console.error('Error deleting tenant:', error);
        alert('Error deleting tenant');
      }
    }
  };

  const deleteExpense = async (id) => {
    if (window.confirm('Are you sure you want to delete this expense?')) {
      try {
        await axios.delete(`${API}/expenses/${id}`);
        await fetchExpenses();
        await fetchDashboard();
        alert('Expense deleted successfully!');
      } catch (error) {
        console.error('Error deleting expense:', error);
        alert('Error deleting expense');
      }
    }
  };

  useEffect(() => {
    fetchApartments();
    fetchTenants();
    fetchRentPayments();
    fetchExpenses();
    fetchDashboard();
  }, []);

  const renderDashboard = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Property Management Dashboard</h2>
      
      {dashboardData && (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-blue-500 text-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold">Total Apartments</h3>
              <p className="text-3xl font-bold">{dashboardData.total_apartments}</p>
            </div>
            <div className="bg-green-500 text-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold">Total Tenants</h3>
              <p className="text-3xl font-bold">{dashboardData.total_tenants}</p>
            </div>
            <div className="bg-purple-500 text-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold">Monthly Income</h3>
              <p className="text-3xl font-bold">${dashboardData.current_month_report.total_rental_income.toFixed(2)}</p>
            </div>
            <div className="bg-red-500 text-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold">Net Profit</h3>
              <p className="text-3xl font-bold">${dashboardData.current_month_report.net_profit.toFixed(2)}</p>
            </div>
          </div>

          {/* Financial Summary */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-xl font-semibold mb-4">{dashboardData.current_month_report.month} {dashboardData.current_month_report.year} Financial Summary</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <p className="text-gray-600">Total Income</p>
                <p className="text-2xl font-bold text-green-600">${dashboardData.current_month_report.total_rental_income.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-gray-600">Total Expenses</p>
                <p className="text-2xl font-bold text-red-600">${dashboardData.current_month_report.total_expenses.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-gray-600">Occupancy Rate</p>
                <p className="text-2xl font-bold text-blue-600">{dashboardData.current_month_report.occupancy_rate.toFixed(1)}%</p>
              </div>
            </div>
          </div>

          {/* Overdue Payments */}
          {dashboardData.overdue_payments_count > 0 && (
            <div className="bg-red-50 p-6 rounded-lg border border-red-200">
              <h3 className="text-xl font-semibold text-red-800 mb-4">Overdue Payments ({dashboardData.overdue_payments_count})</h3>
              <div className="space-y-2">
                {dashboardData.overdue_payments.map((payment) => (
                  <div key={payment.id} className="flex justify-between items-center bg-white p-3 rounded border">
                    <div>
                      <p className="font-semibold">Apartment: {payment.apartment_id}</p>
                      <p className="text-gray-600">Due: {payment.due_date} - Amount: ${payment.amount}</p>
                    </div>
                    <button
                      onClick={() => markRentPaid(payment.id, payment.tenant_id, payment.apartment_id, payment.amount)}
                      className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
                    >
                      Mark Paid
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recent Expenses */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-xl font-semibold mb-4">Recent Expenses</h3>
            <div className="space-y-2">
              {dashboardData.recent_expenses.map((expense) => (
                <div key={expense.id} className="flex justify-between items-center border-b pb-2">
                  <div>
                    <p className="font-semibold">{expense.description}</p>
                    <p className="text-gray-600">{expense.expense_type} - {expense.date}</p>
                  </div>
                  <p className="text-lg font-bold text-red-600">${expense.amount.toFixed(2)}</p>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );

  const renderApartments = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Apartment Management</h2>
      
      {/* Add Apartment Form */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-xl font-semibold mb-4">Add New Apartment</h3>
        <form onSubmit={submitApartment} className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <input
            type="text"
            placeholder="Unit Number"
            value={apartmentForm.unit_number}
            onChange={(e) => setApartmentForm({...apartmentForm, unit_number: e.target.value})}
            className="p-3 border rounded-lg"
            required
          />
          <input
            type="text"
            placeholder="Address"
            value={apartmentForm.address}
            onChange={(e) => setApartmentForm({...apartmentForm, address: e.target.value})}
            className="p-3 border rounded-lg"
            required
          />
          <input
            type="number"
            placeholder="Bedrooms"
            value={apartmentForm.bedrooms}
            onChange={(e) => setApartmentForm({...apartmentForm, bedrooms: e.target.value})}
            className="p-3 border rounded-lg"
            required
          />
          <input
            type="number"
            step="0.5"
            placeholder="Bathrooms"
            value={apartmentForm.bathrooms}
            onChange={(e) => setApartmentForm({...apartmentForm, bathrooms: e.target.value})}
            className="p-3 border rounded-lg"
            required
          />
          <input
            type="number"
            placeholder="Square Feet"
            value={apartmentForm.square_feet}
            onChange={(e) => setApartmentForm({...apartmentForm, square_feet: e.target.value})}
            className="p-3 border rounded-lg"
          />
          <input
            type="number"
            step="0.01"
            placeholder="Monthly Rent"
            value={apartmentForm.monthly_rent}
            onChange={(e) => setApartmentForm({...apartmentForm, monthly_rent: e.target.value})}
            className="p-3 border rounded-lg"
            required
          />
          <input
            type="number"
            step="0.01"
            placeholder="Security Deposit"
            value={apartmentForm.deposit}
            onChange={(e) => setApartmentForm({...apartmentForm, deposit: e.target.value})}
            className="p-3 border rounded-lg"
            required
          />
          <textarea
            placeholder="Description"
            value={apartmentForm.description}
            onChange={(e) => setApartmentForm({...apartmentForm, description: e.target.value})}
            className="p-3 border rounded-lg md:col-span-2"
            rows="3"
          />
          <button
            type="submit"
            disabled={loading}
            className="md:col-span-2 bg-blue-500 text-white p-3 rounded-lg hover:bg-blue-600 disabled:opacity-50"
          >
            {loading ? 'Adding...' : 'Add Apartment'}
          </button>
        </form>
      </div>

      {/* Apartments List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <h3 className="text-xl font-semibold p-6 border-b">Apartments ({apartments.length})</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left p-4 font-semibold">Unit</th>
                <th className="text-left p-4 font-semibold">Address</th>
                <th className="text-left p-4 font-semibold">Bed/Bath</th>
                <th className="text-left p-4 font-semibold">Rent</th>
                <th className="text-left p-4 font-semibold">Deposit</th>
                <th className="text-left p-4 font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody>
              {apartments.map((apartment) => (
                <tr key={apartment.id} className="border-b hover:bg-gray-50">
                  <td className="p-4 font-semibold">{apartment.unit_number}</td>
                  <td className="p-4">{apartment.address}</td>
                  <td className="p-4">{apartment.bedrooms}BR/{apartment.bathrooms}BA</td>
                  <td className="p-4 font-semibold">${apartment.monthly_rent}</td>
                  <td className="p-4">${apartment.deposit}</td>
                  <td className="p-4">
                    <button
                      onClick={() => deleteApartment(apartment.id)}
                      className="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const renderTenants = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Tenant Management</h2>
      
      {/* Add Tenant Form */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-xl font-semibold mb-4">Add New Tenant</h3>
        <form onSubmit={submitTenant} className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <input
            type="text"
            placeholder="First Name"
            value={tenantForm.first_name}
            onChange={(e) => setTenantForm({...tenantForm, first_name: e.target.value})}
            className="p-3 border rounded-lg"
            required
          />
          <input
            type="text"
            placeholder="Last Name"
            value={tenantForm.last_name}
            onChange={(e) => setTenantForm({...tenantForm, last_name: e.target.value})}
            className="p-3 border rounded-lg"
            required
          />
          <input
            type="email"
            placeholder="Email"
            value={tenantForm.email}
            onChange={(e) => setTenantForm({...tenantForm, email: e.target.value})}
            className="p-3 border rounded-lg"
            required
          />
          <input
            type="tel"
            placeholder="Phone"
            value={tenantForm.phone}
            onChange={(e) => setTenantForm({...tenantForm, phone: e.target.value})}
            className="p-3 border rounded-lg"
            required
          />
          <select
            value={tenantForm.apartment_id}
            onChange={(e) => setTenantForm({...tenantForm, apartment_id: e.target.value})}
            className="p-3 border rounded-lg"
          >
            <option value="">Select Apartment</option>
            {apartments.map((apt) => (
              <option key={apt.id} value={apt.id}>
                {apt.unit_number} - {apt.address}
              </option>
            ))}
          </select>
          <input
            type="date"
            placeholder="Lease Start"
            value={tenantForm.lease_start}
            onChange={(e) => setTenantForm({...tenantForm, lease_start: e.target.value})}
            className="p-3 border rounded-lg"
            required
          />
          <input
            type="date"
            placeholder="Lease End"
            value={tenantForm.lease_end}
            onChange={(e) => setTenantForm({...tenantForm, lease_end: e.target.value})}
            className="p-3 border rounded-lg"
            required
          />
          <input
            type="number"
            step="0.01"
            placeholder="Monthly Rent"
            value={tenantForm.monthly_rent}
            onChange={(e) => setTenantForm({...tenantForm, monthly_rent: e.target.value})}
            className="p-3 border rounded-lg"
            required
          />
          <input
            type="number"
            step="0.01"
            placeholder="Deposit Paid"
            value={tenantForm.deposit_paid}
            onChange={(e) => setTenantForm({...tenantForm, deposit_paid: e.target.value})}
            className="p-3 border rounded-lg"
            required
          />
          <input
            type="text"
            placeholder="Emergency Contact Name"
            value={tenantForm.emergency_contact_name}
            onChange={(e) => setTenantForm({...tenantForm, emergency_contact_name: e.target.value})}
            className="p-3 border rounded-lg"
          />
          <input
            type="tel"
            placeholder="Emergency Contact Phone"
            value={tenantForm.emergency_contact_phone}
            onChange={(e) => setTenantForm({...tenantForm, emergency_contact_phone: e.target.value})}
            className="p-3 border rounded-lg"
          />
          <button
            type="submit"
            disabled={loading}
            className="md:col-span-2 bg-green-500 text-white p-3 rounded-lg hover:bg-green-600 disabled:opacity-50"
          >
            {loading ? 'Adding...' : 'Add Tenant'}
          </button>
        </form>
      </div>

      {/* Tenants List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <h3 className="text-xl font-semibold p-6 border-b">Tenants ({tenants.length})</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left p-4 font-semibold">Name</th>
                <th className="text-left p-4 font-semibold">Contact</th>
                <th className="text-left p-4 font-semibold">Lease</th>
                <th className="text-left p-4 font-semibold">Rent</th>
                <th className="text-left p-4 font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody>
              {tenants.map((tenant) => {
                const apartment = apartments.find(apt => apt.id === tenant.apartment_id);
                return (
                  <tr key={tenant.id} className="border-b hover:bg-gray-50">
                    <td className="p-4">
                      <div>
                        <p className="font-semibold">{tenant.first_name} {tenant.last_name}</p>
                        <p className="text-gray-600 text-sm">{apartment ? apartment.unit_number : 'No apartment'}</p>
                      </div>
                    </td>
                    <td className="p-4">
                      <div>
                        <p>{tenant.email}</p>
                        <p className="text-gray-600 text-sm">{tenant.phone}</p>
                      </div>
                    </td>
                    <td className="p-4">
                      <div>
                        <p>{tenant.lease_start} to</p>
                        <p>{tenant.lease_end}</p>
                      </div>
                    </td>
                    <td className="p-4 font-semibold">${tenant.monthly_rent}</td>
                    <td className="p-4">
                      <button
                        onClick={() => deleteTenant(tenant.id)}
                        className="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const renderExpenses = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Expense Management</h2>
      
      {/* Add Expense Form */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-xl font-semibold mb-4">Add New Expense</h3>
        <form onSubmit={submitExpense} className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <select
            value={expenseForm.apartment_id}
            onChange={(e) => setExpenseForm({...expenseForm, apartment_id: e.target.value})}
            className="p-3 border rounded-lg"
          >
            <option value="">Select Apartment (Optional)</option>
            {apartments.map((apt) => (
              <option key={apt.id} value={apt.id}>
                {apt.unit_number} - {apt.address}
              </option>
            ))}
          </select>
          <select
            value={expenseForm.expense_type}
            onChange={(e) => setExpenseForm({...expenseForm, expense_type: e.target.value})}
            className="p-3 border rounded-lg"
            required
          >
            <option value="maintenance">Maintenance</option>
            <option value="utilities">Utilities</option>
            <option value="insurance">Insurance</option>
            <option value="taxes">Taxes</option>
            <option value="family">Family</option>
            <option value="other">Other</option>
          </select>
          <input
            type="number"
            step="0.01"
            placeholder="Amount"
            value={expenseForm.amount}
            onChange={(e) => setExpenseForm({...expenseForm, amount: e.target.value})}
            className="p-3 border rounded-lg"
            required
          />
          <input
            type="date"
            value={expenseForm.date}
            onChange={(e) => setExpenseForm({...expenseForm, date: e.target.value})}
            className="p-3 border rounded-lg"
            required
          />
          <input
            type="text"
            placeholder="Vendor/Company"
            value={expenseForm.vendor}
            onChange={(e) => setExpenseForm({...expenseForm, vendor: e.target.value})}
            className="p-3 border rounded-lg"
          />
          <textarea
            placeholder="Description"
            value={expenseForm.description}
            onChange={(e) => setExpenseForm({...expenseForm, description: e.target.value})}
            className="p-3 border rounded-lg"
            required
          />
          <button
            type="submit"
            disabled={loading}
            className="md:col-span-2 bg-purple-500 text-white p-3 rounded-lg hover:bg-purple-600 disabled:opacity-50"
          >
            {loading ? 'Adding...' : 'Add Expense'}
          </button>
        </form>
      </div>

      {/* Expenses List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <h3 className="text-xl font-semibold p-6 border-b">Expenses ({expenses.length})</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left p-4 font-semibold">Date</th>
                <th className="text-left p-4 font-semibold">Type</th>
                <th className="text-left p-4 font-semibold">Description</th>
                <th className="text-left p-4 font-semibold">Amount</th>
                <th className="text-left p-4 font-semibold">Apartment</th>
                <th className="text-left p-4 font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody>
              {expenses.map((expense) => {
                const apartment = apartments.find(apt => apt.id === expense.apartment_id);
                return (
                  <tr key={expense.id} className="border-b hover:bg-gray-50">
                    <td className="p-4">{expense.date}</td>
                    <td className="p-4">
                      <span className="bg-gray-200 px-2 py-1 rounded text-sm capitalize">
                        {expense.expense_type}
                      </span>
                    </td>
                    <td className="p-4">
                      <div>
                        <p>{expense.description}</p>
                        {expense.vendor && <p className="text-gray-600 text-sm">{expense.vendor}</p>}
                      </div>
                    </td>
                    <td className="p-4 font-semibold text-red-600">${expense.amount.toFixed(2)}</td>
                    <td className="p-4">{apartment ? apartment.unit_number : 'General'}</td>
                    <td className="p-4">
                      <button
                        onClick={() => deleteExpense(expense.id)}
                        className="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-3xl font-bold text-gray-800">Property Management System</h1>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex space-x-8">
            {[
              { key: 'dashboard', label: 'Dashboard', icon: '📊' },
              { key: 'apartments', label: 'Apartments', icon: '🏢' },
              { key: 'tenants', label: 'Tenants', icon: '👥' },
              { key: 'expenses', label: 'Expenses', icon: '💰' }
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`py-4 px-2 border-b-2 font-medium text-sm ${
                  activeTab === tab.key
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                {tab.icon} {tab.label}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {activeTab === 'dashboard' && renderDashboard()}
        {activeTab === 'apartments' && renderApartments()}
        {activeTab === 'tenants' && renderTenants()}
        {activeTab === 'expenses' && renderExpenses()}
      </main>
    </div>
  );
};

export default PropertyManagementApp;