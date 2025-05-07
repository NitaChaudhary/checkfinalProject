import langchain
from langchain_community.document_loaders import PyMuPDFLoader
import re
from groq import Groq
import json
# Set your Groq API key directly in the code
api_key = "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"

# Initialize the Groq client with the API key
client = Groq(api_key=api_key)

def preprocess_text(text):
    """
    Preprocess the input text to make it easier for GPT to extract relevant details.
    """
    text = re.sub(r'\\[a-zA-Z]+', '', text)  # Remove '\ fa' or similar patterns
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces/newlines with a single space
    text = text.strip()  # Remove leading and trailing spaces
    
    text = re.sub(r'\b(name|contact|about me)\b', r'\nNAME:', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(email|e-mail|mail|mail-id)\b', r'\nEMAIL:', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(skills|expertise|abilities)\b', r'\nSKILLS:', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(experience|work history|employment)\b', r'\nEXPERIENCE:', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(name:|email:|skills:|experience:)\b', lambda match: match.group().upper(), text)
    
    return text

def extract_email(text):
    """
    Extract the full email address using regex after removing any unwanted newline characters.
    """
    text = re.sub(r'\n+', ' ', text)  # Replace multiple newlines with a single space
    text = re.sub(r'\bn+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b', r'\1', text)  # Fix common 'n' issue
    
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(email_pattern, text)
    
    if match:
        return match.group(0)
    return None

def convert_experience_to_months(experience_text):
    """
    Convert extracted experience text to months. Look for years and months in the experience text
    and convert it to total months.
    """
    years = re.findall(r'(\d+)\s+years?', experience_text, flags=re.IGNORECASE)
    months = re.findall(r'(\d+)\s+months?', experience_text, flags=re.IGNORECASE)
    
    total_months = 0
    
    if years:
        total_months += sum(int(year) * 12 for year in years)
    if months:
        total_months += sum(int(month) for month in months)
    
    return total_months

def extract_details(text):
    """
    Use GroqCloud to extract the name, gender, skills, and experience from the preprocessed text.
    """
    processed_text = preprocess_text(text)
    extracted_email = extract_email(text)

    # Adjust the prompt to ensure only JSON output is returned
    prompt = f"""
    Please extract and format the following details from the provided resume text into a JSON object. Ensure the output strictly adheres to the specified format and contains no additional information, explanations, or comments:

    - **Name**: The full name of the individual.
    - **Gender**: Determine based on the name, and provide only "Male" or "Female".
    - **Skills**: A list of skills mentioned in the resume. Each skill should be an item in a JSON array. Include all listed skills, and do not truncate.
    - **TotalExperience**: Provide the total number of professional work experience in months as a numeric value. If no experience is mentioned, return 0 instead of null or leaving it blank. Exclude educational experience and personal projects.

    Do not include any explanations of how the total experience was calculated or any other extra information.


    Resume Text:
    {processed_text}

    Output in JSON format:
    """

    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-groq-70b-8192-tool-use-preview",
    )
    
    generated_text = chat_completion.choices[0].message.content.strip()

    # Check if the output starts with a JSON object (to avoid additional text)
    if generated_text.startswith('{'):
        return generated_text
    else:
        # In case extra text appears, attempt to extract JSON manually
        json_start = generated_text.find('{')
        json_end = generated_text.rfind('}') + 1
        return generated_text[json_start:json_end]




def getResumeText(filepath):
    loader = PyMuPDFLoader(filepath)
    pages = loader.load()
    resume_content = []
    data={}
    for page in pages:
        page_content = page.page_content
        resume_content.append(page_content)


    resumeText = " ".join([w for w in resume_content])
    try:
        if resumeText or len(resumeText)!=0:
            extracted_details = extract_details(resumeText)
            if not extracted_details:

                extracted_details = {'TotalExperience':0,'Gender':'No','Skills':'','Name':'No'}
    except:
        extracted_details = {'TotalExperience':0,'Gender':'No','Skills':'','Name':'No'}

    return resumeText,extracted_details