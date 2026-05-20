from odoo import fields, models, _
from odoo.exceptions import UserError


class AdditionalContactRole(models.Model):
    _name = "additional.contact.role"
    _description = "Additional Contact Role"
    _order = "sequence, name, id"

    sequence = fields.Integer(default=10)
    name = fields.Char(required=True, translate=True)
    active = fields.Boolean(default=True)

    def unlink(self):
        primary_role = self.env.ref("additional_contacts.role_primary_customer", raise_if_not_found=False)
        if primary_role and primary_role in self:
            raise UserError(_("The Primary Contact role is required and cannot be deleted."))
        return super().unlink()
