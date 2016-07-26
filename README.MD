XfinityControlWeb by Nicholas Robinson

This project houses a fully functional and re-usable Python library for controlling your Comcast xfinity set top box. A web server and HTML/javascript user interface are provided as an example of how to leverage this library. This project was created for fun to allow me to control the television from any device with a web browser, but could easily be leveraged to integrate channel control into a home automation system.

To see it in action go here (sockets/cURL are disabled for safety):
http://www.nicholassavilerobinson.com/XfinityControlWeb/index.html

Requirements:
- Python

Installation:
- Download/Clone project folder
- sudo pip install -r requirements.txt

Running Web Server:
- python .

Running CLI:
- python . cli

Please let me know if you find this useful or come up with any novel implementations.

Enjoy!

Nicholas Robinson
me@nicholassavilerobinson.com

P.S. You 'could' host your XfinityControlWeb application on the public internet and control your set top box from anywhere. If you choose to go this route, please consider the security implications of potentially allowing anyone on the internet to control your TV.
