import time
import json
import os
from ipaddress import IPv4Network
from git import Repo

os.environ["GIT_PYTHON_REFRESH"] = "quiet"

try:
    # Initial parameters definition
    access_token = os.environ['access_token']
    occupied_repo = os.environ['occupied_repo']
    occupied_file = os.environ.get('occupied_file', 'occupied-range.json')
    committer_name = os.environ.get('committer_name', 'Unique CIDR Manager')
    committer_email = os.environ.get('committer_email', 'cidr@manager.dev')

    # Set params
    HTTPS_REMOTE_URL = f'https://{access_token}@github.com/{occupied_repo}'
    DEST = 'infra'
    OCCUPIED_FILE_PATH = f"{DEST}/{occupied_file}"

    print("Done loading params")
except KeyError: 
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
            # Cloning the infra repo
            print("Cloning")
            Repo.clone_from(HTTPS_REMOTE_URL, DEST)
            print("Repo cloned")
    except Exception as e: 
        print("Git error occurred - restarting container")
        print(e)
        os._exit(1)
    
    # check if file exists, if not create it
    if not os.path.exists(OCCUPIED_FILE_PATH):
        print("Creating empty json state file")
        with open(OCCUPIED_FILE_PATH, 'w') as file:
            json.dump({}, file)


def get_subnet(range_key, subnet_size):
    occupied = json.load(open(OCCUPIED_FILE_PATH))
    # Getting main address range to obtain subnets from it 
    addresses = json.load(open('addresses-range.json'))
    main_range = IPv4Network(addresses[range_key])
    
    # Getting all possible CIDR blocks in the range
    for subnet in main_range.subnets(new_prefix=int(subnet_size)):
        # Check for CIDR availability (not overlapping with already occupied CIDRs)
        is_occupied = any(
            IPv4Network(subnet).overlaps(IPv4Network(occupied[key])) 
            for key in occupied
        )
        
        if not is_occupied:
            return subnet
            
    raise Exception("No available address")


def check_overlap(cidr):
    occupied_cidrs = json.load(open(OCCUPIED_FILE_PATH))
    given_cidr = IPv4Network(cidr)
    
    # Checking if the given CIDR overlaps with any existing occupied CIDR
    for value in occupied_cidrs.values():
        if given_cidr.overlaps(IPv4Network(value)):
            return True
    return False


def is_valid_cidr(cidr):
    try:
        IPv4Network(cidr)
        return True
    except ValueError:
        return False


def check_preconditions(reason, occupied):
    # Checking if reason is empty 
    if not reason:
        return "You must specify a reason, this field is mandatory!"
    
    # Checking if reason was already served and returning existing subnet
    for key in occupied:
        original_reason = key[:-11]  # Removing epoch timestamp
        if original_reason == reason:
            print("Reason already served - getting allocated CIDR")
            return occupied[key]


def write_json(new_data, filename=OCCUPIED_FILE_PATH):
    try:
        with open(filename, 'w') as file:
            json.dump(new_data, file, indent=4)
    except IOError as e:
        raise Exception("Error writing to JSON file: " + str(e))


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
        print("Git error occurred - restarting container")
        print(e)
        os._exit(1)


class GetCIDR:

    def get_unique_cidr(subnet_size, required_range, reason):          
        # Cloning (or pulling if already cloned)
        git_clone(DEST)
        occupied = json.load(open(OCCUPIED_FILE_PATH))
        passed = check_preconditions(reason, occupied)
        
        if passed is not None:
            return passed
        
        # Getting available subnet
        subnet = get_subnet(required_range, subnet_size)
        data = {f"{reason}-{int(time.time())}": str(subnet)}
        print(data)
        
        # Adding the chosen CIDR to the occupied list 
        occupied.update(data)
        print(occupied)
        
        # Writing used CIDR to JSON file
        write_json(occupied)
        
        # Pushing for git final update 
        commit_message = f'Unique CIDR for {reason}'
        push_to_repo(DEST, commit_message)
        
        # Final print for output - used for automation
        return subnet

    def get_next_cidr_no_push(subnet_size, required_range, reason):
        # This function will only show the next available CIDR, but will not save it
        git_clone(DEST)
        occupied = json.load(open(OCCUPIED_FILE_PATH))
        passed = check_preconditions(reason, occupied)
        
        if passed is not None:
            return passed
            
        subnet = get_subnet(required_range, subnet_size)
        return subnet
    
    def get_all_occupied():
        git_clone(DEST)
        occupied = json.load(open(OCCUPIED_FILE_PATH))
        return json.dumps(occupied, indent=4)

    def delete_cidr_from_list(cidr_block):
        git_clone(DEST)
        occupied = json.load(open(OCCUPIED_FILE_PATH))
        key_found = "CIDR not found"
        
        for key in list(occupied.keys()):
            if occupied[key] == cidr_block:
                print(f"Found requested CIDR {cidr_block}, deleting!")
                del occupied[key]
                print(occupied)
                write_json(occupied)
                commit_message = f'Deleting CIDR {cidr_block}'
                push_to_repo(DEST, commit_message)
                key_found = f"{key} deleted!"
                print(key_found)
                break
                
        return key_found
    
    def manually_add_cidr(cidr_block, reason):
        git_clone(DEST)
        
        if not is_valid_cidr(cidr_block):
            return "CIDR is invalid"
        
        if check_overlap(cidr_block):
            return "CIDR already in use"

        occupied = json.load(open(OCCUPIED_FILE_PATH))
        data = {f"{reason}-{int(time.time())}": str(cidr_block)}
        print(data)
        
        # Adding the chosen CIDR to the occupied list 
        occupied.update(data)
        print(occupied)
        
        # Writing used CIDR to JSON file
        write_json(occupied)
        
        # Pushing for git final update 
        commit_message = f'Added CIDR manually: {reason}'
        push_to_repo(DEST, commit_message)
        
        return "CIDR added successfully"