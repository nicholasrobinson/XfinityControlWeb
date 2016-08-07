import keyring
import sys
import re
from xfinity_control_web.xfinity_control import XfinityControl

KEYCHAIN_KEY = "XfinityControlWeb"
KEYCHAIN_SUBKEY = "credentials"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print sys.argv
        print "No channel argument specified."
        sys.exit()

    channel = sys.argv[1]

    credentials = keyring.get_password(KEYCHAIN_KEY, KEYCHAIN_SUBKEY)
    if credentials is None:
        print "Please setup keychain."
        sys.exit()
    else:
        username, password = credentials.split(":", 1)

    xfinity_control = XfinityControl(username, password)
    if re.match(r"^\d+$", channel):
        xfinity_control.change_channel(channel)
        print "Sent channel: %s" % channel
    else:
        for channel_name, channel_number in xfinity_control.channel_map.iteritems():
            if channel_name.lower().startswith(channel):
                xfinity_control.change_channel(channel_number)
                print "Sent channel: %s (%d)" % (channel_name, channel_number)
                sys.exit()
        print "Invalid channel. Please try again."
