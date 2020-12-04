from odoo import _, api, fields, models, SUPERUSER_ID, tools
import base64


class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    attach_design = fields.Boolean('Attach Design', default=False)
    show_design = fields.Boolean('Show Design', default=False, )

    @api.model
    def default_get(self, fields):
        rec = super(MailComposer, self).default_get(fields)
        active_model = self.env.context.get('active_model')
        if active_model == 'sale.order':
            show_design = False
            sale_order = self.env['sale.order'].search([('id', '=', self.env.context.get('active_id'))], limit=1)
            for lines in sale_order.order_line:
                if lines.product_id.product_tmpl_id.pdf_attachment_id.datas:
                    show_design = True
            rec.update({'show_design': show_design})

        return rec

    @api.onchange('attach_design')
    def _onchange_attach_design(self):
        if self.model == 'sale.order' and self.res_id:
            sale_order = self.env['sale.order'].search([('id', '=', self.res_id)], limit=1)
            x = 0
            attachment_list = []
            for rec in self.attachment_ids:
                if x == 0:
                    x += 1
                    attachment_list = [rec]
            if sale_order and self.attach_design:
                for lines in sale_order.order_line:
                    pdf_attachment = lines.product_id.product_tmpl_id.pdf_attachment_id.datas
                    if pdf_attachment:
                        attach_datas = {
                            'name': lines.product_id.product_tmpl_id.attach_design_pdf_filename,
                            'datas': pdf_attachment,
                            # 'datas_fname': lines.product_id.product_tmpl_id.attach_design_pdf_filename,
                            'res_model': 'mail.compose.message',
                            'res_id': 0,
                            'type': 'binary',
                        }
                        attachment = self.env['ir.attachment'].create(attach_datas)
                        attachment_list.append(attachment)
                self.attachment_ids = [(6, 0, [rec.id for rec in attachment_list])]
            elif sale_order and not self.attach_design:
                self.attachment_ids = [(6, 0, [rec.id for rec in attachment_list])]
