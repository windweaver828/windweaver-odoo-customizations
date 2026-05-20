# -*- coding: utf-8 -*-

import logging

from odoo import api, models
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def bb_global_search(self, name="", operator="ilike", limit=8):
        """Search contacts/vendors/customers for the global navbar search only.

        This intentionally does not override name_search(), so normal Odoo
        Many2one dropdown behavior is unchanged.
        """
        term = (name or "").strip()
        if len(term) < 2:
            return []

        if operator not in ("ilike", "like", "=", "=ilike"):
            operator = "ilike"

        limit = min(int(limit or 8), 20)

        fields = [
            "name",
            "display_name",
            "email",
            "phone",
            "mobile",
            "ref",
            "street",
            "street2",
            "city",
            "zip",
            "vat",
        ]
        domains = [[(field, operator, term)] for field in fields if field in self._fields]
        if not domains:
            return self.name_search(name=term, operator=operator, limit=limit)

        try:
            records = self.search(expression.OR(domains), limit=limit)
        except Exception as exc:
            _logger.warning("Global search failed for res.partner: %s", exc)
            return []

        return [(record.id, record.display_name) for record in records]
