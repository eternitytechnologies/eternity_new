from odoo import api, models, fields, _
from odoo.exceptions import UserError
import base64
import csv
from io import StringIO
from tempfile import TemporaryFile


class TransferAttachments(models.Model):
    _name = 'transfer.attachment'

    upload_file = fields.Binary("Upload File")


    def transfer_attachments(self):
        Attachment = self.env['ir.attachment']
        mrp_produce_attachments = self.env['mrp.product.produce'].search([('attach_production_report','!=',False)])
        for mrp_produce in mrp_produce_attachments:

            attachment_value = {
                'name': mrp_produce.attach_production_report_name or '',
                'datas': mrp_produce.attach_production_report or '',
                'type': 'binary',
                'res_model': "mrp.production",
                'res_id': mrp_produce.production_id.id,
            }
            attachment = Attachment.sudo().create(attachment_value)

