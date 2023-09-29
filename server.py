#  coding: utf-8 
import socketserver

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/
import os
import urllib.parse

class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()

        if not self.data:
            return
        print ("Got a request of: %s\n" % self.data)
        request = self.data.decode("utf-8").split(" ", 3)
        method = request[0]
        path = request[1]
        # I have written the whole assignment before failing the path traversal attack on the lab machine and do not 
        # understand how path normalization and absolutization works
        # so hopefully accounting for percent encoded attacks is sufficient

        if ".." in urllib.parse.unquote(path): 
            self.request.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n<html><body><h1>404 Not Found</h1></body></html>")
            return

        if method != "GET":
            self.request.sendall(b"HTTP/1.1 405 Method Not Allowed\r\n\r\n<html><body><h1>405 Method Not Allowed</h1></body></html>")
            return

        error = False

        if os.path.isdir(path) or os.path.isdir("./www" + path): # then this is a folder and not a file
            if path[-1] != "/": # then redirect to the same path but with /
                response = f"HTTP/1.1 301 Moved Permanently\r\nLocation:{path}/".encode()
                

            else: # the path is correct
                html_file_path = "./www" + path + "index.html"
                with open(html_file_path, "r") as f:
                    html_content = f.read()
                response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{html_content}".encode()

                # # since the css files have different names we cannot do the same, but we can just open the first css file we find
                # css_content = ""
                # for filename in os.listdir(path):
                #     if filename.endswith(".css"):
                #         file_path = path + filename
                #         try:
                #             with open(file_path, "rb") as file:
                #                 css_content = file.read()
                #         except PermissionError as e:
                #             response = b"HTTP/1.1 403 Forbidden\r\n\r\n<html><body><h1>403 Forbidden</h1></body></html>"
                #             error = True
                #         except FileNotFoundError as e:
                #             response = b"HTTP/1.1 404 Not Found\r\n\r\n<html><body><h1>404 Not Found</h1></body></html>"
                #             error = True
                #         except Exception as e:
                #             response = b"HTTP/1.1 500 Internal Server Error\r\n\r\n<html><body><h1>500 Internal Server Error</h1></body></html>"
                #             error = True
                #         break
            
                
        else: # then this path is a file and just open it
            try:
                path = "./www" + path
                with open(path, "r") as f:
                    file_content = f.read()
            except PermissionError as e:
                response = b"HTTP/1.1 403 Forbidden\r\n\r\n<html><body><h1>403 Forbidden</h1></body></html>"
                error = True
            except FileNotFoundError as e:
                response = b"HTTP/1.1 404 Not Found\r\n\r\n<html><body><h1>404 Not Found</h1></body></html>"
                error = True
            except Exception as e:
                print(e)
                response = b"HTTP/1.1 500 Internal Server Error\r\n\r\n<html><body><h1>500 Internal Server Error</h1></body></html>"
                error = True


            # deal with the mimetype
            if (path.endswith(".css")):
                mimetype = 'text/css'
            elif(path.endswith(".png")):
                mimetype = 'image/png'
            else:
                mimetype = 'text/html'

            if not error:
                response = f"HTTP/1.1 200 OK\r\nContent-Type: {mimetype}\r\n\r\n{file_content}".encode("utf-8")
        
        self.request.sendall(response)
        
        
if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
