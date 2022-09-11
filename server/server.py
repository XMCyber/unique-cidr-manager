from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse
from cidr import get_cidr
from subnet import get_subnetst_from_cidr

class Server(BaseHTTPRequestHandler): 
  def do_GET(self):
    if self.path.startswith("/get-cidr"):
      print("get-cidr - Request is being served")
      query = urlparse(self.path).query
      query_components = dict(qc.split("=") for qc in query.split("&"))
      print(str(query_components))
      print(str(query))
      subnet_size = query_components["subnet_size"]
      requiredrange = query_components["requiredrange"]
      reason = query_components["reason"]
      self.respond_cidr(subnet_size,requiredrange,reason)
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
    if self.path.startswith("/get-subnets"):
      print("get-subnets - Request is being served")
      query = urlparse(self.path).query
      query_components = dict(qc.split("=") for qc in query.split("&"))
      print(str(query_components))
      print(str(query))
      subnet_size = query_components["subnet_size"]
      cidr = query_components["cidr"]
      self.respond_sunbets(subnet_size,cidr)
    
  def handle_http_cidr(self, status, content_type, subnet_size,requiredrange,reason):
    self.send_response(status)
    self.send_header('Content-type', content_type)
    self.end_headers()
    result=get_cidr.main_function(subnet_size,requiredrange,reason)
    print(str(result))
    return bytes(str(result), "UTF-8")
  
  def handle_http_subnets(self, status, content_type, subnet_size,cidr):
    self.send_response(status)
    self.send_header('Content-type', content_type)
    self.end_headers()
    result=get_subnetst_from_cidr.main_function(subnet_size,cidr)
    print(str(result))
    return bytes(str(result), "UTF-8")
    
  def respond_cidr(self,subnet_size,requiredrange,reason):
    content = self.handle_http_cidr(200, 'text/html', subnet_size,requiredrange,reason)
    self.wfile.write(content)

  def respond_sunbets(self,subnet_size,cidr):
    content = self.handle_http_subnets(200, 'text/html', subnet_size,cidr)
    self.wfile.write(content)