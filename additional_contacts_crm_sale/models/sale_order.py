from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _additional_contacts_is_empty_line_replace(self, commands):
        if not isinstance(commands, list) or not commands:
            return False
        for command in commands:
            if not isinstance(command, (list, tuple)) or not command:
                return False
            operation = command[0]
            if operation == 5:
                continue
            if operation == 6 and len(command) > 2 and not command[2]:
                continue
            return False
        return True

    @api.model
    def _additional_contacts_ignore_empty_line_replace(self, vals):
        if self._additional_contacts_is_empty_line_replace(vals.get("additional_contact_line_ids")):
            vals.pop("additional_contact_line_ids", None)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            opportunity_id = vals.get("opportunity_id") or self.env.context.get("default_opportunity_id")
            if opportunity_id and not vals.get("additional_contact_list_id"):
                opportunity = self.env["crm.lead"].browse(opportunity_id).exists()
                if opportunity:
                    if not opportunity.additional_contact_list_id:
                        opportunity._additional_contacts_ensure_list()
                    if opportunity.additional_contact_list_id:
                        vals["additional_contact_list_id"] = opportunity.additional_contact_list_id.id
                        self._additional_contacts_ignore_empty_line_replace(vals)
        return super().create(vals_list)

    def write(self, vals):
        if (
            vals.get("opportunity_id")
            or vals.get("additional_contact_list_id")
            or any(order.opportunity_id or order.additional_contact_list_id for order in self)
        ):
            self._additional_contacts_ignore_empty_line_replace(vals)
        result = super().write(vals)
        if "opportunity_id" in vals and not self.env.context.get("skip_additional_contacts_sync"):
            for order in self:
                if order.opportunity_id and not order.additional_contact_list_id:
                    if not order.opportunity_id.additional_contact_list_id:
                        order.opportunity_id._additional_contacts_ensure_list()
                    if order.opportunity_id.additional_contact_list_id:
                        order.with_context(skip_additional_contacts_sync=True).write({
                            "additional_contact_list_id": order.opportunity_id.additional_contact_list_id.id,
                        })
                        order._additional_contacts_ensure_list()
        return result
