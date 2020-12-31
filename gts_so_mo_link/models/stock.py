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

    # def button_validate(self):
    #     if self.picking_type_id.code == 'outgoing':
    #         for move in self.move_ids_without_package:
    #             if move.product_uom_qty > move.product_id.qty_available:
    #                 raise UserError(_("Trying to reserve quantities more than on hand quantity !"))
    #
    #     res = super(StockPicking, self).button_validate()
    #     return res


class Uom(models.Model):
    _inherit='uom.uom'


    def _compute_quantity(self, qty, to_unit, round=True, rounding_method='UP', raise_if_failure=True):
        """ Convert the given quantity from the current UoM `self` into a given one
            :param qty: the quantity to convert
            :param to_unit: the destination UoM record (uom.uom)
            :param raise_if_failure: only if the conversion is not possible
                - if true, raise an exception if the conversion is not possible (different UoM category),
                - otherwise, return the initial quantity
        """
        if not self:
            return qty
        self.ensure_one()
        # if self.category_id.id != to_unit.category_id.id:
        #     if raise_if_failure:
        #         raise UserError(_('The unit of measure %s defined on the order line doesn\'t belong to the same category than the unit of measure %s defined on the product. Please correct the unit of measure defined on the order line or on the product, they should belong to the same category.') % (self.name, to_unit.name))
        #     else:
        #         return qty
        amount = qty / self.factor
        if to_unit:
            amount = amount * to_unit.factor
            if round:
                amount = tools.float_round(amount, precision_rounding=to_unit.rounding, rounding_method=rounding_method)
        return amount