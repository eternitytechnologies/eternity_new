from odoo import api, fields, models, exceptions, _
import qrcode
import base64
from io import BytesIO
from datetime import datetime,date, timedelta
from odoo.exceptions import UserError
import json


class MRPProduction(models.Model):
    _inherit = "mrp.production"

    partner_id = fields.Many2one('res.partner', string='Customer')
    untaxed_amount = fields.Float('Untaxed Amount',compute="_compute_untaxed_amount")
    client_order_ref = fields.Char('Order Reference/ PO')
    delivery_date = fields.Datetime('Delivery Date')
    lot_numbers_count = fields.Integer('Lot Count', compute="_compute_lot_numbers", default=0, copy=False)
    test_certificate_count = fields.Integer('Lot Count', compute="_compute_test_certificates", default=0, copy=False)
    test_report_ids = fields.One2many('test.report.mo', 'production_id', string='Test Certificate Lines')

    def action_assign(self):
        self._cr.execute("ALTER TABLE stock_move_line alter column location_dest_id drop not null")
        self._cr.execute("ALTER TABLE stock_move_line alter column location_id drop not null")
        res = super(MRPProduction, self).action_assign()
        return  res

    @api.depends('finished_move_line_ids', 'finished_move_line_ids.lot_id')
    def _compute_lot_numbers(self):
        for rec in self:
            rec.lot_numbers_count = 0
            for lines in rec.finished_move_line_ids:
                if lines.lot_id.id:
                    rec.lot_numbers_count += 1


    @api.depends('name')
    def _compute_untaxed_amount(self):
        for rec in self:
            if rec.name:
               so_rel = self.env['sale.order'].search([('name','=',rec.origin)])
               untaxed_amount = 0.0
               for sales in so_rel:
                   for line in sales.order_line:
                       if line.product_id == rec.product_id:
                           untaxed_amount += line.price_subtotal

               rec.untaxed_amount = untaxed_amount
            else:
                rec.untaxed_amount = 0.0

    def action_view_lot_numbers(self):
        action = self.env.ref('stock.action_production_lot_form').read()[0]
        list_ids = []
        for lines in self.finished_move_line_ids:
            if lines.lot_id.id:
                list_ids.append(lines.lot_id.id)
        action['domain'] = [('id', 'in', list_ids)]
        action['context'] = {'create': False}
        return action

    @api.depends('test_report_ids')
    def _compute_test_certificates(self):
        for rec in self:
            rec.test_certificate_count = 0
            for lines in rec.test_report_ids:
                rec.test_certificate_count += 1

    def action_view_test_certificate(self):
        action = self.env.ref('gts_so_mo_link.action_view_test_report').read()[0]
        action['domain'] = [('production_id', '=', self.id)]
        action['context'] = {'create': False}
        return action


    # def open_produce_product(self):
    #     for raw in self.move_raw_ids:
    #         if raw.product_id.qty_available < raw.product_uom_qty:
    #             raise UserError(_("Quantity on hand and quantity to consume does not match for the components !"))
    #
    #     res = super(MRPProduction, self).open_produce_product()
    #     return  res
    #
    #
    # def button_mark_done(self):
    #     for raw in self.move_raw_ids:
    #         if raw.product_id.qty_available < raw.product_uom_qty:
    #             raise UserError(_("Quantity on hand and quantity to consume does not match for the components !"))
    #     res = super(MRPProduction, self).button_mark_done()
    #     return res
class TestCertificateMO(models.AbstractModel):
    _name = "report.gts_so_mo_link.report_mrp_test_certificate"

    def _get_report_values(self, docids, data=None):
        docs = self.env['mrp.production'].browse(docids)
        if not docs.finished_move_line_ids:
            raise exceptions.AccessError(_('You Cannot print Test Certificate as there is no Quantity Produced !'))
        if docs.state == 'cancel':
            raise exceptions.AccessError(_('You can not print a Test Certificate for a cancelled Manufacturing Order!'))
        if not docs.test_report_ids:
            raise exceptions.AccessError(_('Test Certificate has not been generated yet!'))
        return {
            'doc_ids': docs.ids,
            'doc_model': 'mrp.production',
            'docs': docs,
        }


class TestCertificateMOWithoutHF(models.AbstractModel):
    _name = "report.gts_so_mo_link.report_mrp_without_hf_test_certificate"

    def _get_report_values(self, docids, data=None):
        docs = self.env['mrp.production'].browse(docids)
        if not docs.finished_move_line_ids:
            raise exceptions.AccessError(_('You Cannot print Test Certificate as there is no Quantity Produced !'))
        if docs.state == 'cancel':
            raise exceptions.AccessError(_('You can not print a Test Certificate for a cancelled Manufacturing Order!'))
        if not docs.test_report_ids:
            raise exceptions.AccessError(_('Test Certificate has not been generated yet!'))
        return {
            'doc_ids': docs.ids,
            'doc_model': 'mrp.production',
            'docs': docs,
        }


class QRReportMOCurrent(models.AbstractModel):
    _name = "report.gts_so_mo_link.report_mrp_production_qrcode"

    def _get_report_values(self, docids, data=None):
        docs = self.env['mrp.production'].browse(docids)
        if not docs.finished_move_line_ids:
            raise exceptions.AccessError(_('You Cannot print QR Code as there is no Quantity Produced !'))
        if docs.state == 'cancel':
            raise exceptions.AccessError(_('You can not print QR Report for a Cancelled Manufacturing Order !'))
        for data in docs.finished_move_line_ids:
            if not data.lot_id:
                raise exceptions.AccessError(_('You can not print QR Code as no Serial Number has been provided!'))
        return {
            'doc_ids': docs.ids,
            'doc_model': 'mrp.production',
            'docs': docs,
        }


class QRReportMOUpcoming(models.AbstractModel):
    _name = "report.gts_so_mo_link.report_mrp_production_qrcode_upcoming"

    def _get_report_values(self, docids, data=None):
        docs = self.env['mrp.production'].browse(docids)
        if not docs.finished_move_line_ids:
            raise exceptions.AccessError(_('You Cannot print QR Code as there is no Quantity Produced !'))
        if docs.state == 'cancel':
            raise exceptions.AccessError(_('You can not print QR Report for a Cancelled Manufacturing Order !'))
        for data in docs.finished_move_line_ids:
            if not data.lot_id:
                raise exceptions.AccessError(_('You can not print QR Code as no Serial Number has been provided!'))
        return {
            'doc_ids': docs.ids,
            'doc_model': 'mrp.production',
            'docs': docs,
        }


class LotQRReportMOCurrent(models.AbstractModel):
    _name = "report.gts_so_mo_link.report_lot_qr_code_current"

    def _get_report_values(self, docids, data=None):
        docs = self.env['stock.production.lot'].browse(docids)
        if docs.production_id.state == 'cancel':
            raise exceptions.AccessError(_('You can not download QR Report for a Cancelled Manufacturing Order !'))
        return {
            'data':data,
            'doc_ids': docs.ids,
            'doc_model': 'stock.production.lot',
            'docs': docs,
        }


class LotQRReportMOUpcoming(models.AbstractModel):
    _name = "report.gts_so_mo_link.report_lot_qr_code_upcoming"

    def _get_report_values(self, docids, data=None):
        docs = self.env['stock.production.lot'].browse(docids)
        if docs.production_id.state == 'cancel':
            raise exceptions.AccessError(_('You can not download QR Report for a Cancelled Manufacturing Order !'))
        return {
            'data':data,
            'doc_ids': docs.ids,
            'doc_model': 'stock.production.lot',
            'docs': docs,
        }


class TestCertificateMOSingle(models.AbstractModel):
    _name = 'report.gts_so_mo_link.single_report_mrp_test_certificate'

    def _get_report_values(self, docids, data=None):
        docs = self.env['test.report.mo'].browse(docids)
        if not docs.production_id.finished_move_line_ids:
            raise exceptions.AccessError(_('You Cannot Download Test Certificate as there is no Quantity Produced !'))
        if docs.production_id.state == 'cancel':
            raise exceptions.AccessError(_('You can not download Test Report for a Cancelled Manufacturing Order !'))
        return {
            'doc_ids': docs.ids,
            'doc_model': 'test.report.mo',
            'docs': docs,
        }


class TestCertificateMOSingleWithoutHF(models.AbstractModel):
    _name = 'report.gts_so_mo_link.single_without_hf_test_certificate'

    def _get_report_values(self, docids, data=None):
        docs = self.env['test.report.mo'].browse(docids)
        if not docs.production_id.finished_move_line_ids:
            raise exceptions.AccessError(_('You Cannot Download Test Certificate as there is no Quantity Produced !'))
        if docs.production_id.state == 'cancel':
            raise exceptions.AccessError(_('You can not download Test Report for a Cancelled Manufacturing Order !'))
        return {
            'doc_ids': docs.ids,
            'doc_model': 'test.report.mo',
            'docs': docs,
        }


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _prepare_mo_vals(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values,
                         bom):
        val = super(StockRule, self)._prepare_mo_vals(product_id, product_qty, product_uom, location_id, name, origin,
                                                      company_id, values, bom)
        print(values)
        if origin:
            sale_order = self.env['sale.order'].search([('name', '=', origin)], limit=1)
            if sale_order:
                val['partner_id'] = sale_order.partner_id.id
                val['client_order_ref'] = sale_order.client_order_ref
                val['delivery_date'] = sale_order.commitment_date
        return val


class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    name = fields.Char(
        'Lot/Serial Number', default=lambda self: self.env['ir.sequence'].next_by_code('stock.lot.serial'),
        required=True, help="Unique Lot/Serial Number", track_visibility='onchange')
    ref = fields.Char('Internal Reference', track_visibility='onchange',
                      help="Internal reference number in case it differs from the manufacturer's lot/serial number")
    product_id = fields.Many2one(
        'product.product', 'Product',
        domain=lambda self: self._domain_product_id(), required=True, check_company=True, track_visibility='onchange')
    qr_code = fields.Binary("QR Code", attachment=True)
    attach_production_report = fields.Binary('Production Report', copy=False, track_visibility='onchange')
    attach_production_report_name = fields.Char('Production Report')
    pdf_attachment_id = fields.Many2one('ir.attachment')
    test_report = fields.Binary('Test Report', track_visibility='onchange')
    test_report_name = fields.Char('Test Report Name')
    used_lot = fields.Boolean('Used Lot')
    # battery_type = fields.Char('Battery Type', track_visibility='onchange')
    # rated_capacity = fields.Char('Rated Capacity', track_visibility='onchange')
    # rate_on_sample_cell = fields.Char('Rate Obtained on Sample Cell', track_visibility='onchange')
    production_id = fields.Many2one('mrp.production', string='MO')
    # invoice_date = fields.Date('Invoice Date')
    test_report_id = fields.Many2one('test.report.mo', 'Test Report')
    mo_date = fields.Date('MO Date')
    delivery_date = fields.Date('Delivery Date')
    product_type = fields.Selection(related='product_id.product_type', string='Item Type')
    # warranty_mo_date = fields.Date('Warranty Date on MO', compute='_get_warranty_mo_date', store=True)
    # warranty_delivery_date = fields.Date('Warranty Date on Delivery', compute='_get_warranty_delivery_date', store=True)
    # start_date = fields.Date('Validity From')
    # end_date = fields.Date('Validity To')
    # invoice_number = fields.Char(string='Invoice No.')

    # @api.depends('mo_date')
    # def _get_warranty_mo_date(self):
    #     for data in self:
    #         data.warranty_mo_date = False
    #         if data.mo_date:
    #             if data.product_id.product_warranty > 0:
    #                 data.warranty_mo_date = data.mo_date + timedelta(
    #                     days=365 * int(data.product_id.product_warranty))
    #
    # @api.depends('delivery_date')
    # def _get_warranty_delivery_date(self):
    #     for data in self:
    #         data.warranty_delivery_date = False
    #         if data.delivery_date:
    #             if data.product_id.product_warranty > 0:
    #                 data.warranty_delivery_date = data.delivery_date + timedelta(
    #                     days=365 * int(data.product_id.product_warranty))

    @api.model
    def create(self, vals_list):
        val = super(ProductionLot, self).create(vals_list)
        if val.product_id.tracking == 'serial':
            content = "Eternity Industrial Batteries (India) LLP " + \
                      "Building No. F8, Unit No. 9 & 10" + \
                      "Pimplas, Bhiwandi 421302" + \
                      "Email : info@eternitytechnologies.com" + \
                      "Tel : 927 2222 380" + \
                      "Toll Free : 1800 3132 648" + \
                      "Capacity: " + str(val.product_id.ah) + \
                      "Volts : " + str(val.product_id.volts) + " V" + \
                      "No. of Cells :" + str((val.product_id.volts) / 2) + " Battery Serial No. :" + val.name
            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4,)
            qr.add_data(content)
            qr.make(fit=True)
            img = qr.make_image()
            temp = BytesIO()
            img.save(temp, format="PNG")
            qr_image = base64.b64encode(temp.getvalue())
            val.qr_code = qr_image
        val.mo_date = date.today()
        active_id = self.env.context.get('active_id')
        if active_id:
            mrp = self.env['mrp.production'].search([('id', '=', active_id)], limit=1)
            if mrp:
                val.production_id = mrp.id

                # stock_move = self.env['stock.move'].search([('raw_material_production_id', '=', mrp.id),
                #                                             ('product_id.product_type', '=', 'cell'),
                #                                             ('product_uom_qty', '>', 0)], limit=1)
                # volts = int(val.product_id.volts)
                # ah = int(val.product_id.ah)
                # qty, product_name = 0, ''
                # if stock_move:
                #     qty = int(stock_move.product_uom_qty / mrp.product_qty)
                #     product_name = stock_move.product_id.name
                # val.battery_type = str(volts) + " V " + str(ah) + " AH  (" + str(
                #     qty) + " x " + product_name + ")"
                # val.rated_capacity = str(ah) + " Ah"
                # val.rate_on_sample_cell = str(ah) + " Ah"
        # if val.production_id:
        #     if val.production_id.origin:
        #         invoice = self.env['account.move'].search(
        #             [('invoice_origin', '=', val.production_id.origin), ('state', '!=', 'cancel')], limit=1,
        #             order='create_date desc')
        #         if invoice:
        #             val.invoice_date = invoice.invoice_date
        return val


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    attach_production_report = fields.Binary('Production Report', copy=False)
    attach_production_report_name = fields.Char('Attach Production Report')
    pdf_attachment_id = fields.Many2one('ir.attachment')


class MrpProductProduce(models.TransientModel):
    _inherit = "mrp.product.produce"

    finished_lot_id = fields.Many2one(
        'stock.production.lot', string='Lot/Serial Number',
        domain="[('product_id', '=', product_id), ('company_id', '=', company_id), ('used_lot', '=', False)]", check_company=True)
    attach_production_report = fields.Binary('Attach Production Report', compute='_attachment_name',
                                             inverse='_set_filename', copy=False)
    attach_production_report_name = fields.Char('Attach Production Report')
    pdf_attachment_id = fields.Many2one('ir.attachment', copy=False)
    rate_on_sample_cell = fields.Float('Rate Obtained on Sample Cell')
    product_type = fields.Selection(related='product_id.product_type')

    def _record_production(self):
        rec = super(MrpProductProduce, self)._record_production()
        if not self.attach_production_report:
            raise UserError(_('Please attach Production Report!'))
        lot_id = ''
        if self.finished_lot_id:
            lot_id = self.finished_lot_id.id
            # Test Certificate attach in lot
            # action = self.env.ref('gts_so_mo_link.single_action_report_test_certificate_mrp').render_qweb_pdf(
            #     self.finished_lot_id.id)[0]
            # pdf = base64.b64encode(action)
            # attachment = self.env['ir.attachment'].create({
            #     'name': 'Test Certificate ' + self.finished_lot_id.name,
            #     'datas': pdf,
            #     'res_model': 'mrp.product.produce',
            #     'res_id': self.id,
            #     'type': 'binary',
            # })
            # self.finished_lot_id.test_report = attachment.datas
            # self.finished_lot_id.test_report_name = attachment.name
            self.finished_lot_id.used_lot = True
        stock_move_line = self.env['stock.move.line'].search([('lot_id', '=', self.finished_lot_id.id),
                                                              ('reference', '=', self.production_id.name)], limit=1)
        if stock_move_line and self.attach_production_report:
            stock_move_line.pdf_attachment_id = self.pdf_attachment_id.id or ''
            stock_move_line.attach_production_report = self.pdf_attachment_id.datas or ''
            stock_move_line.attach_production_report_name = self.pdf_attachment_id.name or ''
        else:
            stock_move_line = self.env['stock.move.line'].search([('reference', '=', self.production_id.name),
                                                                  ('attach_production_report', '=', None)], limit=1)
            if stock_move_line and self.attach_production_report:
                stock_move_line.pdf_attachment_id = self.pdf_attachment_id.id or ''
                stock_move_line.attach_production_report = self.pdf_attachment_id.datas or ''
                stock_move_line.attach_production_report_name = self.pdf_attachment_id.name or ''
        if self.finished_lot_id and self.attach_production_report:
            self.finished_lot_id.pdf_attachment_id = self.pdf_attachment_id.id or ''
            self.finished_lot_id.attach_production_report = self.pdf_attachment_id.datas or ''
            self.finished_lot_id.attach_production_report_name = self.pdf_attachment_id.name or ''
        stock_move = self.env['stock.move'].search([('raw_material_production_id', '=', self.production_id.id),
                                                    ('product_id.product_type', '=', 'cell'),
                                                    ('product_uom_qty', '>', 0)], limit=1)
        volts = int(self.product_id.volts)
        ah = int(self.product_id.ah)
        qty, product_name = 0, ''
        if stock_move:
            qty = int((stock_move.product_uom_qty / self.production_id.product_qty) * self.qty_producing)
            product_name = stock_move.product_id.name
        battery_type = str(volts) + " V " + str(ah) + " AH  (" + str(qty) + " x " + product_name + ")"
        no_of_cell_type = str(qty) + " x " + product_name
        # rated_capacity = str(volts) + " V " + str(ah) + " AH"
        # rate_on_sample_cell = str(ah) + " Ah"
        test_date = None
        if self.production_id:
            if self.production_id.origin:
                invoice = self.env['account.move'].search(
                    [('invoice_origin', '=', self.production_id.origin), ('state', '!=', 'cancel')], limit=1,
                    order='create_date desc')
                if invoice:
                    test_date = invoice.invoice_date
        test_report_dict = {
            'battery_type': battery_type,
            'volts': volts,
            'ah': ah,
            # 'rated_capacity': rated_capacity,
            'rate_on_sample_cell': self.rate_on_sample_cell or 0,
            'production_id': self.production_id.id,
            'lot_id': lot_id,
            'date': test_date or date.today(),
            'qty_produced': self.qty_producing,
            'no_of_cell_type': no_of_cell_type
        }
        test_report_id = self.env['test.report.mo'].create(test_report_dict)
        if self.finished_lot_id:
            self.finished_lot_id.test_report_id = test_report_id.id
        return rec

    @api.depends('attach_production_report')
    def _attachment_name(self):
        val = self.pdf_attachment_id.datas or ''
        self.attach_production_report = val or ''

    def _set_filename(self):
        Attachment = self.env['ir.attachment']
        attachment_value = {
            'name': self.attach_production_report_name or '',
            'datas': self.attach_production_report or '',
            # 'datas_fname': self.attach_production_report_name or '',
            'type': 'binary',
            'res_model': "",
            'res_id': self.id,
        }
        attachment = Attachment.sudo().create(attachment_value)
        self.pdf_attachment_id = attachment.id or ''

    def action_generate_serial(self):
        self.ensure_one()
        product_produce_wiz = self.env.ref('mrp.view_mrp_product_produce_wizard', False)
        if self.product_id.product_type == 'battery':
            mnth = datetime.today().strftime('%m')
            year = datetime.today().strftime('%Y')
            a_length = len(year)
            year_ = year[a_length - 2: a_length]
            dict = {'0': 'M', '1': 'O', '2': 'T', '3': 'H', '4': 'E', '5': 'R', '6': 'L', '7': 'A', '8': 'N', '9': 'D'}
            list_, name = [], ''
            nxt_number = self.env['ir.sequence'].next_by_code('stock.lot.serial')
            for a in year_:
                list_.append(dict[a])
                name = ''.join(str(v) for v in list_)
            sequence = "ET-" + str(mnth) + "-" + name + "-" + nxt_number
            self.finished_lot_id = self.env['stock.production.lot'].create({
                'product_id': self.product_id.id,
                'company_id': self.company_id.id,
                'name': sequence
            })
        else:
            self.finished_lot_id = self.env['stock.production.lot'].create({
                'product_id': self.product_id.id,
                'company_id': self.production_id.company_id.id
            })
        return {
            'name': _('Produce'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mrp.product.produce',
            'res_id': self.id,
            'view_id': product_produce_wiz.id,
            'target': 'new',
        }
