import ssl
import socket
import subprocess
from urlparse import urlparse

from flask import Flask, request, redirect, abort, url_for


app = Flask(__name__)


def parse_url(url):
    parsed = urlparse(url)
    if parsed.netloc:
        return parsed.hostname, parsed.port and int(parsed.port)
    else:
        parts = parsed.path.split(':', 1)
        if len(parts) == 1:
            return parts[0], None
        else:
            return parts[0], int(parts[1])


@app.route('/')
def index():

    if 'url' in request.args:
        hostname, port = parse_url(request.args['url'])
        if port:
            hostname = '%s:%d' % (hostname, port)
        return redirect(url_for('main', url=hostname))

    return '''
<!doctype html5>
<head>
    <style>
        html {
            font-family: monospace;
            white-space: pre;
        }
        form {
            margin: 0;
        }
        code {
            background: #eee;
            padding: 2px
        }
        input[type=text] {
            padding: 4px;
            font-family: monospace;
        }
    </style>

<body>Welcome to the <strong>SSL Certificate Fetcher</strong>!

This mini-app will retrieve and display SSL certs for requested servers;
you can quickly check to make sure they match what your browser is reporting
for a safe browsing experience.

<form><input type="text" name="url" size="60" placeholder="https://example.com/" /> <input type="submit" /></form>
This is app is essentially the same as fetching the cert and running:

    <code>openssl x509 -text -noout -nameopt multiline</code>

<a href="https://github.com/mikeboers/SSLCertFetcher">Fork me on GitHub.</a>
'''


@app.route('/<path:url>')
def main(url):

    hostname, port = parse_url(url)
    port = port or 443

    try:
        addr = socket.gethostbyname(hostname)
    except socket.gaierror:
        abort(404)

    try:
        cert = ssl.get_server_certificate((addr, port))
    except ssl.SSLError:
        abort(404)

    proc = subprocess.Popen(['openssl', 'x509', '-text', '-noout', '-nameopt', 'multiline'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    parsed, err = proc.communicate(cert)

    return parsed, 200, [('Content-Type', 'text/plain')]


if __name__ == '__main__':
    app.run(debug=True)
