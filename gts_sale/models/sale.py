from odoo import api, fields, tools, models, _
from odoo import exceptions
from odoo.exceptions import Warning, UserError, ValidationError
from datetime import datetime, timedelta, date
from num2words import num2words


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('state')
    def _compute_type_name(self):
        for record in self:
            record.type_name = _('Quotation') if record.state in ('draft', 'sent', 'cancel', 'approved') else _(
                'Sales Order')

    @api.depends('order_line.product_id', 'order_line.price_unit', 'order_line.product_uom_qty')
    def _get_cost(self):
        for record in self:
            counter = 0
            cost_per_ah = 0
            record.cost_per_ah = 0.00
            for line in record.order_line:
                if line.cost_per_ah:
                    counter += 1
                    cost_per_ah += line.cost_per_ah
            if cost_per_ah:
                record.cost_per_ah = cost_per_ah / counter

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent_for_approval', 'Sent for Approval'),
        ('approved', 'Approved'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    po_number = fields.Char('PO Number', copy=False)
    po_attachment = fields.Binary('Attach PO', compute='_attachment_name', inverse='_set_filename', copy=False)
    po_value = fields.Float('PO Amount', copy=False)
    attached_file_name = fields.Char('File Name', copy=False)
    attachment_id = fields.Many2one('ir.attachment')
    modify_history_ids = fields.One2many('sale.modify.history', 'sale_id', string='Quotation Rejection History')
    modify_history_bool = fields.Boolean('Modify History', default=False, copy=False)
    modify_comments = fields.Text('Remarks')
    type_name = fields.Char('Type Name', compute='_compute_type_name')
    cost_per_ah = fields.Float('Avg SP/AH', compute=_get_cost, store=True)
    x_studio_buyer_inquiry_date = fields.Date('Buyer Inquiry Date')
    x_studio_buyer_inquiry_number = fields.Selection(
        (["Email", "Email"], ["Call", "Call"], ["Website", "Website"], ["Inperson", "Inperson"]),
        'Buyer Inquiry')
    x_studio_delivery_period = fields.Selection(
        [["Immediate", "Immediate"], ["1 Week", "1 Week"], ["2 Week", "2 Week"], ["3 Week", "3 Week"],
         ["4 Week", "4 Week"], ["5 Week", "5 Week"], ["6 Week", "6 Week"]],
        'Delivery Period')
    x_studio_packing = fields.Char('Packing')
    x_studio_warranty_period = fields.Selection(
        [["1 Years As Per Terms & Conditions", "1 Year As Per Terms & Conditions"],
         ["2 Years As Per Terms & Conditions", "2 Years As Per Terms & Conditions"],
         ["3 Years As Per Terms & Conditions", "3 Years As Per Terms & Conditions"],
         ["No Warranty", "No Warranty"]], 'Warranty Period')
    x_with_signature = fields.Boolean('With Signature & Stamp', default=True)
    mail_user_id = fields.Many2one('res.users', "User")
    cancel_reason = fields.Char(string='Remarks',copy=False)
    cancel_hide = fields.Boolean(string='Hide Button',copy=False)
    inv_rej_history_ids = fields.One2many('invoice.rejection.history',
                                          'sale_id', string='Invoice Rejection History')
    is_inv_rejected = fields.Boolean('Invoice Rejected', default=False)
    quotation_approved_by = fields.Many2one('res.users', 'Quotation Approved By')
    quotation_approved_on = fields.Date('Quotation Approved On')
    invoice_approved_by = fields.Many2one('res.users', 'Invoice Creation Approved By')
    invoice_approved_on = fields.Date('Invoice Creation Approved On')
    total_purchase_price = fields.Monetary(compute='_get_total_cost',
                             currency_field='currency_id', store=True)
    margin_percentage = fields.Float(compute='_product_margin_per', string='Margin (%)',
                                        store=True)

    def _find_mail_template(self, force_confirmation_template=False):
        template_id = False

        if force_confirmation_template or (self.state == 'sale' and not self.env.context.get('proforma', False)):
            template_id = int(self.env['ir.config_parameter'].sudo().get_param('sale.default_confirmation_template'))
            template_id = self.env['mail.template'].search([('id', '=', template_id)]).id
            if not template_id:
                template_id = self.env['ir.model.data'].xmlid_to_res_id('gts_sale.mail_template_sale_confirmation', raise_if_not_found=False)
        if not template_id:
            template_id = self.env['ir.model.data'].xmlid_to_res_id('sale.email_template_edi_sale', raise_if_not_found=False)

        return template_id

    @api.depends('margin', 'amount_untaxed')
    def _product_margin_per(self):
        for order in self:
            if order.amount_untaxed != 0.0:
                order.margin_percentage = (order.margin / order.amount_untaxed) * 100
            else:
                order.margin_percentage = 0.0

    @api.depends('order_line.purchase_price_subtotal')
    def _get_total_cost(self):
        if not all(self._ids):
            for order in self:
                order.total_purchase_price = sum(
                    order.order_line.filtered(lambda r: r.state != 'cancel').mapped('purchase_price_subtotal')
                )
        else:
            self.env["sale.order.line"].flush(['purchase_price_subtotal', 'state'])
            grouped_order_lines_data = self.env['sale.order.line'].read_group(
                [
                    ('order_id', 'in', self.ids),
                    ('state', '!=', 'cancel'),
                ], ['purchase_price_subtotal', 'order_id'], ['order_id'])
            mapped_data = {m['order_id'][0]: m['purchase_price_subtotal'] for m in grouped_order_lines_data}
            for order in self:
                order.total_purchase_price = mapped_data.get(order.id, 0.0)

    def print_quotation(self):
        self.filtered(lambda s: s.state == 'approved').write({'state': 'sent'})
        return self.env.ref('sale.action_report_saleorder') \
            .with_context(discard_logo_check=True).report_action(self)

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        if self.env.context.get('mark_so_as_sent'):
            self.filtered(lambda o: o.state == 'approved').with_context(tracking_disable=True).write({'state': 'sent'})
            self.env.user.company_id.set_onboarding_step_done('sale_onboarding_sample_quotation_state')
        return super(SaleOrder, self.with_context(mail_post_autofollow=True)).message_post(**kwargs)

    def action_reject_invoice(self):
        return {
            'name': _('Rejection Remarks'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'approval.cancel',
            'view_id': self.env.ref('gts_sale.view_cancel_event_form').id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': ({'default_sale_id': self.id, }),
        }

    def action_approve_invoice(self):
        for data in self:
            data.invoice_creation_approved = True
            data.apply_invoice_approval = False
            data.sent_for_invoice_approval = False
            data.invoice_created = False
            data.invoice_approved_by = self.env.user
            data.invoice_approved_on = datetime.now()
            email_cc = ''
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            invoice_template_id = self.env.ref('gts_sale.invoice_create_approve_template_id')
            action_id = self.env.ref('sale.action_quotations_with_onboarding').id
            for group_user in self.env['res.users'].search([]):
                if group_user.has_group('gts_sale.quotation_approval'):
                    email_cc += group_user.login + ' ,'
            params = str(base_url) + "/web#id=%s&view_type=form&model=sale.order&action=%s" % (self.id, action_id)
            sales_url = str(params)
            email_to = self.user_id.login + ' ,' + 'odoo@eternitytechnologies.com'
            if invoice_template_id:
                values = invoice_template_id.generate_email(self.id)
                values['email_to'] = self.mail_user_id.email
                values['email_from'] = self.env.user.email
                values['email_cc'] = email_cc
                values['body_html'] = values['body_html'].replace('_sales_url', sales_url)
                mail = self.env['mail.mail'].create(values)
                try:
                    mail.send()
                except Exception:
                    pass

    def action_approval_to_invoice(self):
        self.mail_user_id= self.env.user.id
        self.sent_for_invoice_approval = True
        self.is_inv_rejected = False
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        template_id = self.env.ref('gts_sale.invoice_create_template_id')
        action_id = self.env.ref('gts_sale.action_pending_for_approval').id
        params = str(base_url) + "/web#id=%s&view_type=form&model=sale.order&action=%s" % (self.id, action_id)
        sales_url = str(params)
        users_list = self.env['res.users'].search([])
        email_to, email_from = '', ''
        for group_user in users_list:
            if group_user.has_group('gts_sale.quotation_approval'):
                email_to += group_user.login + ' ,'
        if template_id:
            values = template_id.generate_email(self.id)
            values['email_to'] = email_to
            values['email_from'] = self.env.user.email
            values['reply_to'] = self.user_id.login
            values['body_html'] = values['body_html'].replace('_sales_url', sales_url)
            mail = self.env['mail.mail'].create(values)
            try:
                mail.send()
            except Exception:
                pass

    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        self.apply_invoice_approval = True
        self.invoice_creation_approved = False
        self.sent_for_invoice_approval = False
        self.invoice_created = False
        for data in self:
            for invoice in data.invoice_ids:
                if invoice.state == 'draft':
                    invoice.button_cancel()
        return res

    def quotation_po_mismatch_email(self):
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        template_id = self.env.ref('gts_sale.quotation_po_amount_mismatch')
        action_id = self.env.ref('sale.action_quotations_with_onboarding').id
        params = str(base_url) + "/web#id=%s&view_type=form&model=sale.order&action=%s" % (self.id, action_id)
        sales_url = str(params)
        users_list = self.env['res.users'].search([])
        email_to = ''
        for group_user in users_list:
            if group_user.has_group('gts_sale.quotation_approval'):
                email_to += group_user.login + ' ,'
        if template_id:
            values = template_id.generate_email(self.id)
            values['email_to'] = email_to
            values['email_from'] = self.env.user.login
            values['body_html'] = values['body_html'].replace('_sales_url', sales_url)
            mail = self.env['mail.mail'].create(values)
            try:
                mail.send()
            except Exception:
                pass

    def action_confirm(self):
        rec = super(SaleOrder, self).action_confirm()
        message=''

        if not self.commitment_date:
            if message:
                message+= ', Delivery Date'
            else:
                message= 'Please enter Delivery Date'


        if not self.po_number:
            if message:
                message+= ', PO Number'
            else:
                message= 'Please fill PO Number'

        if not self.po_value:
            if message:
                message+= ', PO Amount'
            else:
                message= 'Please fill PO Amount'

        if not self.attached_file_name:
            if message:
                message+= ' and attach the PO copy'
            else:
                message= 'Please attach the PO copy'

        if message:
            message+=(' before the confirmation of the Sales Order - %s.' % self.name)
            raise UserError(_(message))

        if int(self.po_value) != int(self.amount_total):
            if not self.env.user.has_group('gts_sale.quotation_approval'):
                self.quotation_po_mismatch_email()
                raise UserError(_(
                    'You can not Approve Quotation since there is mismatch in PO amount with Quotation - %s' % self.name))
        if not self.partner_id.vat and self.partner_id.company_type == 'company':
            raise UserError(_('Please update the GSTIN for the selected customer before the confirmation of Sales Order!'))
        elif self.partner_id.company_type == 'person' and self.partner_id.parent_id and not self.partner_id.parent_id.vat:
            raise UserError(_('Please update the GSTIN for the selected customer before the confirmation of Sales Order!'))
        email_act = self.action_quotation_send()
        email_ctx = email_act.get('context', {})
        self.with_context(**email_ctx).message_post_with_template(email_ctx.get('default_template_id'))
        return rec

    @api.depends('po_attachment')
    def _attachment_name(self):
        val = self.attachment_id.datas
        self.po_attachment = val

    def _set_filename(self):
        Attachment = self.env['ir.attachment']
        attachment_value = {
            'name': self.attached_file_name or '',
            'datas': self.po_attachment or '',
            # 'datas_fname': self.attached_file_name or '',
            'type': 'binary',
            'res_model': "sale.order",
            'res_id': self.id,
        }
        attachment = Attachment.sudo().create(attachment_value)
        self.attachment_id = attachment.id

    def action_request_for_approval(self):
        for data in self:
            data.write({'state': 'sent_for_approval'})
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            template_id = self.env.ref('gts_sale.quotation_sent_for_approval')
            action_id = self.env.ref('gts_sale.action_pending_for_approval').id
            params = str(base_url) + "/web#id=%s&view_type=form&model=sale.order&action=%s" % (
                self.id, action_id
            )
            sales_url = str(params)
            users_list = self.env['res.users'].search([])
            email_to, email_from = '', ''
            for group_user in users_list:
                if group_user.has_group('gts_sale.quotation_approval'):
                    email_to += group_user.login + ' ,'
            email_from = self.user_id.name + ' ,' + 'odoo@eternitytechnologies.com'
            if template_id:
                values = template_id.generate_email(self.id)
                values['email_to'] = email_to
                values['email_from'] = email_from
                values['reply_to'] = self.user_id.login
                values['body_html'] = values['body_html'].replace('_sales_url', sales_url)
                mail = self.env['mail.mail'].create(values)
                try:
                    mail.send()
                except Exception:
                    pass

    def action_approve_quotation(self):
        for data in self:
            data.write({'state': 'approved'})
            data.quotation_approved_by = self.env.user
            data.quotation_approved_on = datetime.now()
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            template_id = self.env.ref('gts_sale.quotation_approved_email')
            action_id = self.env.ref('sale.action_quotations_with_onboarding').id
            params = str(base_url) + "/web#id=%s&view_type=form&model=sale.order&action=%s" % (
                self.id, action_id
            )
            sales_url = str(params)
            email_from = self.env.user.name + ' ,' + 'odoo@eternitytechnologies.com'
            if template_id:
                values = template_id.generate_email(self.id)
                values['email_to'] = data.user_id.login or data.create_uid.partner_id.id
                values['email_from'] = email_from
                values['reply_to'] = self.env.user.login
                values['body_html'] = values['body_html'].replace('_sales_url', sales_url)
                mail = self.env['mail.mail'].create(values)
                try:
                    mail.send()
                except Exception:
                    pass

    def has_to_be_paid(self, include_draft=False):
        # transaction = self.get_portal_last_transaction()
        # return (self.state == 'sent' or (self.state == 'draft' and include_draft)) and not self.is_expired and self.require_payment and transaction.state != 'done' and self.amount_total
        return False


class SaleModifyHistory(models.Model):
    _name = "sale.modify.history"
    _order = "request_date desc"

    sale_id = fields.Many2one('sale.order', string='Sale Order')
    request_date = fields.Datetime('Rejected On')
    requested_by = fields.Many2one('res.users', string='Rejected By')
    comment = fields.Text('Remarks')


class InvoiceRejectionHistory(models.Model):
    _name = "invoice.rejection.history"
    _order = "request_date desc"

    sale_id = fields.Many2one('sale.order', string='Sale Order')
    request_date = fields.Datetime('Rejected On')
    requested_by = fields.Many2one('res.users', string='Rejected By')
    comment = fields.Text('Remarks')


class SaleReportSaleorderDocument(models.AbstractModel):
    _name = 'report.sale.report_saleorder'

    def _get_report_values(self, docids, data=None):
        docs = self.env['sale.order'].browse(docids)
        if docs.state in ['draft', 'sent_for_approval']:
            raise exceptions.AccessError(_('You Cannot Download Quotation as it is not Approved!'))
        return {
            'doc_ids': docs.ids,
            'doc_model': 'sale.order',
            'docs': docs,
            'proforma': True
        }


class SaleReportSaleorderProforma(models.AbstractModel):
    _name = 'report.sale.report_saleorder_pro_forma'

    def _get_report_values(self, docids, data=None):
        docs = self.env['sale.order'].browse(docids)
        if docs.state in ['draft', 'sent_for_approval']:
            raise exceptions.AccessError(_('You Cannot Download PRO_FORMA Invoice as it is not Approved!'))
        return {
            'doc_ids': docs.ids,
            'doc_model': 'sale.order',
            'docs': docs,
            'proforma': True
        }


class ReportSaleOrderJar(models.AbstractModel):
    _name = 'report.gts_sale.report_saleorder_without_hf_jar'

    def _get_report_values(self, docids, data=None):
        docs = self.env['sale.order'].browse(docids)
        if docs.state in ['draft', 'sent_for_approval']:
            raise exceptions.AccessError(_('You Cannot Download Quotation as it is not Approved!'))
        return {
            'doc_ids': docs.ids,
            'doc_model': 'sale.order',
            'docs': docs,
            'proforma': True
        }


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id', 'price_unit', 'product_uom_qty')
    def _onchange_cost_per_ah(self):
        for record in self:
            record.cost_per_ah = 0.00
            if record.product_id.product_type == 'battery':
                if record.product_id.calculate_ah and record.product_id.ah:
                    if record.product_id.ah != 0.0 and record.product_id.volts != 0.0:
                        record.cost_per_ah = (record.price_unit / record.product_id.ah) / (
                            record.product_id.volts / 2) or 0.0
            if record.product_id.product_type == 'cell':
                if record.product_id.ah != 0.0:
                    record.cost_per_ah = (record.price_unit / record.product_id.ah)

    @api.onchange('product_id', 'cost_per_ah', 'product_uom_qty')
    def _onchange_cost_per_ah_reverse(self):
        for record in self:
            record.price_unit = 0.00
            if record.product_id.product_type == 'battery':
                if record.product_id.calculate_ah and record.product_id.ah:
                    if record.product_id.ah != 0.0 and record.product_id.volts != 0.0:
                        record.price_unit = ((record.cost_per_ah * record.product_id.ah) * record.product_id.volts / 2)
            if record.product_id.product_type == 'cell':
                if record.product_id.ah != 0.0:
                    record.price_unit = (record.cost_per_ah * record.product_id.ah)

    @api.depends('product_id', 'purchase_price', 'product_uom_qty')
    def _get_cost_subtotal(self):
        for record in self:
            record.purchase_price_subtotal = record.purchase_price * record.product_uom_qty

    cost_per_ah = fields.Float('SP / AH')
    purchase_price_subtotal = fields.Float(
        string='Cost Subtotal', digits='Cost Subtotal',
        compute=_get_cost_subtotal, store=True
    )

    def get_tax_list(self):
        taxes = []
        for data in self:
            for tax_lines in data.tax_id:
                taxes.append(tax_lines)
        return taxes

    @api.onchange('product_id')
    def product_id_change(self):
        rec = super(SaleOrderLine, self).product_id_change()
        if self.product_id:
            attributes, description = '', ''
            if self.product_id.product_template_attribute_value_ids:
                for data in self.product_id.product_template_attribute_value_ids:
                    if data.name == 'NA':
                        continue
                    attributes += "\n" + data.display_name
            if self.product_id.description_sale:
                description = self.product_id.description_sale
            self.name = description + attributes
        return rec


class SaleReport(models.Model):
    _inherit = "sale.report"

    cost_per_ah = fields.Float('SP/AH', group_operator='avg')
    region_id = fields.Many2one('res.country.region', 'Region')

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['cost_per_ah'] = ", l.cost_per_ah as cost_per_ah"
        fields['region_id'] = ", partner.region_id"
        groupby += ', l.cost_per_ah'
        groupby += ', partner.region_id'
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)
