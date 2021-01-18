from odoo import api, fields, tools, models, _
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
class StockLocation(models.Model):
    _inherit = 'stock.location'


    def _should_be_valued(self):
        """ This method returns a boolean reflecting whether the products stored in `self` should
        be considered when valuating the stock of a company.
        """
        # self.ensure_one()
        if self.usage == 'internal' or (self.usage == 'transit' and self.company_id):
            return True
        return False

    def should_bypass_reservation(self):
        # self.ensure_one()
        return self.usage in ('supplier', 'customer', 'inventory', 'production') or self.scrap_location

    # def button_validate(self):
    #     if self.picking_type_id.code == 'outgoing':
    #         for move in self.move_ids_without_package:
    #             if move.product_uom_qty > move.product_id.qty_available:
    #                 raise UserError(_("Trying to reserve quantities more than on hand quantity !"))
    #
    #     res = super(StockPicking, self).button_validate()
    #     return res


