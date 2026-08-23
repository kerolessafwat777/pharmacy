from odoo  import models,fields,api
from odoo.exceptions import ValidationError

class medicine(models.Model):
    _inherit=['product.template']

    is_medicine = fields.Boolean(
            string="Is Medicine?", 
            help="Check if this product is a pharmaceutical medicine.",
        default=True

        )

  
    requires_prescription = fields.Boolean(
        string="Requires Prescription", 
        help="Check if this medicine requires a doctor's prescription."
    )

   
    min_stock_qty = fields.Float(
        string="Minimum Stock Quantity", 
        default=0.0
    )
    # في ملف البايثون models/medicine.py (أو الموديل الممتد لـ product.template)

    is_low_stock = fields.Boolean(
        string='Is Low Stock', 
        compute='_compute_is_low_stock', 
        store=True 
    )

    @api.depends('qty_available', 'min_stock_qty')
    def _compute_is_low_stock(self):
        for rec in self:
            rec.is_low_stock = rec.qty_available < rec.min_stock_qty
    @api.constrains('min_stock_qty')
    def _check_min_stock_qty_greater_zero(self):
        for rec in self:
            if rec.min_stock_qty<0:
                raise ValidationError("the Minimum Stock Quantity be a positive number")


    @api.constrains('expiration_date')
    def _check_expiration_date(self):
        for rec in self:
            if rec.expiration_date and rec.expiration_date < fields.Datetime.now():
                raise ValidationError((
                    "You cannot set an expiration date in the past. "
                    "Please enter a valid date for Lot/Serial: %s"
                ) % rec.name)
            