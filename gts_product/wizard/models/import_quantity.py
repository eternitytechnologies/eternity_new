from odoo import api, models, fields, _
from odoo.exceptions import UserError
import base64
import csv
from io import StringIO
from tempfile import TemporaryFile

class ImportQuantity(models.TransientModel):
    _name = 'update.lot.quantity'

    upload_file = fields.Binary("Upload File")

    def import_quant(self):
        csv_datas = self.upload_file
        fileobj = TemporaryFile('wb+')
        csv_datas = base64.decodestring(csv_datas)
        fileobj.write(csv_datas)
        fileobj.seek(0)
        str_csv_data = fileobj.read().decode('utf-8')
        lis = csv.reader(StringIO(str_csv_data), delimiter=',')
        row_num = 0
        stock_quant = self.env['stock.quant']
        location = self.env['stock.location'].search([('name','=','Stock')])
        # warehouse = self.env['stock.warehouse'].search(
        #     [('company_id', '=', self.env.company.id)], limit=1
        # )
        qty_index =[8,10,12,14,16,18]
        lot_index =[9,11,13,15,17,19]
        for row in lis:
            if row_num==0:
                row_num+=1
            else:
                if len(row) > 9:
                    internal_ref = row[0]
                    name = row[1]
                    qty_index_visited = []
                    lot_index_visited = []
                    current_index = 8
                    # lot_current_index = 6

                    if name:
                        external_id = str(row[7]).split("_")
                        id = external_id[6]
                        product = self.env['product.product'].search([('id', '=', id)])
                        lot = ''
                        quant = 0.0
                        for col in row[8:]:
                            if current_index in qty_index and current_index not in qty_index_visited:
                                quant = col
                                qty_index_visited.append(current_index)

                            if current_index in lot_index and current_index not in lot_index_visited:
                                lot = col
                                lot_index_visited.append(current_index)

                            current_index +=1


                            if len(lot) > 1 :
                                lot_ref = self.env['stock.production.lot'].search([('name','=',lot),('product_id.id','=',product.id)])
                                lot=''
                                if lot_ref and product.type not in ['consu','service']:
                                    stock_quant.with_context(inventory_mode=True).create({
                                        'product_id': product.id,
                                        'location_id':location.id,
                                        'lot_id':lot_ref.id,
                                        'inventory_quantity':float(quant),
                                    })
                                # if lot_ref:
                                #     lot_ref.sudo().write({'product_qty' : float(quant)})

                else:
                    internal_ref = row[0]
                    name = row[1]
                    if name :
                        external_id = str(row[8]).split("_")
                        id = external_id[6]
                        product = self.env['product.product'].search([('id', '=', id)])
                        quant = float(row[5])
                        if product.type not in ['consu','service']:
                            stock_quant.with_context(inventory_mode=True).create({
                                'product_id': product.id,
                                'location_id' : location.id,
                                'inventory_quantity' : float(quant),
                            })
                            # product.qty_available = float(quantity)

