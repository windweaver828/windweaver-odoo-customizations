from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    additional_contact_involvement_ids = fields.One2many(
        "additional.contact.involvement",
        "partner_id",
        string="Involved In",
        readonly=True,
    )
