import os
import json
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import BaseRequestHandler
from xfinity_control_web.xfinity_control import XfinityApiException


class XfinityControlServer(HTTPServer):
    SERVER_ADDRESS = ""
    SERVER_PORT = 8081

    def __init__(self, xfinity_control):
        HTTPServer.__init__(
            self,
            (XfinityControlServer.SERVER_ADDRESS, XfinityControlServer.SERVER_PORT),
            XfinityRequestHandler(xfinity_control),
            True
        )


def XfinityRequestHandler(xfinity_control):
    class RequestHandler(BaseHTTPRequestHandler):
        def __init__(self, request, client_address, server):
            self.xfinity_control = xfinity_control
            BaseRequestHandler.__init__(self, request, client_address, server)

        def do_POST(self):
            if self.path == "/":
                content_len = int(self.headers.getheader('content-length', 0))
                post_body = self.rfile.read(content_len)
                try:
                    try:
                        self.xfinity_control.change_channel(int(post_body))
                    except ValueError:
                        raise XfinityApiException("Invalid channel number.")
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write("OK")
                except XfinityApiException:
                    self.send_response(520)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write("520 (Unknown Error)")
            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write("404 (Not Found)")

        def do_GET(self):
            if self.path == "/":
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'index.html'), "r") as index:
                    self.wfile.write(index.read().replace(
                        "var channelMap = {}",
                        "var channelMap = " + json.dumps(self.xfinity_control.channel_map))
                    )
            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write("404 (Not Found)")

    return RequestHandler
