"""
Pydantic models for request/response validation and serialization.

These models provide automatic validation, serialization, and API documentation
for all endpoints in the CIDR Manager API.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from ipaddress import IPv4Network
import re

class CIDRRequest(BaseModel):
    """Request model for CIDR allocation."""
    
    subnet_size: int = Field(
        ...,
        ge=16,
        le=30,
        description="Subnet size (CIDR prefix length)",
        example=24
    )
    required_range: str = Field(
        ...,
        description="Private IP range identifier",
        example="10"
    )
    reason: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Reason for CIDR allocation (no whitespaces recommended)",
        example="web-server-prod"
    )
    
    @validator('subnet_size')
    def validate_subnet_size(cls, v):
        """Validate subnet size is within acceptable range."""
        if not (16 <= v <= 28):
            raise ValueError(f"Subnet size must be between 16 and 28 (inclusive)")
        return v
    
    @validator('required_range')
    def validate_required_range(cls, v):
        """Validate required range is a valid private range identifier."""
        valid_ranges = ["10", "172", "192"]
        if v not in valid_ranges:
            raise ValueError(f"Required range must be one of: {valid_ranges} (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16)")
        return v
    
    @validator('reason')
    def validate_reason(cls, v):
        """Validate reason format."""
        if not v or v.isspace():
            raise ValueError("Reason cannot be empty or only whitespace")
        
        # Check for whitespace (recommended to avoid)
        if ' ' in v:
            # Allow but warn in logs
            pass
        
        # Check for invalid characters that might cause issues
        if re.search(r'[<>:"/\\|?*]', v):
            raise ValueError("Reason contains invalid characters")
        
        return v.strip()

class CIDRResponse(BaseModel):
    """Response model for CIDR allocation."""
    
    cidr: str = Field(
        ...,
        description="Allocated CIDR block",
        example="10.0.1.0/24"
    )
    message: str = Field(
        ...,
        description="Success message",
        example="CIDR allocated successfully"
    )
    
    @validator('cidr')
    def validate_cidr(cls, v):
        """Validate CIDR format."""
        try:
            IPv4Network(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid CIDR format: {v}")

class SubnetRequest(BaseModel):
    """Request model for subnet calculation."""
    
    subnet_size: int = Field(
        ...,
        ge=16,
        le=30,
        description="Target subnet size (CIDR prefix length)",
        example=26
    )
    cidr: str = Field(
        ...,
        description="Source CIDR block to subdivide",
        example="10.0.0.0/24"
    )
    
    @validator('cidr')
    def validate_cidr(cls, v):
        """Validate CIDR format."""
        try:
            network = IPv4Network(v)
            return str(network)
        except ValueError:
            raise ValueError(f"Invalid CIDR format: {v}")
    
    @validator('subnet_size')
    def validate_subnet_size_vs_cidr(cls, v, values):
        """Validate subnet size is larger than source CIDR prefix."""
        if 'cidr' in values:
            try:
                source_network = IPv4Network(values['cidr'])
                if v <= source_network.prefixlen:
                    raise ValueError(f"Subnet size ({v}) must be larger than source CIDR prefix ({source_network.prefixlen})")
            except ValueError as e:
                if "Invalid CIDR format" not in str(e):
                    raise e
        return v

class SubnetResponse(BaseModel):
    """Response model for subnet calculation."""
    
    subnets: List[str] = Field(
        ...,
        description="List of calculated subnets",
        example=["10.0.0.0/26", "10.0.0.64/26", "10.0.0.128/26", "10.0.0.192/26"]
    )
    message: str = Field(
        ...,
        description="Success message",
        example="Subnets calculated successfully"
    )

class DeleteCIDRRequest(BaseModel):
    """Request model for CIDR deletion."""
    
    cidr: str = Field(
        ...,
        description="CIDR block to delete from occupied list",
        example="10.0.1.0/24"
    )
    
    @validator('cidr')
    def validate_cidr(cls, v):
        """Validate CIDR format."""
        try:
            IPv4Network(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid CIDR format: {v}")

class AddCIDRRequest(BaseModel):
    """Request model for manually adding CIDR."""
    
    cidr: str = Field(
        ...,
        description="CIDR block to add to occupied list",
        example="10.0.2.0/24"
    )
    reason: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Reason for manual CIDR addition",
        example="external-allocation"
    )
    
    @validator('cidr')
    def validate_cidr(cls, v):
        """Validate CIDR format."""
        try:
            IPv4Network(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid CIDR format: {v}")
    
    @validator('reason')
    def validate_reason(cls, v):
        """Validate reason format."""
        if not v or v.isspace():
            raise ValueError("Reason cannot be empty or only whitespace")
        
        # Check for invalid characters
        if re.search(r'[<>:"/\\|?*]', v):
            raise ValueError("Reason contains invalid characters")
        
        return v.strip()

class OccupiedListResponse(BaseModel):
    """Response model for occupied CIDR list."""
    
    occupied_cidrs: Dict[str, Any] = Field(
        ...,
        description="Dictionary of occupied CIDR blocks with their reasons and timestamps",
        example={
            "web-server-prod-1694123456": "10.0.1.0/24",
            "database-staging-1694123789": "10.0.2.0/24"
        }
    )
    message: str = Field(
        ...,
        description="Success message",
        example="Occupied list retrieved successfully"
    )

class ErrorResponse(BaseModel):
    """Standard error response model."""
    
    detail: str = Field(
        ...,
        description="Error message",
        example="Invalid CIDR format"
    )

class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: str = Field(
        ...,
        description="Service status",
        example="healthy"
    )
    service: str = Field(
        ...,
        description="Service name",
        example="cidr-manager"
    )
    version: str = Field(
        ...,
        description="Service version",
        example="3.0.0"
    )

# Additional models for enhanced functionality

class CIDRAllocationInfo(BaseModel):
    """Detailed information about a CIDR allocation."""
    
    cidr: str = Field(..., description="CIDR block")
    reason: str = Field(..., description="Allocation reason")
    timestamp: int = Field(..., description="Unix timestamp of allocation")
    allocated_by: Optional[str] = Field(None, description="User who allocated the CIDR")
    
    @validator('cidr')
    def validate_cidr(cls, v):
        """Validate CIDR format."""
        try:
            IPv4Network(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid CIDR format: {v}")

class RangeInfo(BaseModel):
    """Information about available IP ranges."""
    
    range_id: str = Field(..., description="Range identifier", example="10")
    network: str = Field(..., description="Network CIDR", example="10.0.0.0/8")
    description: str = Field(..., description="Range description", example="Class A private range")
    total_addresses: int = Field(..., description="Total available addresses")

class CIDRStatistics(BaseModel):
    """Statistics about CIDR usage."""
    
    total_allocated: int = Field(..., description="Total number of allocated CIDRs")
    by_range: Dict[str, int] = Field(..., description="Allocation count by range")
    by_subnet_size: Dict[str, int] = Field(..., description="Allocation count by subnet size")
    last_allocation: Optional[str] = Field(None, description="Timestamp of last allocation")
