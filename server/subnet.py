from ipaddress import IPv4Network

class get_subnetst_from_cidr():
    def main_function(subnet_size, cidr):
        subnetslist = ""
        print("cidr: " + cidr)
        cidr = IPv4Network(cidr)
        for subnet in cidr.subnets(new_prefix=int(subnet_size)):
            subnetslist = subnetslist + str(subnet) + ' '
        return subnetslist