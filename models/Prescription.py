from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Prescription(models.Model):
    _name = "prescription"  # يفضل حروف صغيرة
    _description = 'Pharmacy Prescription'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Reference', default="New", readonly=1, tracking=True, required=True)
    
    patient_id = fields.Many2one(
        'res.partner', 
        string='Patient', 
        required=True,
        tracking=True
    )
    
    doctor_id = fields.Many2one(
        'res.partner', 
        string='Doctor'
    )

    date = fields.Date(
        string='Date', 
        default=fields.Date.context_today, 
        required=True
    )

    status = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('delivered', 'Delivered'),
    ], default='draft', string='Status', required=True, tracking=True)

    line_ids = fields.One2many(
        'prescription.lines', 
        'prescription_id', 
        string='Prescription Lines')
    # العلاقه بين الجدول ده والجدول الوسيط العلاقه ان الرشته الواحد بتشيل كذا سطر فا هي مجموع من عندي و واحد من هند الدو

    total_amount = fields.Float(
        string='Grand Total', 
        compute='_compute_total_amount', 
        store=True, 
        tracking=True
    )
    # أضف هذا الحقل داخل الكلاس
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', readonly=True)

    @api.depends('line_ids.price_subtotal')
    def _compute_total_amount(self):
        for rec in self:
            total = 0.0            
            for line in rec.line_ids:  
                total += line.price_subtotal 
            rec.total_amount = total 


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # تم تعديل ref إلى name ليتطابق مع الحقل
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('kero_Prescription') or 'New'
        return super(Prescription, self).create(vals_list)

    def action_draft(self):
        for rec in self:
            rec.status = 'draft'
            
    def action_confirmed(self):
        for rec in self:
            rec.status = 'confirmed'

    def action_delivered(self):
        for rec in self:
            # التأكد من عدم وجود أمر بيع سابق واستخدام line_ids
            if not rec.sale_order_id and rec.line_ids:
                order_lines = []
                
                for line in rec.line_ids:
                    order_lines.append((0, 0, {
                        'product_id': line.product_id.id,
                        'product_uom_qty': line.quantity,
                        'price_unit': line.price_unit,
                    }))

                # إنشاء أمر البيع
                sale_order = self.env['sale.order'].create({
                    'partner_id': rec.patient_id.id,
                    'order_line': order_lines,
                    'origin': rec.name,
                })

                # تأكيد أمر البيع لخصم المخزون
                sale_order.action_confirm()
                
                # حفظ رقم أمر البيع
                rec.sale_order_id = sale_order.id

            rec.status = 'delivered'


class PrescriptionLines(models.Model):
    _name = 'prescription.lines'
    _description = 'Pharmacy Prescription Line'

    # تم تعديل اسم الموديل ليتطابق مع كلاس الروشتة فوق
    prescription_id = fields.Many2one(
        'prescription', 
        string='Prescription', 
        ondelete='cascade', 
        required=True
    )

    product_id = fields.Many2one(
        'product.product', 
        string='Medicine', 
        required=True
    )

    batch_number = fields.Char(string='Batch Number')
    quantity = fields.Float(string='Quantity', default=1.0, required=True)
    price_unit = fields.Float(string='Price Unit', required=True)

    price_subtotal = fields.Float(
        string='Subtotal', 
        compute='_compute_subtotal', 
        store=True
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.price_unit = self.product_id.lst_price

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit