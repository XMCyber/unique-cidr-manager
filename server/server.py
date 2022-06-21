from http.server import BaseHTTPRequestHandler
from cidr import get_cidr

class Server(BaseHTTPRequestHandler): 
  def do_GET(self):
    if self.path == "/get-cidr":
      print("Request is being served")
      self.respond()
    
  def handle_http(self, status, content_type):
    self.send_response(status)
    self.send_header('Content-type', content_type)
    self.end_headers()
    result=get_cidr.main_function()
    print(str(result))
    return bytes(str(result), "UTF-8")
    
  def respond(self):
    content = self.handle_http(200, 'text/html')
    self.wfile.write(content)