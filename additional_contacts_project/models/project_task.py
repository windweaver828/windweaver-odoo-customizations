from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    additional_contact_list_id = fields.Many2one(
        "additional.contact.list",
        related="project_id.additional_contact_list_id",
        string="Project Additional Contact List",
        readonly=True,
    )
    additional_contact_line_ids = fields.Many2many(
        "additional.contact.line",
        "project_task_additional_contact_line_rel",
        "task_id",
        "line_id",
        string="Additional Contacts",
        domain="[('list_id', '=', additional_contact_list_id)]",
        help="Contacts from the project additional contact list that are relevant to this task.",
    )
