from ipaddress import IPv4Network


class Subnets:
    
    def get_subnets_from_cidr(self, subnet_size, cidr):
        subnets_list = []  # Using a list for better performance
        print("cidr: " + cidr)
        cidr = IPv4Network(cidr)
        
        for subnet in cidr.subnets(new_prefix=int(subnet_size)):
            subnets_list.append(str(subnet))
        
        return ' '.join(subnets_list)  # Joining the list into a single string