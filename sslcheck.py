import ssl
import socket
import subprocess
from urlparse import urlparse

from flask import Flask, request, abort


app = Flask(__name__)


@app.route('/<path:url>')
def main(url):

    parsed = urlparse(url)
    hostname = parsed.netloc or parsed.path

    try:
        addr = socket.gethostbyname(hostname)
    except socket.gaierror:
        abort(404)

    cert = ssl.get_server_certificate((addr, 443))

    proc = subprocess.Popen(['openssl', 'x509', '-text', '-noout', '-nameopt', 'multiline'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    parsed, err = proc.communicate(cert)

    return parsed, 200, [('Content-Type', 'text/plain')]


if __name__ == '__main__':
    app.run(debug=True)
