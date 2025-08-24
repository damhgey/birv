# -*- coding: utf-8 -*-
{
    "name": "clubcloud™ Brivo Integration",
    "version": "18.0.0.1",
    "website": "http://www.clubcloud.com",
    'author': 'Ready Element LLC',
    'maintainer': 'Ready Element LLC',
    'contributors': ["Ready Element LLC"],

    "depends": [
        "web",
        "ksc_club_cloud"
    ],
    "license": "Other proprietary",
    "category": "sales",

    "summary": """Adds models and views for Brivo integration""",
    'data': [
        # Security
        'security/ir.model.access.csv',
        # Wizards
        'wizard/assign_brivo_group_wizard.xml',
        'wizard/manage_suspended_status_wizard.xml',
        # Views
        'views/club_system_settings.xml',
        'views/sale_order_template.xml',
        'views/res_partner.xml',
        # Crons
        'data/cron/cron_sync_brivo_groups.xml'
    ],
    "assets": {},
    'installable': True,
    'auto_install': False,
    'application': False,    
}
