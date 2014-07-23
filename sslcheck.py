import ssl
import socket
import subprocess
from urlparse import urlparse

from flask import Flask, request, redirect, abort, url_for


app = Flask(__name__)


@app.route('/')
def index():

    if 'url' in request.args:
        return redirect(url_for('main', url=request.args['url']))

    return '''
<!doctype html5>
<head>
    <style>
        html {
            font-family: monospace;
            white-space: pre;
        }
    </style>

<body>Welcome to the SSL checker!

This mini-app will retrieve and display SSL certs for requested servers;
you can quickly check to make sure they match what your browser is reporting
for a safe browsing experience.

<form><input name="url" size="100" placeholder="example.com" /> <input type="submit" /></form>

'''


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
