import json
from collections import deque
import os
from odoo import http
from odoo.http import request
# from fpdf import FPDF, HTMLMixin
# from odoo.addons.web.controllers.main import content_disposition
from odoo.tools import ustr
from odoo.tools.misc import xlwt


# class HTML2PDF(FPDF, HTMLMixin):
#     pass


class PivotPdfReport(http.Controller):

    @http.route('/web/pivot/export_pdf', type='http', auth="user")
    def export_pdf(self, data, token):
        # data_dict = json.loads(data)
        # render_template = "pivot_pdf_report.report_inventory_move"

        # html = request.env['ir.ui.view'].render_template(
        #     render_template, {'header_data': data_dict['headers'],
        #                       'measure_data': data_dict['measure_row']})
        # html_data = html.decode("utf-8")
        # print(html_data)
        # pdf = HTML2PDF()
        # pdf.add_page()
        # pdf.write_html(html_data)
        # pdf.output('/tmp/html2pdf.pdf')
        # output_file = open("/tmp/html2pdf.pdf", "rb")
        # response = request.make_response(
        #     output_file,
        #     [('Content-Type', 'application/octet-stream'),
        #      ('Content-Disposition', content_disposition("sample" + '.pdf'))])
        # os.remove('/tmp/html2pdf.pdf')
        jdata = json.loads(data)
        nbr_measures = jdata['nbr_measures']
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet(jdata['title'])
        header_bold = xlwt.easyxf(
            "font: bold on; pattern: pattern solid, fore_colour gray25;")
        header_plain = xlwt.easyxf(
            "pattern: pattern solid, fore_colour gray25;")
        bold = xlwt.easyxf("font: bold on;")

        # Step 1: writing headers
        headers = jdata['headers']

        # x,y: current coordinates
        # carry: queue containing cell information when a cell has a >= 2 height
        #      and the drawing code needs to add empty cells below
        x, y, carry = 1, 0, deque()
        for i, header_row in enumerate(headers):
            worksheet.write(i, 0, '', header_plain)
            for header in header_row:
                while (carry and carry[0]['x'] == x):
                    cell = carry.popleft()
                    for i in range(nbr_measures):
                        worksheet.write(y, x + i, '', header_plain)
                    if cell['height'] > 1:
                        carry.append({'x': x, 'height': cell['height'] - 1})
                    x = x + nbr_measures
                style = header_plain if 'expanded' in header else header_bold
                for i in range(header['width']):
                    worksheet.write(
                        y, x + i, header['title'] if i == 0 else '', style)
                if header['height'] > 1:
                    carry.append({'x': x, 'height': header['height'] - 1})
                x = x + header['width']
            while (carry and carry[0]['x'] == x):
                cell = carry.popleft()
                for i in range(nbr_measures):
                    worksheet.write(y, x + i, '', header_plain)
                if cell['height'] > 1:
                    carry.append({'x': x, 'height': cell['height'] - 1})
                x = x + nbr_measures
            x, y = 1, y + 1

        # Step 2: measure row
        if nbr_measures > 1:
            worksheet.write(y, 0, '', header_plain)
            for measure in jdata['measure_row']:
                style = header_bold if measure['is_bold'] else header_plain
                worksheet.write(y, x, measure['measure'], style)
                x = x + 1
            y = y + 1

        # Step 3: writing data
        x = 0
        for row in jdata['rows']:
            worksheet.write(y, x, row['indent'] *
                            '     ' + ustr(row['title']), header_plain)
            for cell in row['values']:
                x = x + 1
                if cell.get('is_bold', False):
                    worksheet.write(y, x, cell['value'], bold)
                else:
                    worksheet.write(y, x, cell['value'])
            x, y = 0, y + 1

        import pdb
        pdb.set_trace()
        # return response
