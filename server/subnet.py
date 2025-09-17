from ipaddress import IPv4Network


class Subnets:
    
    @staticmethod
    def get_subnets_from_cidr(subnet_size, cidr):
        """
        Calculate all subnets of a given size from a CIDR block.
        
        Args:
            subnet_size: Target subnet prefix length (as string or int)
            cidr: Source CIDR block (as string)
            
        Returns:
            str: Space-separated list of subnet CIDR strings
            
        Raises:
            ValueError: If CIDR is invalid or subnet size is inappropriate
        """
        try:
            # Validate inputs
            if not subnet_size or not cidr:
                raise ValueError("Both subnet_size and cidr parameters are required")
            
            # Convert subnet_size to int if it's a string
            if isinstance(subnet_size, str):
                subnet_size = int(subnet_size)
            
            print(f"Processing CIDR: {cidr} with subnet_size: {subnet_size}")
            
            # Parse the CIDR
            network = IPv4Network(cidr)
            
            # Validate subnet size
            if subnet_size <= network.prefixlen:
                raise ValueError(
                    f"Subnet size /{subnet_size} must be larger than source CIDR prefix /{network.prefixlen}"
                )
            
            if subnet_size > 30:
                raise ValueError("Subnet size cannot be larger than /30")
            
            # Generate subnets
            subnets_list = []
            for subnet in network.subnets(new_prefix=subnet_size):
                subnets_list.append(str(subnet))
            
            result = ' '.join(subnets_list)
            print(f"Generated {len(subnets_list)} subnets: {result}")
            
            return result
            
        except ValueError as e:
            print(f"Error in get_subnets_from_cidr: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error in get_subnets_from_cidr: {e}")
            raise ValueError(f"Failed to generate subnets: {e}")