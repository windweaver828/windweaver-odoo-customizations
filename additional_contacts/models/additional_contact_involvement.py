from odoo import fields, models, tools


class AdditionalContactInvolvement(models.Model):
    _name = "additional.contact.involvement"
    _description = "Additional Contact Involvement"
    _auto = False
    _order = "link_name, id"

    partner_id = fields.Many2one("res.partner", readonly=True)
    list_id = fields.Many2one("additional.contact.list", readonly=True)
    line_id = fields.Many2one("additional.contact.line", readonly=True)
    link_id = fields.Many2one("additional.contact.link", readonly=True)
    role_id = fields.Many2one("additional.contact.role", readonly=True)
    notes = fields.Text(readonly=True)
    res_model = fields.Char(readonly=True)
    res_id = fields.Integer(readonly=True)
    link_name = fields.Char(string="Record", readonly=True)
    model_description = fields.Char(string="Type", readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                SELECT
                    row_number() OVER (ORDER BY line.id, link.id) AS id,
                    line.partner_id AS partner_id,
                    line.list_id AS list_id,
                    line.id AS line_id,
                    link.id AS link_id,
                    line.role_id AS role_id,
                    line.notes AS notes,
                    link.res_model AS res_model,
                    link.res_id AS res_id,
                    link.name AS link_name,
                    link.model_description AS model_description
                FROM additional_contact_line line
                JOIN additional_contact_link link ON link.list_id = line.list_id
                WHERE link.active IS TRUE
            )
        """)

    def action_open_record(self):
        self.ensure_one()
        return self.link_id.action_open_record()
