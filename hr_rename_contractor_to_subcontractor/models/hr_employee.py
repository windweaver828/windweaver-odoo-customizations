from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    # Keep the database value as "contractor" but display it as "Subcontractor".
    # Using selection_add avoids redefining the entire field, so future upstream
    # or third-party employee_type options are less likely to be accidentally lost.
    employee_type = fields.Selection(
        selection_add=[("contractor", "Subcontractor")],
    )
