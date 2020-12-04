from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError, ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_company = fields.Boolean(string='Is a Company', default=True,
                                help="Check if the contact is a company, otherwise it is a person")
    pan = fields.Char(string="PAN", size=10)
    region_id = fields.Many2one('res.country.region', 'Region', related='state_id.region_id', store=True)

    @api.onchange('pan')
    def onchange_pan(self):
        if self.supplier_rank and self.pan:
            if len(self.pan) < 10:
                self.pan = ''
                raise UserError(
                    _('PAN Number %s should be 10 digits' % self.pan))

    @api.model
    def default_get(self, fields):
        rec = super(ResPartner, self).default_get(fields)
        country = self.env['res.country'].search([('code', '=', 'IN')], limit=1)
        if country:
            rec['country_id'] = country.id
        return rec
