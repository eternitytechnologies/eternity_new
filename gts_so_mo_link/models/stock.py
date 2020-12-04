from odoo import api, fields, models, exceptions, _
import qrcode
import base64
from io import BytesIO
from datetime import datetime, date, timedelta
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_done(self):
        rec = super(StockPicking, self).action_done()
        if self.move_line_ids_without_package:
            for lines in self.move_line_ids_without_package:
                if lines.lot_id and self.date_done:
                    lines.lot_id.delivery_date = self.date_done.strftime('%Y-%m-%d')
        return rec
