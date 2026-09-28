# MAUZO PRO - Professional Sales & Inventory System

A Django-based POS and inventory management system for small and medium businesses.

## Included modules
- Secure login and role-based access (Admin, Manager, Seller)
- Dashboard and low-stock monitoring
- Products, categories and suppliers
- Stock-in/purchases and controlled stock adjustments
- POS sales with discount limits
- Tax, amount paid and change calculation
- Sales history and printable invoices
- Sale cancellation with stock restoration and reason
- Product returns with stock restoration
- Date-filtered revenue, discount, cost and gross-profit reports
- Sensitive-action audit log
- Business settings and discount limits
- SQLite database backup download
- Django Admin

## Default account
Username: `admin`
Password: `admin12345`

Change the password before using the system in a real business.

## Windows setup
1. Extract the ZIP.
2. Double-click `setup.bat`.
3. Double-click `run.bat`.
4. Open http://127.0.0.1:8000/

## Roles
- Admin: full control.
- Manager: inventory, suppliers, purchases, reports, sensitive actions and configured discount limit.
- Seller: sales and customers; discount is limited by Business Settings.

## Important controls
Discounts are recorded with the sale and audit log. Cancellation, returns, purchases and stock adjustments are also logged with the responsible user and reason.

## Backup
Managers/Admins can download the SQLite database from Settings > Download Database Backup. Keep backups in a safe location.

## Production note
Before public deployment, change SECRET_KEY, set DEBUG=False, configure ALLOWED_HOSTS, use HTTPS, and move to PostgreSQL/MySQL if the business grows beyond a small local installation.

## Simplified POS checkout

The New Sale screen is optimized for fast cashier use:
- Walk-in Customer is selected automatically.
- Cash is the default payment method.
- Seller enters product quantities and an optional discount percentage.
- Subtotal, discount, tax, final total, and change are calculated live.
- Amount Paid defaults to the exact total; the cashier only changes it when the customer pays a different amount.
- Stock, sale, discount, payment, and audit records are saved automatically when the sale is completed.

## POS Discount Entry
The POS now uses a direct **Discount Amount (TZS)** instead of asking the seller to calculate a percentage. The seller enters the money amount to discount; the system calculates the equivalent percentage for reporting, validates the seller's configured discount limit, recalculates tax and total, and records the discount in the audit log.
