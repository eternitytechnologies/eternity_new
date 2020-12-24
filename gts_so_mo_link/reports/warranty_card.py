from odoo import api, models
import datetime

class WarrantyCard(models.AbstractModel):
    """ Model to contain the information related to printing the information about
    the COA report"""

    _name = "report.gts_so_mo_link.warranty_view_pdf"

    @api.model
    def _get_report_values(self, docids, data=None):
        """Get the report values.
                        :param : model
                        :param : docids
                        :param : data
                        :return : data
                        :return : Lot/Serial Number records"""
        mrp = self.env['mrp.production'].browse(docids)
        serial_numbers = []
        # lot_serial_no = self.env['stock.production.lot'].search([('product_id','=',mrp.product_id.id),('product_qty','>',0)])
        inv_ref = self.env['account.move'].search([('invoice_origin','=',mrp.origin)],limit=1).name
        so = self.env['sale.order'].search([('name','=',mrp.origin)],limit=1)
        # today = datetime.datetime.strftime(datetime.datetime.today(), "%m/%d/%Y")
        days = 0
        if so.x_studio_warranty_period == '1 Years As Per Terms & Conditions':
            days = 365
        if so.x_studio_warranty_period == '2 Years As Per Terms & Conditions':
            days = 365 * 2
        if so.x_studio_warranty_period == '3 Years As Per Terms & Conditions':
           days = 365 * 3

        today = datetime.datetime.strftime(so.commitment_date, "%d/%m/%Y")
        expiry = datetime.datetime.strftime(so.commitment_date + datetime.timedelta(days=days), "%d/%m/%Y")
        warranty = today + " To " + expiry
        for lot in mrp.finished_move_line_ids:
            serial_numbers.append(lot.lot_id.name)

        return {
            'data': data,
            'docs': mrp,
            'serial_nos':serial_numbers,
            'inv_ref':inv_ref,
            'warranty':warranty
        }