from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse
from cidr import get_cidr
from subnet import subnets

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
    
    if self.path.startswith("/get-next-cidr-no-push"):
      print("get-next-cidr-no-push - Request is being served")
      query = urlparse(self.path).query
      query_components = dict(qc.split("=") for qc in query.split("&"))
      print(str(query_components))
      print(str(query))
      subnet_size = query_components["subnet_size"]
      requiredrange = query_components["requiredrange"]
      reason = query_components["reason"]
      self.respond_get_next_cidr_no_push(subnet_size,requiredrange,reason)

    if self.path.startswith("/delete-cidr-from-list"):
      print("delete_cidr_from_list - Request is being served")
      query = urlparse(self.path).query
      query_components = dict(qc.split("=") for qc in query.split("&"))
      print(str(query_components))
      print(str(query))
      cidr_deletion = query_components["cidr_deletion"]
      self.respond_delete_cidr_from_list(cidr_deletion)

    if self.path.startswith("/add-cidr-manually"):
      print("add-cidr-manually - Request is being served")
      query = urlparse(self.path).query
      query_components = dict(qc.split("=") for qc in query.split("&"))
      print(str(query_components))
      print(str(query))
      cidr = query_components["cidr"]
      reason = query_components["reason"]
      self.respond_add_cidr_manually(cidr,reason)

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

    if  self.path.endswith(".css"):
      content = open('frontend'+self.path, 'rb').read()
      self.send_response(200)
      self.send_header('Content-type','text/css')
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
    
    if self.path.startswith("/get-occupied-list"):
      print("get-occupied-list - Request is being served")
      self.respond_get_occupied_list()
  
  #### get_unique_cidr ####
  def handle_http_cidr(self, status, content_type, subnet_size,requiredrange,reason):
    self.send_response(status)
    self.send_header('Content-type', content_type)
    self.end_headers()
    result=get_cidr.get_unique_cidr(subnet_size,requiredrange,reason)
    print(str(result))
    return bytes(str(result), "UTF-8")
  
  def respond_cidr(self,subnet_size,requiredrange,reason):
    content = self.handle_http_cidr(200, 'text/html', subnet_size,requiredrange,reason)
    self.wfile.write(content)
  
  #### get_subnets_from_cidr ####
  def handle_http_subnets(self, status, content_type, subnet_size,cidr):
    self.send_response(status)
    self.send_header('Content-type', content_type)
    self.end_headers()
    result=subnets.get_subnets_from_cidr(subnet_size,cidr)
    print(str(result))
    return bytes(str(result), "UTF-8")
  
  def respond_sunbets(self,subnet_size,cidr):
    content = self.handle_http_subnets(200, 'text/html', subnet_size,cidr)
    self.wfile.write(content)

  #### get_all_occupied ####
  def handle_get_occupied_list(self, status, content_type):
    self.send_response(status)
    self.send_header('Content-type', content_type)
    self.end_headers()
    result=get_cidr.get_all_occupied()
    print(str(result))
    return bytes(str(result), "UTF-8")

  def respond_get_occupied_list(self):
    content = self.handle_get_occupied_list(200, 'text/html')
    self.wfile.write(content)

  #### get-next-cidr-no-push ####
  def handle_http_get_next_cidr_no_push(self, status, content_type, subnet_size,requiredrange,reason):
    self.send_response(status)
    self.send_header('Content-type', content_type)
    self.end_headers()
    result=get_cidr.get_next_cidr_no_push(subnet_size,requiredrange,reason)
    print(str(result))
    return bytes(str(result), "UTF-8")
  
  def respond_get_next_cidr_no_push(self,subnet_size,requiredrange,reason):
    content = self.handle_http_get_next_cidr_no_push(200, 'text/html', subnet_size,requiredrange,reason)
    self.wfile.write(content)

  #### delete-cidr-from-list ####
  def handle_http_get_delete_cidr_from_list(self, status, content_type, cidr_deletion):
    self.send_response(status)
    self.send_header('Content-type', content_type)
    self.end_headers()
    result=get_cidr.delete_cidr_from_list(cidr_deletion)
    print(str(result))
    return bytes(str(result), "UTF-8")
  
  def respond_delete_cidr_from_list(self,cidr_deletion):
    content = self.handle_http_get_delete_cidr_from_list(200, 'text/html', cidr_deletion)
    self.wfile.write(content)

  #### add-cidr-manually ####
  def handle_add_cidr_manually(self,cidr,reason):
    self.send_response(status)
    self.send_header('Content-type', content_type)
    self.end_headers()
    result=get_cidr.manually_add_cidr(cidr,reason)
    print(str(result))
    return bytes(str(result), "UTF-8")

  def respond_add_cidr_manually(self,cidr,reason):
    content = self.handle_add_cidr_manually(200, 'text/html', cidr,reason)
    self.wfile.write(content)