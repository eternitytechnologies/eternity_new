from odoo import api, fields, models, exceptions, _


class TestCertificateMOSingle(models.AbstractModel):
    _name = 'report.gts_so_mo_link.single_report_mrp_test_certificate'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['test.report.mo'].browse(docids)
        cell_qty_produced = 0
        if not docs.production_id.finished_move_line_ids:
            raise exceptions.AccessError(_('You Cannot Download Test Certificate as there is no Quantity Produced !'))
        if docs.production_id.state == 'cancel':
            raise exceptions.AccessError(_('You can not download Test Report for a Cancelled Manufacturing Order !'))
        else:
            for doc in docs:
                if doc.production_id.finished_move_line_ids:
                    for finished_move in doc.production_id.finished_move_line_ids:
                        cell_qty_produced +=finished_move.qty_done

        return {
            'data':data,
            'doc_ids': docs.ids,
            'doc_model': 'test.report.mo',
            'cell_produced':str(cell_qty_produced),
            'docs': docs,
        }


class TestCertificateMOSingleWithoutHF(models.AbstractModel):
    _name = 'report.gts_so_mo_link.single_without_hf_test_certificate'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['test.report.mo'].browse(docids)
        cell_qty_produced = 0

        if not docs.production_id.finished_move_line_ids:
            raise exceptions.AccessError(_('You Cannot Download Test Certificate as there is no Quantity Produced !'))
        if docs.production_id.state == 'cancel':
            raise exceptions.AccessError(_('You can not download Test Report for a Cancelled Manufacturing Order !'))
        else:
            for doc in docs:
                if doc.production_id.finished_move_line_ids:
                    for finished_move in doc.production_id.finished_move_line_ids:
                        cell_qty_produced += finished_move.qty_done

        return {
            'data':data,
            'doc_ids': docs.ids,
            'doc_model': 'test.report.mo',
            'cell_produced': cell_qty_produced,
            'docs': docs,
        }