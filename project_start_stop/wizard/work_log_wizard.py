
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

from odoo import api, fields, models
from odoo import tools, _

_logger = logging.getLogger(__name__)


class WorkLogWizard(models.TransientModel):
    _name = "work.log.wizard"
    _description = "Wizard For Work Log"

    @api.multi
    def _set_message(self):
        for obj in self:
            if obj.task_name:
                obj.message = "You are currently working on " + obj.task_name + " task."
            if obj.issue_name:
                obj.message = "You are currently working on " + obj.issue_name + " issue."

    task_work_log_id = fields.Many2one("account.analytic.line", string="Task Work Log")
    issue_work_log_id = fields.Many2one("account.analytic.line", string="Task Work Log")
    task_id = fields.Many2one("project.task", "Task")
    issue_id = fields.Many2one("project.issue", "Issue")
    task_name = fields.Char(string="Task Name", help="Task Name")
    issue_name = fields.Char(string="Issue Name", help="Issue Name")
    message = fields.Char(compute="_set_message", string='Week No')

    @api.multi
    def countinue(self):
        for obj in self:
            if obj.task_work_log_id:
                 obj.task_work_log_id.task_id.task_stop()
            if obj.issue_work_log_id:
                obj.issue_work_log_id.issue_id.issue_stop()
            if self._context.get('active_model') == 'project.task':
                if self._context.get('active_id') :
                        task = self.env["project.task"].browse(self._context.get('active_id'))
                        self.env["account.analytic.line"].task_start(task)
            if self._context.get('active_model') == 'project.issue':
                if self._context.get('active_id') :
                    issue = self.env["project.issue"].browse(self._context.get('active_id'))
                    self.env["account.analytic.line"].issue_start(issue)
        return {
                'type': 'ir.actions.client',
                'tag': 'reload',
        }

class WorkLogTimeWizard(models.TransientModel):
    _name = "work.log.time.wizard"
    _description = "Wizard For Work Log"

    @api.model
    def _set_task_id(self):
        if self._context.get('active_model') == 'project.task':
            return self._context.get('active_id')
        else :
            return False

    @api.model
    def _set_issue_id(self):
        if self._context.get('active_model') == 'project.issue':
            return self._context.get('active_id')
        else :
            return False

    task_id = fields.Many2one("project.task", string="Task")
    issue_id = fields.Many2one("project.issue", string="Issue")
    total_time = fields.Char(string="Total time spent")
    total_time_report = fields.Html(string="Time Log Report")

    @api.model
    def default_get(self, fields):
        res = super(WorkLogTimeWizard, self).default_get(fields)
        if self._context.get('time_report'):
            time_report = self._context.get('time_report')
            message="<table style='width:100%;background-color: #fff;border-collapse: separate;'><tr style='background-color: #36364B;color: white;'><th style='text-align:center;padding: 5px;'>S.no </th><th style='text-align:center;padding: 5px;'> Employee </th><th style='text-align:center;padding: 5px;'> Spent Time </th></tr>"
            count=1
            for key in time_report.keys():
                user_obj = self.env["res.users"].browse(key)
                message+='<tr>'
                message+="<td style='text-align:center; background-color: #eee;'> "+str(count)+".</td><td style='text-align:center; background-color: #eee;'>"+user_obj.name+"</td><td style='text-align:center; background-color: #eee;text-align:center;'>"+ time_report[key]  +"</td></td>"
                message+='</tr>'
                count+=1
            message+="</table>"
            res['total_time_report'] = message
        return res
