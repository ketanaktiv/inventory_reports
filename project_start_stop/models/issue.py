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

import logging
import math
import time

from datetime import date
from datetime import datetime, timedelta
from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)
class ProjectIssue(models.Model):
    """ Inherit project.issue for providing additional feature to every issue."""

    _inherit = "project.issue"

    @api.multi
    def _last_update_date(self):
        """ Function for computed field 'last_update'."""
        for obj in self:
            date = datetime.strptime(obj.write_date, '%Y-%m-%d %H:%M:%S').date()
            str_date = date.strftime('%Y-%m-%d')
            obj.last_update = str_date


    last_update = fields.Date(compute="_last_update_date", string="Last Update Date", store=True)
    log_action = fields.Selection([("working", "Working"), ("not_working", "Not Working"), ("closed", "Closed")], string="Log Action", copy=False, default="not_working")
    last_start_time = fields.Datetime(string="Last Start Time", help="Shows latest work start time.")
    log_ids = fields.One2many("account.analytic.line", 'issue_id', string="Logs")
    create_uid = fields.Many2one("res.users")
    create_date = fields.Datetime("Creation Date", readonly=1)
    write_date = fields.Datetime("Update Date", readonly=1)

    @api.multi
    def stop_all_issue(self):
        if not self:
            objs = self.search([('user_id', '=', self._uid), ('log_action', '=', 'working')])
            objs.issue_stop()
        return True

    @api.multi
    def copy(self, default=None):
        issue_id = super(ProjectIssue, self).copy(default=default)
        if issue_id:
            issue_id.write({'log_action': 'not_working'})
        return issue_id

    @api.multi
    def issue_start(self):
        """ Function to start issue time log."""
        wiz = self.env["account.analytic.line"].issue_start(self)
        return wiz

    @api.multi
    def get_issue_time_duration(self):
        """ Function to calculate total time spent by employee on the issue."""
        res = self.env["account.analytic.line"].get_issue_time_duration(self.ids)
        return res

    @api.multi
    def issue_stop(self):
        """ Function to stop issue time log."""
        res = self.env["account.analytic.line"].issue_stop(self)
        return res

    @api.multi
    def write(self, vals):
        for obj in self:
            if obj.log_action == "working" and vals.get('user_id'):
                raise UserError(_("Currently, this issue is in working state. First stop the issue and then assign to other user."))
            if vals.get("stage_id", False):
                stage_obj = self.env["project.task.type"].browse(vals.get("stage_id"))
                if stage_obj and stage_obj.name.lower() in ["done", "cancel", 'cancelled']:
                    if obj.log_action == "working":
                        obj.issue_stop()
                    obj.log_action = "closed"
                elif obj.stage_id.name.lower() in ["done", "cancel", 'cancelled']:
                    obj.log_action = "not_working"
        return super(ProjectIssue, self).write(vals)
