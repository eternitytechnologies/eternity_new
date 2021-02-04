from odoo import api, fields, models, exceptions, _
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'


    def get_overdue_invoices(self):
        for rec in self:
            invoice_obj = self.env['account.move']
            move_ids = invoice_obj.search([
                ('partner_id', '=', rec.partner_id.id),
                ('invoice_payment_state', '=', 'not_paid'),
                ('invoice_date_due', '<', datetime.today()),
                ('state', '=', 'posted'),
            ])
            return move_ids

    def find_for_invoice_approval(self):
        for rec in self:
            invoice_obj = self.env['account.move']
            move_ids = invoice_obj.search([
                ('partner_id', '=', rec.partner_id.id),
                ('invoice_payment_state', '=', 'not_paid'),
                ('invoice_date_due', '<', datetime.today()),
                ('state', '=', 'posted'),
            ])
            total_residual = 0.0
            for data in move_ids:
                total_residual += data.amount_residual_signed
            rec.residual_amount = total_residual
            if rec.residual_amount > 0.0 and rec.invoice_creation_approved is True and rec.invoice_created is True:
                rec.apply_invoice_approval = False
            if rec.residual_amount > 0.0 and rec.invoice_creation_approved is False and rec.invoice_created is False:
                rec.apply_invoice_approval = True
            if rec.residual_amount == 0.0:
                rec.apply_invoice_approval = False
                rec.invoice_creation_approved = True
                rec.sent_for_invoice_approval = False
                rec.invoice_created = True

    production_ids = fields.One2many('mrp.production', compute="_compute_production_ids",
                                     string='Related MO Orders')
    production_count = fields.Integer(compute="_compute_production_count",
                                      string='MO Count')
    invoice_approval = fields.Boolean("Invoice approval", copy=False, default=False)
    create_invoice = fields.Boolean("Can Create Invoice", copy=False, default=False)
    create_invoice_invisible = fields.Boolean("Create Invisible", copy=False, default=False)
    approval_invoice_invisible = fields.Boolean("Approval Invisible", copy=False, default=False)
    default_invoice_invisible = fields.Boolean("Default Invoice Button Invisible", copy=False, default=False)

    apply_invoice_approval = fields.Boolean("Apply Invoice Approval", copy=False)
    sent_for_invoice_approval = fields.Boolean("Sent for Invoice Approval", copy=False)
    invoice_creation_approved = fields.Boolean("Invoice Creation Approved", copy=False, default=False)
    invoice_created = fields.Boolean("Invoice Created", copy=False, default=False)
    residual_amount = fields.Monetary(string='Amount Overdue', copy=False,
                                      compute='find_for_invoice_approval', )
    categ_id = fields.Many2many(related='partner_id.category_id',string="Tags")


    @api.depends('name')
    def _compute_production_count(self):
        production_obj = self.env['mrp.production']
        for order in self:
            production_recs = production_obj.search([('origin', '=', order.name)])
            order.production_count = len(production_recs.ids)

    @api.depends('name')
    def _compute_production_ids(self):
        production_obj = self.env['mrp.production']
        for order in self:
            order.production_ids = production_obj.search([('origin', '=', order.name)])

    def view_production_orders(self):
        '''
        This function returns an action that display related production orders
        of current sales order.'''
        action = self.env.ref('mrp.mrp_production_action').read()[0]
        production_recs = self.mapped('production_ids')
        if len(production_recs) > 1:
            action['domain'] = [('id', 'in', production_recs.ids)]
        elif production_recs:
            action['views'] = [(self.env.ref('mrp.mrp_production_form_view').id, 'form')]
            action['res_id'] = production_recs.id
        return action

    def create_mo_script(self):
        order_ids = self.search([('confirmation_date', '>=', '2020-04-01'), ('state', '=', 'sale')])
        picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'mrp_operation'),
            (
                'warehouse_id.company_id', 'in',
                [self.env.context.get('company_id', self.env.user.company_id.id), False])],
            limit=1)
        mrp = self.env['mrp.production']
        counter = 0
        for order in order_ids:
            if not order.production_ids:
                for line in order.order_line:
                    mrp_vals = {}
                    if 1 in line.product_id.route_ids.ids and line.product_id.bom_count:
                        bom = self.env['mrp.bom']._bom_find(product=line.product_id, picking_type=picking_type,
                                                            company_id=order.company_id.id, bom_type='normal')
                        mrp_vals = {
                            'product_qty': line.product_uom_qty,
                            'origin': order.name,
                            'date_planned_start': order.confirmation_date,
                            'create_date': order.confirmation_date,
                            'company_id': order.company_id.id,
                            'product_id': line.product_id.id,
                            'product_uom_id': line.product_uom.id,
                            'picking_type_id': 8,
                            'bom_id': bom.id,
                        }
                        counter += 1
                        mrp_data = mrp.new(mrp_vals)
                        mrp_data._onchange_bom_id()
                        new_vals = mrp_data._convert_to_write(mrp_data._cache)
                        production = mrp.create(new_vals)
                        production._onchange_move_raw()
                        production.action_confirm()

    @api.onchange('commitment_date')
    def onchange_commitment_date(self):
        mrp = self.env['mrp.production'].search([('origin', '=', self.name)])
        if mrp:
            for data in mrp:
                data.update({'delivery_date': self.commitment_date})


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.model
    def default_get(self, fields):
        res = super(SaleAdvancePaymentInv, self).default_get(fields)
        context = self._context
        sale_obj = self.env['sale.order']
        active_id = context.get('active_id')
        if active_id:
            search_id = sale_obj.browse(active_id)
            search_id.invoice_created = True
            search_id.invoice_creation_approved = False
        return res


    def create_invoices(self):
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        # for sale in sale_orders:
        #     mrps = self.env['mrp.production'].search([('origin','=',sale.name)])
        #     for mrp in mrps:
        #         if mrp.state != 'done':
        #             raise UserError(_('Any of the manufacturing order for this sale order is not done yet!!'))

        if self.advance_payment_method == 'delivered':
            sale_orders._create_invoices(final=self.deduct_down_payments)
        else:
            # Create deposit product if necessary
            if not self.product_id:
                vals = self._prepare_deposit_product()
                self.product_id = self.env['product.product'].create(vals)
                self.env['ir.config_parameter'].sudo().set_param('sale.default_deposit_product_id', self.product_id.id)

            sale_line_obj = self.env['sale.order.line']
            for order in sale_orders:
                if self.advance_payment_method == 'percentage':
                    amount = order.amount_untaxed * self.amount / 100
                else:
                    amount = self.fixed_amount
                if self.product_id.invoice_policy != 'order':
                    raise UserError(_('The product used to invoice a down payment should have an invoice policy set to "Ordered quantities". Please update your deposit product to be able to create a deposit invoice.'))
                if self.product_id.type != 'service':
                    raise UserError(_("The product used to invoice a down payment should be of type 'Service'. Please use another product or update this product."))
                taxes = self.product_id.taxes_id.filtered(lambda r: not order.company_id or r.company_id == order.company_id)
                if order.fiscal_position_id and taxes:
                    tax_ids = order.fiscal_position_id.map_tax(taxes, self.product_id, order.partner_shipping_id).ids
                else:
                    tax_ids = taxes.ids
                context = {'lang': order.partner_id.lang}
                analytic_tag_ids = []
                for line in order.order_line:
                    analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in line.analytic_tag_ids]
                so_line = sale_line_obj.create({
                    'name': _('Down Payment: %s') % (datetime.strftime('%m %Y'),),
                    'price_unit': amount,
                    'product_uom_qty': 0.0,
                    'order_id': order.id,
                    'discount': 0.0,
                    'product_uom': self.product_id.uom_id.id,
                    'product_id': self.product_id.id,
                    'analytic_tag_ids': analytic_tag_ids,
                    'tax_id': [(6, 0, tax_ids)],
                    'is_downpayment': True,
                })
                del context
                self._create_invoice(order, so_line, amount)
        if self._context.get('open_invoices', False):
            return sale_orders.action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}


    def _create_invoice(self, order, so_line, amount):
        if (self.advance_payment_method == 'percentage' and self.amount <= 0.00) or (self.advance_payment_method == 'fixed' and self.fixed_amount <= 0.00):
            raise UserError(_('The value of the down payment amount must be positive.'))
        if self.advance_payment_method == 'percentage':
            amount = order.amount_untaxed * self.amount / 100
            name = _("Down payment of %s%%") % (self.amount,)
        else:
            amount = self.fixed_amount
            name = _('Down Payment')

        invoice_vals = {
            'type': 'out_invoice',
            'invoice_origin': order.name,
            'invoice_user_id': order.user_id.id,
            'narration': order.note,
            'partner_id': order.partner_invoice_id.id,
            'fiscal_position_id': order.fiscal_position_id.id or order.partner_id.property_account_position_id.id,
            'partner_shipping_id': order.partner_shipping_id.id,
            'currency_id': order.pricelist_id.currency_id.id,
            'invoice_payment_ref': order.client_order_ref,
            'invoice_payment_term_id': order.payment_term_id.id,
            'team_id': order.team_id.id,
            'campaign_id': order.campaign_id.id,
            'medium_id': order.medium_id.id,
            'source_id': order.source_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': name,
                'price_unit': amount,
                'quantity': 1.0,
                'product_id': self.product_id.id,
                'product_uom_id': so_line.product_uom.id,
                'tax_ids': [(6, 0, so_line.tax_id.ids)],
                'sale_line_ids': [(6, 0, [so_line.id])],
                'analytic_tag_ids': [(6, 0, so_line.analytic_tag_ids.ids)],
                'analytic_account_id': order.analytic_account_id.id or False,
            })],
        }
        if order.fiscal_position_id:
            invoice_vals['fiscal_position_id'] = order.fiscal_position_id.id
        invoice = self.env['account.move'].create(invoice_vals)
        invoice.message_post_with_view('mail.message_origin_link',
                    values={'self': invoice, 'origin': order},
                    subtype_id=self.env.ref('mail.mt_note').id)
        return invoice