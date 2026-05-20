from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    global_search_model_ids = fields.Many2many(
        "ir.model",
        related="company_id.global_search_model_ids",
        readonly=False,
    )
    global_search_limit_per_group = fields.Integer(
        related="company_id.global_search_limit_per_group",
        readonly=False,
    )
    global_search_limit_total = fields.Integer(
        related="company_id.global_search_limit_total",
        readonly=False,
    )
