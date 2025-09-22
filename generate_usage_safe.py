#!/usr/bin/env python3
"""
Safe version of usage generator with rate limiting and retry logic.
This creates minimal usage data that can later be retrieved using main.py for metrics analysis.

Usage:
    python generate_usage_safe.py config.yaml
"""

import sys
import yaml
import time
import random
from datetime import datetime
from openai import OpenAI
import backoff


def load_config(config_file):
    """Load configuration from YAML file."""
    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config file: {e}")
        sys.exit(1)


def create_client(api_key, base_url):
    """Create OpenAI client."""
    try:
        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        return client
    except Exception as e:
        print(f"Error creating OpenAI client: {e}")
        sys.exit(1)


@backoff.on_exception(
    backoff.expo,
    Exception,
    max_tries=3,
    max_time=60,
    jitter=backoff.random_jitter
)
def safe_api_call(func, *args, **kwargs):
    """Wrapper for API calls with exponential backoff."""
    return func(*args, **kwargs)


def generate_minimal_chat_completions(client, num_calls=2):
    """Generate minimal chat completion usage with very short responses."""
    print(f"Generating {num_calls} minimal chat completion requests...")
    
    # Use only the cheapest model
    model = "gpt-3.5-turbo"
    
    # Very short prompts to minimize token usage
    prompts = [
        "Say hi",
        "Count to 3",
        "Name a color",
        "What is 2+2?"
    ]
    
    successful_calls = 0
    
    for i in range(num_calls):
        try:
            prompt = random.choice(prompts)
            
            print(f"  Call {i+1}/{num_calls}: {model} - {prompt}")
            
            response = safe_api_call(
                client.chat.completions.create,
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10,  # Very small response
                temperature=0.5
            )
            
            usage = response.usage
            print(f"    ✓ Success: {usage.prompt_tokens} input, {usage.completion_tokens} output tokens")
            successful_calls += 1
            
            # Longer delay to avoid rate limiting
            time.sleep(5)
            
        except Exception as e:
            print(f"    ✗ Error: {e}")
            if "quota" in str(e).lower() or "billing" in str(e).lower():
                print(f"    ⚠ Billing/quota issue detected. Please check your OpenAI account.")
                break
            time.sleep(10)  # Wait longer on error
    
    print(f"Chat completions: {successful_calls}/{num_calls} successful calls\n")
    return successful_calls


def generate_minimal_embeddings(client, num_calls=1):
    """Generate minimal embeddings usage."""
    print(f"Generating {num_calls} minimal embedding requests...")
    
    # Very short text to minimize token usage
    texts = ["Hello", "Test", "AI", "Data"]
    
    successful_calls = 0
    
    for i in range(num_calls):
        try:
            text = random.choice(texts)
            
            print(f"  Call {i+1}/{num_calls}: embedding '{text}'")
            
            response = safe_api_call(
                client.embeddings.create,
                model="text-embedding-3-small",
                input=text
            )
            
            usage = response.usage
            print(f"    ✓ Success: {usage.total_tokens} tokens")
            successful_calls += 1
            
            time.sleep(5)
            
        except Exception as e:
            print(f"    ✗ Error: {e}")
            if "quota" in str(e).lower() or "billing" in str(e).lower():
                print(f"    ⚠ Billing/quota issue detected. Please check your OpenAI account.")
                break
            time.sleep(10)
    
    print(f"Embeddings: {successful_calls}/{num_calls} successful calls\n")
    return successful_calls


def test_account_status(client):
    """Test account status with a minimal request."""
    print("Testing account status...")
    try:
        # Try the cheapest possible request
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=1
        )
        print("✓ Account status: OK - API key working")
        return True
    except Exception as e:
        print(f"✗ Account status: {e}")
        if "quota" in str(e).lower():
            print("⚠ Quota exceeded - please add credits to your OpenAI account")
        elif "billing" in str(e).lower():
            print("⚠ Billing issue - please check your payment method")
        elif "insufficient" in str(e).lower():
            print("⚠ Insufficient credits - please add credits to your account")
        return False


def main():
    """Main function to generate minimal usage safely."""
    if len(sys.argv) != 2:
        print("Usage: python generate_usage_safe.py config.yaml")
        sys.exit(1)
    
    config_file = sys.argv[1]
    config = load_config(config_file)
    
    api_key = config.get('api_key')
    base_url = config.get('base_url', 'https://api.openai.com/v1')
    
    if not api_key:
        print("Error: api_key is required in config file")
        sys.exit(1)
    
    if api_key == "your-openai-api-key-here":
        print("Error: Please set a valid API key in the config file")
        sys.exit(1)
    
    print("=" * 60)
    print("SAFE OPENAI USAGE GENERATOR")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {base_url}")
    print()
    
    client = create_client(api_key, base_url)
    
    # Test account status first
    if not test_account_status(client):
        print("\n" + "="*60)
        print("CANNOT PROCEED - ACCOUNT ISSUES")
        print("="*60)
        print("Please resolve the account issues above before generating usage data.")
        print("Visit https://platform.openai.com/account/billing to check your account.")
        return
    
    print()
    total_successful = 0
    
    # Generate very minimal usage
    total_successful += generate_minimal_chat_completions(client, 2)
    total_successful += generate_minimal_embeddings(client, 1)
    
    print("=" * 60)
    print("SAFE USAGE GENERATION COMPLETE")
    print("=" * 60)
    print(f"Total successful API calls: {total_successful}")
    
    if total_successful > 0:
        print(f"✓ Successfully generated minimal usage data")
        print(f"You can now run 'python main.py {config_file}' to see the usage metrics")
        print("Note: It may take a few minutes for usage data to appear in OpenAI's system")
    else:
        print("⚠ No usage data was generated due to account issues")
        print("Please resolve billing/quota issues and try again")


if __name__ == "__main__":
    main()
