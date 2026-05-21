{
    "name": "Global Search",
    "version": "18.0.0.1",
    "category": "Extra Tools",
    "summary": "Search Across Multiple Models from Navbar",
    "description": """
Global Search Across Models
===========================
This module allows users to search records across multiple models using a global search bar in the navbar.

Key Features:
-------------
- Select searchable models from Settings (res.config.settings)
- Add a search icon to the top navbar
- Search across selected models
- Navigate to form view directly from results
    """,
    "author": "Keith Brandenburg (Rewrote Original), Dhrushil Butani (Original Author)",
    "license": "AGPL-3",
    "website": "https://www.windweaver.org",
    "depends": ["base", "web"],
    'images': ['static/description/banner.png'],
    "data": [
        "views/res_config_settings_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "bb_global_search/static/src/css/global_search.css",
            "bb_global_search/static/src/js/global_search.js",
            "bb_global_search/static/src/xml/global_search.xml",
        ],
    },
    "installable": True,
    "application": True,
}
