from odoo import api, models


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["sale.order", "additional.contact.mixin"]

    def _additional_contacts_get_origin_partner(self):
        self.ensure_one()
        return self.partner_id

    def _additional_contacts_make_list_name(self):
        self.ensure_one()
        return self._additional_contacts_sale_context_name() or self.name or super()._additional_contacts_make_list_name()

    def _additional_contacts_sale_context_name(self):
        self.ensure_one()
        if "opportunity_id" in self._fields and self.opportunity_id:
            return self.opportunity_id.name
        if "project_ids" in self._fields and self.project_ids:
            return self.project_ids[:1].name
        return self.partner_id.display_name if self.partner_id else False

    def _additional_contacts_link_label(self):
        self.ensure_one()
        context_name = self._additional_contacts_sale_context_name()
        if context_name:
            return "Sales Order: %s - %s" % (context_name, self.name or "New")
        return "Sales Order: %s" % (self.name or self.display_name)

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
            watched = {"partner_id", "name", "additional_contact_list_id", "opportunity_id"}
            if watched.intersection(vals):
                for record in self:
                    if record.partner_id or record.additional_contact_list_id:
                        record._additional_contacts_ensure_list()
        return result
