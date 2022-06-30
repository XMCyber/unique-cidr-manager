from http.server import BaseHTTPRequestHandler
#from http.server import SimpleHTTPRequestHandler
from urllib.parse import urlparse
from cidr import get_cidr

class Server(BaseHTTPRequestHandler): 
  def do_GET(self):
    if self.path.startswith("/get-cidr"):
      print("Request is being served")
      query = urlparse(self.path).query
      query_components = dict(qc.split("=") for qc in query.split("&"))
      print(str(query_components))
      print(str(query))
      subnet_size = query_components["subnet_size"]
      requiredrange = query_components["requiredrange"]
      reason = query_components["reason"]
      self.respond(subnet_size,requiredrange,reason)
    if self.path == "/":
      self.path = '/cidr.html'
      content = open('frontend'+self.path, 'rb').read()
      self.send_response(200)
      self.send_header('Content-type','text/html')
      self.end_headers()
      self.wfile.write(content)
    if  self.path.endswith(".js"):
      content = open('frontend'+self.path, 'rb').read()
      self.send_response(200)
      self.send_header('Content-type','text/html')
      self.end_headers()
      self.wfile.write(content)
    
  def handle_http(self, status, content_type, subnet_size,requiredrange,reason):
    self.send_response(status)
    self.send_header('Content-type', content_type)
    self.end_headers()
    result=get_cidr.main_function(subnet_size,requiredrange,reason)
    print(str(result))
    return bytes(str(result), "UTF-8")
    
  def respond(self,subnet_size,requiredrange,reason):
    content = self.handle_http(200, 'text/html', subnet_size,requiredrange,reason)
    self.wfile.write(content)