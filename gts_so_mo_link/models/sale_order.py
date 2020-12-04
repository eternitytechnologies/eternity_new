from odoo import api, fields, models, exceptions, _
from datetime import datetime, timedelta, date


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
