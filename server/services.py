"""
Service classes for CIDR and subnet management.

This module contains the business logic separated from the web framework,
making it easier to test and maintain.
"""

import time
import json
import os
import logging
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from ipaddress import IPv4Network
from git import Repo

from config import get_settings

logger = logging.getLogger(__name__)

class GitManager:
    """Handles Git operations for the CIDR management system."""
    
    def __init__(self):
        self.settings = get_settings()
        self.dest = self.settings.git_dest_dir
        self.occupied_file_path = Path(self.dest) / self.settings.occupied_file
        
    def clone_or_pull(self) -> None:
        """Clone repository or pull latest changes if it already exists."""
        try:
            if Path(self.dest).exists():
                logger.info("Repository already exists - pulling latest changes")
                repo = Repo(self.dest)
                repo.remotes.origin.pull()
            else:
                logger.info("Cloning repository")
                Repo.clone_from(self.settings.https_remote_url, self.dest)
                logger.info("Repository cloned successfully")
        except Exception as e:
            logger.error(f"Git error occurred: {e}")
            raise Exception(f"Failed to clone/pull repository: {e}")
        
        # Ensure occupied file exists
        if not self.occupied_file_path.exists():
            logger.info("Creating empty occupied CIDRs file")
            self.occupied_file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.occupied_file_path, 'w') as file:
                json.dump({}, file)
    
    def push_changes(self, commit_message: str) -> None:
        """Commit and push changes to the repository."""
        try:
            repo = Repo(self.dest)
            
            # Configure git user
            with repo.config_writer() as config:
                config.set_value('user', 'name', self.settings.committer_name)
                config.set_value('user', 'email', self.settings.committer_email)
            
            # Add, commit, and push
            repo.index.add([self.settings.occupied_file])
            repo.index.commit(commit_message)
            origin = repo.remote('origin')
            origin.push().raise_if_error()
            
            logger.info(f"Changes pushed successfully: {commit_message}")
        except Exception as e:
            logger.error(f"Failed to push changes: {e}")
            raise Exception(f"Failed to push changes to repository: {e}")

class CIDRService:
    """Service for managing CIDR allocations."""
    
    def __init__(self):
        self.settings = get_settings()
        self.git_manager = GitManager()
        self.addresses_file = Path("addresses-range.json")
        
    def _load_occupied_cidrs(self) -> Dict[str, str]:
        """Load occupied CIDRs from file."""
        try:
            with open(self.git_manager.occupied_file_path, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Could not load occupied CIDRs: {e}")
            return {}
    
    def _save_occupied_cidrs(self, occupied: Dict[str, str]) -> None:
        """Save occupied CIDRs to file."""
        try:
            with open(self.git_manager.occupied_file_path, 'w') as file:
                json.dump(occupied, file, indent=4)
        except Exception as e:
            logger.error(f"Failed to save occupied CIDRs: {e}")
            raise Exception(f"Failed to save occupied CIDRs: {e}")
    
    def _load_address_ranges(self) -> Dict[str, str]:
        """Load available address ranges from configuration."""
        try:
            with open(self.addresses_file, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            logger.warning("addresses-range.json not found, using default ranges")
            return {
                "10": "10.0.0.0/8",
                "172": "172.16.0.0/12",
                "192": "192.168.0.0/16"
            }
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in addresses-range.json: {e}")
            raise ValueError("Invalid address ranges configuration")
    
    def _get_next_available_subnet(self, range_key: str, subnet_size: int) -> IPv4Network:
        """Find the next available subnet in the specified range."""
        occupied = self._load_occupied_cidrs()
        addresses = self._load_address_ranges()
        
        if range_key not in addresses:
            raise ValueError(f"Invalid range key: {range_key}. Available ranges: {list(addresses.keys())}")
        
        main_range = IPv4Network(addresses[range_key])
        logger.info(f"Searching for /{subnet_size} subnet in {main_range}")
        
        # Get all possible subnets of the requested size
        for subnet in main_range.subnets(new_prefix=subnet_size):
            # Check if this subnet overlaps with any occupied CIDR
            is_occupied = any(
                IPv4Network(subnet).overlaps(IPv4Network(occupied_cidr))
                for occupied_cidr in occupied.values()
            )
            
            if not is_occupied:
                logger.info(f"Found available subnet: {subnet}")
                return subnet
        
        raise Exception(f"No available /{subnet_size} subnets in range {addresses[range_key]}")
    
    def _check_reason_already_used(self, reason: str, occupied: Dict[str, str]) -> Optional[str]:
        """Check if reason was already used and return existing CIDR if found."""
        for key, cidr in occupied.items():
            # Remove timestamp suffix to get original reason
            original_reason = key.rsplit('-', 1)[0] if '-' in key else key
            if original_reason == reason:
                logger.info(f"Reason '{reason}' already used, returning existing CIDR: {cidr}")
                return cidr
        return None
    
    def _validate_reason(self, reason: str) -> None:
        """Validate the reason parameter."""
        if not reason or reason.isspace():
            raise ValueError("Reason is required and cannot be empty")
        
        if len(reason.strip()) == 0:
            raise ValueError("Reason cannot be empty after trimming whitespace")
    
    def _is_valid_cidr(self, cidr: str) -> bool:
        """Check if a string is a valid CIDR."""
        try:
            IPv4Network(cidr)
            return True
        except ValueError:
            return False
    
    def _check_cidr_overlap(self, cidr: str) -> bool:
        """Check if a CIDR overlaps with any existing occupied CIDR."""
        occupied_cidrs = self._load_occupied_cidrs()
        given_cidr = IPv4Network(cidr)
        
        for occupied_cidr in occupied_cidrs.values():
            if given_cidr.overlaps(IPv4Network(occupied_cidr)):
                return True
        return False
    
    def get_unique_cidr(self, subnet_size: int, required_range: str, reason: str) -> IPv4Network:
        """
        Get a unique CIDR and mark it as occupied.
        
        Args:
            subnet_size: The subnet prefix length (e.g., 24 for /24)
            required_range: The range identifier ("10", "172", "192")
            reason: The reason for allocation
            
        Returns:
            IPv4Network: The allocated CIDR block
            
        Raises:
            ValueError: If parameters are invalid
            Exception: If no CIDR is available or Git operations fail
        """
        self._validate_reason(reason)
        
        # Clone/pull repository
        self.git_manager.clone_or_pull()
        
        # Load current occupied CIDRs
        occupied = self._load_occupied_cidrs()
        
        # Check if reason was already used
        existing_cidr = self._check_reason_already_used(reason, occupied)
        if existing_cidr:
            return IPv4Network(existing_cidr)
        
        # Find next available subnet
        subnet = self._get_next_available_subnet(required_range, subnet_size)
        
        # Create new entry with timestamp
        timestamp = int(time.time())
        key = f"{reason}-{timestamp}"
        occupied[key] = str(subnet)
        
        # Save to file
        self._save_occupied_cidrs(occupied)
        
        # Commit and push changes
        commit_message = f"Allocated CIDR {subnet} for {reason}"
        self.git_manager.push_changes(commit_message)
        
        logger.info(f"Successfully allocated CIDR {subnet} for reason '{reason}'")
        return subnet
    
    def get_next_cidr_no_push(self, subnet_size: int, required_range: str, reason: str) -> IPv4Network:
        """
        Preview the next available CIDR without allocating it.
        
        Args:
            subnet_size: The subnet prefix length
            required_range: The range identifier
            reason: The reason (for duplicate checking)
            
        Returns:
            IPv4Network: The next available CIDR block
        """
        self._validate_reason(reason)
        
        # Clone/pull repository
        self.git_manager.clone_or_pull()
        
        # Load current occupied CIDRs
        occupied = self._load_occupied_cidrs()
        
        # Check if reason was already used
        existing_cidr = self._check_reason_already_used(reason, occupied)
        if existing_cidr:
            return IPv4Network(existing_cidr)
        
        # Find next available subnet (but don't allocate it)
        subnet = self._get_next_available_subnet(required_range, subnet_size)
        
        logger.info(f"Next available CIDR for reason '{reason}': {subnet}")
        return subnet
    
    def get_all_occupied(self) -> Dict[str, str]:
        """
        Get all occupied CIDR blocks.
        
        Returns:
            Dict[str, str]: Dictionary of reason-timestamp keys to CIDR values
        """
        self.git_manager.clone_or_pull()
        occupied = self._load_occupied_cidrs()
        logger.info(f"Retrieved {len(occupied)} occupied CIDRs")
        return occupied
    
    def delete_cidr_from_list(self, cidr_block: str) -> str:
        """
        Delete a CIDR block from the occupied list.
        
        Args:
            cidr_block: The CIDR block to delete
            
        Returns:
            str: Success or error message
        """
        if not self._is_valid_cidr(cidr_block):
            raise ValueError(f"Invalid CIDR format: {cidr_block}")
        
        self.git_manager.clone_or_pull()
        occupied = self._load_occupied_cidrs()
        
        # Find and delete the CIDR
        key_to_delete = None
        for key, cidr in occupied.items():
            if cidr == cidr_block:
                key_to_delete = key
                break
        
        if key_to_delete is None:
            return f"CIDR {cidr_block} not found in occupied list"
        
        # Delete the entry
        del occupied[key_to_delete]
        
        # Save changes
        self._save_occupied_cidrs(occupied)
        
        # Commit and push
        commit_message = f"Deleted CIDR {cidr_block}"
        self.git_manager.push_changes(commit_message)
        
        logger.info(f"Successfully deleted CIDR {cidr_block}")
        return f"CIDR {cidr_block} deleted successfully (key: {key_to_delete})"
    
    def manually_add_cidr(self, cidr_block: str, reason: str) -> str:
        """
        Manually add a CIDR block to the occupied list.
        
        Args:
            cidr_block: The CIDR block to add
            reason: The reason for adding it
            
        Returns:
            str: Success or error message
        """
        self._validate_reason(reason)
        
        if not self._is_valid_cidr(cidr_block):
            return "Invalid CIDR format"
        
        if self._check_cidr_overlap(cidr_block):
            return "CIDR overlaps with existing allocation"
        
        self.git_manager.clone_or_pull()
        occupied = self._load_occupied_cidrs()
        
        # Create new entry
        timestamp = int(time.time())
        key = f"{reason}-{timestamp}"
        occupied[key] = cidr_block
        
        # Save changes
        self._save_occupied_cidrs(occupied)
        
        # Commit and push
        commit_message = f"Manually added CIDR {cidr_block} for {reason}"
        self.git_manager.push_changes(commit_message)
        
        logger.info(f"Successfully added CIDR {cidr_block} manually for reason '{reason}'")
        return "CIDR added successfully"

class SubnetService:
    """Service for subnet calculations."""
    
    def get_subnets_from_cidr(self, subnet_size: int, cidr: str) -> List[str]:
        """
        Calculate all subnets of a given size from a CIDR block.
        
        Args:
            subnet_size: Target subnet prefix length
            cidr: Source CIDR block
            
        Returns:
            List[str]: List of subnet CIDR strings
            
        Raises:
            ValueError: If CIDR is invalid or subnet size is inappropriate
        """
        try:
            network = IPv4Network(cidr)
        except ValueError as e:
            raise ValueError(f"Invalid CIDR format '{cidr}': {e}")
        
        if subnet_size <= network.prefixlen:
            raise ValueError(
                f"Subnet size /{subnet_size} must be larger than source CIDR prefix /{network.prefixlen}"
            )
        
        if subnet_size > 30:
            raise ValueError("Subnet size cannot be larger than /30")
        
        subnets = []
        try:
            for subnet in network.subnets(new_prefix=subnet_size):
                subnets.append(str(subnet))
        except ValueError as e:
            raise ValueError(f"Cannot create /{subnet_size} subnets from {cidr}: {e}")
        
        logger.info(f"Generated {len(subnets)} subnets of size /{subnet_size} from {cidr}")
        return subnets
