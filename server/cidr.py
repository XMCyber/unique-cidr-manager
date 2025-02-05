import time
import json
import os
from ipaddress import IPv4Network
os.environ["GIT_PYTHON_REFRESH"] = "quiet"
from git import Repo

try:
    #initial params definition
    access_token = os.environ['access_token']
    occupied_repo = os.environ['occupied_repo']
    occupied_file = os.environ.get('occupied_file', 'occupied-range.json')
    committer_name = os.environ.get('committer_name', 'Unique CIDR Manager')
    committer_email = os.environ.get('committer_email', 'cidr@manager.dev')
    #set params
    HTTPS_REMOTE_URL = 'https://' + access_token + '@github.com/' + occupied_repo3
    DEST = 'infra'
    OCCUPIED_FILE_PATH = f"{DEST}/{occupied_file}"

    print("Done loading params")
except: 
    print("Initial setup failed")
    print("Make sure all env vars are provided: access_token, occupied_repo")
    os._exit(1)

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
        print("git error occured - restaring container")
        os._exit(1)
        
def get_subnet(range,subnet_size):
    occupied = json.load(open(OCCUPIED_FILE_PATH))
    #getting main address range to obtian subnets from it 
    addresses = json.load(open('addresses-range.json'))
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

def check_overlap(cidr):
    occupied_cidrs = json.load(open(OCCUPIED_FILE_PATH))
    given_cidr = IPv4Network(cidr)
    # Checking if the given cidr overlaps with any existing occupied cidr
    for key, value in occupied_cidrs.items():
        occupied_cidr = IPv4Network(value)
        if given_cidr.overlaps(occupied_cidr):
            return True
        if str(given_cidr) == str(occupied_cidr): 
            return True
    return False

def is_valid_cidr(cidr):
    try:
        IPv4Network(cidr)
        return True
    except Exception:
        return False

def check_preconditions(reason, occupied):
    #checking if reason is empty 
    if reason == "":
        return "You must specify reason, this field is mandatory!"
    #checking if reason was already served and reture existing subnet
    for key in occupied:
        #removing epoch time stamp, 10 chars for epoch, 1 char for dash
        original_reason=key[:len(key)-11]
        if original_reason == reason:
            #reason already served - getting allocated CIDR
            print("reason already served - getting allocated CIDR")
            subnet=occupied[key]
            return subnet
        
def write_json(new_data, filename=OCCUPIED_FILE_PATH):
    try:
        with open(filename,'w') as file:
            json.dump(new_data, file, indent = 4)
    except:
        raise Exception("Error writing to json file")

def push_to_repo(repo_dir, commit_message):
    file_list = [occupied_file]
    repo = Repo(repo_dir)
    # Set committing user and email
    with repo.config_writer() as config:
        config.set_value('user', 'name', committer_name)
        config.set_value('user', 'email', committer_email)
    repo.index.add(file_list)
    repo.index.commit(commit_message)
    origin = repo.remote('origin')
    try:
        origin.push().raise_if_error()
    except Exception as e:
        print(e)
        print("git error occured - restaring container")
        os._exit(1)

class get_cidr():
    def get_unique_cidr(subnet_size,requiredrange,reason):          
        #cloning(or pulling if already cloned)
        git_clone(DEST)
        occupied = json.load(open(OCCUPIED_FILE_PATH))
        passed = check_preconditions(reason, occupied)
        if passed is not None:
            return passed
        
        #getting available subnet
        subnet = get_subnet(requiredrange,subnet_size)
        data={reason+ '-' + str(int(time.time())):str(subnet)}
        print(data)
        #adding the chosen CIDR to the occupied list 
        occupied.update(data)
        print(occupied)
        #appending used CIDR to list
        write_json(occupied)
        #pushing for git final update 
        commit_message = 'unique CIDR for ' + reason
        push_to_repo(DEST, commit_message)
        #final print for output - used for automaion
        return subnet
    
    def get_next_cidr_no_push(subnet_size,requiredrange,reason):
        #this function will only show the next available cidr, but will not save it
        git_clone(DEST)
        occupied = json.load(open(OCCUPIED_FILE_PATH))
        passed = check_preconditions(reason, occupied)
        if passed is not None:
            return passed
        subnet = get_subnet(requiredrange,subnet_size)
        return subnet
    
    def get_all_occupied():
        git_clone(DEST)
        occupied = json.load(open(OCCUPIED_FILE_PATH))
        return json.dumps(occupied,indent=4)
    
    def delete_cidr_from_list(cidr_block):
        git_clone(DEST)
        occupied = json.load(open(OCCUPIED_FILE_PATH))
        keyfound="CIDR not found"
        for key in occupied:
            if occupied[key] == cidr_block:
                print("found requested CIDR " + cidr_block + ", deleing!")
                del occupied[key]
                print(occupied)
                write_json(occupied)
                commit_message = 'deleting CIDR ' + cidr_block
                push_to_repo(DEST, commit_message)
                keyfound=key + " deleted!"
                print(keyfound)
                break
        return keyfound

    def manually_add_cidr(cidr_block, reason):
        git_clone(DEST)
        if not is_valid_cidr(cidr_block):
            return "CIDR is invalid"
        if check_overlap(cidr_block):
            return "CIDR already in use"

        occupied = json.load(open(OCCUPIED_FILE_PATH))
        data={reason+ '-' + str(int(time.time())):str(cidr_block)}
        print(data)
        #adding the chosen CIDR to the occupied list 
        occupied.update(data)
        print(occupied)
        #appending used CIDR to list
        write_json(occupied)
        #pushing for git final update 
        commit_message = 'Added CIDR manually ' + reason
        push_to_repo(DEST, commit_message)
        
        return "CIDR added successfully"

