from odoo import api, fields, models, _
from odoo import exceptions
from odoo.exceptions import Warning, UserError, ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"


    def button_confirm(self):
        rec = super(PurchaseOrder, self).button_confirm()
        if not self.partner_id.vat and self.partner_id.company_type == 'company':
            raise UserError(_('Please enter GSTIN Number for the Vendor.'))
        elif self.partner_id.company_type == 'person' and self.partner_id.parent_id and not self.partner_id.parent_id.vat:
            raise UserError(_('Please enter GSTIN Number for the Vendor.'))
        return rec

    x_dead_date = fields.Date('RFQ Dead Line')
    x_with_signature = fields.Boolean('With Signature & Stamp', default=True)


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def get_tax_list(self):
        taxes = []
        for data in self:
            for tax_lines in data.taxes_id:
                taxes.append(tax_lines)
        return taxes

    @api.onchange('product_id')
    def onchange_product_id(self):
        rec = super(PurchaseOrderLine, self).onchange_product_id()
        if self.product_id:
            attributes, description = '', ''
            if self.product_id.product_template_attribute_value_ids:
                for data in self.product_id.product_template_attribute_value_ids:
                    if data.name == 'NA':
                        continue
                    attributes += "\n" + data.display_name
            if self.product_id.description_purchase:
                description = self.product_id.description_purchase
            self.name = description + attributes
        return rec
