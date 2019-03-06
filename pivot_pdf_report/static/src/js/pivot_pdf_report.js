odoo.define('pivot_pdf_report.PivotPDF', function (require) {
"use strict";
    var core = require('web.core');
    var framework = require('web.framework');
    var crash_manager = require('web.crash_manager');
    var ajax = require('web.ajax');
    var session = require('web.session');
    var PivotView = require('web.PivotController');
    var _t = core._t;
    var QWeb = core.qweb;

    PivotView.include({
        _downloadPDF: function () {
            var self = this;
            var table = this.model.exportData();
            if(table.measure_row.length + 1 > 256) {
                crash_manager.show_message(_t("For Excel compatibility, data cannot be exported if there are more than 256 columns.\n\nTip: try to flip axis, filter further or reduce the number of measures."));
                framework.unblockUI();
                return;
            }
            framework.blockUI();
            table.title = this.title;
            // ajax.jsonRpc('/web/pivot/export_pdf', 'call', {'data':JSON.stringify(table)});
            session.get_file({
                url: '/web/pivot/export_pdf',
                data: {data: JSON.stringify(table)},
                complete: framework.unblockUI,
                error: crash_manager.rpc_error.bind(crash_manager)
            });
        },

        pass_data: function(html_data){
            this.main_html = html_data;
        },

        _onButtonClick: function (event) {
            this._super(event);
            var $target = $(event.target);
            if ($target.hasClass('o_pdf_download')) {
                this._downloadPDF();
            }
        },

        // Passed current model in context
        renderButtons: function ($node) {
            if ($node) {
                var context = {measures: _.pairs(_.omit(this.measures, '__count')), model: this.modelName};
                this.$buttons = $(QWeb.render('PivotView.buttons', context));
                this.$buttons.click(this._onButtonClick.bind(this));
                this.$buttons.find('button').tooltip();

                this.$buttons.appendTo($node);
                this._updateButtons();
            }
        },
    });
});