from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    additional_contact_partner_id = fields.Many2one(
        "res.partner",
        string="Additional Contacts Partner",
        compute="_compute_additional_contact_partner_id",
        readonly=True,
    )
    additional_contact_involvement_ids = fields.Many2many(
        "additional.contact.involvement",
        string="Involved In",
        compute="_compute_additional_contact_involvement_ids",
        readonly=True,
    )

    @api.depends("user_id", "user_id.partner_id")
    def _compute_additional_contact_partner_id(self):
        for employee in self:
            partner = False
            if "work_contact_id" in employee._fields and employee.work_contact_id:
                partner = employee.work_contact_id
            elif "address_home_id" in employee._fields and employee.address_home_id:
                partner = employee.address_home_id
            elif employee.user_id and employee.user_id.partner_id:
                partner = employee.user_id.partner_id
            employee.additional_contact_partner_id = partner

    @api.depends("additional_contact_partner_id")
    def _compute_additional_contact_involvement_ids(self):
        involvement_model = self.env["additional.contact.involvement"]
        for employee in self:
            if employee.additional_contact_partner_id:
                employee.additional_contact_involvement_ids = involvement_model.search([
                    ("partner_id", "=", employee.additional_contact_partner_id.id)
                ])
            else:
                employee.additional_contact_involvement_ids = False
