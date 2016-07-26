import getpass
import sys
from xfinity_control_web.xfinity_control import XfinityControl, XfinityLoginException, XfinityApiException
from xfinity_control_web.xfinity_control_server import XfinityControlServer


if __name__ == "__main__":
    if "help" in sys.argv:
        print "Usage: python . [cli]"
        sys.exit()

    print "Enter xfinity credentials."
    username = raw_input("Username: ")
    password = getpass.getpass()
    try:
        xfinity_control = XfinityControl(username, password)
        if "cli" in sys.argv:
            while True:
                try:
                    param = raw_input("Enter channel number:")
                    xfinity_control.change_channel(param)
                except XfinityApiException:
                    print "API interaction failed: Please try again later."
                    sys.exit()
                except KeyboardInterrupt:
                    print ''
                    sys.exit()
        else:
            xfinity_control_server = XfinityControlServer(xfinity_control)
            print "HTTP server listening on http://%s:%d" % (
                XfinityControlServer.SERVER_ADDRESS if XfinityControlServer.SERVER_ADDRESS != "" else "localhost",
                XfinityControlServer.SERVER_PORT)
            try:
                xfinity_control_server.serve_forever()
            except KeyboardInterrupt:
                xfinity_control_server.socket.close()
                sys.exit()
    except XfinityLoginException:
        print "Authentication failed: Please check your credentials."
        sys.exit()
