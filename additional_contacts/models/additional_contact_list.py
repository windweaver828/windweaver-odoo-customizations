from odoo import api, fields, models


class AdditionalContactList(models.Model):
    _name = "additional.contact.list"
    _description = "Additional Contact List"
    _order = "name, id"

    name = fields.Char(required=True, default="Additional Contacts")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    line_ids = fields.One2many(
        "additional.contact.line",
        "list_id",
        string="Additional Contacts",
        copy=True,
    )
    link_ids = fields.One2many(
        "additional.contact.link",
        "list_id",
        string="Linked Records",
        copy=False,
    )

    def _ensure_link_for_record(self, record):
        """Ensure this list has a link row to the supplied business record."""
        self.ensure_one()
        if not record or not record.id:
            return self.env["additional.contact.link"]

        label = self._get_link_label_for_record(record)
        link_model = self.env["additional.contact.link"]
        link = link_model.search([
            ("list_id", "=", self.id),
            ("res_model", "=", record._name),
            ("res_id", "=", record.id),
        ], limit=1)
        values = {
            "name": label,
            "model_description": self._get_model_description(record._name),
            "active": True,
        }
        if link:
            link.write(values)
            return link
        values.update({
            "list_id": self.id,
            "res_model": record._name,
            "res_id": record.id,
        })
        return link_model.create(values)

    def _get_link_label_for_record(self, record):
        if hasattr(record, "_additional_contacts_link_label"):
            return record._additional_contacts_link_label()
        return "%s: %s" % (self._get_model_description(record._name), record.display_name)

    def _get_model_description(self, model_name):
        model = self.env["ir.model"].sudo().search([("model", "=", model_name)], limit=1)
        return model.name or model_name
