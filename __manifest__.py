{
'name':'Pharmacy_Management_System',
'author':'keroles software',
'website':'www.t-keroles.com',
'summary':'odoo 18 Developer',

'depends': ['base', 'product', 'stock', 'sale_management'],
'data':[
    "security/pharmacy_security.xml", 
    "security/ir.model.access.csv",
    "security/pharmacy_rules.xml", 
    "data/sequence.xml", 
    "views/base_menu.xml",
    "views/medicine_view.xml",
    "views/Prescription_view.xml",
    'wizards/prescription_excel_wizard_view.xml',
    "reports/Prescription_report.xml"


],
  'application': True,
  'assets': {
    'web.assets_backend': [
        'Al_Shifa_pharmacy/static/src/css/style.css',
    ],
},
}