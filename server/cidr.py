from genericpath import exists
import time
import json
import os
from os import path
from ipaddress import IPv4Network
from git import Repo

global range_repo, reason, requiredrange, access_token, addresses, occupied, subnet_size

try:
    #initial params definition
    #access_token = os.environ['access_token']
    access_token = "yourgithubtoken"
    #requiredrange = os.environ['requiredrange']
    subnet_size = os.environ['subnet_size']
    subnet_size = "26"
    requiredrange = "10"
    #reason = os.environ['reason']
    reason = "test-server-python"
    #repo = os.environ['repo']
    range_repo = "range_repo"
    HTTPS_REMOTE_URL = 'https://' + access_token + '@github.com/' + range_repo
    DEST = 'infra'
    #reading json data
    addresses = json.load(open(DEST+'/addresses-range.json'))
    occupied = json.load(open(DEST+'/occupied-range.json'))
    #print("Done loading params")
    
except: 
    print("Initial setup failed")
    print("Make sure all env params are exported: access_token,requiredrange,reason,repo")
    os._exit(1)

class get_cidr():
    def main_function():   
        def git_clone(repo_dir):
            try:
                if path.exists(DEST):
                    repo = Repo(repo_dir)
                    repo.remotes.origin.pull()
                else:        
                    #cloning the infra repo
                    Repo.clone_from(HTTPS_REMOTE_URL, DEST)
            except:
                print("Error cloning repo")
                os._exit(1)
        def get_subnet(range):
            #getting main address range to obtian subnets from it 
            main_range = IPv4Network(addresses[range])
            #getting all possible CIDRs blocks in the range - block size can be modified using /subnet_size/
            for subnet in main_range.subnets(new_prefix=subnet_size):
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
        subnet = get_subnet(requiredrange)
        data={reason+str(int(time.time())):str(subnet)}
        #adding the chosen CIDR to the occupied list 
        occupied.update(data)
        #appending used CIDR to list
        write_json(occupied)
        #pushing for git final update 
        push_to_repo(DEST)
        #final print for output - used for automaion
        return subnet

    if __name__ == '__main__':
        main_function()
