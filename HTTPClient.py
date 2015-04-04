import gzip
import socket
import sys
import urlparse
from StringIO import StringIO

response_text = ''
response_header_dict = {}
response_list = ''
status_code = None
response = ''
redirectCount = 0


def getHeader(header=None):
    if header is None:
        return -1
    if header in response_header_dict.keys():
        return response_header_dict[header]
    return -1


def statusFunc():
    if status_code in range(200, 300):
        sys.exit(0)
    elif status_code in range(300, 400):
        sys.exit(3)
    elif status_code in range(400, 500):
        sys.exit(4)
    elif status_code in range(500, 600):
        sys.exit(5)
    else:
        sys.exit(1)


def end(text):
    x = text.split('\r\n\r\n')
    for i in x:
        k = i.split('\r\n')
        for s in k:
            try:
                v = int(s, 16)
                if v == 0:
                    return True
            except Exception:
                pass
    return False


def fetchMore(con, text):
    while True:
        r = con.recv(4096)
        text += r
        isFlag = end(r)
        if isFlag:
            break
    outputResponse(text)


def outputResponse(text):
    global response_text
    b = ''
    l = 0
    for j in range(0, len(text)):
        try:
            if text[j] == '\r' and text[j + 1] == '\n':
                temp = int(text[l:j], 16)
                b += text[j + 2: j + 2 + temp]
        except Exception:
            l = j + 2
    response_text = ''
    response_text = b


def fetchResponse(c):
    global response_text, response_list, response

    if response_list == '':
        response_text = ''
        return

    if getHeader("Transfer-Encoding") != -1:
        if not end(response_list):
            fetchMore(c, response_list)
    else:
        response_text += response_list
        length = int(getHeader("Content-Length"))
        remaining = length - len(response_list)
        while remaining > 0:
            bal = c.recv(remaining)
            response_text += bal
            remaining = remaining - len(bal)


def checkRedirect(status_code, con):
    global redirectCount
    redirectCount += 1
    if status_code in [301, 302, 303, 307]:
        if "Location" in response_header_dict.keys():
            con.close()
            main(sys.argv[1], response_header_dict["Location"])


def create_response_header_dict(response_headers):
    global response_header_dict
    for x in response_headers:
        pos = x.find(': ')
        response_header_dict[x[:pos]] = x[pos + 2:]


def main(method, url):
    global response_list, response_header_dict, status_code, response
    response_headers = ''
    parsed_url = urlparse.urlparse(url)
    parse_url = parsed_url.netloc.split(":")
    if len(parse_url) > 1:
        connection_parameters = (parse_url[0], parse_url[1])
    else:
        connection_parameters = (parse_url[0], 80)
    con = socket.create_connection(connection_parameters)
    path = parsed_url.path
    if path is '':
        path = '/'

    request = method + " " + path + " HTTP/1.1\r\nHost:" + parsed_url.netloc \
        + "\r\nAccept: */*\r\nAccept-Encoding: gzip,deflate\r\n\r\n"

    con.send(request)

    while True:
        response = con.recv(4096)
        pos = response.find('\r\n\r\n')
        if pos == -1:
            response_headers += response
        else:
            response_headers += response[:pos]
            response_list = response[pos + 4:]
            break
    response_headers = response_headers.split("\r\n")
    create_response_header_dict(response_headers)
    status_code = int(response_headers[0].split(' ')[1])
    if redirectCount < 5:
        checkRedirect(status_code, con)

    if redirectCount >= 5:
        sys.exit(1)

    fetchResponse(con)

    if getHeader("Content-Encoding") == "gzip":
        sys.stdout.write(str(gzip.GzipFile(fileobj=StringIO(response_text)).read()))
    else:
        sys.stdout.write(response_text)

    statusFunc()

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
