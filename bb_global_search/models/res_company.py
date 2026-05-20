from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    global_search_model_ids = fields.Many2many("ir.model")
    global_search_limit_per_group = fields.Integer(
        string="Global Search Max Results Per Group",
        default=10,
        help="Maximum results shown per result group. Leave blank or set to 0 for no enforced group limit.",
    )
    global_search_limit_total = fields.Integer(
        string="Global Search Max Total Results",
        default=40,
        help="Maximum total results shown in the global search popup. Leave blank or set to 0 for no enforced total limit.",
    )
