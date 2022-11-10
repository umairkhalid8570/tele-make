
import re
import io
import json
import operator
import logging
from tele.applets.web.controllers.main import ExportFormat,serialize_exception, ExportXlsxWriter
from tele.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import datetime
from tele import http
from tele.http import content_disposition, request
from tele.tools import pycompat
from ..common_lib.tele_date_filter_selections import tele_get_date, tele_convert_into_utc, tele_convert_into_local
import os
import pytz
_logger = logging.getLogger(__name__)


class TeleListExport(http.Controller):

    def base(self, data):
        params = json.loads(data)
        # header,list_data = operator.itemgetter('header','chart_data')(params)
        header, list_data, item_id, tele_export_boolean, context, params = operator.itemgetter('header', 'chart_data',
                                                                                             'tele_item_id',
                                                                                             'tele_export_boolean',
                                                                                             'context', 'params')(
            params)
        list_data = json.loads(list_data)
        if tele_export_boolean:
            item = request.env['tele_dashboard_ninja.item'].browse(int(item_id))
            tele_timezone = item._context.get('tz') or item.env.user.tz
            if not tele_timezone:
                tele_tzone = os.environ.get('TZ')
                if tele_tzone:
                    tele_timezone = tele_tzone
                elif os.path.exists('/etc/timezone'):
                    tele_tzone = open('/etc/timezone').read()
                    tele_timezone = tele_tzone[0:-1]
                    try:
                        datetime.now(pytz.timezone(tele_timezone))
                    except Exception as e:
                        _logger.info('Please set the local timezone')

                else:
                    _logger.info('Please set the local timezone')
            orderby = item.tele_sort_by_field.id
            sort_order = item.tele_sort_by_order
            tele_start_date = context.get('teleDateFilterStartDate', False)
            tele_end_date = context.get('teleDateFilterEndDate', False)
            teleDateFilterSelection = context.get('teleDateFilterSelection', False)
            if context.get('allowed_company_ids', False):
                item = item.with_context(allowed_company_ids=context.get('allowed_company_ids'))
            if item.tele_data_calculation_type == 'query':
                query_start_date = item.tele_query_start_date
                query_end_date = item.tele_query_end_date
                tele_query = str(item.tele_custom_query)
            if tele_start_date and tele_end_date:
                tele_start_date = datetime.datetime.strptime(tele_start_date,DEFAULT_SERVER_DATETIME_FORMAT)
                tele_end_date = datetime.datetime.strptime(tele_end_date,DEFAULT_SERVER_DATETIME_FORMAT)
            item = item.with_context(teleDateFilterStartDate=tele_start_date)
            item = item.with_context(teleDateFilterEndDate=tele_end_date)
            item = item.with_context(teleDateFilterSelection=teleDateFilterSelection)

            if item._context.get('teleDateFilterSelection', False):
                tele_date_filter_selection = item._context['teleDateFilterSelection']
                if tele_date_filter_selection == 'l_custom':
                    item = item.with_context(teleDateFilterStartDate=tele_start_date)
                    item = item.with_context(teleDateFilterEndDate=tele_end_date)
                    item = item.with_context(teleIsDefultCustomDateFilter=False)

            else:
                tele_date_filter_selection = item.tele_dashboard_ninja_board_id.tele_date_filter_selection
                item = item.with_context(teleDateFilterStartDate=item.tele_dashboard_ninja_board_id.tele_dashboard_start_date)
                item = item.with_context(teleDateFilterEndDate=item.tele_dashboard_ninja_board_id.tele_dashboard_end_date)
                item = item.with_context(teleDateFilterSelection=tele_date_filter_selection)
                item = item.with_context(teleIsDefultCustomDateFilter=True)

            if tele_date_filter_selection not in ['l_custom', 'l_none']:
                tele_date_data = tele_get_date(tele_date_filter_selection, request, 'datetime')
                item = item.with_context(teleDateFilterStartDate=tele_date_data["selected_start_date"])
                item = item.with_context(teleDateFilterEndDate=tele_date_data["selected_end_date"])

            item_domain = params.get('tele_domain_1', [])
            tele_chart_domain = item.tele_convert_into_proper_domain(item.tele_domain, item,item_domain)
            # list_data = item.tele_fetch_list_view_data(item,tele_chart_domain, tele_export_all=
            if list_data['type'] == 'ungrouped':
                list_data = item.tele_fetch_list_view_data(item, tele_chart_domain, tele_export_all=True)
            elif list_data['type'] == 'grouped':
                list_data = item.get_list_view_record(orderby, sort_order, tele_chart_domain, tele_export_all=True)
            elif item.tele_data_calculation_type == 'query':
                if tele_start_date or tele_end_date:
                    query_start_date = tele_start_date
                    query_end_date = tele_end_date
                tele_query_result = item.tele_get_list_query_result(tele_query, query_start_date, query_end_date, tele_offset=0,
                                                                tele_export_all=True)
                list_data = item.tele_format_query_result(tele_query_result)

        # chart_data['labels'].insert(0,'Measure')
        columns_headers = list_data['label']
        import_data = []

        for dataset in list_data['data_rows']:
            if not list_data['type'] == 'grouped':
                for count, index in enumerate(dataset['tele_column_type']):
                    if index == 'datetime':
                        tele_converted_date = False
                        date_string = dataset['data'][count]
                        if dataset['data'][count]:
                            tele_converted_date = tele_convert_into_local(datetime.datetime.strptime(date_string, '%m/%d/%y %H:%M:%S'),tele_timezone)
                        dataset['data'][count] = tele_converted_date
            for tele_count, val in enumerate(dataset['data']):
                if isinstance(val, (float, int)):
                    if val >= 0:
                        try:
                            tele_precision = item.sudo().env.ref('tele_dashboard_ninja.tele_dashboard_ninja_precision').digits
                        except Exception as e:
                            tele_precision = 2
                        dataset['data'][tele_count] = item.env['ir.qweb.field.float'].sudo().value_to_html(val,
                                                                             {'precision': tele_precision})
            import_data.append(dataset['data'])

        return request.make_response(self.from_data(columns_headers, import_data),
            headers=[('Content-Disposition',
                            content_disposition(self.filename(header))),
                     ('Content-Type', self.content_type)],
            # cookies={'fileToken': token}
                                     )


class TeleListExcelExport(TeleListExport, http.Controller):

    # Excel needs raw data to correctly handle numbers and date values
    raw_data = True

    @http.route('/tele_dashboard_ninja/export/list_xls', type='http', auth="user")
    @serialize_exception
    def index(self, data):
        return self.base(data)

    @property
    def content_type(self):
        return 'application/vnd.ms-excel'

    def filename(self, base):
        return base + '.xls'

    def from_data(self, fields, rows):
        with ExportXlsxWriter(fields, len(rows)) as xlsx_writer:
            for row_index, row in enumerate(rows):
                for cell_index, cell_value in enumerate(row):
                    xlsx_writer.write_cell(row_index + 1, cell_index, cell_value)

        return xlsx_writer.value


class TeleListCsvExport(TeleListExport, http.Controller):

    @http.route('/tele_dashboard_ninja/export/list_csv', type='http', auth="user")
    @serialize_exception
    def index(self, data):
        return self.base(data)

    @property
    def content_type(self):
        return 'text/csv;charset=utf8'

    def filename(self, base):
        return base + '.csv'

    def from_data(self, fields, rows):
        fp = io.BytesIO()
        writer = pycompat.csv_writer(fp, quoting=1)

        writer.writerow(fields)

        for data in rows:
            row = []
            for d in data:
                # Spreadsheet apps tend to detect formulas on leading =, + and -
                if isinstance(d, str)    and d.startswith(('=', '-', '+')):
                    d = "'" + d

                row.append(pycompat.to_text(d))
            writer.writerow(row)

        return fp.getvalue()
