# -*- coding: utf-8 -*-

import logging

from odoo import api, models
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = "crm.lead"

    @api.model
    def bb_global_search(self, name="", operator="ilike", limit=8):
        """Search leads/opportunities for the global navbar search only.

        Odoo stores both leads and opportunities in crm.lead; the record type
        distinguishes them. This method searches both.
        """
        term = (name or "").strip()
        if len(term) < 2:
            return []

        if operator not in ("ilike", "like", "=", "=ilike"):
            operator = "ilike"

        limit = min(int(limit or 8), 20)

        fields = [
            "name",
            "partner_name",
            "contact_name",
            "email_from",
            "phone",
            "mobile",
            "street",
            "street2",
            "city",
            "zip",
            "partner_id.name",
            "partner_id.email",
            "partner_id.phone",
            "partner_id.mobile",
            "partner_id.street",
            "partner_id.street2",
            "partner_id.city",
            "partner_id.zip",
            "partner_id.ref",
        ]
        domains = []
        for field in fields:
            root = field.split(".", 1)[0]
            if root in self._fields:
                domains.append([(field, operator, term)])

        if not domains:
            return self.name_search(name=term, operator=operator, limit=limit)

        try:
            records = self.search(expression.OR(domains), limit=limit)
        except Exception as exc:
            _logger.warning("Global search failed for crm.lead: %s", exc)
            return []

        return [(record.id, record.display_name) for record in records]
