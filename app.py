import streamlit as st
import re
import time
import requests
import PyPDF2
import io
from typing import Dict, List

# Hugging Face API details
# Get your free API key from: https://huggingface.co/settings/tokens
# Make sure to select "Inference API" permissions when creating the token
HUGGINGFACE_API_KEY = "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"  # Replace with your actual Hugging Face API key
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
TOKEN_LIMIT = 400
RATE_LIMIT_DELAY = 15

# Alternative: Use a free model that doesn't require special permissions
ALTERNATIVE_API_URL = "https://api-inference.huggingface.co/models/gpt2"

# Page configuration
st.set_page_config(
    page_title="MediSimplify - AI Medical Report Simplifier",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Working Language mapping
LANGUAGE_MAPPING = {
    "English": "English",
    "Hindi": "हिंदी (Hindi)",
    "Bengali": "বাংলা (Bengali)",
    "Telugu": "తెలుగు (Telugu)",
    "Marathi": "मराठी (Marathi)",
    "Tamil": "தமிழ் (Tamil)",
    "Gujarati": "ગુજરાતી (Gujarati)",
    "Kannada": "ಕನ್ನಡ (Kannada)",
    "Malayalam": "മലയാളം (Malayalam)",
    "Punjabi": "ਪੰਜਾਬੀ (Punjabi)",
    "Odia": "ଓଡ଼ିଆ (Odia)",
    "Urdu": "اردو (Urdu)",
    "Spanish": "Español (Spanish)",
    "French": "Français (French)",
    "German": "Deutsch (German)",
    "Chinese": "中文 (Chinese)",
    "Arabic": "العربية (Arabic)",
    "Portuguese": "Português (Portuguese)",
    "Russian": "Русский (Russian)",
    "Japanese": "日本語 (Japanese)",
}

# Enhanced Professional CSS with Medical Theme
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Poppins', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        min-height: 100vh;
    }
    
    /* Main background with medical theme */
    .main .block-container {
        background: linear-gradient(135deg, #2c3e50 0%, #3498db 25%, #9b59b6 50%, #e74c3c 75%, #f39c12 100%);
        background-size: 400% 400%;
        animation: gradientShift 20s ease infinite;
        padding: 2rem 1rem;
        border-radius: 25px;
        margin: 1rem;
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        position: relative;
        overflow: hidden;
    }
    
    .main .block-container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: 
            radial-gradient(circle at 20% 80%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
        animation: backgroundFloat 15s ease-in-out infinite;
        z-index: 0;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes backgroundFloat {
        0%, 100% { transform: translateX(0) translateY(0) rotate(0deg); }
        25% { transform: translateX(-20px) translateY(-10px) rotate(90deg); }
        50% { transform: translateX(20px) translateY(10px) rotate(180deg); }
        75% { transform: translateX(-10px) translateY(20px) rotate(270deg); }
    }
    
    /* Header styling with medical icons */
    .main-header {
        font-family: 'Poppins', sans-serif;
        font-size: 4.5rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(45deg, #3498db 0%, #667eea 100%);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: rainbow 4s ease-in-out infinite;
        margin-bottom: 1.5rem;
        position: relative;
        z-index: 1;
    }
    
    .main-header::before {
        content: '🏥';
        position: absolute;
        left: -80px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 3rem;
        animation: pulse 2s infinite;
    }
    
    .main-header::after {
        content: '💊';
        position: absolute;
        right: -80px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 3rem;
        animation: pulse 2s infinite reverse;
    }
    
    @keyframes rainbow {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    @keyframes pulse {
        0%, 100% { transform: translateY(-50%) scale(1); }
        50% { transform: translateY(-50%) scale(1.1); }
    }
    
    .subtitle {
        text-align: center;
        font-family: 'Poppins', sans-serif;
        font-size: 1.6rem;
        font-weight: 500;
        color: #ffffff;
        margin-bottom: 3rem;
        padding: 1rem 2rem;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        margin: 1rem;
        padding: 1rem;
    }
    
    .sidebar .sidebar-content {
        background: transparent;
    }
    
    /* Card styling */
    .result-box {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
        padding: 2.5rem;
        border-radius: 20px;
        border: none;
        margin: 2rem 0;
        color: #2c3e50 !important;
        font-family: 'Poppins', sans-serif;
        line-height: 1.8;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .result-box::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4, #feca57);
        background-size: 300% 100%;
        animation: rainbow 2s ease-in-out infinite;
    }
    
    .result-box * {
        color: #2c3e50 !important;
    }
    
    /* Translation info box */
    .translation-info {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        color: #1565c0 !important;
        padding: 1.5rem;
        border-radius: 15px;
        border: none;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(33, 150, 243, 0.2);
        border-left: 5px solid #2196f3;
        font-family: 'Poppins', sans-serif;
        font-weight: 500;
    }
    
    .translation-info * {
        color: #1565c0 !important;
    }
    
    /* Feature cards */
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        margin: 1rem 0;
        text-align: center;
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.1), transparent);
        transform: rotate(45deg);
        transition: all 0.5s;
        opacity: 0;
    }
    
    .feature-card:hover::before {
        animation: shine 0.8s ease-in-out;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.4);
    }
    
    @keyframes shine {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); opacity: 0; }
        50% { opacity: 1; }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); opacity: 0; }
    }
    
    /* Language section styling */
    .language-section {
        background: rgba(255, 255, 255, 0.1);
        padding: 2rem;
        border-radius: 20px;
        margin: 2rem 0;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        font-size: 1.1rem;
        box-shadow: 0 8px 25px rgba(255, 107, 107, 0.3);
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(255, 107, 107, 0.4);
        background: linear-gradient(135deg, #ff5252 0%, #26a69a 100%);
    }
    
    /* File uploader styling */
    .stFileUploader > div > div {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        border: 2px dashed #667eea;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div > div:hover {
        background: rgba(255, 255, 255, 1);
        border-color: #4ecdc4;
        transform: scale(1.02);
    }
    
    /* Text area styling */
    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        border: 2px solid #e0e0e0;
        font-family: 'Poppins', sans-serif;
        padding: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        border: 2px solid #e0e0e0;
        font-family: 'Poppins', sans-serif;
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div:hover {
        border-color: #667eea;
    }
    
    /* Radio button styling */
    .stRadio > div {
        background: rgba(255, 255, 255, 0.1);
        padding: 1rem;
        border-radius: 15px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Tab styling */
    .stTabs > div > div > div {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px 15px 0 0;
        backdrop-filter: blur(10px);
    }
    
    .stTabs > div > div > div > button {
        background: transparent;
        color: white;
        font-family: 'Poppins', sans-serif;
        font-weight: 500;
        border-radius: 10px;
        margin: 0.25rem;
        transition: all 0.3s ease;
    }
    
    .stTabs > div > div > div > button:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: translateY(-2px);
    }
    
    /* Success/Error message styling */
    .stSuccess {
        background: linear-gradient(135deg, #4caf50 0%, #8bc34a 100%);
        color: white;
        border-radius: 15px;
        padding: 1rem;
        font-family: 'Poppins', sans-serif;
        font-weight: 500;
    }
    
    .stError {
        background: linear-gradient(135deg, #f44336 0%, #ff5722 100%);
        color: white;
        border-radius: 15px;
        padding: 1rem;
        font-family: 'Poppins', sans-serif;
        font-weight: 500;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #2196f3 0%, #03a9f4 100%);
        color: white;
        border-radius: 15px;
        padding: 1rem;
        font-family: 'Poppins', sans-serif;
        font-weight: 500;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #ff9800 0%, #ffc107 100%);
        color: white;
        border-radius: 15px;
        padding: 1rem;
        font-family: 'Poppins', sans-serif;
        font-weight: 500;
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        color: white;
        padding: 2rem;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        margin-top: 2rem;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        font-family: 'Poppins', sans-serif;
    }
    
    /* Spinner styling */
    .stSpinner > div {
        border-color: #667eea transparent #667eea transparent;
    }
    
    /* Override default text colors */
    .stMarkdown, .stMarkdown p, .stMarkdown div {
        color: #2c3e50 !important;
    }
    
    div[data-testid="stMarkdownContainer"] * {
        color: #2c3e50 !important;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5a6fd8, #6a4190);
    }
    
    /* Medical Icons and Professional Elements */
    .medical-icon {
        font-size: 2.5rem;
        margin: 0 10px;
        display: inline-block;
        animation: pulse 2s infinite;
        filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));
    }
    
    .medical-icon:nth-child(even) {
        animation-delay: 1s;
    }
    
    /* Professional Cards */
    .professional-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
        padding: 2.5rem;
        border-radius: 20px;
        margin: 2rem 0;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.3);
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(10px);
    }
    
    .professional-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb, #f5576c);
        background-size: 300% 100%;
        animation: gradientMove 3s ease infinite;
    }
    
    @keyframes gradientMove {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    /* Status Indicators */
    .status-normal {
        background: linear-gradient(135deg, #4CAF50, #45a049);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        margin: 0.2rem;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
    }
    
    .status-warning {
        background: linear-gradient(135deg, #FF9800, #F57C00);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        margin: 0.2rem;
        box-shadow: 0 4px 15px rgba(255, 152, 0, 0.3);
    }
    
    .status-danger {
        background: linear-gradient(135deg, #F44336, #D32F2F);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        margin: 0.2rem;
        box-shadow: 0 4px 15px rgba(244, 67, 54, 0.3);
    }
    
    /* Enhanced Typography */
    .section-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2c3e50;
        margin: 2rem 0 1rem 0;
        text-align: center;
        position: relative;
    }
    
    .section-title::after {
        content: '';
        position: absolute;
        bottom: -10px;
        left: 50%;
        transform: translateX(-50%);
        width: 100px;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 2px;
    }
    
    /* Loading Animation */
    .loading-spinner {
        display: inline-block;
        width: 40px;
        height: 40px;
        border: 4px solid #f3f3f3;
        border-top: 4px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Enhanced Metrics */
    .metric-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .metric-item {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        transition: transform 0.3s ease;
    }
    
    .metric-item:hover {
        transform: translateY(-5px);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
        font-weight: 500;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Mobile Responsive */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2.5rem;
        }
        
        .main-header::before,
        .main-header::after {
            display: none;
        }
        
        .professional-card {
            padding: 1.5rem;
        }
        
        .metric-container {
            grid-template-columns: 1fr;
        }
    }
</style>
""", unsafe_allow_html=True)

# Function to extract text from PDF
def extract_pdf_text(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return f"Error extracting PDF text: {e}"

# Function to identify medical test types
def identify_test_types(text):
    test_patterns = {
        'CBC': r'(?i)(hemoglobin|hematocrit|white blood cell|red blood cell|platelet|mcv|mch|mchc|wbc|rbc)',
        'Lipid Profile': r'(?i)(cholesterol|triglycerides|hdl|ldl|vldl)',
        'Liver Function': r'(?i)(alt|ast|bilirubin|alkaline phosphatase|ggt|sgpt|sgot)',
        'Kidney Function': r'(?i)(creatinine|urea|bun|egfr)',
        'Thyroid': r'(?i)(tsh|t3|t4|thyroid)',
        'Diabetes': r'(?i)(glucose|hba1c|insulin|blood sugar)',
        'Cardiac': r'(?i)(troponin|ck-mb|bnp|pro-bnp)',
        'Electrolytes': r'(?i)(sodium|potassium|chloride|calcium|magnesium)'
    }
    
    detected_tests = []
    for test_name, pattern in test_patterns.items():
        if re.search(pattern, text):
            detected_tests.append(test_name)
    
    return detected_tests

# FIXED: Enhanced translation function
def simplify_medical_report(text, detected_tests, target_language="English"):
    # For now, use fallback explanation due to API issues
    # TODO: Fix API connection when models are available
    return generate_fallback_explanation(text, detected_tests, target_language)
    # return generate_fallback_explanation(text, detected_tests, target_language) # This line was forcing fallback. Commented out to enable API calls.
    
    # Check if API key is properly configured
    if HUGGINGFACE_API_KEY == "hf_your_api_key_here" or not HUGGINGFACE_API_KEY.startswith("hf_"):
        return generate_fallback_explanation(text, detected_tests, target_language)
    
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    test_context = ", ".join(detected_tests) if detected_tests else "general medical tests"
    
    # Create a comprehensive prompt for medical report simplification
    prompt = f"""You are a medical report simplifier. Convert this complex medical report into simple, patient-friendly explanations in {target_language}.

Medical Report:
{text}

Detected Test Types: {test_context}

Please provide:
1. A simple explanation of what each test measures
2. Whether values are normal, high, or low
3. What abnormal values might mean for health
4. Basic recommendations if applicable
5. A disclaimer about consulting healthcare professionals

Format with emojis and bullet points for better readability. Keep language simple and easy to understand for patients."""

    # Try multiple models in order of preference
    models_to_try = [
        "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium",
        "https://api-inference.huggingface.co/models/gpt2",
        "https://api-inference.huggingface.co/models/distilgpt2",
        "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill",
        "https://api-inference.huggingface.co/models/microsoft/DialoGPT-small"
    ]
    
    for model_url in models_to_try:
        try:
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_length": 800,
                    "temperature": 0.7,
                    "do_sample": True,
                    "top_p": 0.9,
                    "repetition_penalty": 1.1
                }
            }
            
            response = requests.post(model_url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                # Handle different response formats from Hugging Face
                if isinstance(result, list) and len(result) > 0:
                    if "generated_text" in result[0]:
                        generated_text = result[0]["generated_text"]
                    elif "text" in result[0]:
                        generated_text = result[0]["text"]
                    else:
                        generated_text = str(result[0])
                elif isinstance(result, dict):
                    if "generated_text" in result:
                        generated_text = result["generated_text"]
                    elif "text" in result:
                        generated_text = result["text"]
                    else:
                        generated_text = str(result)
                else:
                    generated_text = str(result)
                
                # Clean up the generated text
                if generated_text.startswith(prompt):
                    generated_text = generated_text[len(prompt):].strip()
                
                # If we got a reasonable response, return it
                if len(generated_text) > 50:
                    # DEBUG: Show what language was requested vs what we got
                    if target_language != "English":
                        st.info(f"🔄 Requested translation to: {target_language}")
                        if len(generated_text) > 100:
                            st.info(f"📝 First 100 chars of result: {generated_text[:100]}...")
                    
                    return generated_text
                else:
                    continue  # Try next model
                    
            elif response.status_code == 404:
                st.warning(f"⚠ Model not found: {model_url.split('/')[-1]}. Trying next model...")
                continue  # Try next model
            elif response.status_code == 429:
                st.warning("⏳ Rate limit exceeded. Trying next model...")
                continue  # Try next model
            elif response.status_code == 401:
                return "❌ Authentication failed. Please check your Hugging Face API key."
            elif response.status_code == 403:
                return "❌ Permission denied. Your API key needs 'Inference API' permissions. Please create a new token with proper permissions."
            elif response.status_code == 503:
                st.warning("⏳ Model is loading. Trying next model...")
                continue  # Try next model
            else:
                st.warning(f"⚠ API Error {response.status_code} with {model_url.split('/')[-1]}. Trying next model...")
                continue  # Try next model
                
        except Exception as e:
            st.warning(f"⚠ Error with {model_url.split('/')[-1]}: {str(e)}. Trying next model...")
            continue  # Try next model
    
    # If all models failed, return fallback
    st.warning("⚠ All AI models failed. Using fallback explanation.")
    return generate_fallback_explanation(text, detected_tests, target_language)

def extract_medical_values(text):
    """Extract actual medical values from the report text"""
    import re
    
    values = {}
    
    # Common medical value patterns
    patterns = {
        'hemoglobin': r'(?i)hemoglobin[:\s]([0-9.]+)\s(g/dL|g/dl)',
        'wbc': r'(?i)(white blood cell|wbc)[:\s]([0-9,]+)\s(cells/μL|cells/ul)',
        'platelets': r'(?i)platelets?[:\s]([0-9,]+)\s(cells/μL|cells/ul)',
        'cholesterol': r'(?i)(?:total\s+)?cholesterol[:\s]([0-9]+)\s(mg/dL|mg/dl)',
        'ldl': r'(?i)ldl[:\s]([0-9]+)\s(mg/dL|mg/dl)',
        'hdl': r'(?i)hdl[:\s]([0-9]+)\s(mg/dL|mg/dl)',
        'tsh': r'(?i)tsh[:\s]([0-9.]+)\s(mIU/L|miu/l)',
        't4': r'(?i)t4[:\s]([0-9.]+)\s(μg/dL|ug/dl)',
        'creatinine': r'(?i)creatinine[:\s]([0-9.]+)\s(mg/dL|mg/dl)',
        'bun': r'(?i)bun[:\s]([0-9]+)\s(mg/dL|mg/dl)',
        'glucose': r'(?i)(?:fasting\s+)?(?:glucose|blood\s+sugar)[:\s]([0-9]+)\s(mg/dL|mg/dl)',
        'hba1c': r'(?i)hba1c[:\s]([0-9.]+)\s%'
    }
    
    for key, pattern in patterns.items():
        matches = re.findall(pattern, text)
        if matches:
            if key in ['wbc', 'platelets']:
                # For WBC and platelets, the number is in the second group
                values[key] = matches[0][1].replace(',', '')
            else:
                # For others, the number is in the first group
                values[key] = matches[0][0] if isinstance(matches[0], str) else matches[0][0]
    
    return values

def generate_value_analysis(test_type, extracted_values, target_language="English"):
    """Generate specific analysis based on extracted values"""
    
    if not extracted_values:
        return ""
    
    analysis = ""
    
    is_hindi = target_language == "Hindi"

    if test_type == "CBC":
        if 'hemoglobin' in extracted_values:
            hgb = float(extracted_values['hemoglobin'])
            if hgb < 12:
                status = "कम" if is_hindi else "Low"
                analysis += f"*Hemoglobin: {hgb} g/dL - {status}*\n"
                analysis += "• संभावित एनीमिया - आयरन युक्त भोजन पर विचार करें" if is_hindi else "• Possible anemia - consider iron-rich foods"
            elif hgb > 16:
                status = "उच्च" if is_hindi else "High"
                analysis += f"*Hemoglobin: {hgb} g/dL - {status}*\n"
                analysis += "• निर्जलीकरण या अन्य स्थितियों का संकेत हो सकता है" if is_hindi else "• May indicate dehydration or other conditions"
            else:
                status = "सामान्य" if is_hindi else "Normal"
                analysis += f"*Hemoglobin: {hgb} g/dL - {status}*\n"
        
        if 'wbc' in extracted_values:
            wbc = int(extracted_values['wbc'])
            if wbc > 11000:
                status = "उच्च" if is_hindi else "High"
                analysis += f"*White Blood Cells: {wbc:,} cells/μL - {status}*\n"
                analysis += "• संभावित संक्रमण या सूजन" if is_hindi else "• Possible infection or inflammation"
            elif wbc < 4500:
                status = "कम" if is_hindi else "Low"
                analysis += f"*White Blood Cells: {wbc:,} cells/μL - {status}*\n"
                analysis += "• प्रतिरक्षा प्रणाली की समस्याओं का संकेत हो सकता है" if is_hindi else "• May indicate immune system issues"
            else:
                status = "सामान्य" if is_hindi else "Normal"
                analysis += f"*White Blood Cells: {wbc:,} cells/μL - {status}*\n"
    
    elif test_type == "Lipid Profile":
        if 'cholesterol' in extracted_values:
            chol = int(extracted_values['cholesterol'])
            if chol > 200:
                status = "उच्च" if is_hindi else "High"
                analysis += f"*Total Cholesterol: {chol} mg/dL - {status}*\n"
                analysis += "• हृदय रोग का बढ़ा जोखिम - आहार परिवर्तन पर विचार करें" if is_hindi else "• Increased heart disease risk - consider diet changes"
            else:
                status = "सामान्य" if is_hindi else "Normal"
                analysis += f"*Total Cholesterol: {chol} mg/dL - {status}*\n"
        
        if 'ldl' in extracted_values:
            ldl = int(extracted_values['ldl'])
            if ldl > 100:
                status = "उच्च" if is_hindi else "High"
                analysis += f"*LDL: {ldl} mg/dL - {status}*\n"
                analysis += "• जीवनशैली परिवर्तन और दवा पर विचार करें" if is_hindi else "• Consider lifestyle changes and medication"
            else:
                status = "सामान्य" if is_hindi else "Normal"
                analysis += f"*LDL: {ldl} mg/dL - {status}*\n"
    
    elif test_type == "Thyroid":
        if 'tsh' in extracted_values:
            tsh = float(extracted_values['tsh'])
            if tsh > 4.0:
                status = "उच्च" if is_hindi else "High"
                analysis += f"*TSH: {tsh} mIU/L - {status}*\n"
                analysis += "• संभावित हाइपोथायरॉयडिज्म - एंडोक्रिनोलॉजिस्ट से सलाह लें" if is_hindi else "• Possible hypothyroidism - consult endocrinologist"
            elif tsh < 0.4:
                status = "कम" if is_hindi else "Low"
                analysis += f"*TSH: {tsh} mIU/L - {status}*\n"
                analysis += "• संभावित हाइपरथायरॉयडिज्म - एंडोक्रिनोलॉजिस्ट से सलाह लें" if is_hindi else "• Possible hyperthyroidism - consult endocrinologist"
            else:
                status = "सामान्य" if is_hindi else "Normal"
                analysis += f"*TSH: {tsh} mIU/L - {status}*\n"
    
    elif test_type == "Diabetes":
        if 'glucose' in extracted_values:
            glucose = int(extracted_values['glucose'])
            if glucose > 126:
                status = "उच्च" if is_hindi else "High"
                analysis += f"*Fasting Glucose: {glucose} mg/dL - {status}*\n"
                analysis += "• संभावित मधुमेह - तुरंत डॉक्टर से सलाह लें" if is_hindi else "• Possible diabetes - consult doctor immediately"
            elif glucose > 100:
                status = "सीमा रेखा" if is_hindi else "Borderline"
                analysis += f"*Fasting Glucose: {glucose} mg/dL - {status}*\n"
                analysis += "• प्रीडायबिटीज - निगरानी और जीवनशैली परिवर्तन" if is_hindi else "• Prediabetes - monitor and lifestyle changes"
            else:
                status = "सामान्य" if is_hindi else "Normal"
                analysis += f"*Fasting Glucose: {glucose} mg/dL - {status}*\n"
    
    return analysis

def generate_fallback_explanation(text, detected_tests, target_language="English"):
    """Generate a comprehensive medical explanation without API calls"""
    
    # Extract actual values from the medical report
    extracted_values = extract_medical_values(text)
    
    # Comprehensive medical explanations for common tests
    explanations = {
        "CBC": {
            "English": """🩸 *Complete Blood Count (CBC) Analysis*

*What it measures:*
• Red blood cells (RBC) - carry oxygen throughout your body
• White blood cells (WBC) - fight infections and diseases
• Hemoglobin (Hgb) - protein that carries oxygen in red blood cells
• Hematocrit (Hct) - percentage of blood made up by red blood cells
• Platelets - help with blood clotting

*Normal ranges:*
• Hemoglobin: 12-16 g/dL (women), 14-18 g/dL (men)
• White blood cells: 4,500-11,000 cells/μL
• Platelets: 150,000-450,000 cells/μL

*What abnormal values might mean:*
• Low hemoglobin: Possible anemia, iron deficiency
• High WBC: Possible infection or inflammation
• Low platelets: Risk of bleeding

*Recommendations:*
• Eat iron-rich foods (spinach, red meat, beans)
• Stay hydrated
• Follow up with your doctor for detailed interpretation""",
            
            "Hindi": """🩸 *पूर्ण रक्त गणना (CBC) विश्लेषण*

*यह क्या मापता है:*
• लाल रक्त कोशिकाएं (RBC) - आपके शरीर में ऑक्सीजन ले जाती हैं
• सफेद रक्त कोशिकाएं (WBC) - संक्रमण और बीमारियों से लड़ती हैं
• हीमोग्लोबिन (Hgb) - लाल रक्त कोशिकाओं में ऑक्सीजन ले जाने वाला प्रोटीन
• हेमाटोक्रिट (Hct) - लाल रक्त कोशिकाओं से बने रक्त का प्रतिशत
• प्लेटलेट्स - रक्त के थक्के जमाने में मदद करते हैं

*सामान्य सीमा:*
• हीमोग्लोबिन: 12-16 g/dL (महिलाएं), 14-18 g/dL (पुरुष)
• सफेद रक्त कोशिकाएं: 4,500-11,000 cells/μL
• प्लेटलेट्स: 150,000-450,000 cells/μL

*असामान्य मूल्यों का मतलब:*
• कम हीमोग्लोबिन: संभावित एनीमिया, आयरन की कमी
• उच्च WBC: संभावित संक्रमण या सूजन
• कम प्लेटलेट्स: रक्तस्राव का जोखिम

*सुझाव:*
• आयरन युक्त भोजन खाएं (पालक, लाल मांस, बीन्स)
• हाइड्रेटेड रहें
• विस्तृत व्याख्या के लिए अपने डॉक्टर से मिलें"""
        },
        
        "Lipid Profile": {
            "English": """💓 *Lipid Profile Analysis*

*What it measures:*
• Total Cholesterol - overall cholesterol level
• LDL (Bad Cholesterol) - can build up in arteries
• HDL (Good Cholesterol) - helps remove cholesterol from arteries
• Triglycerides - stored fat used for energy

*Normal ranges:*
• Total Cholesterol: < 200 mg/dL
• LDL: < 100 mg/dL (optimal)
• HDL: > 60 mg/dL (good)
• Triglycerides: < 150 mg/dL

*What abnormal values might mean:*
• High LDL: Increased heart disease risk
• Low HDL: Higher risk of heart problems
• High triglycerides: Risk of metabolic syndrome

*Recommendations:*
• Eat heart-healthy foods (fruits, vegetables, whole grains)
• Limit saturated and trans fats
• Exercise regularly
• Maintain healthy weight""",
            
            "Hindi": """💓 *लिपिड प्रोफाइल विश्लेषण*

*यह क्या मापता है:*
• कुल कोलेस्ट्रॉल - समग्र कोलेस्ट्रॉल स्तर
• LDL (खराब कोलेस्ट्रॉल) - धमनियों में जमा हो सकता है
• HDL (अच्छा कोलेस्ट्रॉल) - धमनियों से कोलेस्ट्रॉल हटाने में मदद करता है
• ट्राइग्लिसराइड्स - ऊर्जा के लिए उपयोग की जाने वाली संग्रहीत वसा

*सामान्य सीमा:*
• कुल कोलेस्ट्रॉल: < 200 mg/dL
• LDL: < 100 mg/dL (इष्टतम)
• HDL: > 60 mg/dL (अच्छा)
• ट्राइग्लिसराइड्स: < 150 mg/dL

*असामान्य मूल्यों का मतलब:*
• उच्च LDL: हृदय रोग का बढ़ा जोखिम
• कम HDL: हृदय समस्याओं का अधिक जोखिम
• उच्च ट्राइग्लिसराइड्स: मेटाबॉलिक सिंड्रोम का जोखिम

*सुझाव:*
• हृदय-स्वस्थ भोजन खाएं (फल, सब्जियां, साबुत अनाज)
• संतृप्त और ट्रांस वसा सीमित करें
• नियमित व्यायाम करें
• स्वस्थ वजन बनाए रखें"""
        },
        
        "Liver Function": {
            "English": """🫀 *Liver Function Tests*

*What it measures:*
• ALT/SGPT - enzyme that indicates liver damage
• AST/SGOT - enzyme found in liver and other organs
• Bilirubin - waste product processed by liver
• ALP - enzyme related to bile ducts

*Normal ranges:*
• ALT: 7-56 U/L
• AST: 10-40 U/L
• Bilirubin: 0.1-1.2 mg/dL
• ALP: 44-147 U/L

*What abnormal values might mean:*
• High ALT/AST: Possible liver damage or inflammation
• High bilirubin: Possible liver or bile duct problems
• High ALP: Possible bile duct obstruction

*Recommendations:*
• Avoid alcohol and unnecessary medications
• Eat liver-friendly foods (leafy greens, nuts, fish)
• Stay hydrated
• Consult your doctor for further evaluation""",
            
            "Hindi": """🫀 *यकृत कार्य परीक्षण*

*यह क्या मापता है:*
• ALT/SGPT - एंजाइम जो यकृत क्षति का संकेत देता है
• AST/SGOT - यकृत और अन्य अंगों में पाया जाने वाला एंजाइम
• बिलीरुबिन - यकृत द्वारा संसाधित अपशिष्ट उत्पाद
• ALP - पित्त नलिकाओं से संबंधित एंजाइम

*सामान्य सीमा:*
• ALT: 7-56 U/L
• AST: 10-40 U/L
• बिलीरुबिन: 0.1-1.2 mg/dL
• ALP: 44-147 U/L

*असामान्य मूल्यों का मतलब:*
• उच्च ALT/AST: संभावित यकृत क्षति या सूजन
• उच्च बिलीरुबिन: संभावित यकृत या पित्त नलिका समस्याएं
• उच्च ALP: संभावित पित्त नलिका अवरोध

*सुझाव:*
• शराब और अनावश्यक दवाओं से बचें
• यकृत-स्वस्थ भोजन खाएं (पत्तेदार साग, नट्स, मछली)
• हाइड्रेटेड रहें
• आगे के मूल्यांकन के लिए अपने डॉक्टर से सलाह लें"""
        },
        
        "Thyroid": {
            "English": """🦋 *Thyroid Function Tests*

*What it measures:*
• TSH (Thyroid Stimulating Hormone) - controls thyroid function
• T3 (Triiodothyronine) - active thyroid hormone
• T4 (Thyroxine) - main thyroid hormone

*Normal ranges:*
• TSH: 0.4-4.0 mIU/L
• T3: 80-200 ng/dL
• T4: 4.5-12.5 μg/dL

*What abnormal values might mean:*
• High TSH: Possible hypothyroidism (underactive thyroid)
• Low TSH: Possible hyperthyroidism (overactive thyroid)
• High T3/T4: Possible hyperthyroidism
• Low T3/T4: Possible hypothyroidism

*Recommendations:*
• Follow up with an endocrinologist
• Monitor symptoms (fatigue, weight changes, mood)
• Take medications as prescribed
• Regular follow-up blood tests""",
            
            "Hindi": """🦋 *थायरॉयड कार्य परीक्षण*

*यह क्या मापता है:*
• TSH (थायरॉयड स्टिमुलेटिंग हार्मोन) - थायरॉयड कार्य को नियंत्रित करता है
• T3 (ट्राईआयोडोथायरोनिन) - सक्रिय थायरॉयड हार्मोन
• T4 (थायरोक्सिन) - मुख्य थायरॉयड हार्मोन

*सामान्य सीमा:*
• TSH: 0.4-4.0 mIU/L
• T3: 80-200 ng/dL
• T4: 4.5-12.5 μg/dL

*असामान्य मूल्यों का मतलब:*
• उच्च TSH: संभावित हाइपोथायरॉयडिज्म (अंडरएक्टिव थायरॉयड)
• कम TSH: संभावित हाइपरथायरॉयडिज्म (ओवरएक्टिव थायरॉयड)
• उच्च T3/T4: संभावित हाइपरथायरॉयडिज्म
• कम T3/T4: संभावित हाइपोथायरॉयडिज्म

*सुझाव:*
• एंडोक्रिनोलॉजिस्ट से फॉलो-अप करें
• लक्षणों की निगरानी करें (थकान, वजन परिवर्तन, मूड)
• निर्धारित दवाएं लें
• नियमित फॉलो-अप रक्त परीक्षण"""
        },
        
        "Diabetes": {
            "English": """🍯 *Diabetes Tests*

*What it measures:*
• Fasting Glucose - blood sugar after 8+ hours without food
• HbA1c - average blood sugar over 2-3 months
• Random Glucose - blood sugar at any time

*Normal ranges:*
• Fasting Glucose: 70-100 mg/dL
• HbA1c: < 5.7%
• Random Glucose: < 140 mg/dL

*What abnormal values might mean:*
• High fasting glucose: Possible diabetes or prediabetes
• High HbA1c: Poor long-term blood sugar control
• High random glucose: Possible diabetes

*Recommendations:*
• Monitor blood sugar regularly
• Follow a diabetic-friendly diet
• Exercise regularly
• Take medications as prescribed
• Regular check-ups with your doctor""",
            
            "Hindi": """🍯 *मधुमेह परीक्षण*

*यह क्या मापता है:*
• फास्टिंग ग्लूकोज - 8+ घंटे बिना भोजन के रक्त शर्करा
• HbA1c - 2-3 महीनों में औसत रक्त शर्करा
• रैंडम ग्लूकोज - किसी भी समय रक्त शर्करा

*सामान्य सीमा:*
• फास्टिंग ग्लूकोज: 70-100 mg/dL
• HbA1c: < 5.7%
• रैंडम ग्लूकोज: < 140 mg/dL

*असामान्य मूल्यों का मतलब:*
• उच्च फास्टिंग ग्लूकोज: संभावित मधुमेह या प्रीडायबिटीज
• उच्च HbA1c: खराब दीर्घकालिक रक्त शर्करा नियंत्रण
• उच्च रैंडम ग्लूकोज: संभावित मधुमेह

*सुझाव:*
• रक्त शर्करा की नियमित निगरानी करें
• मधुमेह-अनुकूल आहार का पालन करें
• नियमित व्यायाम करें
• निर्धारित दवाएं लें
• अपने डॉक्टर के साथ नियमित जांच"""
        },
        
        "Kidney Function": {
            "English": """🫘 *Kidney Function Tests*

*What it measures:*
• Creatinine - waste product filtered by kidneys
• BUN (Blood Urea Nitrogen) - nitrogen waste in blood
• eGFR - estimated kidney filtering function
• Uric Acid - waste product from protein breakdown

*Normal ranges:*
• Creatinine: 0.6-1.2 mg/dL (men), 0.5-1.1 mg/dL (women)
• BUN: 7-20 mg/dL
• eGFR: > 60 mL/min/1.73m²
• Uric Acid: 3.5-7.0 mg/dL (men), 2.5-6.0 mg/dL (women)

*What abnormal values might mean:*
• High creatinine: Possible kidney dysfunction
• High BUN: Possible kidney problems or dehydration
• Low eGFR: Reduced kidney function
• High uric acid: Possible gout or kidney stones

*Recommendations:*
• Stay well hydrated
• Limit protein intake if advised
• Control blood pressure and diabetes
• Avoid excessive salt
• Regular follow-up with nephrologist""",
            
            "Hindi": """🫘 *गुर्दे के कार्य परीक्षण*

*यह क्या मापता है:*
• क्रिएटिनिन - गुर्दे द्वारा फिल्टर किया गया अपशिष्ट उत्पाद
• BUN (ब्लड यूरिया नाइट्रोजन) - रक्त में नाइट्रोजन अपशिष्ट
• eGFR - अनुमानित गुर्दे की फिल्टरिंग कार्य
• यूरिक एसिड - प्रोटीन टूटने से अपशिष्ट उत्पाद

*सामान्य सीमा:*
• क्रिएटिनिन: 0.6-1.2 mg/dL (पुरुष), 0.5-1.1 mg/dL (महिलाएं)
• BUN: 7-20 mg/dL
• eGFR: > 60 mL/min/1.73m²
• यूरिक एसिड: 3.5-7.0 mg/dL (पुरुष), 2.5-6.0 mg/dL (महिलाएं)

*असामान्य मूल्यों का मतलब:*
• उच्च क्रिएटिनिन: संभावित गुर्दे की शिथिलता
• उच्च BUN: संभावित गुर्दे की समस्याएं या निर्जलीकरण
• कम eGFR: कम गुर्दे का कार्य
• उच्च यूरिक एसिड: संभावित गाउट या गुर्दे की पथरी

*सुझाव:*
• अच्छी तरह हाइड्रेटेड रहें
• सलाह दी गई हो तो प्रोटीन सेवन सीमित करें
• रक्तचाप और मधुमेह को नियंत्रित करें
• अत्यधिक नमक से बचें
• नेफ्रोलॉजिस्ट के साथ नियमित फॉलो-अप"""
        },
        
        "Cardiac": {
            "English": """❤ *Cardiac Markers*

*What it measures:*
• Troponin - protein released during heart muscle damage
• CK-MB - enzyme released from heart muscle
• BNP/NT-proBNP - hormone indicating heart failure
• Myoglobin - protein released from muscle damage

*Normal ranges:*
• Troponin I: < 0.04 ng/mL
• Troponin T: < 0.01 ng/mL
• CK-MB: < 5.0 ng/mL
• BNP: < 100 pg/mL
• Myoglobin: < 90 ng/mL

*What abnormal values might mean:*
• High troponin: Possible heart attack or heart damage
• High CK-MB: Heart muscle injury
• High BNP: Possible heart failure
• High myoglobin: Muscle damage (heart or other muscles)

*Recommendations:*
• Seek immediate medical attention if high
• Follow cardiac rehabilitation program
• Take prescribed heart medications
• Maintain heart-healthy lifestyle
• Regular cardiology follow-up""",
            
            "Hindi": """❤ *हृदय मार्कर*

*यह क्या मापता है:*
• ट्रोपोनिन - हृदय की मांसपेशी क्षति के दौरान जारी प्रोटीन
• CK-MB - हृदय की मांसपेशी से जारी एंजाइम
• BNP/NT-proBNP - हृदय की विफलता का संकेत देने वाला हार्मोन
• मायोग्लोबिन - मांसपेशी क्षति से जारी प्रोटीन

*सामान्य सीमा:*
• ट्रोपोनिन I: < 0.04 ng/mL
• ट्रोपोनिन T: < 0.01 ng/mL
• CK-MB: < 5.0 ng/mL
• BNP: < 100 pg/mL
• मायोग्लोबिन: < 90 ng/mL

*असामान्य मूल्यों का मतलब:*
• उच्च ट्रोपोनिन: संभावित हृदयाघात या हृदय क्षति
• उच्च CK-MB: हृदय की मांसपेशी चोट
• उच्च BNP: संभावित हृदय की विफलता
• उच्च मायोग्लोबिन: मांसपेशी क्षति (हृदय या अन्य मांसपेशियां)

*सुझाव:*
• उच्च होने पर तुरंत चिकित्सा सहायता लें
• हृदय पुनर्वास कार्यक्रम का पालन करें
• निर्धारित हृदय दवाएं लें
• हृदय-स्वस्थ जीवनशैली बनाए रखें
• नियमित कार्डियोलॉजी फॉलो-अप"""
        },
        
        "Electrolytes": {
            "English": """⚡ *Electrolyte Panel*

*What it measures:*
• Sodium (Na) - maintains fluid balance and nerve function
• Potassium (K) - essential for heart and muscle function
• Chloride (Cl) - helps maintain acid-base balance
• Calcium (Ca) - important for bones and muscle function
• Magnesium (Mg) - supports muscle and nerve function

*Normal ranges:*
• Sodium: 136-145 mEq/L
• Potassium: 3.5-5.0 mEq/L
• Chloride: 98-107 mEq/L
• Calcium: 8.5-10.5 mg/dL
• Magnesium: 1.7-2.2 mg/dL

*What abnormal values might mean:*
• High sodium: Dehydration or kidney problems
• Low potassium: Muscle weakness, heart rhythm issues
• High calcium: Possible bone disease or parathyroid issues
• Low magnesium: Muscle cramps, irregular heartbeat

*Recommendations:*
• Stay well hydrated
• Eat balanced diet with fruits and vegetables
• Limit processed foods high in sodium
• Take supplements only if prescribed
• Regular monitoring if levels are abnormal""",
            
            "Hindi": """⚡ *इलेक्ट्रोलाइट पैनल*

*यह क्या मापता है:*
• सोडियम (Na) - द्रव संतुलन और तंत्रिका कार्य बनाए रखता है
• पोटेशियम (K) - हृदय और मांसपेशी कार्य के लिए आवश्यक
• क्लोराइड (Cl) - अम्ल-क्षार संतुलन बनाए रखने में मदद करता है
• कैल्शियम (Ca) - हड्डियों और मांसपेशी कार्य के लिए महत्वपूर्ण
• मैग्नीशियम (Mg) - मांसपेशी और तंत्रिका कार्य का समर्थन करता है

*सामान्य सीमा:*
• सोडियम: 136-145 mEq/L
• पोटेशियम: 3.5-5.0 mEq/L
• क्लोराइड: 98-107 mEq/L
• कैल्शियम: 8.5-10.5 mg/dL
• मैग्नीशियम: 1.7-2.2 mg/dL

*असामान्य मूल्यों का मतलब:*
• उच्च सोडियम: निर्जलीकरण या गुर्दे की समस्याएं
• कम पोटेशियम: मांसपेशी कमजोरी, हृदय ताल समस्याएं
• उच्च कैल्शियम: संभावित हड्डी रोग या पैराथायरॉयड समस्याएं
• कम मैग्नीशियम: मांसपेशी ऐंठन, अनियमित हृदय ताल

*सुझाव:*
• अच्छी तरह हाइड्रेटेड रहें
• फल और सब्जियों के साथ संतुलित आहार लें
• सोडियम में उच्च प्रसंस्कृत खाद्य पदार्थ सीमित करें
• केवल निर्धारित होने पर सप्लीमेंट लें
• स्तर असामान्य होने पर नियमित निगरानी"""
        }
    }
    
    # Generate explanation based on detected tests with actual values
    if detected_tests:
        test_explanations = []
        for test in detected_tests:
            if test in explanations:
                base_explanation = explanations[test].get(target_language, explanations[test]["English"])
                
                # Add specific value analysis if we have extracted values
                value_analysis = generate_value_analysis(test, extracted_values, target_language)
                if value_analysis:
                    base_explanation += "\n\n" + value_analysis
                
                test_explanations.append(base_explanation)
        
        if test_explanations:
            result = "\n\n" + "="*50 + "\n\n".join(test_explanations)
        else:
            result = explanations["CBC"].get(target_language, explanations["CBC"]["English"])
    else:
        result = explanations["CBC"].get(target_language, explanations["CBC"]["English"])
    
    # Add comprehensive general health tips
    health_tips = {
        "English": """
🏥 *Comprehensive Health Guidelines:*

*💧 Hydration & Nutrition:*
• Drink 8-10 glasses of water daily
• Eat 5-7 servings of fruits and vegetables
• Include whole grains, lean proteins, and healthy fats
• Limit processed foods, sugar, and excessive salt
• Consider portion control and mindful eating

*🏃‍♂ Physical Activity:*
• Aim for 150 minutes of moderate exercise weekly
• Include both cardio and strength training
• Take regular breaks from sitting
• Walk 10,000 steps daily if possible
• Find activities you enjoy to stay consistent

*😴 Sleep & Recovery:*
• Maintain consistent sleep schedule
• Create a relaxing bedtime routine
• Keep bedroom cool, dark, and quiet
• Avoid screens 1 hour before bed
• Aim for 7-9 hours of quality sleep

*🧘‍♀ Mental Health:*
• Practice stress management techniques
• Take time for hobbies and relaxation
• Stay connected with family and friends
• Consider meditation or deep breathing
• Seek professional help if needed

*🚭 Lifestyle Choices:*
• Avoid smoking and secondhand smoke
• Limit alcohol to moderate amounts
• Practice safe sun exposure
• Maintain good hygiene habits
• Stay up-to-date with vaccinations

*🏥 Preventive Care:*
• Schedule regular health check-ups
• Know your family medical history
• Monitor vital signs (blood pressure, weight)
• Get recommended screenings
• Keep a personal health record""",
        
        "Hindi": """
🏥 *व्यापक स्वास्थ्य दिशानिर्देश:*

*💧 हाइड्रेशन और पोषण:*
• दैनिक 8-10 गिलास पानी पिएं
• 5-7 सर्विंग फल और सब्जियां खाएं
• साबुत अनाज, लीन प्रोटीन और स्वस्थ वसा शामिल करें
• प्रसंस्कृत खाद्य पदार्थ, चीनी और अत्यधिक नमक सीमित करें
• पोर्शन कंट्रोल और माइंडफुल ईटिंग पर विचार करें

*🏃‍♂ शारीरिक गतिविधि:*
• साप्ताहिक 150 मिनट मध्यम व्यायाम का लक्ष्य रखें
• कार्डियो और स्ट्रेंथ ट्रेनिंग दोनों शामिल करें
• बैठने से नियमित ब्रेक लें
• यदि संभव हो तो दैनिक 10,000 कदम चलें
• निरंतर रहने के लिए ऐसी गतिविधियां खोजें जो आपको पसंद हों

*😴 नींद और रिकवरी:*
• निरंतर नींद का समय बनाए रखें
• आरामदायक सोने की दिनचर्या बनाएं
• बेडरूम को ठंडा, अंधेरा और शांत रखें
• सोने से 1 घंटे पहले स्क्रीन से बचें
• 7-9 घंटे गुणवत्तापूर्ण नींद का लक्ष्य रखें

*🧘‍♀ मानसिक स्वास्थ्य:*
• तनाव प्रबंधन तकनीकों का अभ्यास करें
• शौक और विश्राम के लिए समय निकालें
• परिवार और दोस्तों के साथ जुड़े रहें
• ध्यान या गहरी सांस लेने पर विचार करें
• आवश्यकता हो तो पेशेवर मदद लें

*🚭 जीवनशैली विकल्प:*
• धूम्रपान और सेकेंडहैंड स्मोक से बचें
• शराब को मध्यम मात्रा तक सीमित करें
• सुरक्षित सूर्य एक्सपोजर का अभ्यास करें
• अच्छी स्वच्छता आदतें बनाए रखें
• टीकाकरण के साथ अपडेट रहें

*🏥 निवारक देखभाल:*
• नियमित स्वास्थ्य जांच शेड्यूल करें
• अपने पारिवारिक चिकित्सा इतिहास को जानें
• महत्वपूर्ण संकेतों की निगरानी करें (रक्तचाप, वजन)
• अनुशंसित स्क्रीनिंग करवाएं
• व्यक्तिगत स्वास्थ्य रिकॉर्ड रखें"""
    }
    
    result += health_tips.get(target_language, health_tips["English"])
    
    # Add summary section
    summary = generate_summary(extracted_values, detected_tests, target_language)
    if summary:
        result += "\n\n" + "="*50 + "\n" + summary
    
    # Add disclaimer
    disclaimer = {
        "English": "\n\n⚠ *Important Disclaimer*: This is a basic educational explanation. Always consult your healthcare provider for detailed interpretation of your medical report and personalized medical advice.",
        "Hindi": "\n\n⚠ *महत्वपूर्ण अस्वीकरण*: यह एक बुनियादी शैक्षिक व्याख्या है। अपनी चिकित्सा रिपोर्ट की विस्तृत व्याख्या और व्यक्तिगत चिकित्सा सलाह के लिए हमेशा अपने स्वास्थ्य सेवा प्रदाता से सलाह लें।"
    }
    
    result += disclaimer.get(target_language, disclaimer["English"])
    
    # Add API setup reminder
    result += f"\n\n🔑 *Note*: For AI-powered detailed analysis, please set up your Hugging Face API key with 'Inference API' permissions at https://huggingface.co/settings/tokens"
    
    return result

def generate_summary(extracted_values, detected_tests, target_language="English"):
    """Generate an overall summary of the medical report"""
    
    if not extracted_values:
        return ""
    
    summary = ""
    
    if target_language == "Hindi":  # Hindi
        summary += "📊 *रिपोर्ट सारांश:*\n\n"
        
        # Count abnormal values
        abnormal_count = 0
        normal_count = 0
        
        # Check each value
        if 'hemoglobin' in extracted_values:
            hgb = float(extracted_values['hemoglobin'])
            if hgb < 12 or hgb > 16:
                abnormal_count += 1
            else:
                normal_count += 1
        
        if 'cholesterol' in extracted_values:
            chol = int(extracted_values['cholesterol'])
            if chol > 200:
                abnormal_count += 1
            else:
                normal_count += 1
        
        if 'tsh' in extracted_values:
            tsh = float(extracted_values['tsh'])
            if tsh < 0.4 or tsh > 4.0:
                abnormal_count += 1
            else:
                normal_count += 1
        
        if 'glucose' in extracted_values:
            glucose = int(extracted_values['glucose'])
            if glucose > 100:
                abnormal_count += 1
            else:
                normal_count += 1
        
        # Generate summary based on counts
        if abnormal_count == 0:
            summary += "✅ *समग्र स्थिति: सभी मूल्य सामान्य सीमा में प्रतीत होते हैं*\n"
            summary += "• स्वस्थ जीवनशैली बनाए रखें\n"
            summary += "• नियमित जांच की सिफारिश\n"
        elif abnormal_count <= 2:
            summary += "⚠ *समग्र स्थिति: कुछ मूल्यों पर ध्यान देने की आवश्यकता*\n"
            summary += "• असामान्य मूल्यों की निकट निगरानी करें\n"
            summary += "• जीवनशैली संशोधन पर विचार करें\n"
            summary += "• अपने डॉक्टर से फॉलो-अप करें\n"
        else:
            summary += "🚨 *समग्र स्थिति: कई मूल्यों पर तुरंत ध्यान देने की आवश्यकता*\n"
            summary += "• जल्द से जल्द अपने डॉक्टर से सलाह लें\n"
            summary += "• व्यापक स्वास्थ्य मूल्यांकन पर विचार करें\n"
            summary += "• चिकित्सा सिफारिशों का बारीकी से पालन करें\n"
        
        summary += f"\n*विश्लेषित मूल्य:* {len(extracted_values)} परीक्षण\n"
        summary += f"*सामान्य:* {normal_count} | *असामान्य:* {abnormal_count}\n"
    else:  # English and other languages default to English
        summary += "📊 *Report Summary:*\n\n"
        
        # Count abnormal values
        abnormal_count = 0
        normal_count = 0
        
        # Check each value
        if 'hemoglobin' in extracted_values:
            hgb = float(extracted_values['hemoglobin'])
            if hgb < 12 or hgb > 16:
                abnormal_count += 1
            else:
                normal_count += 1
        
        if 'cholesterol' in extracted_values:
            chol = int(extracted_values['cholesterol'])
            if chol > 200:
                abnormal_count += 1
            else:
                normal_count += 1
        
        if 'tsh' in extracted_values:
            tsh = float(extracted_values['tsh'])
            if tsh < 0.4 or tsh > 4.0:
                abnormal_count += 1
            else:
                normal_count += 1
        
        if 'glucose' in extracted_values:
            glucose = int(extracted_values['glucose'])
            if glucose > 100:
                abnormal_count += 1
            else:
                normal_count += 1
        
        # Generate summary based on counts
        if abnormal_count == 0:
            summary += "✅ *Overall Status: All values appear to be within normal ranges*\n"
            summary += "• Continue maintaining healthy lifestyle\n"
            summary += "• Regular check-ups recommended\n"
        elif abnormal_count <= 2:
            summary += "⚠ *Overall Status: Some values need attention*\n"
            summary += "• Monitor abnormal values closely\n"
            summary += "• Consider lifestyle modifications\n"
            summary += "• Follow up with your doctor\n"
        else:
            summary += "🚨 *Overall Status: Multiple values require immediate attention*\n"
            summary += "• Consult your doctor as soon as possible\n"
            summary += "• Consider comprehensive health evaluation\n"
            summary += "• Follow medical recommendations closely\n"
        
        summary += f"\n*Values Analyzed:* {len(extracted_values)} tests\n"
        summary += f"*Normal:* {normal_count} | *Abnormal:* {abnormal_count}\n"
        
    return summary

# FIXED: Enhanced additional resources function
def show_additional_resources(target_language="English"):
    """Show additional resources with proper translation"""
    
    translations = {
        "English": {
            "title": "📚 Additional Resources",
            "find_doctor": "🩺 Find a Doctor",
            "learn_more": "📖 Learn More",
            "emergency": "📞 Emergency Info",
            "doctor_info": "💡 Consider consulting a healthcare provider for detailed interpretation.",
            "learn_info": "📚 Research your conditions on reputable medical websites.",
            "emergency_info": "🚨 Emergency: 102 (India), 911 (US), 112 (EU), 999 (UK)"
        },
        "Hindi": {
            "title": "📚 अतिरिक्त संसाधन",
            "find_doctor": "🩺 डॉक्टर खोजें",
            "learn_more": "📖 और जानें",
            "emergency": "📞 आपातकालीन जानकारी",
            "doctor_info": "💡 विस्तृत व्याख्या के लिए स्वास्थ्य सेवा प्रदाता से सलाह लें।",
            "learn_info": "📚 प्रतिष्ठित चिकित्सा वेबसाइटों पर अपनी स्थितियों के बारे में जानकारी लें।",
            "emergency_info": "🚨 आपातकाल: 102 (भारत), 911 (अमेरिका), 112 (यूरोप), 999 (यूके)"
        },
        "Spanish": {
            "title": "📚 Recursos Adicionales",
            "find_doctor": "🩺 Encontrar un Médico",
            "learn_more": "📖 Aprender Más",
            "emergency": "📞 Información de Emergencia",
            "doctor_info": "💡 Considere consultar a un proveedor de atención médica para una interpretación detallada.",
            "learn_info": "📚 Investigue sus condiciones en sitios web médicos confiables.",
            "emergency_info": "🚨 Emergencia: 102 (India), 911 (EE.UU.), 112 (UE), 999 (Reino Unido)"
        }
    }
    
    lang_pack = translations.get(target_language, translations["English"])
    
    title = lang_pack["title"]
    find_doctor = lang_pack["find_doctor"]
    learn_more = lang_pack["learn_more"]
    emergency = lang_pack["emergency"]
    doctor_info = lang_pack["doctor_info"]
    learn_info = lang_pack["learn_info"]
    emergency_info = lang_pack["emergency_info"]
    
    st.markdown(f'<h3 style="color: #2c3e50; font-family: \'Poppins\', sans-serif;">{title}</h3>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(find_doctor, key="find_doctor_btn"):
            st.info(doctor_info)
    
    with col2:
        if st.button(learn_more, key="learn_more_btn"):
            st.info(learn_info)
    
    with col3:
        if st.button(emergency, key="emergency_btn"):
            st.warning(emergency_info)

# Main UI with Enhanced Professional Design
st.markdown("""
<div class="main-header">
    <span class="medical-icon">🏥</span>
    MediSimplify
    <span class="medical-icon">💊</span>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="subtitle">
    <span class="medical-icon">🔬</span>
    AI-Powered Medical Report Simplifier
    <span class="medical-icon">📊</span>
    <br>
    <small style="font-size: 1rem; opacity: 0.8;">Professional Medical Analysis • Multi-Language Support • Instant Results</small>
</div>
""", unsafe_allow_html=True)

# Professional Feature Cards
st.markdown("""
<div class="metric-container">
    <div class="metric-item">
        <div class="metric-value">🏥</div>
        <div class="metric-label">Medical Analysis</div>
    </div>
    <div class="metric-item">
        <div class="metric-value">🌐</div>
        <div class="metric-label">Multi-Language</div>
    </div>
    <div class="metric-item">
        <div class="metric-value">⚡</div>
        <div class="metric-label">Instant Results</div>
    </div>
    <div class="metric-item">
        <div class="metric-value">🔒</div>
        <div class="metric-label">Secure & Private</div>
    </div>
</div>
""", unsafe_allow_html=True)

# API Key Setup Section
if HUGGINGFACE_API_KEY == "hf_your_api_key_here":
    st.markdown("""
    <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ffa726 100%); padding: 2rem; border-radius: 15px; margin: 2rem 0; color: white; text-align: center;">
        <h3>🔑 Setup Required</h3>
        <p><strong>To use this app, you need a free Hugging Face API key:</strong></p>
        <ol style="text-align: left; display: inline-block;">
            <li>Go to <a href="https://huggingface.co/settings/tokens" target="_blank" style="color: white; text-decoration: underline;">https://huggingface.co/settings/tokens</a></li>
            <li>Create a free account if you don't have one</li>
            <li>Generate a new token (select "Inference API" access)</li>
            <li>Copy the token and replace "hf_your_api_key_here" in the code</li>
        </ol>
        <p><em>Don't worry, it's completely free and takes just 2 minutes!</em></p>
    </div>
    """, unsafe_allow_html=True)
elif "403" in str(HUGGINGFACE_API_KEY) or "authentication" in str(HUGGINGFACE_API_KEY).lower():
    st.markdown("""
    <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ffa726 100%); padding: 2rem; border-radius: 15px; margin: 2rem 0; color: white; text-align: center;">
        <h3>🔑 API Key Issue</h3>
        <p><strong>Your API key needs "Inference API" permissions:</strong></p>
        <ol style="text-align: left; display: inline-block;">
            <li>Go to <a href="https://huggingface.co/settings/tokens" target="_blank" style="color: white; text-decoration: underline;">https://huggingface.co/settings/tokens</a></li>
            <li>Delete your current token</li>
            <li>Create a new token with "Inference API" access (not just "Read")</li>
            <li>Update the API key in the code</li>
        </ol>
        <p><em>This will fix the 403 permission error!</em></p>
    </div>
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown('<div style="color: white; font-family: \'Poppins\', sans-serif;"><h3>🇮🇳 Indian Languages</h3></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="color: white; font-family: 'Poppins', sans-serif; line-height: 1.8;">
    • हिंदी (Hindi)<br>
    • বাংলা (Bengali)<br>
    • తెలుగు (Telugu)<br>
    • मराठी (Marathi)<br>
    • தமிழ் (Tamil)<br>
    • ગુજરાતી (Gujarati)<br>
    • ಕನ್ನಡ (Kannada)<br>
    • മലയാളം (Malayalam)<br>
    • ਪੰਜਾਬੀ (Punjabi)<br>
    • ଓଡ଼ିଆ (Odia)<br>
    • اردو (Urdu)
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div style="color: white; font-family: \'Poppins\', sans-serif;"><h3>🌍 International</h3></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="color: white; font-family: 'Poppins', sans-serif; line-height: 1.8;">
    • English • Español • Français<br>
    • Deutsch • 中文 • العربية<br>
    • Português • Русский • 日本語
    </div>
    """, unsafe_allow_html=True)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<h3 style="color: white; font-family: \'Poppins\', sans-serif; font-size: 1.8rem; font-weight: 600; text-align: center;">📄 Upload Your Medical Report</h3>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📁 Upload PDF File", "📝 Paste Text Directly"])
    report_text_from_pdf = ""
    
    with tab1:
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0;">
            <div class="medical-icon">📄</div>
            <h3 style="color: #2c3e50; margin: 1rem 0;">Upload Your Medical Report PDF</h3>
            <p style="color: #666; margin-bottom: 2rem;">Supported formats: PDF files up to 200MB</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=['pdf'],
            help="Upload your medical test report PDF",
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            report_text_from_pdf = extract_pdf_text(uploaded_file)
            if "Error" not in report_text_from_pdf:
                st.success("✅ PDF uploaded successfully!")
                with st.expander("📋 View Extracted Text"):
                    st.text_area("Extracted Content", report_text_from_pdf, height=200)
            else:
                st.error(report_text_from_pdf)
    
    with tab2:
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0;">
            <div class="medical-icon">📝</div>
            <h3 style="color: #2c3e50; margin: 1rem 0;">Paste Your Medical Report Text</h3>
            <p style="color: #666; margin-bottom: 2rem;">Copy and paste the text from your medical report directly</p>
        </div>
        """, unsafe_allow_html=True)
        
        report_text_from_paste = st.text_area(
            "Paste your medical report text here:",
            height=200,
            placeholder="""Example:
COMPLETE BLOOD COUNT:
Hemoglobin: 10.5 g/dL (Normal: 12.0-15.5)
Total Cholesterol: 240 mg/dL (Normal: <200)
TSH: 5.8 mIU/L (Normal: 0.4-4.0)""",
            label_visibility="collapsed"
        )

with col2:
    st.markdown('<h3 style="color: white; font-family: \'Poppins\', sans-serif; font-size: 1.8rem; font-weight: 600; text-align: center;">🌐 Select Your Language</h3>', unsafe_allow_html=True)

    # Group languages for better UX
    indian_languages = ["Hindi", "Bengali", "Telugu", "Marathi", "Tamil", "Gujarati", "Kannada", "Malayalam", "Punjabi", "Odia", "Urdu"]
    international_languages = ["English", "Spanish", "French", "German", "Chinese", "Arabic", "Portuguese", "Russian", "Japanese"]
    
    # Create display options with separators
    language_options = (
        ["--- Indian Languages ---"] + [LANGUAGE_MAPPING[lang] for lang in indian_languages] +
        ["--- International Languages ---"] + [LANGUAGE_MAPPING[lang] for lang in international_languages]
    )
    
    # Reverse mapping to get key from value
    reverse_language_mapping = {v: k for k, v in LANGUAGE_MAPPING.items()}
    
    selected_language_display = st.selectbox(
        "Choose your preferred language",
        options=language_options,
        index=language_options.index("English"), # Default to English
        label_visibility="collapsed"
    )
    
    # Get the actual language key
    if "---" in selected_language_display:
        selected_language = "English" # Default if a separator is somehow selected
    else:
        selected_language = reverse_language_mapping[selected_language_display]

    # Simplify button
    if st.button("✨ Simplify My Report", use_container_width=True):
        report_text = report_text_from_paste or report_text_from_pdf
        
        if report_text:
            with st.spinner("🔬 Analyzing your report... This may take a moment..."):
                time.sleep(1) # Simulate work
                
                # Identify test types
                detected_tests = identify_test_types(report_text)
                
                # Simplify the report
                simplified_report = simplify_medical_report(report_text, detected_tests, selected_language)
                
                # Display results
                st.session_state.simplified_report = simplified_report
                st.session_state.detected_tests = detected_tests
                st.session_state.selected_language = selected_language
        else:
            st.warning("Please upload a PDF or paste text to simplify.")

# Display results below the columns
if 'simplified_report' in st.session_state:
    st.markdown("---")
    st.markdown('<h2 class="section-title">Your Simplified Report</h2>', unsafe_allow_html=True)
    
    # Display detected tests
    if st.session_state.detected_tests:
        tests_str = '`, `'.join(st.session_state.detected_tests)
        st.markdown(f"**Detected Test Types:** `{tests_str}`")
    
    # Display translation info
    if st.session_state.selected_language != "English":
        st.markdown(f"""
        <div class="translation-info">
            <p><strong>Translation Info:</strong> The report has been simplified and translated into <strong>{st.session_state.selected_language}</strong>. Please note that this is an AI-generated translation and may not be perfect. Always consult a professional for critical medical decisions.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Display the simplified report in a professional card
    report_html = st.session_state.simplified_report.replace('\n', '<br>')
    st.markdown(f"""
    <div class="professional-card">
        {report_html}
    </div>
    """, unsafe_allow_html=True)
    
    # Show additional resources
    show_additional_resources(st.session_state.selected_language)

# Footer
st.markdown("""
<div class="footer">
    <p><strong>MediSimplify</strong> &copy; 2024 | AI-Powered Medical Report Simplification</p>
    <p><em>This tool is for informational purposes only and does not constitute medical advice.</em></p>
    <p>Developed with ❤️ using Streamlit & Hugging Face</p>
</div>
""", unsafe_allow_html=True)