# Copyright 2026 Keith Brandenburg
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

"""Install-time defaults for OCA auditlog.

This module intentionally avoids logging reads because read logging is usually
very noisy. It creates rules only for models already present in the database, so
it can be installed on light or heavy Odoo instances without requiring every app.
"""

COMMON_AUDIT_MODELS = [
    # Core business/contact data
    "res.partner",
    "res.users",
    "product.template",
    "product.product",
    # CRM / sales flow
    "crm.lead",
    "sale.order",
    # Project / job workflow
    "project.project",
    "project.task",
    "account.analytic.line",  # timesheets
    # Accounting documents. Avoid account.move.line by default: too noisy.
    "account.move",
    "account.payment",
    "account.bank.statement",
    "account.bank.statement.line",
    # Purchasing / inventory if installed
    "purchase.order",
    "stock.picking",
    "stock.move",
    # HR if installed
    "hr.employee",
    "hr.contract",
    "hr.expense",
    # Website / lead capture / appointments if installed
    "calendar.event",
    "event.event",
    # DMS / documents if installed
    "dms.directory",
    "dms.file",
    # Helpdesk / maintenance / field service style apps if installed
    "helpdesk.ticket",
    "maintenance.request",
    "fsm.order",
]


def _ensure_rule(env, model_name):
    IrModel = env["ir.model"].sudo()
    Rule = env["auditlog.rule"].sudo()

    model = IrModel.search([("model", "=", model_name)], limit=1)
    if not model:
        return False

    existing = Rule.search([("model_id", "=", model.id)], limit=1)
    vals = {
        "name": f"Audit {model.name}",
        "model_id": model.id,
        "log_read": False,
        "log_create": True,
        "log_write": True,
        "log_unlink": True,
        "log_export_data": True,
        "log_type": "full",
        "capture_record": True,
    }

    if existing:
        # Do not force state back/forth unnecessarily, but make sure the rule
        # has the safety defaults wanted for this deployment style.
        existing.write(vals)
        rule = existing
    else:
        rule = Rule.create(vals)

    if rule.state != "subscribed":
        rule.subscribe()
    return True


def post_init_hook(env):
    """Create common audit rules for installed models."""
    for model_name in COMMON_AUDIT_MODELS:
        _ensure_rule(env, model_name)
