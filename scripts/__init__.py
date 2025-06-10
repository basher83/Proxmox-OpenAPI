"""
Proxmox OpenAPI Generator Scripts

This package contains scripts for generating OpenAPI specifications
from Proxmox API documentation for both PVE and PBS.
"""

__version__ = "1.0.0"
__author__ = "Proxmox OpenAPI Contributors"
__email__ = ""

from .unified_parser import main as unified_main

__all__ = ["unified_main"] 