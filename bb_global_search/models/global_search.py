# -*- coding: utf-8 -*-

import logging

from odoo import api, models
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class Base(models.AbstractModel):
    _inherit = "base"

    @api.model
    def bb_global_search(self, name="", operator="ilike", limit=8):
        """Search records for the bb_global_search navbar widget.

        This intentionally does not override normal name_search() behavior.
        Only the navbar search calls this method. Enhanced behavior is provided
        for selected business models; all other selected models fall back to
        Odoo's normal name_search().
        """
        query = (name or "").strip()
        if not query:
            return []

        # Two-character searches are reserved for exact state-code matching on
        # supported enhanced models. Avoid broad "AL"/"MS" searches everywhere.
        if len(query) < 3 and not (len(query) == 2 and query.isalpha()):
            return []

        limit = self._bb_normalize_limit(limit)

        try:
            if self._name == "res.partner":
                return self._bb_search_res_partner(query, operator, limit)

            if self._name == "crm.lead":
                return self._bb_search_crm_lead(query, operator, limit)

            if self._name == "account.move":
                return self._bb_search_account_move(query, operator, limit)

            if self._name == "project.project":
                return self._bb_search_project_project(query, operator, limit)

            if self._name == "hr.employee":
                return self._bb_search_hr_employee(query, operator, limit)

            if len(query) < 3:
                return []
            return [
                self._bb_result_tuple(
                    record_id,
                    display_name,
                    match_info="",
                    label=self._description or self._name,
                    group=self._description or self._name,
                    priority=500,
                )
                for record_id, display_name in self.name_search(
                    name=query,
                    operator=operator,
                    limit=limit or None,
                )
            ]
        except Exception:
            _logger.exception("Global search failed for model %s", self._name)
            return []

    @api.model
    def _bb_search_res_partner(self, query, operator="ilike", limit=8):
        state_code_only = len(query) == 2 and query.isalpha()
        fields = self._bb_partner_match_fields()

        if state_code_only:
            terms = self._bb_valid_terms([("state_id.code", "=ilike", query)])
        else:
            terms = self._bb_terms_from_fields(query, operator, fields)
            terms.extend(self._bb_phone_terms(query))

        records = self._bb_search_records(terms, limit=limit)
        return self._bb_format_global_search_results(
            records,
            query,
            fields,
            label_func=lambda record: self._bb_partner_label(record),
            default_group="Contacts",
        )

    @api.model
    def _bb_search_crm_lead(self, query, operator="ilike", limit=8):
        state_code_only = len(query) == 2 and query.isalpha()
        fields = self._bb_crm_lead_match_fields()

        if state_code_only:
            terms = self._bb_valid_terms([
                ("state_id.code", "=ilike", query),
                ("partner_id.state_id.code", "=ilike", query),
            ])
        else:
            terms = self._bb_terms_from_fields(query, operator, fields)
            terms.extend(self._bb_phone_terms(query))
            terms.extend(self._bb_related_partner_phone_terms(query))

        records = self._bb_search_records(terms, limit=limit)
        return self._bb_format_global_search_results(
            records,
            query,
            fields,
            label_func=lambda record: "Opportunity" if record.type == "opportunity" else "Lead",
            group_func=lambda record: "Opportunities" if record.type == "opportunity" else "Leads",
        )

    @api.model
    def _bb_search_account_move(self, query, operator="ilike", limit=8):
        if "move_type" not in self._fields:
            return []

        state_code_only = len(query) == 2 and query.isalpha()
        fields = self._bb_account_move_match_fields()

        if state_code_only:
            terms = self._bb_valid_terms([
                ("partner_id.state_id.code", "=ilike", query),
            ])
        else:
            terms = self._bb_terms_from_fields(query, operator, fields)
            terms.extend(self._bb_related_partner_phone_terms(query))

        invoice_domain = [
            ("move_type", "in", [
                "out_invoice",
                "out_refund",
                "in_invoice",
                "in_refund",
                "out_receipt",
                "in_receipt",
            ])
        ]
        records = self._bb_search_records(terms, extra_domain=invoice_domain, limit=limit)
        return self._bb_format_global_search_results(
            records,
            query,
            fields,
            label_func=lambda record: self._bb_account_move_label(record),
            group_func=lambda record: "Invoices / Bills",
        )

    @api.model
    def _bb_search_project_project(self, query, operator="ilike", limit=8):
        state_code_only = len(query) == 2 and query.isalpha()
        fields = self._bb_project_project_match_fields()

        if state_code_only:
            terms = self._bb_valid_terms([
                ("partner_id.state_id.code", "=ilike", query),
            ])
        else:
            terms = self._bb_terms_from_fields(query, operator, fields)
            terms.extend(self._bb_related_partner_phone_terms(query))

        records = self._bb_search_records(terms, limit=limit)
        return self._bb_format_global_search_results(
            records,
            query,
            fields,
            default_label="Project",
            default_group="Projects",
        )

    @api.model
    def _bb_search_hr_employee(self, query, operator="ilike", limit=8):
        # Employee searches are intentionally conservative and only run when
        # hr.employee is selected in the normal module settings. Do not search
        # private/personal fields here.
        if len(query) < 3:
            return []

        fields = self._bb_hr_employee_match_fields()
        terms = self._bb_terms_from_fields(query, operator, fields)
        terms.extend(self._bb_phone_field_terms(query, ["work_phone", "mobile_phone"]))

        records = self._bb_search_records(terms, limit=limit)
        return self._bb_format_global_search_results(
            records,
            query,
            fields,
            label_func=lambda record: self._bb_employee_label(record),
            default_group="Employees",
        )

    @api.model
    def _bb_search_records(self, terms, extra_domain=None, limit=8):
        if not terms:
            return self.browse()
        search_domain = expression.OR([[term] for term in terms])
        domain = expression.AND([extra_domain or [], search_domain])
        return self.search(domain, limit=limit)

    @api.model
    def _bb_terms_from_fields(self, query, operator, match_fields):
        terms = []
        for field_info in match_fields:
            if len(field_info) > 2 and field_info[2] == "phone":
                continue
            field_path = field_info[0]
            terms.append((field_path, operator, query))
        return self._bb_valid_terms(terms)

    @api.model
    def _bb_phone_terms(self, query):
        digits = "".join(ch for ch in query if ch.isdigit())
        if len(digits) < 3:
            return []

        if "phone_mobile_search" in self._fields:
            return [("phone_mobile_search", "ilike", digits)]

        terms = []
        for field in ("phone", "mobile"):
            if field in self._fields:
                terms.append((field, "ilike", query))
                if digits != query:
                    terms.append((field, "ilike", digits))
        return terms

    @api.model
    def _bb_phone_field_terms(self, query, field_names):
        digits = "".join(ch for ch in query if ch.isdigit())
        if len(digits) < 3:
            return []

        terms = []
        for field_name in field_names:
            if field_name in self._fields:
                terms.append((field_name, "ilike", query))
                if digits != query:
                    terms.append((field_name, "ilike", digits))
        return terms

    @api.model
    def _bb_related_partner_phone_terms(self, query):
        partner_ids = self._bb_partner_ids_matching_phone(query, limit=200)
        if partner_ids and self._bb_field_path_exists("partner_id"):
            return [("partner_id", "in", partner_ids)]
        return []

    @api.model
    def _bb_partner_ids_matching_phone(self, query, limit=200):
        digits = "".join(ch for ch in query if ch.isdigit())
        if len(digits) < 3 or not self.env.registry.get("res.partner"):
            return []

        partner_model = self.env["res.partner"]
        if "phone_mobile_search" not in partner_model._fields:
            return []

        partners = partner_model.search([("phone_mobile_search", "ilike", digits)], limit=limit)
        return partners.ids

    @api.model
    def _bb_format_global_search_results(
        self,
        records,
        query,
        match_fields,
        default_label=None,
        default_group=None,
        label_func=None,
        group_func=None,
    ):
        scored = []
        for record in records:
            match_info, priority = self._bb_match_detail(record, query, match_fields)
            label = label_func(record) if label_func else (default_label or self._description or self._name)
            group = group_func(record) if group_func else (default_group or label)
            scored.append((priority, record, match_info, label, group))

        scored.sort(key=lambda item: (item[0], (item[1].display_name or "").lower(), item[1].id))
        return [
            self._bb_result_tuple(
                record.id,
                record.display_name,
                match_info=match_info,
                label=label,
                group=group,
                priority=priority,
            )
            for priority, record, match_info, label, group in scored
        ]

    @api.model
    def _bb_result_tuple(self, record_id, display_name, match_info="", label="", group="", priority=500):
        return (record_id, display_name, match_info or "", label or "", group or label or "", priority)

    @api.model
    def _bb_partner_match_fields(self):
        return [
            ("name", "Name", "text", 10),
            ("email", "Email", "email", 40),
            ("phone", "Phone", "phone", 50),
            ("mobile", "Mobile", "phone", 50),
            ("ref", "Reference", "text", 60),
            ("vat", "Tax ID", "text", 65),
            ("city", "City", "text", 80),
            ("zip", "ZIP", "text", 80),
            ("state_id.code", "State", "state", 82),
            ("state_id.name", "State", "text", 84),
            ("street", "Street", "text", 100),
            ("street2", "Street 2", "text", 105),
        ]

    @api.model
    def _bb_crm_lead_match_fields(self):
        return [
            ("name", "Name", "text", 10),
            ("partner_name", "Company", "text", 20),
            ("contact_name", "Contact", "text", 25),
            ("email_from", "Email", "email", 40),
            ("phone", "Phone", "phone", 50),
            ("mobile", "Mobile", "phone", 50),
            ("partner_id.name", "Customer", "text", 55),
            ("partner_id.email", "Customer Email", "email", 58),
            ("partner_id.phone", "Customer Phone", "phone", 60),
            ("partner_id.mobile", "Customer Mobile", "phone", 60),
            ("partner_id.ref", "Customer Reference", "text", 66),
            ("partner_id.vat", "Customer Tax ID", "text", 68),
            ("city", "City", "text", 80),
            ("zip", "ZIP", "text", 80),
            ("state_id.code", "State", "state", 82),
            ("state_id.name", "State", "text", 84),
            ("street", "Street", "text", 100),
            ("street2", "Street 2", "text", 105),
            ("partner_id.city", "Customer City", "text", 110),
            ("partner_id.zip", "Customer ZIP", "text", 110),
            ("partner_id.state_id.code", "Customer State", "state", 112),
            ("partner_id.state_id.name", "Customer State", "text", 114),
            ("partner_id.street", "Customer Street", "text", 130),
            ("partner_id.street2", "Customer Street 2", "text", 135),
        ]

    @api.model
    def _bb_account_move_match_fields(self):
        return [
            ("name", "Number", "text", 10),
            ("ref", "Reference", "text", 12),
            ("payment_reference", "Payment Reference", "text", 14),
            ("invoice_origin", "Invoice Origin", "text", 18),
            ("partner_id.name", "Customer/Vendor", "text", 30),
            ("partner_id.email", "Customer/Vendor Email", "email", 45),
            ("partner_id.phone", "Customer/Vendor Phone", "phone", 55),
            ("partner_id.mobile", "Customer/Vendor Mobile", "phone", 55),
            ("partner_id.ref", "Customer/Vendor Reference", "text", 62),
            ("partner_id.vat", "Customer/Vendor Tax ID", "text", 64),
            ("partner_id.city", "Customer/Vendor City", "text", 100),
            ("partner_id.zip", "Customer/Vendor ZIP", "text", 100),
            ("partner_id.state_id.code", "Customer/Vendor State", "state", 102),
            ("partner_id.state_id.name", "Customer/Vendor State", "text", 104),
            ("partner_id.street", "Customer/Vendor Street", "text", 120),
            ("partner_id.street2", "Customer/Vendor Street 2", "text", 125),
        ]

    @api.model
    def _bb_project_project_match_fields(self):
        return [
            ("name", "Project", "text", 10),
            ("partner_id.name", "Customer", "text", 30),
            ("partner_id.email", "Customer Email", "email", 45),
            ("partner_id.phone", "Customer Phone", "phone", 55),
            ("partner_id.mobile", "Customer Mobile", "phone", 55),
            ("partner_id.ref", "Customer Reference", "text", 62),
            ("partner_id.vat", "Customer Tax ID", "text", 64),
            ("partner_id.city", "Customer City", "text", 100),
            ("partner_id.zip", "Customer ZIP", "text", 100),
            ("partner_id.state_id.code", "Customer State", "state", 102),
            ("partner_id.state_id.name", "Customer State", "text", 104),
            ("partner_id.street", "Customer Street", "text", 120),
            ("partner_id.street2", "Customer Street 2", "text", 125),
        ]

    @api.model
    def _bb_hr_employee_match_fields(self):
        return [
            ("name", "Name", "text", 10),
            ("work_email", "Work Email", "email", 40),
            ("work_phone", "Work Phone", "phone", 50),
            ("mobile_phone", "Mobile Phone", "phone", 50),
            ("job_title", "Job Title", "text", 60),
            ("department_id.name", "Department", "text", 70),
            ("employee_type", "Employee Type", "selection", 80),
        ]

    @api.model
    def _bb_match_detail(self, record, query, match_fields):
        query = (query or "").strip()
        query_lower = query.lower()
        query_digits = "".join(ch for ch in query if ch.isdigit())
        state_code_only = len(query) == 2 and query.isalpha()

        best = (999, "")
        for field_info in match_fields:
            field_path = field_info[0]
            label = field_info[1]
            match_type = field_info[2] if len(field_info) > 2 else "text"
            base_priority = field_info[3] if len(field_info) > 3 else 500

            value = self._bb_read_field_path(record, field_path)
            if value in (False, None, ""):
                continue

            value_text = str(value)
            value_lower = value_text.lower()
            matched = False
            priority = base_priority

            if match_type == "phone" and len(query_digits) >= 3:
                value_digits = "".join(ch for ch in value_text if ch.isdigit())
                if query_digits in value_digits:
                    matched = True
                    priority = base_priority

            elif match_type == "state" and state_code_only:
                if query_lower == value_lower:
                    matched = True
                    priority = 5

            elif match_type == "selection":
                field = record._fields.get(field_path)
                selection_label = self._bb_selection_label(record, field_path, value_text)
                selection_lower = selection_label.lower()
                if query_lower and (query_lower in value_lower or query_lower in selection_lower):
                    matched = True
                    if value_lower == query_lower or selection_lower == query_lower:
                        priority = min(priority, 1)
                    elif value_lower.startswith(query_lower) or selection_lower.startswith(query_lower):
                        priority = min(priority, 3)
                    value_text = selection_label

            elif query_lower and query_lower in value_lower:
                matched = True
                if value_lower == query_lower:
                    priority = min(priority, 1)
                elif value_lower.startswith(query_lower):
                    priority = min(priority, 3)

            if matched:
                detail = self._bb_format_match_label(label, value_text)
                if priority < best[0]:
                    best = (priority, detail)

        return best[1], best[0]

    @api.model
    def _bb_partner_label(self, record):
        company_type = getattr(record, "company_type", False)
        if company_type == "company":
            return "Company"
        if company_type == "person":
            return "Individual"
        return "Contact"

    @api.model
    def _bb_employee_label(self, record):
        return self._bb_selection_label(record, "employee_type", "Employee")

    @api.model
    def _bb_selection_label(self, record, field_name, fallback=""):
        if field_name not in record._fields:
            return fallback or ""
        value = record[field_name]
        if not value:
            return fallback or ""
        field = record._fields[field_name]
        selection = field.selection
        if isinstance(selection, str):
            selection_method = getattr(record, selection, None)
            selection = selection_method() if selection_method else []
        elif callable(selection):
            selection = selection(record)
        return dict(selection or []).get(value, fallback or str(value))

    @api.model
    def _bb_account_move_label(self, record):
        return {
            "out_invoice": "Customer Invoice",
            "in_invoice": "Vendor Bill",
            "out_refund": "Customer Credit Note",
            "in_refund": "Vendor Credit Note",
            "out_receipt": "Sales Receipt",
            "in_receipt": "Purchase Receipt",
        }.get(record.move_type, "Journal Entry")

    @api.model
    def _bb_format_match_label(self, label, value):
        value = " ".join(str(value).split())
        if len(value) > 80:
            value = value[:77] + "..."
        return f"Matched {label}: {value}"

    @api.model
    def _bb_read_field_path(self, record, field_path):
        value = record
        for part in field_path.split("."):
            if not value:
                return False
            value = value[part]
        if hasattr(value, "display_name"):
            return value.display_name
        return value

    @api.model
    def _bb_valid_terms(self, terms):
        return [term for term in terms if self._bb_field_path_exists(term[0])]

    @api.model
    def _bb_field_path_exists(self, field_path):
        model = self
        parts = field_path.split(".")
        for index, part in enumerate(parts):
            field = model._fields.get(part)
            if not field:
                return False
            if index == len(parts) - 1:
                return True
            comodel = getattr(field, "comodel_name", None)
            if not comodel or not self.env.registry.get(comodel):
                return False
            model = self.env[comodel]
        return True

    @api.model
    def _bb_normalize_limit(self, limit):
        try:
            limit = int(limit or 0)
        except (TypeError, ValueError):
            limit = 0
        return limit if limit > 0 else False
