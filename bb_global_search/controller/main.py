from odoo import http
from odoo.http import request


class CrmController(http.Controller):
    @http.route('/company/get_search_models', type='json', auth='user', methods=['GET', 'POST'])
    def get_company_search_models(self):
        company = request.env.company
        models = [
            {"name": model_id.name, "model": model_id.model}
            for model_id in company.global_search_model_ids
        ]
        return {
            "models": models,
            "limit_per_group": company.global_search_limit_per_group or 0,
            "limit_total": company.global_search_limit_total or 0,
        }
