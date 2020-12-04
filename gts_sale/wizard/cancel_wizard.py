from odoo import models, api, fields, _
from odoo.exceptions import UserError


class ApprovalCancel(models.TransientModel):
    _name = 'approval.cancel'

    reason_for_cancel = fields.Char(string='Remarks')
    sale_id = fields.Many2one('sale.order', 'SO')

    def action_cancel_reason_apply(self):
        context = self._context
        active_id = self.env['sale.order'].browse(self._context['active_id'])
        self.sale_id.write({'cancel_reason': self.reason_for_cancel,
                            'apply_invoice_approval': True,
                            'sent_for_invoice_approval': False,
                            'is_inv_rejected': True
                            })
        dict = {
            'sale_id': active_id.id,
            'requested_by': self.env.user.id,
            'request_date': fields.Datetime.now(),
            'comment': self.reason_for_cancel
        }
        self.env['invoice.rejection.history'].create(dict)
        email_cc = ''
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        invoice_template_id = self.env.ref('gts_sale.invoice_reject_template_id')
        action_id = self.env.ref('sale.action_quotations_with_onboarding').id
        for group_user in self.env['res.users'].search([]):
            if group_user.has_group('gts_sale.quotation_approval'):
                email_cc += group_user.login + ' ,'
        params = str(base_url) + "/web#id=%s&view_type=form&model=sale.order&action=%s" % (self.sale_id.id, action_id)
        sales_url = str(params)
        if invoice_template_id:
            values = invoice_template_id.generate_email(self.sale_id.id)
            values['email_to'] = self.sale_id.mail_user_id.email
            values['email_from'] = self.env.user.email
            values['email_cc'] = email_cc
            values['body_html'] = values['body_html'].replace('_sales_url', sales_url)
            mail = self.env['mail.mail'].create(values)
            try:
                mail.send()
            except Exception:
                pass
