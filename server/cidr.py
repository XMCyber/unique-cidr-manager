import time
import json
import os
from ipaddress import IPv4Network
os.environ["GIT_PYTHON_REFRESH"] = "quiet"
from git import Repo

global range_repo, reason, requiredrange, access_token, addresses

try:
    #initial params definition
    requiredrange = ""
    subnet_size = ""
    reason = ""
    access_token = os.environ['access_token']

    occupied_repo = os.environ['occupied_repo']
    HTTPS_REMOTE_URL = 'https://' + access_token + '@github.com/' + occupied_repo
    DEST = 'infra'
    print("Done loading params")
    
except: 
    print("Initial setup failed")
    print("Make sure all env params are exported: 1)access_token 2)requiredrange 3)reason 4)range_repo 5)subnet_size")
    os._exit(1)

class get_cidr():
    def main_function(subnet_size,requiredrange,reason):
        def git_clone(repo_dir):
            try:
                if os.path.exists(DEST):
                    print("Repo already exists - pulling (refresh state)")
                    repo = Repo(repo_dir)
                    repo.remotes.origin.pull()
                else:        
                    #cloning the infra repo
                    print("Cloning")
                    Repo.clone_from(HTTPS_REMOTE_URL, DEST)
                    print("Repo cloned")
            except Exception as e: 
                print(e)
                raise e

        def get_subnet(range,subnet_size):

            #getting main address range to obtian subnets from it 
            addresses = json.load(open('addresses-range.json'))
            occupied = json.load(open(DEST+'/occupied-range.json'))
            main_range = IPv4Network(addresses[range])
            #getting all possible CIDRs blocks in the range - block size can be modified using /subnet_size/
            for subnet in main_range.subnets(new_prefix=int(subnet_size)):
                #getting all accupied CIDRs to compare with
                is_occupied = False
                for key in occupied:
                    occupied_cidr = (occupied[key])
                    #checking for cidr availability (not overlapping  awithlready accupied CIDRs)
                    if IPv4Network(subnet).overlaps(IPv4Network(occupied_cidr)): 
                        #if subnet overlaps, go to next CIDR
                        is_occupied = True
                        break
                        #if subnet doesn't overlaps, use this subnet as chosen CIDR
                    else:
                        if str(subnet) == str(occupied_cidr): 
                            is_occupied = True
                            break
                if is_occupied:
                    continue
                return subnet
            raise Exception("No available address")
            
        def write_json(new_data, filename='infra/occupied-range.json'):
            try:
                with open(filename,'r+') as file:
                    json.dump(new_data, file, indent = 4)
            except:
                raise Exception("Error writing to json file")

        def push_to_repo(repo_dir):
            file_list = [
                'occupied-range.json'
            ]
            commit_message = 'unique CIDR for ' + reason
            repo = Repo(repo_dir)
            repo.index.add(file_list)
            repo.index.commit(commit_message)
            origin = repo.remote('origin')
            origin.push()

        #cloning(or pulling if already cloned)
        git_clone(DEST)
        #getting available subnet
        subnet = get_subnet(requiredrange,subnet_size)
        data={reason+ '-' + str(int(time.time())):str(subnet)}
        print(data)
        #adding the chosen CIDR to the occupied list 
        occupied = json.load(open(DEST+'/occupied-range.json'))
        occupied.update(data)
        #appending used CIDR to list
        write_json(occupied)
        #pushing for git final update 
        push_to_repo(DEST)
        #final print for output - used for automaion
        return subnet

