"""List available Gemini models."""

import google.generativeai as genai
import os

# Configure API
api_key = "AIzaSyC-dMjyJL4Qlyw_QmcB0KszLpSO8CzO0h4"
genai.configure(api_key=api_key)

print("Available Gemini models:\n")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"  • {model.name}")
        print(f"    Display Name: {model.display_name}")
        print(f"    Description: {model.description[:100]}...")
        print()
