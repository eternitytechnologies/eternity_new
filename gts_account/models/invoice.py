from collections import defaultdict

from odoo import api, fields, models
from odoo.tools import float_is_zero


class AccountInvoice(models.Model):
    _inherit = "account.move"

    def _get_invoiced_lot_values(self):
        """ Get and prepare data to show a table of invoiced lot on the invoice's report. """
        self.ensure_one()

        if self.state == 'draft':
            return []

        sale_orders = self.mapped('invoice_line_ids.sale_line_ids.order_id')
        stock_move_lines = sale_orders.mapped('picking_ids.move_lines.move_line_ids')

        # Get the other customer invoices and refunds.
        ordered_invoice_ids = sale_orders.mapped('invoice_ids') \
            .filtered(lambda i: i.state not in ['draft', 'cancel']) \
            .sorted(lambda i: (i.invoice_date, i.id))

        # Get the position of self in other customer invoices and refunds.
        self_index = None
        i = 0
        for invoice in ordered_invoice_ids:
            if invoice.id == self.id:
                self_index = i
                break
            i += 1

        # Get the previous invoice if any.
        previous_invoices = ordered_invoice_ids[:self_index]
        last_invoice = previous_invoices[-1] if len(previous_invoices) else None

        # Get the incoming and outgoing sml between self.invoice_date and the previous invoice (if any).
        write_dates = [wd for wd in self.invoice_line_ids.mapped('write_date') if wd]
        self_datetime = max(write_dates) if write_dates else None
        last_write_dates = last_invoice and [wd for wd in last_invoice.invoice_line_ids.mapped('write_date') if wd]
        last_invoice_datetime = max(last_write_dates) if last_write_dates else None

        def _filter_incoming_sml(ml):
            if ml.state == 'done' and ml.location_id.usage == 'customer' and ml.lot_id:
                if last_invoice_datetime:
                    return last_invoice_datetime <= ml.date <= self_datetime
                else:
                    return ml.date <= self_datetime
            return False

        def _filter_outgoing_sml(ml):
            if ml.state == 'done' and ml.location_dest_id.usage == 'customer' and ml.lot_id:
                if last_invoice_datetime:
                    return last_invoice_datetime <= ml.date <= self_datetime
                else:
                    return ml.date <= self_datetime
            return False

        incoming_sml = stock_move_lines.filtered(_filter_incoming_sml)
        outgoing_sml = stock_move_lines.filtered(_filter_outgoing_sml)

        # Prepare and return lot_values
        qties_per_lot = defaultdict(lambda: 0)
        if self.type == 'out_refund':
            for ml in outgoing_sml:
                qties_per_lot[ml.lot_id] -= ml.product_uom_id._compute_quantity(ml.qty_done, ml.product_id.uom_id)
            for ml in incoming_sml:
                qties_per_lot[ml.lot_id] += ml.product_uom_id._compute_quantity(ml.qty_done, ml.product_id.uom_id)
        else:
            for ml in outgoing_sml:
                qties_per_lot[ml.lot_id] += ml.product_uom_id._compute_quantity(ml.qty_done, ml.product_id.uom_id)
            for ml in incoming_sml:
                qties_per_lot[ml.lot_id] -= ml.product_uom_id._compute_quantity(ml.qty_done, ml.product_id.uom_id)
        lot_values = []
        for lot_id, qty in qties_per_lot.items():
            if float_is_zero(qty, precision_rounding=lot_id.product_id.uom_id.rounding):
                continue
            lot_values.append({
                'product_name': lot_id.product_id.name,
                'quantity': qty,
                'uom_name': lot_id.product_uom_id.name,
                'lot_name': lot_id.name,
            })
        return lot_values

    x_with_signature = fields.Boolean("With Stamp & Signature", default=True)
    bill_attachment = fields.Binary('Attach Bill', attachment=True)
    x_studio_eway_bill_no = fields.Char('E-way Bill No.', default='')
    region_id = fields.Many2one('res.country.region', 'Region', related='partner_id.region_id', store=True)
    margin = fields.Monetary(compute='_product_margin',
                             currency_field='currency_id', store=True)
    margin_percentage = fields.Monetary(compute='_product_margin_per', string='Margin (%)',
                             currency_field='currency_id', store=True)
    total_purchase_price = fields.Monetary(compute='_get_total_cost', string='Total Cost',
                                           currency_field='currency_id', store=True)

    @api.depends('invoice_line_ids.purchase_price_subtotal')
    def _get_total_cost(self):
        purchase_price_total = 0.0
        for move in self:
            if move.type == 'out_invoice':
                for line in move.invoice_line_ids:
                    purchase_price_total += line.purchase_price_subtotal
                move.total_purchase_price = purchase_price_total

    @api.depends('margin', 'amount_untaxed')
    def _product_margin_per(self):
        for move in self:
            if move.amount_untaxed != 0.0 and move.type == 'out_invoice':
                move.margin_percentage = (move.margin / move.amount_untaxed) * 100

    @api.depends('invoice_line_ids.margin')
    def _product_margin(self):
        margin = 0.0
        for move in self:
            if move.type == 'out_invoice':
                for line in move.invoice_line_ids:
                    margin += line.margin
                move.margin = margin


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.depends('product_id', 'purchase_price', 'quantity')
    def _get_cost_subtotal(self):
        for record in self:
            record.purchase_price_subtotal = record.purchase_price * record.quantity

    purchase_price_subtotal = fields.Float(
        string='Cost Subtotal', digits='Cost Subtotal',
        compute=_get_cost_subtotal, store=True
    )
    margin = fields.Float(compute='_product_margin', digits='Product Price', store=True, string='Margin')
    purchase_price = fields.Float(string='Cost', digits='Product Price')

    def get_tax_list(self):
        taxes = []
        for data in self:
            for tax_lines in data.tax_ids:
                taxes.append(tax_lines)
        return taxes

    def _get_computed_name(self):
        self.ensure_one()

        if not self.product_id:
            return ''

        if self.partner_id.lang:
            product = self.product_id.with_context(lang=self.partner_id.lang)
        else:
            product = self.product_id

        values = []
        # if product.partner_ref:
        #     values.append(product.name)
        if self.journal_id.type == 'sale':
            if product.description_sale:
                values.append(product.description_sale)
        elif self.journal_id.type == 'purchase':
            if product.description_purchase:
                values.append(product.description_purchase)
        if product.product_template_attribute_value_ids:
            for data in product.product_template_attribute_value_ids:
                if data.name == 'NA':
                    continue
                attributes = data.display_name
                values.append(attributes)
        return '\n'.join(values)

    def _compute_margin(self, move_id, product_id, product_uom_id):
        frm_cur = self.env.company.currency_id
        to_cur = move_id.currency_id
        purchase_price = product_id.standard_price
        if product_uom_id != product_id.uom_id:
            purchase_price = product_id.uom_id._compute_price(purchase_price, product_uom_id)
        price = frm_cur._convert(
            purchase_price, to_cur, move_id.company_id or self.env.company,
            move_id.date or fields.Date.today(), round=False)
        return price

    @api.onchange('product_id', 'product_uom_id')
    def product_id_change_margin(self):
        if self.move_id.type == 'out_invoice':
            if not self.product_id or not self.product_uom_id:
                return
            self.purchase_price = self._compute_margin(self.move_id, self.product_id, self.product_uom_id)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        # VFE FIXME : bugfix for matrix, the purchase_price will be changed to a computed field in master.
        res = super(AccountMoveLine, self)._onchange_product_id()
        if self.move_id.type == 'out_invoice':
            self.product_id_change_margin()
        return res

    @api.depends('product_id', 'purchase_price', 'quantity', 'price_unit', 'price_subtotal')
    def _product_margin(self):
        for line in self:
            if line.move_id.type == 'out_invoice':
                currency = line.move_id.currency_id
                price = line.purchase_price
                margin = line.price_subtotal - (price * line.quantity)
                line.margin = currency.round(margin) if currency else margin
            else:
                line.margin = 0.0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'purchase_price' not in vals:
                move_id = self.env['account.move'].browse(vals.get('move_id'))
                product_id = self.env['product.product'].browse(vals.get('product_id'))
                product_uom_id = self.env['uom.uom'].browse(vals.get('product_uom_id'))
                if move_id.type == 'out_invoice':
                    vals['purchase_price'] = self._compute_margin(move_id, product_id, product_uom_id)
        return super(AccountMoveLine, self).create(vals_list)

