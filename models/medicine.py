from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Medicine(models.Model):
    _inherit = ['product.template']

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

    is_low_stock = fields.Boolean(
        string='Is Low Stock',
        compute='_compute_is_low_stock',
        store=True
    )

    active = fields.Boolean(string='Active', default=True)

    @api.depends('qty_available', 'min_stock_qty')
    def _compute_is_low_stock(self):
        for rec in self:
            rec.is_low_stock = rec.qty_available < rec.min_stock_qty

    @api.constrains('min_stock_qty')
    def _check_min_stock_qty_greater_zero(self):
        for rec in self:
            if rec.min_stock_qty < 0:
                raise ValidationError("the Minimum Stock Quantity be a positive number")

    # لما is_medicine=True، نفرض إن المنتج يتتبع باللوت أوتوماتيك
    # عشان أودو يسمح أصلاً بربط stock.lot بيه
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('is_medicine'):
                vals['tracking'] = 'lot'
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('is_medicine'):
            vals['tracking'] = 'lot'
        return super().write(vals)

    # ---------------------------------------------------------
    # استقبال كمية جديدة (لوت جديد) وإضافتها للمخزون الحالي
    # ---------------------------------------------------------
    def action_add_stock_lot(self, lot_name, new_qty, expiration_date=None):
        """
        يستقبل: اسم اللوت، الكمية الجديدة، تاريخ الانتهاء (اختياري)
        - لو اللوت مش موجود لنفس المنتج: يعمله create
        - لو موجود: يحدث تاريخ الانتهاء لو اتبعت، ويضيف عليه الكمية
        - يعمل تحديث فعلي على المخزون عن طريق stock.quant
        """
        self.ensure_one()

        if not self.is_medicine:
            raise ValidationError("This product is not marked as a medicine.")

        if not lot_name:
            raise ValidationError("Lot name is required.")

        if not new_qty or new_qty <= 0:
            raise ValidationError("New purchased quantity must be greater than zero.")

        product = self.product_variant_id
        if not product:
            raise ValidationError("This product has no variant to update stock for.")

        # مكان التخزين الافتراضي للشركة (أول مخزن)
        warehouse = self.env['stock.warehouse'].search(
            [('company_id', '=', self.env.company.id)], limit=1
        )
        if not warehouse:
            raise ValidationError("No warehouse found for this company.")
        location = warehouse.lot_stock_id

        # البحث عن اللوت لنفس المنتج، أو إنشاء واحد جديد
        lot = self.env['stock.lot'].search([
            ('name', '=', lot_name),
            ('product_id', '=', product.id),
            ('company_id', '=', self.env.company.id),
        ], limit=1)

        if not lot:
            lot = self.env['stock.lot'].create({
                'name': lot_name,
                'product_id': product.id,
                'company_id': self.env.company.id,
                'expiration_date': expiration_date,
            })
        elif expiration_date:
            lot.expiration_date = expiration_date

        # البحث عن الكمية الحالية لنفس اللوت في نفس المكان
        quant = self.env['stock.quant'].search([
            ('product_id', '=', product.id),
            ('lot_id', '=', lot.id),
            ('location_id', '=', location.id),
        ], limit=1)

        if quant:
            quant.sudo().inventory_quantity = quant.quantity + new_qty
        else:
            quant = self.env['stock.quant'].sudo().create({
                'product_id': product.id,
                'lot_id': lot.id,
                'location_id': location.id,
                'inventory_quantity': new_qty,
            })

        quant.sudo().action_apply_inventory()

        return {
            'success': True,
            'lot_id': lot.id,
            'lot_name': lot.name,
            'new_total_qty': product.qty_available,
        }


class MedicineLot(models.Model):
    _inherit = ['stock.lot']

    # منقول من product.template لأن expiration_date حقل موجود
    # على stock.lot (بعد تفعيل موديول Expiration Dates) مش على المنتج نفسه
    # (متعلّقة مؤقتاً زي ما طلبت، ممكن ترجعها لما تكون جاهز)
    # @api.constrains('expiration_date')
    # def _check_expiration_date(self):
    #     for rec in self:
    #         if rec.expiration_date and rec.expiration_date < fields.Datetime.now():
    #             raise ValidationError((
    #                 "You cannot set an expiration date in the past. "
    #                 "Please enter a valid date for Lot/Serial: %s"
    #             ) % rec.name)