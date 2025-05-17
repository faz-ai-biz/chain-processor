#!/usr/bin/env python3
"""
Chain Processor Demo

This script demonstrates the complete workflow for using the Chain Processor API:
1. Register nodes in the database (if needed)
2. Create a chain strategy
3. Add text processing nodes to the chain
4. Execute the chain with sample text
5. Display the results

Usage:
    python demo_chain_processor.py

Requirements:
    - Docker environment with the Chain Processor services running
    - requests library (pip install requests)
"""

import requests
import json
import sys
import time
import uuid
from typing import Dict, List, Optional

# =============================================================================
# Configuration
# =============================================================================

# API base URL - change to match your deployment
API_URL = "http://10.10.10.187:8095/api"

# Demo options
SAMPLE_TEXT = "Hello world! This is a demonstration of the Chain Processor API."
VERBOSE = True  # Set to False for less output

# =============================================================================
# Utility Functions
# =============================================================================

def print_response(response, message=None):
    """Print a formatted API response with optional message."""
    if message and VERBOSE:
        print(f"\n=== {message} ===")
    
    if VERBOSE:
        print(f"Status Code: {response.status_code}")
        if response.status_code >= 400:
            print("Error:")
    
    try:
        return response.json()
    except:
        if VERBOSE:
            print(response.text)
        return None

def print_separator():
    """Print a separator line."""
    if VERBOSE:
        print("\n" + "=" * 80 + "\n")

def check_api_health():
    """Check if the API is running and healthy."""
    try:
        health_check = requests.get(f"{API_URL.rsplit('/api', 1)[0]}/health")
        if health_check.status_code != 200:
            print("API is not running or health check failed.")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print(f"Cannot connect to API at {API_URL}. Make sure it's running.")
        sys.exit(1)

# =============================================================================
# Node Registration Functions
# =============================================================================

def register_nodes_in_database():
    """Register built-in nodes from registry to database."""
    print_separator()
    print("STEP 1: REGISTER NODES IN DATABASE")
    
    # First check if nodes are already in database
    response = requests.get(f"{API_URL}/nodes/")
    db_nodes = print_response(response, "Current Database Nodes")
    
    if db_nodes and len(db_nodes) > 0:
        print(f"\nFound {len(db_nodes)} nodes already in database.")
        return {node['name']: node['id'] for node in db_nodes}
    
    print("\nNo nodes found in database. Creating sample nodes...")
    
    # Check available node types in registry
    response = requests.get(f"{API_URL}/nodes/available")
    available_nodes = print_response(response, "Available Node Types from Registry")
    
    if not available_nodes or len(available_nodes) == 0:
        print("No nodes available in registry. Please ensure nodes are properly imported.")
        print("Add 'from . import text_processing' to chain_processor_core/src/chain_processor_core/nodes/__init__.py")
        sys.exit(1)
    
    print(f"\nFound {len(available_nodes)} nodes in registry.")
    print("You need to register these in the database using a script inside Docker.")
    print("\nHere's how to do it:")
    print("1. Create a script to register nodes (similar to docker_register_nodes.py)")
    print("2. Copy it to the API container: docker cp script.py chain-processor-api:/app/")
    print("3. Run it in the container: docker exec chain-processor-api python /app/script.py")
    
    print("\nSkipping automatic registration as it requires Docker access...")
    print("Please register nodes manually and rerun this demo.")
    
    return {}

# =============================================================================
# Chain Strategy Functions
# =============================================================================

def create_chain_strategy():
    """Create a new chain strategy."""
    print_separator()
    print("STEP 2: CREATE CHAIN STRATEGY")
    
    chain_data = {
        "name": "Text Processing Demo Chain",
        "description": "A chain that demonstrates text processing capabilities",
        "tags": ["demo", "text", "processing"]
    }
    
    response = requests.post(f"{API_URL}/chains/", json=chain_data)
    result = print_response(response, "Chain Creation Result")
    
    if not result or response.status_code != 200:
        print("Failed to create chain strategy. Exiting.")
        sys.exit(1)
    
    chain_id = result["id"]
    print(f"\nCreated chain with ID: {chain_id}")
    return chain_id

# =============================================================================
# Node Management Functions
# =============================================================================

def add_nodes_to_chain(chain_id, db_nodes):
    """Add nodes to the chain strategy."""
    print_separator()
    print("STEP 3: ADD NODES TO CHAIN")
    
    if not db_nodes:
        print("No nodes available to add to chain. Exiting.")
        sys.exit(1)
    
    # Select nodes for our processing chain (uppercase -> lowercase -> count words)
    preferred_nodes = ['UppercaseNode', 'LowercaseNode', 'count_words']
    node_chain = []
    
    for node_name in preferred_nodes:
        if node_name in db_nodes:
            node_chain.append((node_name, db_nodes[node_name]))
    
    if not node_chain:
        # Fallback to any nodes if our preferred ones aren't available
        node_chain = [(name, id) for name, id in list(db_nodes.items())[:3]]
    
    if not node_chain:
        print("No nodes found to add to chain. Exiting.")
        sys.exit(1)
    
    # Add each node to the chain
    for position, (node_name, node_id) in enumerate(node_chain, 1):
        print(f"Adding node: {node_name} at position {position}")
        
        node_data = {
            "node_id": node_id,
            "position": position,
            "config": {}  # Empty config for simple nodes
        }
        
        response = requests.post(f"{API_URL}/chains/{chain_id}/nodes", json=node_data)
        
        if response.status_code == 201:
            print(f"Successfully added {node_name} to chain at position {position}")
        else:
            print(f"Warning: Failed to add node {node_name} to chain")
            print_response(response)
    
    return [name for name, _ in node_chain]

# =============================================================================
# Chain Execution Functions
# =============================================================================

def execute_chain(chain_id, input_text, db_nodes):
    """Execute the chain with the given input text."""
    print_separator()
    print("STEP 4: EXECUTE CHAIN")
    
    print(f"Input text: \"{input_text}\"")
    print("Executing chain...")
    
    execution_data = {
        "input_text": input_text
    }
    
    response = requests.post(f"{API_URL}/chains/{chain_id}/execute", json=execution_data)
    result = print_response(response, "Chain Execution Result")
    
    if not result or response.status_code != 200:
        print("Chain execution failed.")
        return
    
    # Print a summary of the execution
    print_separator()
    print("STEP 5: EXECUTION SUMMARY")
    
    print(f"Input: {result['input_text']}")
    print(f"Final Output: {result['output_text']}")
    print(f"Execution Status: {result['status']}")
    print(f"Total Execution Time: {result['execution_time_ms']}ms")
    
    print("\nNode Results:")
    for node_result in result.get("node_results", []):
        # Try to map node IDs back to names for clearer output
        node_id = node_result['node_id']
        node_name = "Unknown"
        
        for name, id_val in db_nodes.items():
            if id_val == node_id:
                node_name = name
                break
                
        print(f"- Node: {node_name}")
        print(f"  Input: {node_result['input_text']}")
        print(f"  Output: {node_result['output_text']}")
        print()

# =============================================================================
# Main Demo Function
# =============================================================================

def main():
    """Run the complete demo workflow."""
    print("\n========== CHAIN PROCESSOR API DEMO ==========\n")
    
    # Check if API is running
    check_api_health()
    
    # Register nodes in the database (or get existing ones)
    db_nodes = register_nodes_in_database()
    
    # If no nodes were found and registration was skipped
    if not db_nodes:
        # Try to get nodes again in case they were manually registered
        response = requests.get(f"{API_URL}/nodes/")
        db_nodes = {node['name']: node['id'] for node in response.json()}
    
    if not db_nodes:
        print("No nodes available. Please register nodes and try again.")
        sys.exit(1)
    
    # Create a chain strategy
    chain_id = create_chain_strategy()
    
    # Add nodes to the chain
    node_chain = add_nodes_to_chain(chain_id, db_nodes)
    
    # Execute the chain
    execute_chain(chain_id, SAMPLE_TEXT, db_nodes)
    
    print("\n========== DEMO COMPLETED ==========\n")
    print("Next Steps:")
    print("1. Explore the API documentation at http://10.10.10.187:8095/docs")
    print("2. Create your own chains and node configurations")
    print("3. Develop custom nodes by extending TextChainNode")

if __name__ == "__main__":
    main() 