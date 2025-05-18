#!/usr/bin/env python3
"""
Node Registration Script

This script registers all available nodes from the registry into the database.
"""

import requests
import sys
import os
import uuid

# API base URL - can be overridden with environment variable
API_URL = os.environ.get("API_URL", "http://localhost:8095/api")

def register_nodes():
    """Register all available nodes from the registry to the database."""
    print("Fetching available nodes from registry...")
    
    # Fetch available node types
    response = requests.get(f"{API_URL}/nodes/available")
    if response.status_code != 200:
        print(f"Error fetching available nodes: {response.status_code}")
        print(response.text)
        return False
    
    available_nodes = response.json()
    if not available_nodes:
        print("No nodes available in registry")
        return False
    
    print(f"Found {len(available_nodes)} nodes in registry:")
    for node in available_nodes:
        print(f"- {node}")
    
    # Check if nodes already exist in database
    response = requests.get(f"{API_URL}/nodes/")
    if response.status_code == 200:
        response_data = response.json()
        if response_data and 'items' in response_data and response_data['items']:
            existing_nodes = response_data['items']
            existing_names = [node['name'] for node in existing_nodes]
            print(f"\nFound {len(existing_names)} existing nodes in database: {', '.join(existing_names)}")
            nodes_to_register = [n for n in available_nodes if n not in existing_names]
        else:
            nodes_to_register = available_nodes
    else:
        nodes_to_register = available_nodes
    
    if not nodes_to_register:
        print("All nodes are already registered")
        return True
    
    # Hard-coded node registration script
    # In a real application, you would fetch node metadata from the registry
    node_definitions = {
        "UppercaseNode": {
            "name": "UppercaseNode",
            "description": "Converts text to uppercase",
            "tags": ["text", "transformation"]
        },
        "LowercaseNode": {
            "name": "LowercaseNode",
            "description": "Converts text to lowercase",
            "tags": ["text", "transformation"]
        },
        "ReverseTextNode": {
            "name": "ReverseTextNode",
            "description": "Reverses the input text",
            "tags": ["text", "transformation"]
        },
        "count_words": {
            "name": "count_words",
            "description": "Counts the number of words in the text",
            "tags": ["text", "analysis"]
        },
        "count_characters": {
            "name": "count_characters",
            "description": "Counts the number of characters in the text",
            "tags": ["text", "analysis"]
        },
        "remove_whitespace": {
            "name": "remove_whitespace",
            "description": "Removes extra whitespace from text",
            "tags": ["text", "cleaning"]
        }
    }
    
    # Register each node
    registered_count = 0
    for node_name in nodes_to_register:
        node_data = node_definitions.get(node_name, {
            "name": node_name,
            "description": f"Node type: {node_name}",
            "tags": ["auto-registered"]
        })
        
        print(f"\nRegistering node: {node_name}")
        response = requests.post(f"{API_URL}/nodes/", json=node_data)
        
        if response.status_code == 200:
            registered_node = response.json()
            print(f"Successfully registered {node_name} with ID: {registered_node['id']}")
            registered_count += 1
        else:
            print(f"Failed to register {node_name}: {response.status_code}")
            print(response.text)
    
    print(f"\nRegistered {registered_count} nodes")
    return registered_count > 0

if __name__ == "__main__":
    print("\n===== Node Registration Script =====\n")
    success = register_nodes()
    if success:
        print("\nNode registration completed successfully")
        sys.exit(0)
    else:
        print("\nNode registration failed")
        sys.exit(1) 