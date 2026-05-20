from odoo import models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    def _prepare_opportunity_quotation_context(self):
        context = super()._prepare_opportunity_quotation_context()
        self.ensure_one()
        if not self.additional_contact_list_id:
            self._additional_contacts_ensure_list()
        if self.additional_contact_list_id:
            context["default_additional_contact_list_id"] = self.additional_contact_list_id.id
        return context
