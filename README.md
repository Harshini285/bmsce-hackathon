# bmsce-hackathon
#  MediSimplify - AI Medical Report Simplifier

A beautiful, multi-language medical report simplifier that converts complex medical test results into simple, patient-friendly explanations using Hugging Face AI.

## Features

-  **20+ Languages Support** (11 Indian + 9 International)
-  **PDF Upload** - Upload medical report PDFs
-  **Text Input** - Paste medical report text directly
-  **Smart Analysis** - AI-powered medical interpretation
-  **Beautiful UI** - Modern, colorful, and responsive design
-  **Free to Use** - Uses free Hugging Face API

##  Quick Start

### 1. Setup Virtual Environment
```bash
python -m venv myenv
myenv\Scripts\activate  # On Windows
# or
source myenv/bin/activate  # On Mac/Linux
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Get Hugging Face API Key
1. Go to [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Create a free account if you don't have one
3. Generate a new token (select "Read" access)
4. Copy the token

### 4. Update API Key
Open `app.py` and replace `hf_your_api_key_here` with your actual API key:
```python
HUGGINGFACE_API_KEY = "hf_your_actual_api_key_here"
```

### 5. Run the App
```bash
streamlit run app.py
```

##  Supported Languages

### Indian Languages
- हिंदी (Hindi)
- বাংলা (Bengali)
- తెలుగు (Telugu)
- मराठी (Marathi)
- தமிழ் (Tamil)
- ગુજરાતી (Gujarati)
- ಕನ್ನಡ (Kannada)
- മലയാളം (Malayalam)
- ਪੰਜਾਬੀ (Punjabi)
- ଓଡ଼ିଆ (Odia)
- اردو (Urdu)

### International Languages
- English
- Español (Spanish)
- Français (French)
- Deutsch (German)
- 中文 (Chinese)
- العربية (Arabic)
- Português (Portuguese)
- Русский (Russian)
- 日本語 (Japanese)

## 📋 How to Use

1. **Upload or Paste** your medical report
2. **Select Language** for explanation
3. **Click Analyze** to get simplified explanation
4. **View Results** in your chosen language

## 🔧 Technical Details

- **Framework**: Streamlit
- **AI Model**: Hugging Face DialoGPT-Large
- **PDF Processing**: PyPDF2
- **API**: Hugging Face Inference API

## ⚠ Disclaimer

This tool is for educational purposes only. Always consult healthcare professionals for medical advice and interpretation of your reports.

##  License

This project is open source and available under the MIT License.

##  Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

If you encounter any issues, please create an issue on GitHub or contact the development team.

