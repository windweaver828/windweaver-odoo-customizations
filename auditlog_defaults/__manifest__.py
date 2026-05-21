{
    "name": "Audit Log Defaults",
    "summary": "Seed common auditlog rules and keep 60 days of audit history",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "category": "Technical",
    "author": "Keith Brandenburg",
    "website": "https://www.windweaver.org",
    "depends": ["auditlog"],
    "data": [
        "data/ir_cron.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "application": False,
}
