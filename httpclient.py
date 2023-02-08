#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        parsedUrl = urllib.parse.urlparse(url)
        return parsedUrl.hostname, parsedUrl.port

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port or 80))
        return None

    def get_code(self, data):
        return None

    def get_headers(self,data):
        return None

    def get_body(self, data):
        return None
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            try:
                part = sock.recv(1024)
            except socket.timeout:
                done = True
                continue
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer

    def GET(self, url, args=None):
        host, port = self.get_host_port(url)
        self.connect(host, port)
        parsedUrl = urllib.parse.urlparse(url)
        if parsedUrl.path == "":
            header = ("GET / HTTP/1.1\r\n" +
                "Host: " + parsedUrl.hostname + "\r\n" + 
                "Accept: */*\r\n" +
                "Accept-Charset: UTF-8\r\n\r\n")
        else:
            header = ("GET " + parsedUrl.path + " HTTP/1.1\r\n" +
                    "Host: " + parsedUrl.hostname + "\r\n" + 
                    "Accept-Charset: UTF-8\r\n\r\n")
        self.sendall(header)
        self.socket.settimeout(0.5)
        response = self.recvall(self.socket)
        headers, body = response.split(b"\r\n\r\n", 1)
        headers = headers.decode(encoding="utf-8").split("\r\n")
        code = int((headers[0].split(" "))[1])
        encoding = "utf-8"
        for header in headers:
            if "charset=" in header:
                encoding = (header.split("="))[1]
        body = body.decode(encoding=encoding)
        self.close()
        print(body)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        if args is not None:
            args = urllib.parse.urlencode(args)
        host, port = self.get_host_port(url)
        self.connect(host, port)
        parsedUrl = urllib.parse.urlparse(url)
        if args is None:
            header = ("POST / HTTP/1.1\r\n" +
                "Host: " + parsedUrl.hostname + "\r\n" + 
                "Content-Type: application/x-www-form-urlencoded\r\n" +
                "Content-Length: " + "0" + "\r\n" +
                "Accept-Charset: UTF-8\r\n\r\n")
        elif parsedUrl.path == "":
            header = ("POST / HTTP/1.1\r\n" +
                "Host: " + parsedUrl.hostname + "\r\n" + 
                "Content-Type: application/x-www-form-urlencoded\r\n" +
                "Content-Length: " + str(len(args)) + "\r\n" +
                "Accept-Charset: UTF-8\r\n\r\n" +
                args)
        else:
            header = ("POST " + parsedUrl.path + " HTTP/1.1\r\n" +
                    "Host: " + parsedUrl.hostname + "\r\n" + 
                    "Content-Type: application/x-www-form-urlencoded\r\n" +
                    "Content-Length: " + str(len(args)) + "\r\n" +
                    "Accept-Charset: UTF-8\r\n\r\n" +
                    args)
        self.sendall(header)
        self.socket.settimeout(0.5)
        response = self.recvall(self.socket)
        headers, body = response.split(b"\r\n\r\n", 1)
        headers = headers.decode(encoding="utf-8").split("\r\n")
        code = int((headers[0].split(" "))[1])
        encoding = "utf-8"
        for header in headers:
            if "charset=" in header:
                encoding = (header.split("="))[1]
        body = body.decode(encoding=encoding)
        self.close()
        print(body)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
