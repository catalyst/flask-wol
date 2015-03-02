#!/usr/bin/env python

"""
Tiny Flask web application to send Wake-on-LAN packets. Requires `fping' binary to be installed in /usr/bin.

Michael Fincham <michael.fincham@catalyst.net.nz>.

This file is licensed under the GNU General Public License version 3.
"""

import socket
import os

from netaddr import EUI, IPAddress
from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

def send_magic_packet(destination_mac, destination_ip='255.255.255.255', destination_port=9):
    """
    Send a Wake-on-LAN magic packet to the given destination IP and MAC addresses
    """

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # WoL magic packet is six bytes of 0xFF then the MAC repeated 16 times
    return sock.sendto('\xff' * 6 + EUI(destination_mac).packed * 16, (str(IPAddress(destination_ip)), int(destination_port)))

def send_ping(destination_ip):
    """
    Send a single ping packet to the IP and return True if there is a response.
    """

    return os.system('/usr/bin/fping -q -c 1 -t 100 %i' % int(IPAddress(destination_ip))) == 0

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/magic-packet', methods=['POST'])
def magic_packet():
    """
    POST /magic-packet

    mac=ab:ab:ab:ab:ab:ab&ip=192.0.2.1&port=9

    {"status": "success"}
    """
    try:
        return jsonify(
            status='success' if send_magic_packet(
                request.form['mac'],
                request.form.get('ip', '255.255.255.255'),
                request.form.get('port', 9),
            ) else 'failure')
    except:
        return jsonify(status='error')

@app.route('/ping/<address>', methods=['GET'])
def ping(address=None):
    """
    GET /ping/192.0.2.1

    {"status": "down"}
    """

    try:
        return jsonify(status='up' if send_ping(address) else 'down')
    except:
        return jsonify(status='error')

if __name__ == '__main__':
    app.run()
