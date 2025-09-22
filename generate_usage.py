#!/usr/bin/env python3
"""
Script to generate OpenAI API usage across different models and endpoints.
This creates usage data that can later be retrieved using main.py for metrics analysis.

Usage:
    python generate_usage.py config.yaml
"""

import sys
import yaml
import time
import random
from datetime import datetime
from openai import OpenAI


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


def generate_chat_completions(client, num_calls=5):
    """Generate chat completion usage across different models."""
    print(f"Generating {num_calls} chat completion requests...")
    
    models = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
    
    prompts = [
        "Write a short poem about artificial intelligence",
        "Explain quantum computing in simple terms",
        "Create a recipe for chocolate chip cookies",
        "Write a brief story about a robot learning to paint",
        "Explain the difference between machine learning and deep learning",
        "Create a marketing slogan for a sustainable energy company",
        "Write a short description of a futuristic city",
        "Explain how photosynthesis works",
        "Create a dialogue between two characters meeting for the first time",
        "Write a brief review of an imaginary science fiction movie"
    ]
    
    successful_calls = 0
    
    for i in range(num_calls):
        try:
            model = random.choice(models)
            prompt = random.choice(prompts)
            
            print(f"  Call {i+1}/{num_calls}: {model} - {prompt[:50]}...")
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=random.randint(100, 300),
                temperature=random.uniform(0.3, 0.9)
            )
            
            usage = response.usage
            print(f"    ✓ Success: {usage.prompt_tokens} input, {usage.completion_tokens} output tokens")
            successful_calls += 1
            
            # Add small delay to avoid rate limiting
            time.sleep(1)
            
        except Exception as e:
            print(f"    ✗ Error: {e}")
    
    print(f"Chat completions: {successful_calls}/{num_calls} successful calls\n")
    return successful_calls


def generate_embeddings(client, num_calls=3):
    """Generate embeddings usage."""
    print(f"Generating {num_calls} embedding requests...")
    
    texts = [
        "Artificial intelligence is transforming the way we work and live",
        "Machine learning algorithms can identify patterns in large datasets",
        "Natural language processing enables computers to understand human language",
        "Computer vision allows machines to interpret and analyze visual information",
        "Deep learning neural networks are inspired by the human brain",
        "Data science combines statistics, programming, and domain expertise",
        "Cloud computing provides scalable and flexible computing resources",
        "Cybersecurity protects digital systems from threats and attacks",
        "Blockchain technology enables secure and decentralized transactions",
        "Internet of Things connects everyday objects to the internet"
    ]
    
    successful_calls = 0
    
    for i in range(num_calls):
        try:
            text_batch = random.sample(texts, random.randint(1, 3))
            
            print(f"  Call {i+1}/{num_calls}: embedding {len(text_batch)} texts")
            
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text_batch
            )
            
            usage = response.usage
            print(f"    ✓ Success: {usage.total_tokens} tokens for {len(response.data)} embeddings")
            successful_calls += 1
            
            time.sleep(1)
            
        except Exception as e:
            print(f"    ✗ Error: {e}")
    
    print(f"Embeddings: {successful_calls}/{num_calls} successful calls\n")
    return successful_calls


def generate_image_generation(client, num_calls=2):
    """Generate DALL-E image generation usage."""
    print(f"Generating {num_calls} image generation requests...")
    
    prompts = [
        "A futuristic cityscape at sunset with flying cars",
        "A cozy library with books floating in mid-air",
        "A robot gardener tending to a flower garden",
        "A steampunk-style coffee machine in a Victorian kitchen",
        "A peaceful mountain lake reflecting the stars",
        "A colorful market street in a fantasy medieval town",
        "A modern office space with holographic displays",
        "A serene bamboo forest with a small pagoda"
    ]
    
    successful_calls = 0
    
    for i in range(num_calls):
        try:
            prompt = random.choice(prompts)
            
            print(f"  Call {i+1}/{num_calls}: DALL-E - {prompt[:50]}...")
            
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )
            
            print(f"    ✓ Success: Generated {len(response.data)} image(s)")
            successful_calls += 1
            
            time.sleep(2)  # Longer delay for image generation
            
        except Exception as e:
            print(f"    ✗ Error: {e}")
    
    print(f"Image generation: {successful_calls}/{num_calls} successful calls\n")
    return successful_calls


def generate_text_to_speech(client, num_calls=2):
    """Generate text-to-speech usage."""
    print(f"Generating {num_calls} text-to-speech requests...")
    
    texts = [
        "Hello, this is a test of OpenAI's text-to-speech capabilities.",
        "Artificial intelligence is revolutionizing how we interact with technology.",
        "The future of computing lies in the seamless integration of AI and human creativity.",
        "Machine learning models are becoming increasingly sophisticated and powerful."
    ]
    
    voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    
    successful_calls = 0
    
    for i in range(num_calls):
        try:
            text = random.choice(texts)
            voice = random.choice(voices)
            
            print(f"  Call {i+1}/{num_calls}: TTS with voice '{voice}' - {text[:50]}...")
            
            response = client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text
            )
            
            print(f"    ✓ Success: Generated speech audio")
            successful_calls += 1
            
            time.sleep(1)
            
        except Exception as e:
            print(f"    ✗ Error: {e}")
    
    print(f"Text-to-speech: {successful_calls}/{num_calls} successful calls\n")
    return successful_calls


def generate_moderation(client, num_calls=3):
    """Generate moderation API usage."""
    print(f"Generating {num_calls} moderation requests...")
    
    texts = [
        "This is a completely normal and appropriate text for testing.",
        "I love spending time with my family and friends on weekends.",
        "Programming is a great skill to learn for career development.",
        "The weather today is perfect for a walk in the park.",
        "I enjoy reading books about science and technology."
    ]
    
    successful_calls = 0
    
    for i in range(num_calls):
        try:
            text = random.choice(texts)
            
            print(f"  Call {i+1}/{num_calls}: Moderation check")
            
            response = client.moderations.create(input=text)
            
            result = response.results[0]
            print(f"    ✓ Success: Flagged={result.flagged}")
            successful_calls += 1
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"    ✗ Error: {e}")
    
    print(f"Moderation: {successful_calls}/{num_calls} successful calls\n")
    return successful_calls


def main():
    """Main function to generate usage across different OpenAI endpoints."""
    if len(sys.argv) != 2:
        print("Usage: python generate_usage.py config.yaml")
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
    print("OPENAI USAGE GENERATOR")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {base_url}")
    print()
    
    client = create_client(api_key, base_url)
    
    total_successful = 0
    
    # Generate different types of usage
    total_successful += generate_chat_completions(client, 8)
    total_successful += generate_embeddings(client, 4) 
    total_successful += generate_moderation(client, 3)
    
    # Optional: Try image generation and TTS (these might not be available in all setups)
    try:
        total_successful += generate_image_generation(client, 1)
    except Exception as e:
        print(f"Image generation not available: {e}\n")
    
    try:
        total_successful += generate_text_to_speech(client, 2)
    except Exception as e:
        print(f"Text-to-speech not available: {e}\n")
    
    print("=" * 60)
    print("USAGE GENERATION COMPLETE")
    print("=" * 60)
    print(f"Total successful API calls: {total_successful}")
    print(f"You can now run 'python main.py {config_file}' to see the usage metrics")
    print("Note: It may take a few minutes for usage data to appear in OpenAI's system")


if __name__ == "__main__":
    main()

