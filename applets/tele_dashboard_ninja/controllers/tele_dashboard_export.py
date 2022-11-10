import io
import json
import operator

from tele.applets.web.controllers.main import ExportFormat,serialize_exception

from tele import http
from tele.http import request
from tele.http import content_disposition,request


class TeleDashboardExport(http.Controller):

    def base(self, data):
        params = json.loads(data)
        header, dashboard_data = operator.itemgetter('header', 'dashboard_data')(params)
        return request.make_response(self.from_data(dashboard_data),
                                     headers=[('Content-Disposition',
                                               content_disposition(self.filename(header))),
                                              ('Content-Type', self.content_type)],
                                     # cookies={'fileToken': token}
                                     )


class TeleDashboardJsonExport(TeleDashboardExport, http.Controller):

    @http.route('/tele_dashboard_ninja/export/dashboard_json', type='http', auth="user")
    @serialize_exception
    def index(self, data):
        return self.base(data)

    @property
    def content_type(self):
        return 'text/csv;charset=utf8'

    def filename(self, base):
        return base + '.json'

    def from_data(self, dashboard_data):
        fp = io.StringIO()
        fp.write(json.dumps(dashboard_data))

        return fp.getvalue()

class TeleItemJsonExport(TeleDashboardExport, http.Controller):

    @http.route('/tele_dashboard_ninja/export/item_json', type='http', auth="user")
    @serialize_exception
    def index(self, data):
        data = json.loads(data)
        item_id = data["item_id"]
        data['dashboard_data'] = request.env['tele_dashboard_ninja.board'].tele_export_item(item_id)
        data = json.dumps(data)
        return self.base(data)

    @property
    def content_type(self):
        return 'text/csv;charset=utf8'

    def filename(self, base):
        return base + '.json'

    def from_data(self, dashboard_data):
        fp = io.StringIO()
        fp.write(json.dumps(dashboard_data))

        return fp.getvalue()
