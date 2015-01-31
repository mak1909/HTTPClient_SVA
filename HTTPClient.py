#!/usr/bin/python
import gzip
import socket
import sys
import urlparse
import zlib
from StringIO import StringIO

method = sys.argv[1]
url = sys.argv[2]
parsed_url = urlparse.urlparse(url)
connection_parameters = (parsed_url.netloc, 80)
conn = socket.create_connection(connection_parameters)
request = "GET "+parsed_url.path+" HTTP/1.1 \r\nHost:"+parsed_url.netloc+"\r\nAccept: */*\r\nAccept-Encoding: gzip, deflate\r\n\r\n"
print request
conn.send(request)
response = conn.recv(8192)
print response
response_list = response.split("\r\n\r\n")
response_headers = response_list[0]
print type(response_headers)
for i in response_list:
	print "PART"
	print i
content = response_list[1]
contents = content.split("\r\n")
gz = content
print "psdspdsa"
print contents[0]
print gz
data = gzip.GzipFile(fileobj=StringIO(gz)).read()
data = str(data)
print data
