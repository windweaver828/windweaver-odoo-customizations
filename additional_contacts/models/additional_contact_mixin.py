from odoo import fields, models


class AdditionalContactMixin(models.AbstractModel):
    _name = "additional.contact.mixin"
    _description = "Additional Contacts Mixin"

    additional_contact_list_id = fields.Many2one(
        "additional.contact.list",
        string="Additional Contact List",
        copy=False,
        ondelete="set null",
    )
    additional_contact_line_ids = fields.One2many(
        related="additional_contact_list_id.line_ids",
        string="Additional Contacts",
        readonly=False,
    )
    additional_contact_link_ids = fields.One2many(
        related="additional_contact_list_id.link_ids",
        string="Additional Contact Links",
        readonly=True,
    )

    def _additional_contacts_make_list_name(self):
        self.ensure_one()
        return self.display_name or "Additional Contacts"

    def _additional_contacts_get_origin_partner(self):
        """Override in business modules to return the main/customer partner."""
        self.ensure_one()
        return self.env["res.partner"]

    def _additional_contacts_origin_role(self):
        return self.env.ref("additional_contacts.role_primary_customer", raise_if_not_found=False)

    def _additional_contacts_link_label(self):
        self.ensure_one()
        model = self.env["ir.model"].sudo().search([("model", "=", self._name)], limit=1)
        model_name = model.name or self._name
        return "%s: %s" % (model_name, self.display_name)

    def _additional_contacts_prepare_list_values(self):
        self.ensure_one()
        values = {"name": self._additional_contacts_make_list_name()}
        if "company_id" in self._fields and self.company_id:
            values["company_id"] = self.company_id.id
        return values

    def _additional_contacts_ensure_list(self):
        list_model = self.env["additional.contact.list"]
        for record in self:
            if not record.additional_contact_list_id:
                contact_list = list_model.create(record._additional_contacts_prepare_list_values())
                record.with_context(skip_additional_contacts_sync=True).write({
                    "additional_contact_list_id": contact_list.id,
                })
            record.additional_contact_list_id._ensure_link_for_record(record)
            record._additional_contacts_ensure_origin_line()
        return self.mapped("additional_contact_list_id")

    def _additional_contacts_ensure_origin_line(self):
        line_model = self.env["additional.contact.line"]
        for record in self:
            contact_list = record.additional_contact_list_id
            if not contact_list:
                continue
            partner = record._additional_contacts_get_origin_partner()
            if not partner:
                continue
            role = record._additional_contacts_origin_role()
            existing_for_record = contact_list.line_ids.filtered(
                lambda line: line.is_origin
                and line.origin_res_model == record._name
                and line.origin_res_id == record.id
            )[:1]
            if existing_for_record:
                values = {"partner_id": partner.id}
                if role:
                    values["role_id"] = role.id
                existing_for_record.with_context(allow_additional_contact_origin_update=True).write(values)
                continue

            # If this shared list already has an origin line from the source record,
            # do not add another automatic origin line. Different customers can be
            # added manually if needed.
            if contact_list.line_ids.filtered("is_origin"):
                continue

            values = {
                "list_id": contact_list.id,
                "sequence": 0,
                "partner_id": partner.id,
                "is_origin": True,
                "origin_res_model": record._name,
                "origin_res_id": record.id,
            }
            if role:
                values["role_id"] = role.id
            line_model.create(values)

    def _additional_contacts_refresh_link(self):
        for record in self.filtered("additional_contact_list_id"):
            record.additional_contact_list_id._ensure_link_for_record(record)

    def action_ensure_additional_contacts(self):
        self._additional_contacts_ensure_list()
        return {"type": "ir.actions.client", "tag": "reload"}
