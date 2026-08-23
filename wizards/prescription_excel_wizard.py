import io
import base64
import xlsxwriter

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class PrescriptionExcelWizard(models.TransientModel):
    _name = 'prescription.excel.wizard'
    _description = 'Export Prescription Excel Report Wizard'

    from_date = fields.Date(string="From Date", required=True)
    to_date = fields.Date(string="To Date", required=True)
    state = fields.Selection([
        ('all', 'All Prescriptions'),
        ('confirmed', 'Confirmed Only'),
        ('delivered', 'Delivered Only'),
    ], string="Filter Status", default='delivered', required=True)

    # الحقلين اللي كانوا ناقصين ومسببين الإيرور:
    excel_file = fields.Binary(string="Excel File", readonly=True)
    file_name = fields.Char(string="File Name", readonly=True)

    @api.constrains('from_date', 'to_date')
    def _check_dates(self):
        for record in self:
            if record.from_date and record.to_date and record.from_date > record.to_date:
                raise ValidationError("From Date cannot be after To Date!")

    def action_export_excel(self):
        self.ensure_one()
        
        domain = [
            ('date', '>=', self.from_date),
            ('date', '<=', self.to_date)
        ]
        if self.state != 'all':
            domain.append(('status', '=', self.state))  # تصحيح اسم الحقل إلى status

        prescriptions = self.env['prescription'].search(domain)

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Prescriptions')

        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D3D3D3',
            'border': 1,
            'align': 'center'
        })
        cell_format = workbook.add_format({'border': 1, 'align': 'left'})

        headers = ['Reference', 'Patient Name', 'Doctor', 'Date', 'Pharmacist', 'Status', 'Total Amount']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
            worksheet.set_column(col, col, 18)

        row = 1
        for pres in prescriptions:
            worksheet.write(row, 0, pres.name or '', cell_format)
            worksheet.write(row, 1, pres.patient_id.name if pres.patient_id else '', cell_format)
            worksheet.write(row, 2, pres.doctor_id.name if pres.doctor_id else '', cell_format)
            worksheet.write(row, 3, str(pres.date) if pres.date else '', cell_format)
            worksheet.write(row, 4, pres.create_uid.name or '', cell_format)
            worksheet.write(row, 5, pres.status or '', cell_format)  # تصحيح اسم الحقل إلى status
            worksheet.write(row, 6, pres.total_amount or 0.0, cell_format)
            row += 1

        workbook.close()
        output.seek(0)

        file_data = base64.b64encode(output.read())
        output.close()

        self.write({
            'excel_file': file_data,
            'file_name': f"Prescriptions_{self.from_date}_to_{self.to_date}.xlsx"
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'prescription.excel.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }