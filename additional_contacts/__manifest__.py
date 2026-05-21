{
    "name": "Additional Contacts",
    "summary": "Shared additional contact lists with per-record roles and involvement tracking",
    "version": "18.0.1.0.1",
    "license": "AGPL-3",
    "category": "Contacts",
    "author": "Keith Brandenburg",
    "website": "https://www.windweaver.org",
    "depends": ["contacts"],
    "data": [
        "security/ir.model.access.csv",
        "data/additional_contact_role_data.xml",
        "views/additional_contact_role_views.xml",
        "views/additional_contact_settings_views.xml",
    ],
    "installable": True,
    "application": False,
}
