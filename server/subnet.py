from ipaddress import IPv4Network

class subnets():
    
    def get_subnets_from_cidr(subnet_size, cidr):
        subnetslist = ""
        print("cidr: " + cidr)
        cidr = IPv4Network(cidr)
        for subnet in cidr.subnets(new_prefix=int(subnet_size)):
            subnetslist = subnetslist + str(subnet) + ' '
        return subnetslist
