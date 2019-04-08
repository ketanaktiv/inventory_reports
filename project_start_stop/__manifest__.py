# -*- coding: utf-8 -*-
##########################################################################
# 2010-2017 Webkul.
#
# NOTICE OF LICENSE
#
# All right is reserved,
# Please go through this link for complete license : https://store.webkul.com/license.html
#
# DISCLAIMER
#
# Do not edit or add to this file if you wish to upgrade this module to newer
# versions in the future. If you wish to customize this module for your
# needs please refer to https://store.webkul.com/customisation-guidelines/ for more information.
#
# @Author        : Webkul Software Pvt. Ltd. (<support@webkul.com>)
# @Copyright (c) : 2010-2017 Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# @License       : https://store.webkul.com/license.html
#
##########################################################################

{
    "name": "Project Task Start Stop",
    "summary":  "Project Task Start Stop",
    "category":  "Project Management",
    "version":  "1.0.0",
    "sequence":  1,
    "author":  "Webkul Software Pvt. Ltd.",
    "license":  "Other proprietary",
    'website': 'http://www.webkul.com',
    "description": """
        Project Task Start Stop.
    """,
    "live_test_url": 'http://odoodemo.webkul.com/?module=project_start_stop&version=11.0',
    'depends': ['project', 'hr_timesheet', 'wk_wizard_messages'],
    'data': [
        'wizard/work_log_wizard_view.xml',
        'security/project_timesheet_security.xml',
        'security/ir.model.access.csv',
        'views/project_timesheet_view.xml',
        'views/task_view.xml',
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "price": 25,
    "currency": 'EUR',
    "pre_init_hook": "pre_init_check",
    "images": ['static/description/Banner.png'],


}
