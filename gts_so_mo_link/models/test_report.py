from odoo import api, fields, models, exceptions, _
import qrcode
import base64
from io import BytesIO
from datetime import datetime,date, timedelta
from odoo.exceptions import UserError


class TestReportMO(models.Model):
    _name = "test.report.mo"
    _rec_name = "production_id"

    battery_type = fields.Char('Battery Type', track_visibility='onchange')
    # rated_capacity = fields.Char('Rated Capacity', track_visibility='onchange')
    volts = fields.Float('Volts')
    ah = fields.Float('AH')
    rate_on_sample_cell = fields.Float('Rate Obtained on Sample Cell', track_visibility='onchange')
    production_id = fields.Many2one('mrp.production', string='MO')
    date = fields.Date('Date')
    lot_id = fields.Many2one('stock.production.lot', 'Lot/Serial No.')
    qty_produced = fields.Float('Qty Produced')
    no_of_cell_type = fields.Char('No. of CELL & Type')
