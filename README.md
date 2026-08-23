# Al Shifa Pharmacy Management System

An Odoo 18 (Community Edition) module for managing a pharmacy's medicines, prescriptions, and related sales operations.

## Overview

Al Shifa Pharmacy is a custom Odoo module that extends the standard Product, Stock, and Sales apps to handle pharmacy-specific workflows. It allows a pharmacy to:

- Mark products as medicines and track prescription requirements and minimum stock levels.
- Record patient prescriptions with line items, and convert confirmed prescriptions into sale orders that automatically deduct stock.
- Export prescription data to Excel for reporting.
- Print prescriptions as PDF reports.
- Control access with role-based security (Cashier, Pharmacist, Manager).

It is intended for small to medium pharmacies that need lightweight prescription and medicine tracking on top of Odoo's existing inventory and sales functionality.

## Features

**Medicine Management**
- Flag any product as a medicine (`is_medicine`).
- Mark whether a medicine requires a prescription (`requires_prescription`).
- Define a minimum stock quantity per product and automatically compute a low-stock flag.
- Validation to prevent negative minimum stock quantities and expiration dates set in the past.

**Prescription Management**
- Create prescriptions linked to a patient and (optionally) a doctor, both `res.partner` records.
- Add multiple prescription lines, each with a medicine, batch number, quantity, and unit price.
- Automatic subtotal and grand total computation.
- Prescription status workflow: Draft → Confirmed → Delivered.
- On delivery, automatically creates and confirms a linked Sale Order to deduct stock.
- Auto-generated sequential prescription reference numbers.
- Chatter/activity tracking (via `mail.thread` and `mail.activity.mixin`).

**Reporting**
- QWeb PDF report for individual prescriptions.
- Excel export wizard to export prescriptions filtered by date range and status (All / Confirmed / Delivered).

**Security**
- Three access levels: Cashier (read-only), Pharmacist (read/write/create), and Manager (full access, including delete).
- Record rule restricting Pharmacists to prescriptions they created; Managers can see all prescriptions.

## Technologies

- Odoo 18 (Community Edition)
- Python
- XML (views, reports, security)
- QWeb (PDF reports)
- PostgreSQL (Odoo's default database)
- `xlsxwriter` (Python library used for Excel export)

## Project Structure

```text
Al_Shifa_pharmacy/
├── models/
│   ├── medicine.py                  # Extends product.template with pharmacy fields
│   ├── Prescription.py              # Prescription and prescription line models
│   └── __init__.py
├── wizards/
│   ├── prescription_excel_wizard.py # Excel export wizard
│   ├── prescription_excel_wizard_view.xml
│   └── __init__.py
├── views/
│   ├── base_menu.xml                # Root application menu
│   ├── medicine_view.xml            # Product/medicine related views
│   └── Prescription_view.xml        # Prescription views (form, list, actions)
├── reports/
│   └── Prescription_report.xml      # QWeb PDF report for prescriptions
├── security/
│   ├── pharmacy_security.xml        # User groups (Cashier, Pharmacist, Manager)
│   ├── ir.model.access.csv          # Model-level access rights
│   └── pharmacy_rules.xml           # Record rules
├── data/
│   └── sequence.xml                 # Sequence for prescription references
├── static/src/css/style.css         # Backend styling asset
├── __init__.py
└── __manifest__.py
```

## Installation

**Requirements**
- A running Odoo 18 Community Edition instance.
- Python dependency: `xlsxwriter` (required for the Excel export wizard).

**Steps**

1. Clone or copy this module into your Odoo custom addons directory:
   ```bash
   git clone <repository-url> Al_Shifa_pharmacy
   ```
2. Place the `Al_Shifa_pharmacy` folder inside your Odoo addons path (the directory referenced by `addons_path` in your `odoo.conf`).
3. Install the required Python dependency:
   ```bash
   pip install xlsxwriter
   ```
4. Restart the Odoo server.
5. In Odoo, enable Developer Mode, go to **Apps**, and click **Update Apps List**.
6. Search for **Pharmacy_Management_System** and click **Install**.

## Configuration

After installation:

- Go to **Settings → Users & Companies → Groups** (or the Pharmacy module category) and assign users to one of: **Cashier**, **Pharmacist**, or **Manager**.
- Mark relevant products as medicines from the Product form (`is_medicine`, `requires_prescription`, `min_stock_qty`).
- Ensure Sales (`sale_management`) and Inventory (`stock`) apps are properly configured (warehouses, units of measure) since prescription delivery generates real sale orders.

## Usage

1. Create or edit a product and mark it as a medicine, setting whether it requires a prescription and its minimum stock quantity.
2. Open the **Al Shifa Pharmacy** menu and create a new **Prescription**, selecting a patient and optionally a doctor.
3. Add one or more prescription lines with medicine, batch number, and quantity.
4. Confirm the prescription (Draft → Confirmed).
5. Mark it as **Delivered** — this automatically creates and confirms a Sale Order, deducting the medicines from stock.
6. Print the prescription as a PDF report, or use the **Export to Excel** wizard to download prescriptions for a given date range and status.

## Models

| Model                       | Technical Name             | Purpose                                             |
|------------------------------|-----------------------------|------------------------------------------------------|
| Product Template (extended)  | `product.template`          | Adds medicine-specific fields to products            |
| Prescription                 | `prescription`               | Stores prescription header data                      |
| Prescription Line             | `prescription.lines`         | Stores individual medicine lines of a prescription    |
| Prescription Excel Wizard     | `prescription.excel.wizard`  | Transient model used to export prescriptions to Excel |

## Custom Fields

| Field                  | Model                | Type     | Description                                             |
|-------------------------|-----------------------|----------|-----------------------------------------------------------|
| `is_medicine`            | `product.template`    | Boolean  | Marks a product as a pharmaceutical medicine               |
| `requires_prescription`  | `product.template`    | Boolean  | Marks whether the medicine requires a doctor's prescription |
| `min_stock_qty`          | `product.template`    | Float    | Minimum stock quantity threshold                            |
| `is_low_stock`           | `product.template`    | Boolean (computed) | True when available quantity is below `min_stock_qty` |
| `name`                   | `prescription`        | Char     | Auto-generated prescription reference                       |
| `patient_id`             | `prescription`        | Many2one (`res.partner`) | The patient the prescription is for              |
| `doctor_id`               | `prescription`        | Many2one (`res.partner`) | The prescribing doctor                            |
| `status`                  | `prescription`        | Selection | Workflow state: Draft, Confirmed, Delivered                 |
| `total_amount`            | `prescription`        | Float (computed) | Sum of all prescription line subtotals               |
| `sale_order_id`           | `prescription`        | Many2one (`sale.order`) | Sale order generated on delivery                  |
| `product_id`              | `prescription.lines`  | Many2one (`product.product`) | The prescribed medicine                     |
| `batch_number`            | `prescription.lines`  | Char     | Batch/lot number of the dispensed medicine                  |
| `quantity`                 | `prescription.lines`  | Float    | Quantity of medicine prescribed                              |
| `price_unit`               | `prescription.lines`  | Float    | Unit price, auto-filled from the product's sales price       |
| `price_subtotal`           | `prescription.lines`  | Float (computed) | Line subtotal (quantity × price_unit)               |

## Security

- **User Groups** (`security/pharmacy_security.xml`): Cashier, Pharmacist (implies Cashier), and Manager (implies Pharmacist), grouped under a "Pharmacy Management" category.
- **Access Rights** (`security/ir.model.access.csv`): Cashiers have read-only access to medicines and prescriptions; Pharmacists have read/write/create access; Managers have full access including deletion. The Excel export wizard is restricted to Managers.
- **Record Rules** (`security/pharmacy_rules.xml`): Pharmacists can only read/write prescriptions they personally created; Managers can view and manage all prescriptions.

## Dependencies

Declared in `__manifest__.py`:

- `base` – core Odoo framework.
- `product` – underlying product/template model extended for medicines.
- `stock` – inventory management, used for stock quantities and low-stock computation.
- `sale_management` – used to generate sale orders when a prescription is delivered.

## Business Workflow

```text
Product Setup (mark as medicine)
        ↓
Prescription Creation (Draft)
        ↓
Prescription Confirmation
        ↓
Prescription Delivery
        ↓
Sale Order Created & Confirmed
        ↓
Stock Deducted
```

## Screenshots

### Prescription Form
![Prescription Form](docs/screenshots/prescription-form.png)

### Excel Export Wizard
![Excel Export Wizard](docs/screenshots/excel-export-wizard.png)

## Development

- **Odoo Version:** 18 Community Edition.
- **Module structure** follows the standard Odoo layout (`models`, `views`, `wizards`, `reports`, `security`, `data`, `static`).
- When adding new fields or models, remember to update `security/ir.model.access.csv` and, if needed, `security/pharmacy_rules.xml`.
- The Excel wizard relies on the `xlsxwriter` Python package — ensure it is installed in the Odoo Python environment.

## Testing

Automated tests are not currently included in this module.

## Troubleshooting

- **Module not visible in Apps list:** Make sure Developer Mode is enabled and click **Update Apps List** before searching for the module.
- **Excel export fails:** Confirm that the `xlsxwriter` Python package is installed in the same environment running the Odoo server.
- **Sale order not created on delivery:** This only happens if the prescription has at least one line and does not already have a linked sale order; verify prescription lines exist before marking it as Delivered.

## Contributing

Contributions are welcome. Please open an issue to discuss any significant change before submitting a pull request, and keep new features consistent with the existing module structure and Odoo 18 conventions.

## License

> No license has been specified yet.

