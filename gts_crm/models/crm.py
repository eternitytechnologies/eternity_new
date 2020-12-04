from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError


class Lead(models.Model):
    _inherit = "crm.lead"


    def write(self, values):
        res = super(Lead, self).write(values)
        if 'default_type' in self.env.context and self.env.context['default_type'] == 'opportunity':
            if self.planned_revenue <= 0:
                raise UserError(_('Expected Revenue cannot be Zero!'))
        return res

    @api.model
    def create(self, values):
        if values.get('type') == 'opportunity' and 'planned_revenue' in values:
            if values.get('planned_revenue') <= 0:
                raise UserError(_('Expected Revenue cannot be Zero!'))
        rec = super(Lead, self).create(values)
        return rec
