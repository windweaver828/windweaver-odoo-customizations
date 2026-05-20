{
    "name": "DMS File Description",
    "summary": "Adds editable descriptions to DMS files and displays them in DMS views",
    "version": "18.0.1.0.9",
    "category": "Document Management",
    "author": "Windweaver Customizations",
    "license": "AGPL-3",
    "depends": ["dms"],
    "assets": {
        "web.assets_backend": [
            "dms_file_description/static/src/js/dms_document_preview_description.esm.js",
            "dms_file_description/static/src/scss/dms_file_description.scss",
        ],
    },
    "installable": True,
    "application": False,
}
