Al-Shifa Pharmacy Management System

A custom Odoo 18 Community Edition module for managing pharmacy operations, including medicine inventory, doctor prescriptions, and prescription-to-sale workflows.

Overview

Al-Shifa Pharmacy Management System (declared in the manifest as Pharmacy_Management_System) is an Odoo 18 application module that extends Odoo's Product, Stock, and Sales apps to support pharmacy-specific operations.

The module solves the problem of tracking medicines as a distinct product category (with prescription requirements and minimum stock thresholds) and formalizing the prescription lifecycle — from a doctor's prescription, through pharmacist confirmation, to delivery and automatic conversion into a Sales Order that deducts stock.

It is designed for pharmacy staff operating with three levels of responsibility — Cashier, Pharmacist, and Manager — each with different levels of access to medicine and prescription records.

Features
Medicine Management
Extends product.template with pharmacy-specific fields: whether a product is a medicine, whether it requires a prescription, and a minimum stock quantity.
Automatic low-stock flag computed from available quantity vs. the configured minimum.
Validation to prevent a negative minimum stock quantity.
Validation to prevent setting an expiration date in the past.
Prescription Management
Dedicated prescription model with patient, doctor, date, and status (Draft → Confirmed → Delivered) tracked via mail.thread / mail.activity.mixin (chatter and activity tracking).
Prescription lines (prescription.lines) capturing medicine, batch number, quantity, and unit price, with an automatically computed subtotal.
Automatic sequence-based reference numbering for new prescriptions.
Auto-fill of the unit price from the product's sales price when a medicine is selected on a line.
Automatically computed grand total from all prescription lines.
Sales Integration
On delivery, a prescription automatically generates and confirms a sale.order (one order line per prescription line), linking the created sale order back to the prescription and triggering stock deduction through the standard Odoo sales/stock flow.
Reporting
A QWeb PDF report ("Prescription Report") printable directly from the Prescription form, showing patient/doctor details, prescribed medicines, quantities, prices, subtotals, grand total, and a pharmacist signature block.
Excel Export Wizard
A transient wizard (prescription.excel.wizard) to export prescriptions within a date range to an .xlsx file using xlsxwriter, with an optional filter by status (All / Confirmed / Delivered). The generated file is offered as a downloadable binary attachment inside the wizard.
Security
Three-tier group hierarchy (Cashier → Pharmacist → Manager) with cumulative permissions via implied_ids.
Access Control List (ir.model.access.csv) defining per-group CRUD permissions on medicines, prescriptions, prescription lines, and the export wizard.
Record rules restricting pharmacists to prescriptions they created, while managers can see all records.
Menus
A dedicated top-level "Al Shifa pharmacy" menu with entries for Prescriptions and the Export Monthly Report wizard.

Note: The module also ships a view file (views/medicine_view.xml) that, despite its name, currently implements a Gym Member form/list/action on res.partner (with fields such as is_gym_member, plan_type, start_date, end_date). This does not correspond to any medicine-related feature in the current codebase and appears to be unrelated/leftover content rather than part of the pharmacy functionality described above.

Technologies
Odoo 18 Community Edition
Python 3 (Odoo ORM, api.depends, api.constrains, api.model_create_multi)
XML (views, actions, menus, security, QWeb report template)
PostgreSQL (Odoo's default database backend)
QWeb (PDF report template, web.external_layout)
xlsxwriter (Python library used for Excel export in the wizard)
Project Structure
text
Al_Shifa_pharmacy/
├── models/
│   ├── __init__.py
│   ├── medicine.py                 # product.template extension (medicine fields, validations)
│   └── Prescription.py             # prescription and prescription.lines models
├── wizards/
│   ├── __init__.py
│   └── prescription_excel_wizard.py  # Excel export TransientModel
├── views/
│   ├── base_menu.xml                # Root application menu
│   ├── medicine_view.xml            # res.partner (gym member) view — see note above
│   └── Prescription_view.xml        # Prescription form/list views, action, menu item
├── wizards/
│   └── prescription_excel_wizard_view.xml  # Wizard form view, action, menu item
├── reports/
│   └── Prescription_report.xml      # QWeb PDF report action + template
├── security/
│   ├── pharmacy_security.xml        # Module category and user groups
│   ├── ir.model.access.csv          # Access Control List
│   └── pharmacy_rules.xml           # Record rules
├── static/
│   └── src/css/style.css            # Backend CSS asset
├── __init__.py
└── __manifest__.py
Installation
Requirements
Odoo 18 Community Edition installed and running.
Python 3 with the packages required by your Odoo installation, plus the xlsxwriter package (required by the Excel export wizard).
bash
pip3 install xlsxwriter
Steps
Get the module
Place the module folder (e.g. Al_Shifa_pharmacy) into your Odoo custom addons directory.
Add the addons path
Ensure the parent directory containing the module is listed in your odoo.conf:
ini
   [options]
   addons_path = /path/to/odoo/addons, /path/to/custom/addons
Restart the Odoo service
bash
   sudo systemctl restart odoo

or, if running from source:

bash
   ./odoo-bin -c /etc/odoo/odoo.conf
Update the Apps List
In Odoo, activate developer mode, go to Apps, and click Update Apps List.
Install the module
Search for Pharmacy_Management_System (or the module's technical name, Al_Shifa_pharmacy) in the Apps list and click Install.
Configuration

After installation, an administrator should:

Assign user groups: Under Settings → Users & Companies → Users, assign each pharmacy staff member to one of the Pharmacy Management groups — Cashier, Pharmacist, or Manager — under the "Pharmacy Management" category. Since group permissions are cumulative (each higher group implies the lower one), assigning Manager also grants Pharmacist and Cashier rights.
Mark products as medicines: On the Product form (product.template), the Is Medicine? checkbox defaults to enabled for new products; use Requires Prescription and Minimum Stock Quantity to configure pharmacy-specific behavior per product.
Sequence: The prescription model relies on a sequence (kero_Prescription, defined in data/sequence.xml) for automatic reference numbering — no manual setup is required beyond installation.
Usage
Navigate to Al Shifa pharmacy → Prescriptions.
Create a new prescription, selecting the Patient and, optionally, the Doctor.
On the Medicines tab, add prescription lines by selecting a medicine (its price auto-fills from the product's sales price), a batch number, and a quantity.
Click Confirm to move the prescription from Draft to Confirmed.
Click Deliver to move it to Delivered — this automatically creates and confirms a linked Sale Order, deducting the corresponding stock.
Use the print button on the prescription form to generate the Prescription Report PDF.
Go to Al Shifa pharmacy → Export Monthly Report to export prescriptions within a chosen date range (optionally filtered by status) to an Excel file.
Models
Model	Technical Name	Purpose
Prescription	prescription	Header record for a patient prescription (patient, doctor, date, status, total)
Prescription Line	prescription.lines	Individual medicine line on a prescription (product, batch, quantity, price, subtotal)
Prescription Excel Wizard	prescription.excel.wizard	Transient wizard to export prescriptions to Excel over a date range
Medicine (extension)	product.template (inherited)	Adds pharmacy-specific fields to standard products
Custom Fields
Field	Model	Type	Description
is_medicine	product.template	Boolean	Marks the product as a pharmaceutical medicine (defaults to True)
requires_prescription	product.template	Boolean	Indicates the medicine requires a doctor's prescription
min_stock_qty	product.template	Float	Minimum stock quantity threshold for the product
is_low_stock	product.template	Boolean (computed, stored)	True when available quantity is below min_stock_qty
name	prescription	Char	Auto-generated prescription reference (sequence kero_Prescription)
patient_id	prescription	Many2one (res.partner)	The patient the prescription is issued for
doctor_id	prescription	Many2one (res.partner)	The prescribing doctor
date	prescription	Date	Prescription date
status	prescription	Selection	Draft / Confirmed / Delivered workflow state
line_ids	prescription	One2many (prescription.lines)	Medicine lines belonging to the prescription
total_amount	prescription	Float (computed, stored)	Sum of all line subtotals
sale_order_id	prescription	Many2one (sale.order)	Sale order generated on delivery
product_id	prescription.lines	Many2one (product.product)	Medicine dispensed on the line
batch_number	prescription.lines	Char	Batch/lot number of the dispensed medicine
quantity	prescription.lines	Float	Quantity dispensed
price_unit	prescription.lines	Float	Unit price (auto-filled from the product's sales price)
price_subtotal	prescription.lines	Float (computed, stored)	quantity * price_unit
Security
Module category: Pharmacy Management, defined in security/pharmacy_security.xml.
User groups (cumulative, via implied_ids):
group_pharmacy_cashier — Cashier: read-only access to medicines, prescriptions, and prescription lines.
group_pharmacy_pharmacist — Pharmacist: read, write, and create access on medicines, prescriptions, and prescription lines (implies Cashier).
group_pharmacy_manager — Manager: full CRUD (including delete) on medicines, prescriptions, prescription lines, and the Excel export wizard (implies Pharmacist).
Access Control List (security/ir.model.access.csv): defines the CRUD permissions above per group and model (product.template, prescription, prescription.lines, prescription.excel.wizard).
Record rules (security/pharmacy_rules.xml):
Pharmacists can only read/write/create prescriptions they created themselves (create_uid = user.id); they cannot delete prescriptions.
Managers have unrestricted access to all prescription records.
Dependencies

Declared in __manifest__.py:

Module	Reason
base	Core Odoo framework (users, partners, groups)
product	Extends product.template with medicine fields
stock	Provides inventory quantities (qty_available) and expiration-date tracking used for low-stock and expiry validation
sale_management	Used to automatically generate and confirm a Sale Order when a prescription is delivered
Business Workflow
text
Product Setup (mark as Medicine, set Min Stock Qty)
      ↓
Prescription Created (Draft)
      ↓
Prescription Confirmed
      ↓
Prescription Delivered
      ↓
Sale Order Auto-Created & Confirmed
      ↓
Stock Deducted
      ↓
Prescription Report / Excel Export
Screenshots
Main Dashboard

Show Image

Prescription Form

Show Image

Prescription Report

Show Image

Development
Odoo version: 18 Community Edition (uses Odoo 18 syntax, e.g. <list> views and invisible="condition" attribute expressions).
Python version: Not explicitly pinned in the module; should match the Python version required by your Odoo 18 installation.
Module layout: Standard Odoo addon layout — models/, wizards/, views/, reports/, security/, static/.
Development considerations:
The prescription.excel.wizard requires the xlsxwriter Python package to be available in the Odoo environment.
The QWeb report template (Prescription_report.xml) references line.medicine_id, line.lot_id, and line.expiration_date on prescription lines; the current prescription.lines model instead defines product_id and batch_number. This mismatch should be reviewed before relying on the printed report in production.
views/medicine_view.xml currently contains gym-member-related view definitions unrelated to the medicine features described in this README (see note in the Features section).
Testing

No automated tests are currently included in this module.

Troubleshooting
Module fails to install / update: Verify that xlsxwriter is installed in the Python environment used by the Odoo server, since it is imported directly in wizards/prescription_excel_wizard.py.
Prescription Report shows blank/errored fields: The report template references fields (medicine_id, lot_id, expiration_date) that are not defined on the prescription.lines model in this version of the code; align the template with the actual line fields (product_id, batch_number) if this occurs.
"Expiration date" validation errors on products: medicine.py validates an expiration_date field on product.template; ensure the module providing this field (if any, beyond stock) is installed, or confirm the field is available in your Odoo 18 setup before creating/importing medicines with expiry data.
Users cannot see the Pharmacy menu or records: Confirm the user has been assigned to at least the Cashier group under the "Pharmacy Management" category in Settings → Users.
Contributing

Contributions are welcome. Please fork the repository, create a feature branch, and submit a pull request describing your changes. For significant changes, open an issue first to discuss what you would like to modify.

License

No license has been specified yet.

Author

keroles software
Website: www.t-keroles.com
