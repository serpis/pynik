import sys
import re
import urllib
import urllib2
from socket import *

USER_AGENT = 'Pynik/0.1'

def read_url(url, http_headers={}, http_post_data=None):
    m = re.match("^(.{3,5}):\/\/([^\/]*)(:?\d*)(\/.*?)?$", url)
    if m:
        protocol, address, port, file = m.group(1, 2, 3, 4)

        if protocol == 'http' and not http_headers and http_post_data is None:
            return _legacy_http_read(url, protocol, address, port, file)
        elif protocol in ['http', 'https']:
            return _normal_http_read(url, http_headers, http_post_data)
        else:
            print "Only http(s) is supported at this moment."
            return None
    else:
        print "NOT AN URL: %s" % url
        return None

def _write(s, text):
    s.send(text)
    s.send("\r\n")

class _http_get_request:
    def __init__(self, file):
        self.file = file
        self.headers = []

    def add_header(self, name, value):
        self.headers.append((name, value))

    def send(self, s):
        _write(s, "GET %s HTTP/1.0" % self.file)
        _write(s, "\r\n".join(map(lambda x: "%s: %s" % x, self.headers)))
        _write(s, "")
        _write(s, "")

def _read_line(s):
    line = ""

    while True:
        line += s.recv(1)

        if line and line[-1:] == "\n":
            line = line[0:-1]
            if len(line) and line[-1] == "\r":
                line = line[0:-1]

            return line

def _read_http_headers(s):
    m = re.match("^(.+?) (.+?) (.+)$", _read_line(s))
    protocol, response_num, response_string = m.groups()
    headers = {}

    while True:
        line = _read_line(s)
        if len(line) == 0:
            break

        m = re.match("^(.+?) (.+)$", line)
        if m:
            headers[m.group(1)[0:-1]] = m.group(2)

    return (protocol, int(response_num), response_string, headers)

def _read_http_data(s, length):
    data = ''
    while not length or len(data) < length:
        to_receive = 1024
        if length:
            to_receive = min(length - len(data), 1024)

        new_data = s.recv(to_receive)

        if new_data:
            data += new_data
        else:
            break

    return data

def _legacy_http_read(url, protocol, address, port, file):
    if not port:
        port = 80
    if not file:
        file = '/'

    # print "Connecting to %s" % address

    request = _http_get_request(file)
    request.add_header("User-Agent", USER_AGENT)
    request.add_header("Accept", "*/*")
    request.add_header("Host", address)

    s = socket(AF_INET, SOCK_STREAM)

    s.connect((address, port))
    request.send(s)

    protocol, response_num, response_string, headers = _read_http_headers(s)

    if response_num == 301 or response_num == 302:
        s.close()

        # Let's do some simple loop detection...
        if url == headers['Location']:
            print "Redirect loop discovered at: %s" % headers['Location']
            return None
        else:
            print "Site moved to: %s" % headers['Location']
            return read_url(headers['Location'])
    elif response_num == 200:
        # print "Got response 200. Sweet!"
        length = 1024 * 1024  # max one megabyte
        if "Content-Length" in headers:
            length = min(length, int(headers["Content-Length"]))

        data = _read_http_data(s, length)

        s.close()

        return { "url": url, "data": data }
    else:
        print "Got unhandled response code: %s" % response_num
        return None

def _normal_http_read(url, http_headers, http_post_data):
    if http_post_data is not None:
        http_post_data = urllib.urlencode(http_post_data)

    request = urllib2.Request(url, headers=http_headers, data=http_post_data)
    request.add_header('User-Agent', USER_AGENT)

    try:
        file = urllib2.urlopen(request)
    except IOError:
        return None

    result = {"url": file.geturl(),
              "data": file.read(1024 * 1024),
              "info": file.info()}

    file.close()
    return result
