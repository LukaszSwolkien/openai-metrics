#!/usr/bin/env python3
"""
Minimal implementation to test retrieving OpenAI project metrics.
Only requires a config.yaml file as argument.

Usage:
    python main.py config.yaml
"""

import sys
import yaml
import requests
from datetime import datetime, timedelta


def load_config(config_file):
    """Load configuration from YAML file."""
    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config file: {e}")
        sys.exit(1)


def test_api_access(api_key, base_url):
    """Test API access for all endpoints: models, organization/projects, organization/costs, and usage."""
    headers = {'Authorization': f'Bearer {api_key}'}
    
    print("Testing API access...")
    
    endpoints_to_test = [
        "/models",                   # basic API connectivity
        "/organization/projects",    # needs api.management.read
        "/organization/costs",       # needs api.usage.read
        "/usage"                     # needs date parameter
    ]
    
    for endpoint in endpoints_to_test:
        try:
            url = f"{base_url}{endpoint}"
            
            # Special handling for /usage endpoint - needs date parameter
            if endpoint == "/usage":
                test_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
                params = {'date': test_date}
                response = requests.get(url, headers=headers, params=params)
            else:
                response = requests.get(url, headers=headers)
                
            if response.status_code == 200:
                if endpoint == "/models":
                    models = response.json().get('data', [])
                    print(f"✓ {endpoint} - accessible ({len(models)} models available)")
                else:
                    print(f"✓ {endpoint} - accessible")
            elif response.status_code == 401:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', 'Unauthorized')
                    print(f"⚠ {endpoint} - 401: {error_msg}")
                except:
                    print(f"⚠ {endpoint} - 401: Unauthorized")
            else:
                print(f"✗ {endpoint} - {response.status_code}")
        except Exception as e:
            print(f"✗ {endpoint} - error: {e}")


def get_usage_metrics(api_key, base_url, start_date, end_date):
    """Retrieve usage metrics using the /usage endpoint for each date."""
    headers = {'Authorization': f'Bearer {api_key}'}
    
    print(f"Retrieving usage data for date range {start_date} to {end_date}")
    
    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        current_dt = start_dt
        
        all_usage_data = {"data": []}
        
        while current_dt <= end_dt:
            date_str = current_dt.strftime('%Y-%m-%d')
            usage_url = f"{base_url}/usage"
            usage_params = {"date": date_str}
            
            print(f"  Retrieving data for: {date_str}")
            usage_response = requests.get(usage_url, headers=headers, params=usage_params)
            
            if usage_response.status_code == 200:
                day_data = usage_response.json()
                if 'data' in day_data and day_data['data']:
                    all_usage_data['data'].extend(day_data['data'])
                    print(f"    ✓ Found usage data for {date_str}")
                else:
                    print(f"    - No usage data for {date_str}")
            else:
                print(f"    ✗ Failed to get data for {date_str}: {usage_response.status_code}")
            
            current_dt += timedelta(days=1)
        
        if all_usage_data['data']:
            print(f"✓ Successfully collected usage data for {len(all_usage_data['data'])} entries")
            return all_usage_data
        else:
            print("No usage data found for the specified date range")
            return None
            
    except Exception as e:
        print(f"✗ Error retrieving usage data: {e}")
        return None


def get_cost_metrics(api_key, base_url, project_id, start_date, end_date):
    """Retrieve cost metrics using the /organization/costs endpoint."""
    headers = {'Authorization': f'Bearer {api_key}'}
    
    try:
        costs_url = f"{base_url}/organization/costs"
        costs_params = {
            'start_date': start_date,
            'end_date': end_date
        }
        if project_id:
            costs_params['project_ids'] = [project_id]
        
        print(f"Retrieving cost data from organization costs endpoint...")
        costs_response = requests.get(costs_url, headers=headers, params=costs_params)
        
        if costs_response.status_code == 200:
            print("✓ Successfully retrieved cost data from organization endpoint")
            return costs_response.json()
        elif costs_response.status_code == 401:
            try:
                error_data = costs_response.json()
                error_msg = error_data.get('error', {}).get('message', 'Unauthorized')
                print(f"⚠ Organization costs endpoint needs higher permissions: {error_msg}")
            except:
                print("⚠ Organization costs endpoint needs higher permissions")
            return None
        else:
            print(f"✗ Organization costs endpoint failed: {costs_response.status_code}")
            return None
            
    except Exception as e:
        print(f"✗ Organization costs endpoint error: {e}")
        return None


def get_project_metrics(api_key, base_url):
    """Retrieve project information using the /organization/projects endpoint."""
    headers = {'Authorization': f'Bearer {api_key}'}
    
    try:
        projects_url = f"{base_url}/organization/projects"
        
        print(f"Retrieving project data from organization projects endpoint...")
        projects_response = requests.get(projects_url, headers=headers)
        
        if projects_response.status_code == 200:
            print("✓ Successfully retrieved project data from organization endpoint")
            return projects_response.json()
        elif projects_response.status_code == 401:
            try:
                error_data = projects_response.json()
                error_msg = error_data.get('error', {}).get('message', 'Unauthorized')
                print(f"⚠ Organization projects endpoint needs higher permissions: {error_msg}")
            except:
                print("⚠ Organization projects endpoint needs higher permissions")
            return None
        else:
            print(f"✗ Organization projects endpoint failed: {projects_response.status_code}")
            return None
            
    except Exception as e:
        print(f"✗ Organization projects endpoint error: {e}")
        return None


def get_all_metrics(api_key, base_url, days_back = 7):
    """Retrieve all available metrics by calling individual metric functions."""
    print("=" * 50)
    print("RETRIEVING METRICS")
    print("=" * 50)
    
    project_data = get_project_metrics(api_key, base_url)
   
    # Calculate date range
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    
    usage_data = get_usage_metrics(api_key, base_url, start_date, end_date)
    print()
    
    cost_data = get_cost_metrics(api_key, base_url, None, start_date, end_date)
    print()
    
    
    return usage_data, cost_data, project_data


def print_usage_metrics(usage_data):
    """Print usage metrics in a formatted way."""
    if not usage_data or 'data' not in usage_data:
        return
        
    total_input_tokens = 0
    total_output_tokens = 0
    
    print("USAGE METRICS:")
    print("-" * 30)
    
    for entry in usage_data['data']:
        date = entry.get('start_time', 'N/A')
        print(f"\nDate: {date}")
        
        for result in entry.get('results', []):
            input_tokens = result.get('input_tokens', 0)
            output_tokens = result.get('output_tokens', 0)
            model = result.get('model', 'N/A')
            
            total_input_tokens += input_tokens
            total_output_tokens += output_tokens
            
            if input_tokens > 0 or output_tokens > 0:
                print(f"  {model}: {input_tokens:,} input, {output_tokens:,} output tokens")
    
    print(f"\nTOTAL TOKENS:")
    print(f"  Input: {total_input_tokens:,}")
    print(f"  Output: {total_output_tokens:,}")


def print_cost_metrics(cost_data):
    """Print cost metrics in a formatted way."""
    if not cost_data or 'data' not in cost_data:
        return
        
    total_cost = 0
    
    print("\nCOST METRICS:")
    print("-" * 30)
    
    for entry in cost_data['data']:
        for result in entry.get('results', []):
            amount = result.get('amount', {})
            cost = amount.get('value', 0) / 100 if amount.get('currency') == 'usd' else 0
            total_cost += cost
    
    print(f"Total Cost: ${total_cost:.4f}")


def print_project_info(project_data):
    """Print project information in a formatted way."""
    if not project_data:
        return
        
    print("\nPROJECT INFORMATION:")
    print("-" * 30)
    
    projects = project_data.get('data', [])
    if projects:
        for project in projects:
            print(f"Project: {project.get('name', 'N/A')} (ID: {project.get('id', 'N/A')})")
    else:
        print("No project data available")


def print_summary():
    """Print summary when no metrics could be retrieved."""
    print("\nSUMMARY:")
    print("-" * 30)
    print("The script successfully connected to OpenAI's API, so the key is valid.")
    print("No usage metrics could be retrieved.")
    print("Some endpoints exist but need higher permissions (shown with ⚠ above).")


def print_all_metrics(usage_data, cost_data, project_data):
    """Print all metrics in a formatted way."""
    
    if usage_data:
        print_usage_metrics(usage_data)
    
    if cost_data:
        print_cost_metrics(cost_data)
    
    if project_data:
        print_project_info(project_data)
    
    if not usage_data and not cost_data:
        print_summary()
    
    print("=" * 50)


def main():
    """Main function."""
    if len(sys.argv) != 2:
        print("Usage: python main.py config.yaml")
        sys.exit(1)
    
    config_file = sys.argv[1]
    config = load_config(config_file)
    
    api_key = config.get('api_key')
    base_url = config.get('base_url', 'https://api.openai.com/v1')
    days_back = config.get('days_back', 7)
    
    if not api_key:
        print("Error: api_key is required in config file")
        sys.exit(1)
    
    # Test API access first
    test_api_access(api_key, base_url)
    print()
    
    
    usage_data, cost_data, project_data = get_all_metrics(api_key, base_url, days_back)
    
    print_all_metrics(usage_data, cost_data, project_data)


if __name__ == "__main__":
    main()
