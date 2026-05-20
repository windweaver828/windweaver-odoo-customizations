from odoo import fields, models, _
from odoo.exceptions import UserError


class AdditionalContactLink(models.Model):
    _name = "additional.contact.link"
    _description = "Additional Contact Linked Record"
    _order = "model_description, name, id"

    list_id = fields.Many2one(
        "additional.contact.list",
        required=True,
        ondelete="cascade",
        index=True,
    )
    name = fields.Char(required=True)
    model_description = fields.Char(readonly=True)
    res_model = fields.Char(required=True, index=True)
    res_id = fields.Integer(required=True, index=True)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "additional_contact_link_unique",
            "unique(list_id, res_model, res_id)",
            "This record is already linked to the additional contacts list.",
        )
    ]

    def action_open_record(self):
        self.ensure_one()
        record = self.env[self.res_model].browse(self.res_id).exists()
        if not record:
            raise UserError(_("The linked record no longer exists."))
        return {
            "type": "ir.actions.act_window",
            "name": self.name,
            "res_model": self.res_model,
            "res_id": self.res_id,
            "view_mode": "form",
            "target": "current",
        }
