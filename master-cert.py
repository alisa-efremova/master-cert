
import json
from os import environ
from requests import post
from http import HTTPStatus
from http.server import HTTPServer, BaseHTTPRequestHandler
from requestadapter import RequestAdapter
from responseadapter import ResponseAdapter

import rook

if __name__ == "__main__":

    rook.start(token='e2fe21957bb07aba7b222bd7ec9ef1ce2ba6b2c051e3d7120afaebdd2572d6fc')

DOCS_OPPWA_URL = "https://docs.oppwa.com/api-request"


class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        charset = self.headers.get_charset()
        if charset is None:
            charset = "utf-8"
        try:
            content_length = int(self.headers.get("content-length"))
        except (TypeError, ValueError):
            content_length = 0

        try:
            request_obj = json.loads(str(self.rfile.read(content_length), charset), encoding=charset)
        except json.JSONDecodeError as e:
            self.report_error(HTTPStatus.BAD_REQUEST, "Exception while parsing request", e)
            return

        response_obj = {"messageType": "pArs", "p_messageVersion": "1.0.5", "messageVersion": "2.1.0"}

        try:
            oppwa_request = RequestAdapter(request_obj).adapt_request()
        except Exception as e:
            self.report_error(HTTPStatus.BAD_REQUEST, "Exception while adapting request", e)
            return

        try:
            oppwa_response = post(url=DOCS_OPPWA_URL,
                                  data={"xmlData": oppwa_request, "params": {}, "ptype": "paypipe",
                                        "sendtolive": "test", "basicUser": "uuid", "basicPass": "payon"}).text
        except Exception as e:
            self.report_error(HTTPStatus.INTERNAL_SERVER_ERROR, "Exception while contacting OPPWA", e)
            return

        try:
            ResponseAdapter(oppwa_response, response_obj).adapt_response()
        except Exception as e:
            self.report_error(HTTPStatus.BAD_REQUEST, "Exception while adapting response", e)
            return

        content = json.dumps(response_obj).encode("utf-8")
        code = HTTPStatus.OK

        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", len(content))
        self.end_headers()
        self.wfile.write(content)

    def report_error(self, code, msg, e):
        self.log_error(msg + ": %s", format(e))
        self.send_error(code, msg, format(e))


port = int(environ["PORT"])
httpd = HTTPServer(("", port), HttpHandler)
print("Listening on port " + str(port))
httpd.serve_forever()
