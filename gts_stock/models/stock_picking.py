from odoo import api, fields, tools, models, _
from odoo import exceptions
from odoo.exceptions import Warning, UserError, ValidationError
from num2words import num2words
from datetime import datetime,date, timedelta
from dateutil.relativedelta import relativedelta


class StockPicking(models.Model):
    _inherit = "stock.picking"

    x_with_signature = fields.Boolean('With Signature & Stamp', default=True)
    production_ids = fields.Many2many('mrp.production', compute='get_production_ids', store=True)
    cell_serial_list = fields.Char('Cell Serial No')
    warranty_period_count = fields.Integer('Warranty Count', compute="_compute_warranty_period", default=0, copy=False)
    warranty_period_ids = fields.One2many('warranty.period', 'picking_id', string='Warranty')

    @api.depends('warranty_period_ids')
    def _compute_warranty_period(self):
        for rec in self:
            rec.warranty_period_count = 0
            for lines in rec.warranty_period_ids:
                rec.warranty_period_count += 1

    def action_view_warranty_period(self):
        action = self.env.ref('gts_stock.action_view_warranty_period_lot').read()[0]
        action['domain'] = [('picking_id', '=', self.id)]
        action['context'] = {'create': False}
        return action

    @api.onchange('move_line_ids_without_package', 'move_line_ids_without_package.cell_serial_no')
    def onchange_cell_serial_no(self):
        if self.move_line_ids_without_package:
            cell_serial = []
            for lines in self.move_line_ids_without_package:
                if lines.cell_serial_no:
                    cell_serial += [lines.cell_serial_no]
                    list = ', '.join(cell_serial)
                    self.cell_serial_list = list

    @api.depends('move_line_ids_without_package', 'move_line_ids_without_package.product_uom_qty',
                 'move_line_ids_without_package.qty_done')
    def get_production_ids(self):
        for rec in self:
            if rec.move_line_ids_without_package:
                list_ids = []
                for lines in rec.move_line_ids_without_package:
                    if lines.move_id.created_production_id:
                        list_ids.append(lines.move_id.created_production_id)
                rec.production_ids = [(6, 0, [ids.id for ids in list_ids])]


class QRReportPickingCurrent(models.AbstractModel):
    _name = "report.gts_stock.report_delivery_order_qrcode"

    def _get_report_values(self, docids, data=None):
        docs = self.env['stock.picking'].browse(docids)
        if not docs.move_line_ids_without_package:
            raise exceptions.AccessError(_('You can not print QR Report as no quantity is reserved !'))
        if docs.state == 'cancel':
            raise exceptions.AccessError(_('You can not print QR Report for a Cancelled Delivery Order !'))
        for data in docs.move_line_ids_without_package:
            if not data.lot_id:
                raise exceptions.AccessError(_('You can not print QR Code as no Serial Number has been provided!'))
        return {
            'doc_ids': docs.ids,
            'doc_model': 'stock.picking',
            'docs': docs,
        }


class QRReportPickingUpcoming(models.AbstractModel):
    _name = "report.gts_stock.report_delivery_qrcode_upcoming"

    def _get_report_values(self, docids, data=None):
        docs = self.env['stock.picking'].browse(docids)
        if not docs.move_line_ids_without_package:
            raise exceptions.AccessError(_('You can not print QR Report as no quantity is reserved !'))
        if docs.state == 'cancel':
            raise exceptions.AccessError(_('You can not print QR Report for a Cancelled Delivery Order !'))
        for data in docs.move_line_ids_without_package:
            if not data.lot_id:
                raise exceptions.AccessError(_('You can not print QR Code as no Serial Number has been provided!'))
        return {
            'doc_ids': docs.ids,
            'doc_model': 'stock.picking',
            'docs': docs,
        }


class TestReportDO(models.AbstractModel):
    _name = "report.gts_stock.report_delivery_order_test_certificate"

    def _get_report_values(self, docids, data=None):
        docs = self.env['stock.picking'].browse(docids)
        if not docs.move_line_ids_without_package:
            raise exceptions.AccessError(_('You Cannot print Test Certificate as there is no Quantity Produced !'))
        if docs.state == 'cancel':
            raise exceptions.AccessError(_('You can not print a Test Certificate for a cancelled Delivery Order!'))
        if not docs.production_ids:
            raise exceptions.AccessError(_('Test Certificate has not been generated yet!'))
        return {
            'doc_ids': docs.ids,
            'doc_model': 'stock.picking',
            'docs': docs,
        }


class TestReportDOWithouthf(models.AbstractModel):
    _name = "report.gts_stock.report_do_without_hf_test_certificate"

    def _get_report_values(self, docids, data=None):
        docs = self.env['stock.picking'].browse(docids)
        if not docs.move_line_ids_without_package:
            raise exceptions.AccessError(_('You Cannot print Test Certificate as there is no Quantity Produced !'))
        if docs.state == 'cancel':
            raise exceptions.AccessError(_('You can not print a Test Certificate for a cancelled Delivery Order!'))
        if not docs.production_ids:
            raise exceptions.AccessError(_('Test Certificate has not been generated yet!'))
        return {
            'doc_ids': docs.ids,
            'doc_model': 'stock.picking',
            'docs': docs,
        }


# class WarrantyCardPDF(models.AbstractModel):
#     _name = "report.gts_stock.warranty_card_stock_picking"
#
#     def _get_report_values(self, docids, data=None):
#         docs = self.env['stock.picking'].browse(docids)
#         if docs.origin:
#             sale_order = self.env['sale.order'].search([('name', '=', docs.origin)], limit=1)
#             invoice = self.env['account.move'].search([('invoice_origin', '=', docs.origin), ('state', '!=', 'cancel')],
#                                                       limit=1, order='create_date desc')
#             if sale_order and sale_order.x_studio_warranty_period == 'No Warranty':
#                 raise exceptions.AccessError(_("You can't print warranty card as no warranty is set for this order!"))
#             if sale_order and not sale_order.x_studio_warranty_period:
#                 raise exceptions.AccessError(_("You can't print warranty card as no warranty is set for this order!"))
#             if not invoice:
#                 raise exceptions.AccessError(_("You can't print warranty card as invoice has not been created for this order!"))
#             if invoice.state == 'draft':
#                 raise exceptions.AccessError(_("You can't print warranty card as invoice has not been validated yet!"))
#         return {
#             'doc_ids': docs.ids,
#             'doc_model': 'stock.picking',
#             'docs': docs,
#         }


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    cell_serial_no = fields.Char('Cell Serial No.')
