#!/usr/bin/env python3
"""
Test script to verify Hugging Face API connection
"""

import requests
import json

# Your API key
API_KEY = "ur api key here..."

# Test different models
models_to_test = [
    "https://api-inference.huggingface.co/models/google/flan-t5-base",
    "https://api-inference.huggingface.co/models/distilgpt2",
    "https://api-inference.huggingface.co/models/gpt2",
    "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta",
    "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
]

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def test_model(model_url):
    """Test a specific model"""
    print(f"\n🔍 Testing: {model_url.split('/')[-1]}")
    
    payload = {
        "inputs": "Hello, this is a test of medical report simplification.",
        "parameters": {
            "max_length": 100,
            "temperature": 0.7
        }
    }
    
    try:
        response = requests.post(model_url, json=payload, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Response: {str(result)[:200]}...")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def main():
    print("🧪 Testing Hugging Face API Models...")
    print("=" * 50)
    
    working_models = []
    
    for model_url in models_to_test:
        if test_model(model_url):
            working_models.append(model_url.split('/')[-1])
    
    print("\n" + "=" * 50)
    print("📊 Results Summary:")
    
    if working_models:
        print(f"✅ Working models: {', '.join(working_models)}")
        print("🎉 Your API key is working!")
    else:
        print("❌ No models are working. Check your API key permissions.")
        print("💡 Make sure your token has 'Inference API' permissions at:")
        print("   token")

if __name__ == "__main__":
    main()
