from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _timesheet_create_project_prepare_values(self):
        values = super()._timesheet_create_project_prepare_values()
        order = self.order_id
        if order.additional_contact_list_id and not values.get("additional_contact_list_id"):
            values["additional_contact_list_id"] = order.additional_contact_list_id.id
        return values

    def _timesheet_create_project(self):
        project = super()._timesheet_create_project()
        if project and self.order_id.additional_contact_list_id and not project.additional_contact_list_id:
            project.additional_contact_list_id = self.order_id.additional_contact_list_id.id
            project._additional_contacts_ensure_list()
        return project
