from odoo import api, models


class CrmLead(models.Model):
    _name = "crm.lead"
    _inherit = ["crm.lead", "additional.contact.mixin"]

    def _additional_contacts_get_origin_partner(self):
        self.ensure_one()
        return self.partner_id

    def _additional_contacts_make_list_name(self):
        self.ensure_one()
        return self.name or super()._additional_contacts_make_list_name()

    def _additional_contacts_link_label(self):
        self.ensure_one()
        label = "Lead" if self.type == "lead" else "Opportunity"
        return "%s: %s" % (label, self.name or self.display_name)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if not self.env.context.get("skip_additional_contacts_sync"):
            for record in records:
                if record.partner_id or record.additional_contact_list_id:
                    record._additional_contacts_ensure_list()
        return records

    def write(self, vals):
        result = super().write(vals)
        if not self.env.context.get("skip_additional_contacts_sync"):
            watched = {"partner_id", "name", "type", "additional_contact_list_id"}
            if watched.intersection(vals):
                for record in self:
                    if record.partner_id or record.additional_contact_list_id:
                        record._additional_contacts_ensure_list()
                    elif record.additional_contact_list_id:
                        record._additional_contacts_refresh_link()
        return result
