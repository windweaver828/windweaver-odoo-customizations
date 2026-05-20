from odoo import fields, models, _
from odoo.exceptions import UserError


class AdditionalContactLine(models.Model):
    _name = "additional.contact.line"
    _description = "Additional Contact Line"
    _order = "is_origin desc, sequence, id"
    _ORIGIN_USER_WRITABLE_FIELDS = {"notes"}

    list_id = fields.Many2one(
        "additional.contact.list",
        required=True,
        ondelete="cascade",
        index=True,
    )
    sequence = fields.Integer(default=10)
    partner_id = fields.Many2one(
        "res.partner",
        string="Contact",
        required=True,
        ondelete="restrict",
        index=True,
    )
    role_id = fields.Many2one("additional.contact.role", string="Role", ondelete="restrict")
    notes = fields.Text()
    is_origin = fields.Boolean(string="Origin", default=False, copy=False, readonly=True)
    origin_res_model = fields.Char(readonly=True, copy=False)
    origin_res_id = fields.Integer(readonly=True, copy=False)

    company_id = fields.Many2one(
        "res.partner",
        string="Company",
        related="partner_id.parent_id",
        readonly=True,
        store=False,
    )
    phone = fields.Char(related="partner_id.phone", readonly=True, store=False)
    mobile = fields.Char(related="partner_id.mobile", readonly=True, store=False)
    email = fields.Char(related="partner_id.email", readonly=True, store=False)

    def write(self, vals):
        if (
            not self.env.context.get("allow_additional_contact_origin_update")
            and any(line.is_origin for line in self)
            and any(field not in self._ORIGIN_USER_WRITABLE_FIELDS for field in vals)
        ):
            raise UserError(_("The primary/origin contact line can only have notes changed. Change the customer on the linked record instead."))
        return super().write(vals)

    def unlink(self):
        if any(line.is_origin for line in self):
            raise UserError(_("The primary/origin contact line cannot be deleted. Change the customer on the linked record instead."))
        return super().unlink()
