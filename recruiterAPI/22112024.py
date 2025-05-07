import langchain
from langchain_community.document_loaders import PyMuPDFLoader
import re
from groq import Groq
import json
import time
import os
import spacy
import sys
nationality_list = [
   "Afghan",
   "Albanian",
   "Algerian",
   "American",
   "Andorran",
   "Angolan",
   "Antiguans",
   "Argentinean",
   "Armenian",
   "Australian",
   "Austrian",
   "Azerbaijani",
   "Bahamian",
   "Bahraini",
   "Bangladeshi",
   "Barbadian",
   "Barbudans",
   "Batswana",
   "Belarusian",
   "Belgian",
   "Belizean",
   "Beninese",
   "Bhutanese",
   "Bolivian",
   "Bosnian",
   "Brazilian",
   "British",
   "Bruneian",
   "Bulgarian",
   "Burkinabe",
   "Burmese",
   "Burundian",
   "Cambodian",
   "Cameroonian",
   "Canadian",
   "Cape Verdean",
   "Central African",
   "Chadian",
   "Chilean",
   "Chinese",
   "Colombian",
   "Comoran",
   "Congolese",
   "Costa Rican",
   "Croatian",
   "Cuban",
   "Cypriot",
   "Czech",
   "Danish",
   "Djibouti",
   "Dominican",
   "Dutch",
   "East Timorese",
   "Ecuadorean",
   "Egyptian",
   "Emirian",
   "Equatorial Guinean",
   "Eritrean",
   "Estonian",
   "Ethiopian",
   "Fijian",
   "Filipino",
   "Finnish",
   "French",
   "Gabonese",
   "Gambian",
   "Georgian",
   "German",
   "Ghanaian",
   "Greek",
   "Grenadian",
   "Guatemalan",
   "Guinea-Bissauan",
   "Guinean",
   "Guyanese",
   "Haitian",
   "Herzegovinian",
   "Honduran",
   "Hungarian",
   "I-Kiribati",
   "Icelander",
   "Indian",
   "Indonesian",
   "Iranian",
   "Iraqi",
   "Irish",
   "Israeli",
   "Italian",
   "Ivorian",
   "Jamaican",
   "Japanese",
   "Jordanian",
   "Kazakhstani",
   "Kenyan",
   "Kittian and Nevisian",
   "Kuwaiti",
   "Kyrgyz",
   "Laotian",
   "Latvian",
   "Lebanese",
   "Liberian",
   "Libyan",
   "Liechtensteiner",
   "Lithuanian",
   "Luxembourger",
   "Macedonian",
   "Malagasy",
   "Malawian",
   "Malaysian",
   "Maldivan",
   "Malian",
   "Maltese",
   "Marshallese",
   "Mauritanian",
   "Mauritian",
   "Mexican",
   "Micronesian",
   "Moldovan",
   "Monacan",
   "Mongolian",
   "Moroccan",
   "Mosotho",
   "Motswana",
   "Mozambican",
   "Namibian",
   "Nauruan",
   "Nepalese",
   "New Zealander",
   "Nicaraguan",
   "Nigerian",
   "Nigerien",
   "North Korean",
   "Northern Irish",
   "Norwegian",
   "Omani",
   "Pakistani",
   "Palauan",
   "Panamanian",
   "Papua New Guinean",
   "Paraguayan",
   "Peruvian",
   "Polish",
   "Portuguese",
   "Qatari",
   "Romanian",
   "Russian",
   "Rwandan",
   "Saint Lucian",
   "Salvadoran",
   "Samoan",
   "San Marinese",
   "Sao Tomean",
   "Saudi",
   "Scottish",
   "Senegalese",
   "Serbian",
   "Seychellois",
   "Sierra Leonean",
   "Singaporean",
   "Slovakian",
   "Slovenian",
   "Solomon Islander",
   "Somali",
   "South African",
   "South Korean",
   "Spanish",
   "Sri Lankan",
   "Sudanese",
   "Surinamer",
   "Swazi",
   "Swedish",
   "Swiss",
   "Syrian",
   "Taiwanese",
   "Tajik",
   "Tanzanian",
   "Thai",
   "Togolese",
   "Tongan",
   "Trinidadian or Tobagonian",
   "Tunisian",
   "Turkish",
   "Tuvaluan",
   "Ugandan",
   "Ukrainian",
   "Uruguayan",
   "Uzbekistani",
   "Venezuelan",
   "Vietnamese",
   "Welsh",
   "Yemenite",
   "Zambian",
   "Zimbabwean",
   "أفغاني",  # Afghan
    "ألباني",  # Albanian
    "جزائري",  # Algerian
    "أمريكي",  # American
    "أندوري",  # Andorran
    "أنغولي",  # Angolan
    "أنتيغوي",  # Antiguans
    "أرجنتيني",  # Argentinean
    "أرمني",  # Armenian
    "أسترالي",  # Australian
    "نمساوي",  # Austrian
    "أذربيجاني",  # Azerbaijani
    "باهامي",  # Bahamian
    "بحريني",  # Bahraini
    "بنغالي",  # Bangladeshi
    "باربادوسي",  # Barbadian
    "باربوداني",  # Barbudans
    "بوتسواني",  # Batswana
    "بيلاروسي",  # Belarusian
    "بلجيكي",  # Belgian
    "بليز",  # Belizean
    "بنيني",  # Beninese
    "بوتاني",  # Bhutanese
    "بوليفي",  # Bolivian
    "بوسني",  # Bosnian
    "برازيلي",  # Brazilian
    "بريطاني",  # British
    "بروني",  # Bruneian
    "بلغاري",  # Bulgarian
    "بوركيني",  # Burkinabe
    "بورمي",  # Burmese
    "بوروندي",  # Burundian
    "كمبودي",  # Cambodian
    "كاميروني",  # Cameroonian
    "كندي",  # Canadian
    "كاب فيردي",  # Cape Verdean
    "أفريقي مركزي",  # Central African
    "تشادي",  # Chadian
    "تشيلي",  # Chilean
    "صيني",  # Chinese
    "كولومبي",  # Colombian
    "جزر القمر",  # Comoran
    "كونغولي",  # Congolese
    "كوستاريكي",  # Costa Rican
    "كرواتي",  # Croatian
    "كوباني",  # Cuban
    "قبرصي",  # Cypriot
    "تشيكي",  # Czech
    "دنماركي",  # Danish
    "جيبوتي",  # Djibouti
    "دومينيكي",  # Dominican
    "هولندي",  # Dutch
    "تيموري شرقي",  # East Timorese
    "إكوادوري",  # Ecuadorean
    "مصري",  # Egyptian
    "إماراتي",  # Emirian
    "غيني استوائي",  # Equatorial Guinean
    "إريتري",  # Eritrean
    "استوني",  # Estonian
    "أثيوبي",  # Ethiopian
    "فيجي",  # Fijian
    "فلبيني",  # Filipino
    "فنلندي",  # Finnish
    "فرنسي",  # French
    "غابوني",  # Gabonese
    "غامبي",  # Gambian
    "جورجي",  # Georgian
    "ألماني",  # German
    "غاني",  # Ghanaian
    "يوناني",  # Greek
    "غرينادي",  # Grenadian
    "غواتيمالي",  # Guatemalan
    "غيني بيساوي",  # Guinea-Bissauan
    "غيني",  # Guinean
    "غوياني",  # Guyanese
    "هايتي",  # Haitian
    "هرزغوفيني",  # Herzegovinian
    "هندوراسي",  # Honduran
    "هنغاري",  # Hungarian
    "كيريباسي",  # I-Kiribati
    "آيسلندي",  # Icelander
    "هندي",  # Indian
    "إندونيسي",  # Indonesian
    "إيراني",  # Iranian
    "عراقي",  # Iraqi
    "إيرلندي",  # Irish
    "إسرائيلي",  # Israeli
    "إيطالي",  # Italian
    "ساحلي",  # Ivorian
    "جامايكي",  # Jamaican
    "ياباني",  # Japanese
    "أردني",  # Jordanian
    "كازاخستاني",  # Kazakhstani
    "كيني",  # Kenyan
    "كيتيني ونيفيزي",  # Kittian and Nevisian
    "كويتي",  # Kuwaiti
    "قرغيزي",  # Kyrgyz
    "لاوي",  # Laotian
    "لاتفي",  # Latvian
    "لبناني",  # Lebanese
    "ليبيري",  # Liberian
    "ليبي",  # Libyan
    "ليختنشتايني",  # Liechtensteiner
    "لتواني",  # Lithuanian
    "لوكسمبورغي",  # Luxembourger
    "مقدوني",  # Macedonian
    "مدغشقري",  # Malagasy
    "مالاوي",  # Malawian
    "ماليزي",  # Malaysian
    "مالديفي",  # Maldivan
    "مالي",  # Malian
    "مالطي",  # Maltese
    "مارشالي",  # Marshallese
    "مورتاني",  # Mauritanian
    "موريشيوسي",  # Mauritian
    "مكسيكي",  # Mexican
    "ميكرونيزي",  # Micronesian
    "مولدافي",  # Moldovan
    "موناكي",  # Monacan
    "منغولي",  # Mongolian
    "مغربي",  # Moroccan
    "موسوثو",  # Mosotho
    "موتسوانا",  # Motswana
    "موزمبيقي",  # Mozambican
    "ناميبي",  # Namibian
    "ناوروي",  # Nauruan
    "نيبالي",  # Nepalese
    "نيوزيلندي",  # New Zealander
    "نيكاراغوي",  # Nicaraguan
    "نيجيري",  # Nigerian
    "نيجري",  # Nigerien
    "كوري شمالي",  # North Korean
    "أيرلندي شمالي",  # Northern Irish
    "نرويجي",  # Norwegian
    "عماني",  # Omani
    "باكستاني",  # Pakistani
    "بالاواني",  # Palauan
    "بنمي",  # Panamanian
    "بابوا غينيا الجديدة",  # Papua New Guinean
    "باراغواني",  # Paraguayan
    "بيروفي",  # Peruvian
    "بولندي",  # Polish
    "برتغالي",  # Portuguese
    "قطري",  # Qatari
    "روماني",  # Romanian
    "روسي",  # Russian
    "رواندي",  # Rwandan
    "سانت لوسيا",  # Saint Lucian
    "سلفادوري",  # Salvadoran
    "سامواني",  # Samoan
    "سان ماريني",  # San Marinese
    "ساو توميان",  # Sao Tomean
    "سعودي",  # Saudi
    "اسكتلندي",  # Scottish
    "سنغالي",  # Senegalese
    "صربي",  # Serbian
    "سيشيلي",  # Seychellois
    "سيراليوني",  # Sierra Leonean
    "سنغافوري",  # Singaporean
    "سلوفاكي",  # Slovakian
    "سلوفيني",  # Slovenian
    "جزيري سليمان",  # Solomon Islander
    "صومالي",  # Somali
    "جنوب أفريقي",  # South African
    "كوري جنوبي",  # South Korean
    "إسباني",  # Spanish
    "سريلانكي",  # Sri Lankan
    "سوداني",  # Sudanese
    "سورينامي",  # Surinamer
    "سوازي",  # Swazi
    "سويدي",  # Swedish
    "سويسري",  # Swiss
    "سوري",  # Syrian
    "تايواني",  # Taiwanese
    "طاجيكي",  # Tajik
    "تنزاني",  # Tanzanian
    "تايلاندي",  # Thai
    "توغولي",  # Togolese
    "تونغي",  # Tongan
    "ترينيدادي أو تواغو",  # Trinidadian or Tobagonian
    "تونسي",  # Tunisian
    "تركي",  # Turkish
    "توفالي",  # Tuvaluan
    "أوغندي",  # Ugandan
    "أوكراني",  # Ukrainian
    "أورغوياني",  # Uruguayan
    "أوزبكستاني",  # Uzbekistani
    "فنزويلي",  # Venezuelan
    "فيتنامي",  # Vietnamese
    "ويلزي",  # Welsh
    "يمني",  # Yemenite
    "زامبي",  # Zambian
    "زيمبابوي"  # Zimbabwean
    "Afghanistan",
   "Albania",
   "Algeria",
   "United States",
   "Andorra",
   "Angola",
   "Antigua and Barbuda",
   "Argentina",
   "Armenia",
   "Australia",
   "Austria",
   "Azerbaijan",
   "The Bahamas",
   "Bahrain",
   "Bangladesh",
   "Barbados",
   "Barbuda",
   "Botswana",
   "Belarus",
   "Belgium",
   "Belize",
   "Benin",
   "Bhutan",
   "Bolivia",
   "Bosnia and Herzegovina",
   "Brazil",
   "United Kingdom",
   "Brunei",
   "Bulgaria",
   "Burkina Faso",
   "Myanmar",
   "Burundi",
   "Cambodia",
   "Cameroon",
   "Canada",
   "Cabo Verde",
   "Central African Republic",
   "Chad",
   "Chile",
   "China",
   "Colombia",
   "Comoros",
   "Congo",
   "Costa Rica",
   "Croatia",
   "Cuba",
   "Cyprus",
   "Czech Republic",
   "Denmark",
   "Djibouti",
   "The Dominican Republic",
   "The Netherlands",
   "East Timor",
   "Ecuador",
   "Egypt",
   "United Arab Emirates",
   "Equatorial Guinea",
   "Eritrea",
   "Estonia",
   "Ethiopia",
   "Fiji",
   "The Philippines",
   "Finland",
   "France",
   "Gabon",
   "Gambia",
   "Georgia",
   "Germany",
   "Ghana",
   "Greece",
   "Grenada",
   "Guatemala",
   "Guinea-Bissau",
   "Guinea",
   "Guyana",
   "Haiti",
   "Bosnia and Herzegovina",
   "Honduras",
   "Hungary",
   "Kiribati",
   "Iceland",
   "India",
   "Indonesia",
   "Iran",
   "Iraq",
   "Ireland",
   "Israel",
   "Italy",
   "Côte d'Ivoire",
   "Jamaica",
   "Japan",
   "Jordan",
   "Kazakhstan",
   "Kenya",
   "Saint Kitts and Nevis",
   "Kuwait",
   "Kyrgyzstan",
   "Laos",
   "Latvia",
   "Lebanon",
   "Liberia",
   "Libya",
   "Liechtenstein",
   "Lithuania",
   "Luxembourg",
   "North Macedonia",
   "Madagascar",
   "Malawi",
   "Malaysia",
   "Maldives",
   "Mali",
   "Malta",
   "The Marshall Islands",
   "Mauritania",
   "Mauritius",
   "Mexico",
   "Micronesia",
   "Moldova",
   "Monaco",
   "Mongolia",
   "Morocco",
   "Lesotho",
   "Botswana",
   " Mozambique",
   "Namibia",
   "Nauru",
   "Nepal",
   "New Zealand",
   "Nicaragua",
   "Nigeria",
   "Niger",
   "North Korea",
   "Northern Ireland",
   "Norway",
   "Oman",
   "Pakistan",
   "Palau",
   "Panama",
   "Papua New Guinea",
   "Paraguay",
   "Peru",
   "Poland",
   "Portugal",
   "Qatar",
   "Romania",
   "Russia",
   "Rwanda",
   "Saint Lucia",
   "El Salvador",
   "Samoa",
   "San Marino",
   "Sao Tome and Principe",
   "Saudi Arabia",
   "Scotland",
   "Senegal",
   "Serbia",
   "Seychelles",
   "Sierra Leone",
   "Singapore",
   "Slovakia",
   "Slovenia",
   "Solomon Islands",
   "Somalia",
   "South Africa",
   "South Korea",
   "Spain",
   "Sri Lanka",
   "Sudan",
   "Suriname",
   "Swaziland",
   "Sweden",
   "Switzerland",
   "Syria",
   "Taiwan",
   "Tajikistan",
   "Tanzania",
   "Thailand",
   "Togo",
   "Tonga",
   "Trinidad and Tobago",
   "Tunisia",
   "Turkey",
   "Tuvalu",
   "Uganda",
   "Ukraine",
   "Uruguay",
   "Uzbekistan",
   "Venezuela",
   "Vietnam",
   "Wales",
   "Yemen",
   "Zambia",
   "Zimbabwe"
]

sys.path.append(r'recruiterAPI')



# Load spaCy model for named entity recognition (NER)
nlp = spacy.load("en_core_web_sm")

# Keywords in English and Arabic that may indicate nationality
nationality_keywords = [
    'nationality', 'citizenship', 'country of origin', 'origin', 'resident of', 'place of birth', 'born in',
    'الجنسية', 'المواطنة', 'بلد الأصل', 'الأصل', 'مقيم في', 'مكان الميلاد', 'ولد في'
]

def extract_nationality(text):
    text = re.sub(r'\s+', ' ', text).strip()

    # Step 1: Keyword-based extraction
    for keyword in nationality_keywords:
        pattern = rf'({keyword})\s*[:\-]?\s*([\w\s,-]+)'
        match = re.search(pattern, text, re.IGNORECASE | re.UNICODE)
        if match:
            possible_nationality = match.group(2).strip()
            
            # Check for matches in nationality list with partial matching enabled
            for nationality in nationality_list:
                if nationality.lower() in possible_nationality.lower() or possible_nationality.lower() in nationality.lower():
                    return nationality.capitalize()
    
    # Step 2: Direct matching with nationalities
    for nationality in nationality_list:
        if nationality.lower() in text.lower():
            return nationality.capitalize()
    
    # Step 3: NER-based fallback
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "GPE" and any(nationality.lower() == ent.text.lower() for nationality in nationality_list):
            return ent.text.capitalize()
    
    return "Nationality not found"

# Get user input
def user_input():
    print("Paste the resume text below (press Enter on an empty line to finish):\n")
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    return " ".join(lines)



nationality_set = set([n.lower() for n in nationality_list])  # Lowercasing for case-insensitive matching

# Load spaCy's pre-trained English model outside the functions (avoids reloading for each function call)
nlp = spacy.load('en_core_web_sm')


# Set your Groq API key directly in the code
api_key = "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"

# Initialize the Groq client with the API key
client = Groq(api_key=api_key)

# Step 2: Preprocessing functions
def preprocess_resume_text(text):
    return text.strip()

# Step 3: Email Extraction using regex
def extract_email(text):
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    match = re.search(email_pattern, text)
    return match.group(0) if match else None


# Gender Extraction
def extract_gender(resume_text):
    
    male_patterns = [r'\b(male|man|guy|boy)\b', r'\b(his|him|he)\b']
    female_patterns = [r'\b(female|woman|girl)\b', r'\b(hers|her|she)\b']

    for pattern in male_patterns:
        if re.search(pattern, resume_text, re.IGNORECASE):
            return 'Male'

    for pattern in female_patterns:
        if re.search(pattern, resume_text, re.IGNORECASE):
            return 'Female'

    return "No"

# Step 4: Extracting details using Groq API

def extract_details(text):
    try:
        processed_text = preprocess_resume_text(text)
        extracted_email = extract_email(text)
        extracted_nationality = extract_nationality(text)
        extracted_gender = extract_gender(text)

        prompt = f"""
        Please extract and format the following details from the provided resume text into a JSON object:

        - **Name**: The full name of the individual.
        - **Skills**: A list of skills mentioned in the resume. Each skill should be an item in a JSON array. Include all listed skills, and do not truncate.
        - **TotalExperience**: TotalExperience: Calculate the total professional work experience in months as a numeric value by:
                -Identifying full-time, paid professional work experiences that include a start and end date.
                -For each role with dates, calculate the duration in months. Use the following steps:
                -Convert the duration for each role to months (1 year = 12 months).
                -For roles listed as "Present," assume the end date is the current month.
                -Add up all individual durations in months to obtain the total.
                -Exclude any internships, educational experience, volunteer work, or personal projects, as well as roles without valid dates.
                -If no professional work experience is found, return 0.        
        - **ExperienceDetails**: Include only the **job title** and a **brief description** of the person's responsibilities or work done in that role.
        - **Education**: Extract only the **degree** (e.g., Bachelor of Science, Master of Business Administration) from the resume. Do not include the institution name, start/end dates, or any additional information.
        - **Nationality**: {extracted_nationality}
        - **Gender**: {extracted_gender}
        - **Email**: {extracted_email if extracted_email else 'Email not found'}

        Resume Text:
        {processed_text}

        Output in JSON format:
        """

        while True:
            # try:
                # Make the API call to Groq
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama3-groq-70b-8192-tool-use-preview",
                )

                generated_text = chat_completion.choices[0].message.content.strip()

                # Ensure response is in JSON format
                if generated_text.startswith('{'):
                    return generated_text
                else:
                    json_start = generated_text.find('{')
                    json_end = generated_text.rfind('}') + 1
                    return generated_text[json_start:json_end]

            # except Exception as e:
            #     if "exceeded token limit" in str(e).lower():
            #         print("Token limit exceeded, waiting for 3-4 seconds before retrying...")
            #         time.sleep(4)  # Wait for 3-4 seconds
            #         continue
            #     else:
            #         raise e

    except Exception as e:
        print(f"Error during API call: {e}")
        return None


nlp = spacy.load("en_core_web_sm")


# Step 5: Resume Input Validation
def validate_resume_input(resume_text):
    if not resume_text or not resume_text.strip():
        raise ValueError("Resume input is empty or invalid.")

# Step 6: ATS Calculation using Groq Prompt
def calculate_ats(job_description, extracted_details):
    try:
        prompt = f"""
        Given the following job description and resume details, provide only the ATS score as a numeric percentage from 0 to 100, without any additional text.

        Job Description:
        {job_description}

        Resume Details:
        {extracted_details}
        """

        # Make the API call to Groq
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-groq-70b-8192-tool-use-preview",
        )

        ats_score = chat_completion.choices[0].message.content.strip()

        # Ensure the response is a valid number
        ats_score = re.search(r'\d+', ats_score)  # Extract numeric value
        return ats_score.group(0) if ats_score else None

    except Exception as e:
        print(f"Error during ATS calculation: {e}")
        return None



def getResumeText(resumeText,job_description):

    # loader = PyMuPDFLoader(filepath)
    # pages = loader.load()
    # resume_content = []
    # for page in pages:
    #     page_content = page.page_content
    #     resume_content.append(page_content)


    # resumeText = " ".join([w for w in resume_content])
    try:
        if resumeText or len(resumeText)!=0:
            extracted_details = extract_details(resumeText)
            
            if not extracted_details:

                data_dict = {'TotalExperience':0,'Gender':'No','Skills':'','Name':'No','ATSScore':'0%'}
            else:
                required_keys = ['nationality', 'gender']
 
                data_dict = json.loads(extracted_details)
            
                for key in required_keys:
                    if key.lower() not in data_dict:
                        data_dict[key] = "No"
                                        
                ats_score = calculate_ats(job_description, json.dumps(extracted_details))
                    
                data_dict['ATSScore'] = f"{ats_score}%"

    except:
        extracted_details = {'TotalExperience':0,'Gender':'No','Skills':'','Name':'No','ATSScore':'0%'}
        data_dict = json.loads(extracted_details)
    
    # print(data_dict)
    return resumeText,data_dict


























import django
from django.conf import settings
django.setup() 
from django.shortcuts import render
from .models import *
from django.core.exceptions import SuspiciousFileOperation
from django.http import HttpResponse
from .serializers import *
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
import string
import random
import os
from userloginAPI.models import *
from databaseAPI.models import *
from recruiterAPI.models import *
from threading import Lock
from django.core.files.storage import default_storage
import json
from hires.emailsend import mailSend
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import action
import operator

from concurrent.futures import ThreadPoolExecutor, as_completed
import zipfile
import json
from PIL import Image
import fitz
from langchain_community.document_loaders import PyMuPDFLoader
from multiprocessing import Pool, cpu_count
from concurrent.futures import ThreadPoolExecutor
import django
from django.db import connection
import multiprocessing
from datetime import datetime
import time
from functools import partial
from ratelimit import limits, sleep_and_retry
import math
from multiprocessing import Queue
from multiprocessing import Pool,Manager
from itertools import islice
from .extractResumeText import getResumeText
from concurrent.futures import ProcessPoolExecutor

# nlp = spacy.load("en_core_web_sm")

def convert_keys_to_lowercase(data):
    if isinstance(data, dict):
        return {k.lower(): convert_keys_to_lowercase(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_keys_to_lowercase(item) for item in data]
    else:
        return data
    
    
TPM_LIMIT = 14000
TPS_LIMIT = TPM_LIMIT / 60 

def rate_limited_process(queue, getData, uniqueID):
    """
    Process items from the queue with rate limiting.
    """
    results = []
    while not queue.empty():
        chunk = queue.get()
        start_time = time.time()
        
        # Process the chunk (call your function)
        result = process_resume_chunk(chunk, getData, uniqueID)
        results.extend(result)  # Append results from this chunk
        
        # Throttle to respect the TPS_LIMIT
        time_taken = time.time() - start_time
        sleep_time = max(0, (1 / TPS_LIMIT) - time_taken)
        time.sleep(sleep_time)
    
    return results



# def process_resume_chunk(resume_chunk, getData, uniqueID):
#     resume_list = []
    
#     for resume in resume_chunk:
#         print(resume['imgpath'])
#         file_path = resume['file_path']
#         file_name = resume['file_name']
#         fullpath = os.path.join(settings.MEDIA_ROOT, file_path)

#         # Print the full path for debugging
#         print(f"Full file path: {fullpath}")

#         randomstr = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))
#         unique_resumeID = "hires_recruiter_resume_candidate_" + randomstr
                
#         loader = PyMuPDFLoader(resume['job_description_file'])
#         pages = loader.load()

#         jobdescription = []
#         for page in pages:
#             page_content = page.page_content
#             jobdescription.append(page_content)

#         jobdescriptionText = " ".join([w for w in jobdescription])

#         try:
#             resumeText, extracted_details = getResumeText(resume['resumeText'], jobdescriptionText)
#         except Exception as e:
#             print(f"Error extracting resume text: {e}")
#             resumeText = ''
#             extracted_details = {'totalExperience': 0, 'gender': 'No', 'skills': '', 'name': 'No', 'ATSScore': '0%'}

#         lowercase_data = convert_keys_to_lowercase(extracted_details)
#         resume_list.append({
#             "recruiter_resume_candidate_file_path": resume['recruiter_resume_candidate_file_path'],
#             "recruiter_resume_candidate_name": lowercase_data['name'],
#             "aiCompPercentageScore": lowercase_data['atsscore'],
#             "recruiter_resume_candidate_experience": lowercase_data['totalexperience'],
#             "recruiter_resume_candidate_gender": lowercase_data['gender'],
#             "recruiter_resume_candidate_tech_stack": lowercase_data['skills'],
#         })
    
#     print(f"Processed {len(resume_list)} resumes successfully.")  # Print summary of processed resumes
#     return resume_list


def process_single_resume(resume):
    # print(resume)
    try:
        file_path = resume['file_path']
        file_name = resume['file_name']
        fullpath = os.path.join(settings.MEDIA_ROOT, file_path)

        # Print the full path for debugging
        print(f"Full file path: {fullpath}")

        randomstr = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))
        unique_resumeID = "hires_recruiter_resume_candidate_" + randomstr

        loader = PyMuPDFLoader(resume['job_description_file'])
        pages = loader.load()

        jobdescription = []
        for page in pages:
            page_content = page.page_content
            jobdescription.append(page_content)

        jobdescriptionText = " ".join([w for w in jobdescription])

        # Extract resume text using getResumeText
        print(len(resume['resumeText'].split(' ')))
        resumeText, extracted_details = getResumeText(resume['resumeText'], jobdescriptionText)
        lowercase_data = convert_keys_to_lowercase(extracted_details)
        print(lowercase_data)
        return {
            "recruiter_resume_candidate_file_path": resume['recruiter_resume_candidate_file_path'],
            "recruiter_resume_candidate_name": lowercase_data['name'],
            "aiCompPercentageScore": lowercase_data['aiCompPercentageScore'],
            "recruiter_resume_candidate_experience": lowercase_data['totalexperience'],
            "recruiter_resume_candidate_gender": lowercase_data['gender'],
            "recruiter_resume_candidate_tech_stack": lowercase_data['skills'],
        }
    except Exception as e:
        print(f"Error processing resume: {e}")
        return {
            "recruiter_resume_candidate_file_path": resume['recruiter_resume_candidate_file_path'],
            "recruiter_resume_candidate_name": 'No',
            "aiCompPercentageScore": '0%',
            "recruiter_resume_candidate_experience": 0,
            "recruiter_resume_candidate_gender": 'No',
            "recruiter_resume_candidate_tech_stack": '',
        }

# Main function for processing resume chunks
def process_resume_chunk(resume_chunk, getResumeText, uniqueID):
    resume_list = []

    # Use ProcessPoolExecutor for multiprocessing
    with ProcessPoolExecutor() as executor:
        processed_resumes = list(executor.map(process_single_resume, resume_chunk))

    resume_list.extend(processed_resumes)

    print(f"Processed {len(resume_list)} resumes successfully.")  # Print summary of processed resumes
    return resume_list

###################################################################################################################################################


# Create your views here.

class JobDescriptionAPI(APIView):

    '''
        job Description API(INSERT)
        Request : POST
        Data =  {
                    "job_level_name": "hires_job_position_6d9xkfg8wr0nvml",
                    "user_id":"hires_firsetest3_0yyhogjnlh",
                    "job_description_upload_file": grisha.pdf
                    "job_tilte": "Python Developer"
                    "job_description_action": "active"     # active/deactive/archive/draft
                }
    '''
    
    def post(self, request ,format=None):

        getData = request.data

        if NewUser.objects.filter(pk=getData["user_id"]).exists():

            user = NewUser.objects.get(pk=getData["user_id"])
            
            
            if user.user_is_loggedin:

                if not request.FILES:
                        res = {
                            "Status": "error",
                            "Code": 400,
                            "Message": "File is required",
                            "Data": []
                        }
                        return Response(res, status=status.HTTP_400_BAD_REQUEST)
                
                randomstr = ''.join(random.choices(string.ascii_lowercase +
                                    string.digits, k=15))

                uniqueID = "hires_job_description_" + randomstr
                getData["job_description_id"] = uniqueID
                                        
                serializer = JobDescriptionSerializer(data=getData)
                if serializer.is_valid():
                    serializer.save(job_description_id=getData["job_description_id"])
                    res = {
                        "Status": "success",
                        "Code": 201,
                        "Message": "Job Description is Added",
                        "Data": {   
                            "job_description_id" : getData['job_description_id']
                        }
                    }
                    return Response(res, status=status.HTTP_201_CREATED)
                else:
                    res = {
                        "Status": "error",
                        "Code": 400,
                        "Message": list(serializer.errors.values())[0][0],
                        "Data": []
                    }
                    return Response(res, status=status.HTTP_400_BAD_REQUEST)
            
            else:
                res = {
                    "Status": "error",
                    "Code": 401,
                    "Message": "You are not logged in",
                    "Data": []
                    }
                return Response(res, status=status.HTTP_401_UNAUTHORIZED)
        

        else:
            res = {
                "Status": "error",
                "Code": 401,
                "Message": "User is not found",
                "Data": []
                }
            return Response(res, status=status.HTTP_401_UNAUTHORIZED)
    
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]
               
class JobDescriptionUpdateAPI(APIView):

    '''
        job Description API(UPDATE)
        Request : PATCH
        Data =  {
                    "job_description_id":"hires_job_description_6s8ceoxeahnp168",
                    "job_level_name": "hires_job_level_gcs56oghq4ae0gf",
                    "user_id":"hires_firsetest3_0yyhogjnlh",
                    "job_description_upload_file": grisha.pdf,
                    "job_tilte": "Python Developer",
                    "job_description_action": "active" # active/deactive/archive/draft
                }
    '''
    def post(self, request ,format=None):
        getData = request.data.copy()
        
        if "job_description_upload_file" in getData :
            
            if NewUser.objects.filter(pk = getData["user_id"]).exists():
                user = NewUser.objects.get(pk=getData["user_id"])
                
                if JobDescriptionModel.objects.filter(job_description_id = getData["job_description_id"]).exists():
                
                    
                    if user.user_is_loggedin:
                
                        serializer = JobDescriptionSerializer(data=getData)
                        
                        
                        if serializer.is_valid():
                            LastUpdateData = JobDescriptionModel.objects.get(job_description_id = getData["job_description_id"])
                            LastUpdateData.user_id = getData['user_id']
                            LastUpdateData.job_description_upload_file = getData["job_description_upload_file"]
                            LastUpdateData.job_tilte = getData["job_tilte"]
                            LastUpdateData.job_description_action = getData["job_description_action"]
                            LastUpdateData.job_level_name = getData["job_level_name"]
                            LastUpdateData.save()
                            
                            res = {
                                "Status": "success",
                                "Code": 200,
                                "Message": "Job Description is Updated",
                                "Data": {
                                    "job_description_id": getData["job_description_id"],
                                }
                            }
                            return Response(res, status=status.HTTP_200_OK)

                        else:
                            res = {
                                "Status": "error",
                                "Code": 400,
                                "Message": list(serializer.errors.values())[0][0],
                                "Data": []
                            }
                            return Response(res, status=status.HTTP_400_BAD_REQUEST)
                    
                    else:
                        res = {
                            "Status": "error",
                            "Code": 401,
                            "Message": "You are not logged in",
                            "Data": []}
                        return Response(res, status=status.HTTP_401_UNAUTHORIZED)
                                
                else:
                    res = {
                        "Status": "error",
                        "Code": 401,
                        "Message": "Job Description data is not found",
                        "Data": []}
                    return Response(res, status=status.HTTP_401_UNAUTHORIZED)
            else:
                    res = {
                        "Status": "error",
                        "Code": 401,
                        "Message": "User data is not found",
                        "Data": []}
                    return Response(res, status=status.HTTP_401_UNAUTHORIZED)
        
        else:
            if NewUser.objects.filter(pk = getData["user_id"]).exists():
                user = NewUser.objects.get(pk=getData["user_id"])
                
                if JobDescriptionModel.objects.filter(job_description_id = getData["job_description_id"]).exists():
                
                    if user.user_is_loggedin:
                        LastUpdateData = JobDescriptionModel.objects.get(job_description_id = getData["job_description_id"])
                        getData["job_description_upload_file"] = LastUpdateData.job_description_upload_file
                        serializer = JobDescriptionSerializer(data=getData)

                        
                        if serializer.is_valid():
                            LastUpdateData = JobDescriptionModel.objects.get(job_description_id = getData["job_description_id"])
                            LastUpdateData.user_id = getData['user_id']
                            LastUpdateData.job_tilte = getData["job_tilte"]
                            LastUpdateData.job_description_action = getData["job_description_action"]
                            LastUpdateData.job_level_name = getData['job_level_name']
                            LastUpdateData.save()
                            
                            res = {
                                "Status": "success",
                                "Code": 200,
                                "Message": "Job Description is Updated",
                                "Data": {
                                    "job_description_id": getData["job_description_id"],
                                }
                            }
                            return Response(res, status=status.HTTP_200_OK)

                        else:
                            res = {
                                "Status": "error",
                                "Code": 400,
                                "Message": list(serializer.errors.values())[0][0],
                                "Data": []
                            }
                            return Response(res, status=status.HTTP_400_BAD_REQUEST)
                    
                    else:
                        res = {
                            "Status": "error",
                            "Code": 401,
                            "Message": "You are not logged in",
                            "Data": []}
                        return Response(res, status=status.HTTP_401_UNAUTHORIZED)
                        
                        
                else:
                    res = {
                        "Status": "error",
                        "Code": 401,
                        "Message": "Job Description data is not found",
                        "Data": []}
                    return Response(res, status=status.HTTP_401_UNAUTHORIZED)
            else:
                    res = {
                        "Status": "error",
                        "Code": 401,
                        "Message": "User data is not found",
                        "Data": []}
                    return Response(res, status=status.HTTP_401_UNAUTHORIZED)
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]
         
class JobDescriptionDeleteAPI(APIView):
    '''
        job Description API(delete)
        Request : delete
        Data =  {
                    "job_description_id":"hires_job_description_6s8ceoxeahnp168",
                    "user_id":"hires_firsetest3_0yyhogjnlh",
                }
    '''
    def delete(self, request, format=None):
        getData = request.data
        if NewUser.objects.filter(pk=getData["user_id"]).exists():
            user = NewUser.objects.get(pk=getData["user_id"])
            if user.user_is_loggedin:
                
                if JobDescriptionModel.objects.filter(job_description_id = getData["job_description_id"],user_id=getData["user_id"]).exists():
                    
                    JobDescriptionDetail = JobDescriptionModel.objects.get(job_description_id = getData["job_description_id"],user_id=getData["user_id"])
                    JobDescriptionDetail.delete()
                    res = {
                            "Status": "success",
                            "Code": 200,
                            "Message": "Job Description is successfully Deleted",
                            "Data": []
                        }
                    return Response(res, status=status.HTTP_200_OK)
                else:
                    res = {
                        "Status": "error",
                        "Code": 401,
                        "Message": "Job Description data is not found",
                        "Data": []
                        }
                    return Response(res, status=status.HTTP_401_UNAUTHORIZED)
            else:
                res = {
                    "Status": "error",
                    "Code": 401,
                    "Message": "You are not logged in",
                    "Data": []
                    }
                return Response(res, status=status.HTTP_401_UNAUTHORIZED)
        else:
            res = {
                "Status": "error",
                "Code": 401,
                "Message": "User is not found",
                "Data": []
                }
            return Response(res, status=status.HTTP_401_UNAUTHORIZED)

    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]
          
class JobDescriptionGetAPI(APIView):
    '''
        Job Description API(View)
        Request : GET
    '''
    def get(self, request, format=None):
        getData = request.data
        JobDescriptionDetails = JobDescriptionModel.objects.values()
        res = {
                "Status": "success",
                "Code": 200,
                "Message": "Job Description Details",
                "Data": JobDescriptionDetails,
            }
        return Response(res, status=status.HTTP_200_OK)      

    # authentication_classes=[JWTAuthentication]
    # permission_classes=[IsAuthenticated]  
    
class JobDescriptionGetOneAPI(APIView):
    '''
        Get One Job Description API(View)
        Request : POST
        Data =  {
                    "user_id":"hires_firsetest3_0yyhogjnlh",
                    "job_description_id":"hires_job_description_6s8ceoxeahnp168",
                    "job_description_action": "active",  # active/deactive/archive/draft
                }
    '''
    def post(self, request, format=None):
        getData = request.data
        
        if NewUser.objects.filter(pk=getData["user_id"]).exists():
            user = NewUser.objects.get(pk=getData["user_id"])
            
            if user.user_is_loggedin:
                
                if JobDescriptionModel.objects.filter( user_id=getData["user_id"], job_description_id = getData["job_description_id"],job_description_action = getData["job_description_action"]).exists():
                    
                    JobDescriptionDetail = JobDescriptionModel.objects.filter(user_id=getData["user_id"] , job_description_id = getData["job_description_id"],job_description_action = getData["job_description_action"]).values()
                    res = {
                            "Status": "success",
                            "Code": 200,
                            "Message": "Job Description Detail",
                            "Data": JobDescriptionDetail

                        }
                    return Response(res, status=status.HTTP_200_OK)
                else:
                    res = {
                        "Status": "success",
                        "Code": 200,
                        "Message": "Job Description data is not found",
                        "Data": []
                        }
                    return Response(res, status=status.HTTP_200_OK)
            
            else:
                        res = {
                            "Status": "error",
                            "Code": 401,
                            "Message": "You are not logged in",
                            "Data": []
                            }
                        return Response(res, status=status.HTTP_401_UNAUTHORIZED)
        
        else:
            res = {
                "Status": "error",
                "Code": 401,
                "Message": "User is not found",
                "Data": []
                }
            return Response(res, status=status.HTTP_401_UNAUTHORIZED)
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]
    
class JobDescriptionGetUserAPI(APIView):
    '''
        Get One Job Description User API(View)
        Request : POST
        Data =  {
                    "user_id": "hires_firsetest3_0yyhogjnlh",
                    "job_description_action": "active", # active/deactive/archive/draft
                }
    '''
    def post(self, request, format=None):
        getData = request.data
        
        if NewUser.objects.filter(pk=getData["user_id"]).exists():
            user = NewUser.objects.get(pk=getData["user_id"])
            
            if user.user_is_loggedin:
                
                if JobDescriptionModel.objects.filter(user_id = getData["user_id"],job_description_action = getData["job_description_action"]).exists():

                    JobDescriptionDetail = JobDescriptionModel.objects.filter(user_id = getData["user_id"],job_description_action = getData["job_description_action"]).values().order_by('-job_description_registration_date')


                    res = {
                            "Status": "success",
                            "Code": 200,
                            "Message": "Job Description Detail",
                            "Data": {
                                "JobDescriptionDetail":JobDescriptionDetail,
                                "Total_job_posts": len(JobDescriptionDetail)
                            }

                        }
                    return Response(res, status=status.HTTP_200_OK)
                else:
                    res = {
                            "Status": "error",
                            "Code": 401,
                            "Message": "Job Description data is not found",
                            "Data": {
                                "Total_job_posts": 0,
                                "JobDescriptionDetail":[]
                            }
                        }
                    return Response(res, status=status.HTTP_401_UNAUTHORIZED)
            else:
                        res = {
                            "Status": "error",
                            "Code": 401,
                            "Message": "You are not logged in",
                            "Data": []
                            }
                        return Response(res, status=status.HTTP_401_UNAUTHORIZED)
        else:
            res = {
                "Status": "error",
                "Code": 401,
                "Message": "User is not found",
                "Data": []
                }
            return Response(res, status=status.HTTP_401_UNAUTHORIZED)
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]
    
class JobDescriptionGetfromJobPositionJobLevelAPI(APIView):
    '''
        Get One Job Description Job Level Job Position API(View)
        Request : POST
        Data =  {
                    "user_id":"hires_firsetest3_0yyhogjnlh",
                    "job_level_name": "hires_job_level_gcs56oghq4ae0gf",
                    "job_description_action": "active", # active/deactive/archive/draft
                }
    '''
    def post(self, request, format=None):
        getData = request.data
        if NewUser.objects.filter(pk=getData["user_id"]).exists():
            user = NewUser.objects.get(pk=getData["user_id"])

            if user.user_is_loggedin:
                if JobDescriptionModel.objects.filter(user_id=getData["user_id"],job_level_name = getData["job_level_name"],job_description_action = getData["job_description_action"]).exists():
                    
                    JobDescriptionDetail = JobDescriptionModel.objects.filter(user_id=getData["user_id"],job_level_name = getData["job_level_name"],job_description_action = getData["job_description_action"]).values()
                    
                    res = {
                            "Status": "success",
                            "Code": 200,
                            "Message": "Job Description Detail",
                            "Data": JobDescriptionDetail
                        }
                    return Response(res, status=status.HTTP_201_CREATED)
                
                else:
                    res = {
                        "Status": "error",
                        "Code": 401,
                        "Message": "Job Description data is not found",
                        "Data": []
                        }
                    return Response(res, status=status.HTTP_401_UNAUTHORIZED)
            
            else:
                res = {
                    "Status": "error",
                    "Code": 401,
                    "Message": "You are not logged in",
                    "Data": []
                    }
                return Response(res, status=status.HTTP_401_UNAUTHORIZED)
        
        else:
            res = {
                "Status": "error",
                "Code": 401,
                "Message": "User is not found",
                "Data": []
                }
            return Response(res, status=status.HTTP_401_UNAUTHORIZED)        

    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]
     

#################################################################################################################################################

# # # core
# class RecruiterBulkResumeAnalysisAPI(APIView):
#     def post(self, request, format=None):
#         try:
#             getData = request.data

#             if not NewUser.objects.filter(pk=getData["user_id"]).exists():
#                 return Response({"Status": "error", "Code": 401, "Message": "User is not found", "Data": []}, status=status.HTTP_401_UNAUTHORIZED)

#             user = NewUser.objects.get(pk=getData["user_id"])

#             if not JobDescriptionModel.objects.filter(user_id=getData["user_id"], job_description_id=getData["job_description_id"]).exists():
#                 return Response({"Status": "error", "Code": 401, "Message": "Job description is not found", "Data": []}, status=status.HTTP_401_UNAUTHORIZED)

#             if not user.user_is_loggedin:
#                 return Response({"Status": "error", "Code": 401, "Message": "User is not loggedin", "Data": []}, status=status.HTTP_401_UNAUTHORIZED)

#             if not request.FILES:
#                 return Response({"Error": "Zip file is required"}, status=status.HTTP_400_BAD_REQUEST)

#             randomstr = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))
#             uniqueID = "hires_recruiter_bulk_resume_" + randomstr
#             getData["recruiter_bulk_resume_upload_id"] = uniqueID


#             serializer = RecruiterBulkResumeUploadSerializer(data=getData)

#             if not serializer.is_valid():
#                 return Response({"Status": "error", "Code": 400, "Message": list(serializer.errors.values())[0][0], "Data": []}, status=status.HTTP_400_BAD_REQUEST)

#             resp = serializer.data
#             userRes = RecruiterBulkResumeUploadModel(
#                 recruiter_bulk_resume_upload_id=resp["recruiter_bulk_resume_upload_id"],
#                 user_id=resp["user_id"],
#                 recruiter_bulk_resume_upload=getData["recruiter_bulk_resume_upload"],
#             )
#             userRes.save()
        
#             if JobDescriptionModel.objects.filter(user_id=getData["user_id"], job_description_id=getData["job_description_id"]).exists():
#                     uploadedjd = JobDescriptionModel.objects.get(user_id=getData["user_id"], job_description_id=getData["job_description_id"])
#                     jdpath = os.path.join(settings.MEDIA_ROOT, str(uploadedjd.job_description_upload_file))
#                     loader = PyMuPDFLoader(jdpath)
#                     pages = loader.load()

#                     jobdescription = []
#                     for page in pages:
#                         page_content = page.page_content
#                         jobdescription.append(page_content)

#                     jobdescriptionText = " ".join([w for w in jobdescription])
#             else:
#                 return Response({"Status": "error", "Code": 401, "Message": "Invalid file format", "Data": []}, status=status.HTTP_401_UNAUTHORIZED)
#             if userRes.pk:
#                 try:
                    
#                     file_path = ""
#                     data = RecruiterBulkResumeUploadModel.objects.get(recruiter_bulk_resume_upload_id=resp["recruiter_bulk_resume_upload_id"], user_id=resp["user_id"])
#                     original_path = str(data.recruiter_bulk_resume_upload)
#                     fullpath = os.path.join(settings.MEDIA_ROOT, original_path)
#                     if not os.path.exists(fullpath):
#                         return Response({"Status": "error", "Code": 404, "Message": f"File not found: {fullpath}", "Data": []}, status=status.HTTP_404_NOT_FOUND)


#                     target_directory = os.path.join(settings.MEDIA_ROOT, 'extracted_resumes')
#                     os.makedirs(target_directory, exist_ok=True)

#                     # resume_chunk_size = 5
#                     resume_chunk_list = []
#                     with zipfile.ZipFile(fullpath, 'r') as zip_ref:
                        
                        
#                         for file_name in zip_ref.namelist():
#                             file_path = os.path.join(target_directory, file_name)
#                             file_info = zip_ref.getinfo(file_name)
#                              # Extract the file and save it to the specified path
#                             with open(file_path, 'wb') as file:
#                                 file.write(zip_ref.read(file_name))
#                             # print('///////////yyyyyyyyyyyy///////')
#                             loader = PyMuPDFLoader(file_path)
                            
#                             doc = fitz.open(file_path)
#                             page = doc.load_page(0)
#                             pix = page.get_pixmap()
#                             img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
#                             image_directory = os.path.join(settings.MEDIA_ROOT, 'resume_firstpage_images')
#                             os.makedirs(image_directory, exist_ok=True)
#                             image_path = os.path.join(image_directory, f"{file_name}.jpg")
#                             img.save(image_path)
                            
#                             pages = loader.load()
#                             resume_content = []
#                             for page in pages:
#                                 page_content = page.page_content
#                                 resume_content.append(page_content)
                                
#                             #     
                                
#                             resumeText = " ".join([w for w in resume_content])
#                             if not file_info.is_dir() and file_name.lower().endswith('.pdf'):
#                                 resume_chunk_list.append({
#                                     'imgpath':image_path,
#                                     'resumeText':resumeText,
#                                     'file_path': file_path,
#                                     'file_name': file_name,
#                                     'recruiter_resume_candidate_file_path': "extracted_resumes/"+ file_name,
#                                     'recruiter_bulk_resume_upload_id': data.recruiter_bulk_resume_upload_id,
#                                     'user_id': getData["user_id"],
#                                     'job_description_id': getData["job_description_id"],
#                                     'job_description_file': os.path.join(settings.MEDIA_ROOT, str(JobDescriptionModel.objects.get(user_id=getData["user_id"], job_description_id=getData["job_description_id"]).job_description_upload_file)),
#                                 })

#                     fff = []
#                     current_group = []
#                     current_count = 0

#                     for rec in resume_chunk_list:
#                         # print('//////////////////////')
#                         # print(rec)
#                         word_count = len(rec['resumeText'].split(' '))
#                         if current_count + word_count <= 8000:
#                             current_group.append(rec)
#                             current_count += word_count
#                         else:
#                             fff.append(current_group)
#                             current_group = [rec]
#                             current_count = word_count

#                     if current_group:
#                         fff.append(current_group)

#                     final_chunks = []

#                     # Sort records by descending word count for greedy allocation
#                     sorted_records = sorted(resume_chunk_list, key=lambda rec: len(rec['resumeText'].split(' ')), reverse=True)

#                     for rec in sorted_records:
#                         word_count = len(rec['resumeText'].split(' '))
#                         # Try to fit the record into an existing chunk
#                         placed = False
#                         for chunk in final_chunks:
#                             if sum(len(r['resumeText'].split(' ')) for r in chunk) + word_count <= 8000:
#                                 chunk.append(rec)
#                                 placed = True
#                                 break
#                         # If no existing chunk can fit the record, create a new chunk
#                         if not placed:
#                             final_chunks.append([rec])
#                     processed_resumes = []
#                     # print('////yash')
#                     # Process each chunk sequentially, but parallelize the processing within each chunk
#                     # for chunk in final_chunks:
                        
#                     #     if not chunk:  # Skip empty chunks
#                     #         continue
                            
#                     #     # Create tasks for each item in the chunk
#                     #     chunk_tasks = [(item, getData, uniqueID) for item in chunk]
#                     #     print(chunk_tasks)
#                     #     # Process items within the chunk in parallel
#                     #     with Pool(processes=os.cpu_count()) as pool:
#                     #         chunk_results = pool.starmap(process_resume_chunk, chunk_tasks)
#                     print(len(final_chunks))
                    
#                     for chunk in final_chunks:
#                         time.sleep(30)
#                         results = process_resume_chunk(chunk, getData, uniqueID)
#                         print(len(results))
#                         print(results)
#                     # with Pool(processes=os.cpu_count()) as pool:
#                     #     results = pool.starmap(process_resume_chunk, [(chunk, getData, uniqueID) for chunk in final_chunks])

#                     all_resumes = [item for sublist in results for item in sublist]

#                     sorted_resumes = sorted(all_resumes, key=operator.itemgetter('aiCompPercentageScore'), reverse=True)
#                     # sorted_resumes=[]
#                     return Response({"Status": "success", "Code": 201, "Message": "Bulk Resumes uploaded successfully", "Data": sorted_resumes}, status=status.HTTP_201_CREATED)
#                 except Exception as e:
#                     return Response({"Status": "error", "Code": 401, "Message": str(e), "Data": []}, status=status.HTTP_401_UNAUTHORIZED)
#             else:
#                 return Response({"Status": "error", "Code": 400, "Message": list(serializer.errors.values())[0][0], "Data": []}, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({"Status": "error", "Code": 401, "Message": str(e), "Data": []}, status=status.HTTP_401_UNAUTHORIZED)


class RecruiterBulkResumeAnalysisAPI(APIView):
    def post(self, request, format=None):
        try:
            getData = request.data

            if not NewUser.objects.filter(pk=getData["user_id"]).exists():
                return Response({"Status": "error", "Code": 401, "Message": "User is not found", "Data": []}, status=status.HTTP_401_UNAUTHORIZED)

            user = NewUser.objects.get(pk=getData["user_id"])

            if not JobDescriptionModel.objects.filter(user_id=getData["user_id"], job_description_id=getData["job_description_id"]).exists():
                return Response({"Status": "error", "Code": 401, "Message": "Job description is not found", "Data": []}, status=status.HTTP_401_UNAUTHORIZED)

            if not user.user_is_loggedin:
                return Response({"Status": "error", "Code": 401, "Message": "User is not loggedin", "Data": []}, status=status.HTTP_401_UNAUTHORIZED)

            if not request.FILES:
                return Response({"Error": "Zip file is required"}, status=status.HTTP_400_BAD_REQUEST)

            randomstr = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))
            uniqueID = "hires_recruiter_bulk_resume_" + randomstr
            getData["recruiter_bulk_resume_upload_id"] = uniqueID
            
            serializer = RecruiterBulkResumeUploadSerializer(data=getData)

            if not serializer.is_valid():
                return Response({"Status": "error", "Code": 400, "Message": list(serializer.errors.values())[0][0], "Data": []}, status=status.HTTP_400_BAD_REQUEST)
                
            resp = serializer.data
            userRes = RecruiterBulkResumeUploadModel(
                recruiter_bulk_resume_upload_id=resp["recruiter_bulk_resume_upload_id"],
                user_id=resp["user_id"],
                recruiter_bulk_resume_upload=getData["recruiter_bulk_resume_upload"],
            )
            userRes.save()
            
            if userRes.pk:
                try:
                    file_path = ""

                    data = RecruiterBulkResumeUploadModel.objects.get(recruiter_bulk_resume_upload_id=resp["recruiter_bulk_resume_upload_id"], user_id=resp["user_id"])
                    original_path = str(data.recruiter_bulk_resume_upload)
                    fullpath = os.path.join(settings.MEDIA_ROOT, original_path)

                    if not os.path.exists(fullpath):
                        return Response({"Status": "error", "Code": 404, "Message": f"File not found: {fullpath}", "Data": []}, status=status.HTTP_404_NOT_FOUND)

                    target_directory = os.path.join(settings.MEDIA_ROOT, 'extracted_resumes')
                    os.makedirs(target_directory, exist_ok=True)
                    extracted_text = {}
                    resume_list = []
                    
                    with zipfile.ZipFile(fullpath, 'r') as zip_ref:
                        for file_name in zip_ref.namelist():
                            
                            file_info = zip_ref.getinfo(file_name)
                            if file_info.is_dir():
                                continue
                            
                            file_path = os.path.join(target_directory, file_name)
                            if file_path.lower().endswith('.pdf'):
                                zip_ref.extract(file_name, target_directory)
                                doc = fitz.open(file_path)
                                page = doc.load_page(0)
                                pix = page.get_pixmap()
                                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                                image_directory = os.path.join(settings.MEDIA_ROOT, 'resume_firstpage_images')
                                os.makedirs(image_directory, exist_ok=True)
                                image_path = os.path.join(image_directory, f"{uniqueID}.jpg")
                                img.save(image_path)

                                randomstr = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))
                                uniqueID = "hires_recruiter_resume_candidate_" + randomstr
                                try:
                                    if JobDescriptionModel.objects.filter(user_id=getData["user_id"], job_description_id=getData["job_description_id"]).exists():
                                        uploadedjd = JobDescriptionModel.objects.get(user_id=getData["user_id"], job_description_id=getData["job_description_id"])
                                        jdpath = os.path.join(settings.MEDIA_ROOT, str(uploadedjd.job_description_upload_file))
                                        loader = PyMuPDFLoader(jdpath)
                                        pages = loader.load()

                                        jobdescription = []
                                        for page in pages:
                                            page_content = page.page_content
                                            jobdescription.append(page_content)


                                        jobdescriptionText = " ".join([w for w in jobdescription])
                                except Exception as e:
                                    return Response({"Status": "error", "Code": 401, "Message": str(e) + "Job Description", "Data": []}, status=status.HTTP_401_UNAUTHORIZED)


                                try:
                                    resumeText,extracted_details = getResumeText(file_path,jobdescriptionText)

                                except Exception as e:
                                    resumeText = ''
                                    extracted_details = {'TotalExperience':0,'Gender':'No','Skills':'','Name':'No','ATSScore':0}
                                lowercase_data = convert_keys_to_lowercase(extracted_details)

                                recZipfile = RecruiterResumeCandidateModel(
                                    recruiter_resume_candidate_id=uniqueID,
                                    recruiter_bulk_resume_upload_id=data.recruiter_bulk_resume_upload_id,
                                    user_id=getData["user_id"],
                                    job_description_id=getData["job_description_id"],
                                    recruiter_resume_candidate_firstpage_image=image_path.replace(settings.MEDIA_ROOT, '').replace('\\', '/'),
                                    recruiter_resume_candidate_file_path=file_path.split("media")[1].replace("\\", "/"),
                                    recruiter_resume_candidate_experience=lowercase_data.get('totalexperience', 'NO'),
                                    recruiter_resume_candidate_gender=lowercase_data.get('gender', 'NO'),
                                    recruiter_resume_candidate_name=lowercase_data.get('name', 'NO'),
                                    recruiter_resume_tech_stack=lowercase_data.get('skills', 'NO'),
                                    recruiter_resume_candidate_nationality=lowercase_data.get('nationality', 'NO'),
                                    recruiter_resume_candidate_ai_compare_score=lowercase_data.get('atsscore', 'NO'),
                                    recruiter_resume_candidate_extracted_text=resumeText
                                )
                                recZipfile.save()
                                doc.close()

                                print(lowercase_data)

                                extracted_text = {
                                    "recruiter_resume_candidate_file_path": file_path.split("media")[1].replace("\\", "/"),
                                    "recruiter_resume_candidate_name": lowercase_data.get('name', 'NO'),
                                    "aiCompPercentageScore": lowercase_data.get('atsscore', 'NO'),
                                    "recruiter_resume_candidate_experience": lowercase_data.get('totalexperience', 'NO'),
                                    "recruiter_resume_candidate_gender": lowercase_data.get('gender', 'NO'),
                                    "recruiter_resume_tech_stack": lowercase_data.get('skills', 'NO'),
                                    "recruiter_resume_candidate_nationality": lowercase_data.get('nationality', 'NO'),
                                }
                                resume_list.append(extracted_text)

                                
                                # lowercase_data = convert_keys_to_lowercase(extracted_details)
                                # recZipfile = RecruiterResumeCandidateModel(
                                #     recruiter_resume_candidate_id=uniqueID,
                                #     recruiter_bulk_resume_upload_id=data.recruiter_bulk_resume_upload_id,
                                #     user_id=getData["user_id"],
                                #     job_description_id=getData["job_description_id"],
                                #     recruiter_resume_candidate_firstpage_image=image_path.replace(settings.MEDIA_ROOT, '').replace('\\', '/'),
                                #     recruiter_resume_candidate_file_path=file_path.split("media")[1].replace("\\","/"),
                                #     recruiter_resume_candidate_experience = lowercase_data['totalexperience'],
                                #     recruiter_resume_candidate_gender = lowercase_data['gender'],
                                #     recruiter_resume_candidate_name = lowercase_data['name'],
                                #     recruiter_resume_tech_stack = lowercase_data['skills'],
                                #     recruiter_resume_candidate_nationality = lowercase_data['nationality'],
                                #     recruiter_resume_candidate_ai_compare_score = lowercase_data['atsscore'],
                                #     recruiter_resume_candidate_extracted_text=resumeText
                                # )
                                # recZipfile.save()
                                # doc.close()
                                # print(lowercase_data)
                                # extracted_text = {
                                #     "recruiter_resume_candidate_file_path": file_path.split("media")[1].replace("\\","/"),
                                #     "recruiter_resume_candidate_name": lowercase_data['name'],
                                #     "aiCompPercentageScore": lowercase_data['atsscore'],
                                #     "recruiter_resume_candidate_experience": lowercase_data['totalexperience'],
                                #     "recruiter_resume_candidate_gender": lowercase_data['gender'],
                                #     "recruiter_resume_candidate_name": lowercase_data['name'],
                                #     "recruiter_resume_tech_stack": lowercase_data['skills'],
                                #     "recruiter_resume_candidate_nationality": lowercase_data['nationality'],
                                # }
                                # resume_list.append(extracted_text)

                            else:
                                return Response({"Status": "error", "Code": 401, "Message": "Invalid file format", "Data": []}, status=status.HTTP_401_UNAUTHORIZED)
                        sorted_candidates = sorted(resume_list, key=lambda x: int((str(x['aiCompPercentageScore'])).strip('%')), reverse=True)

                        return Response({"Status": "success", "Code": 201, "Message": "Bulk Resumes uploaded successfully", "Data": sorted_candidates}, status=status.HTTP_201_CREATED)

                except Exception as e:
                    return Response({"Status": "error", "Code": 401, "Message": str(e), "Data": []}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({"Status": "error", "Code": 400, "Message": list(serializer.errors.values())[0][0], "Data": []}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"Status": "error", "Code": 401, "Message": str(e), "Data": []}, status=status.HTTP_401_UNAUTHORIZED)# class RecruiterBulkResumeAnalysisAPI(APIView):
    # authentication_classes=[JWTAuthentication]
    # permission_classes=[IsAuthenticated]
#######################################################################################################


class RecruiterBulkResumeAnalysisViewAllAPI(APIView):
    '''
    Get Recruiter Bulk Resume Analysis View All Data API(View)
    Request : POST
    Data =  {
                "user_id":"hires_firsetest3_0yyhogjnlh",
                "job_description_id":"hires_job_description_6s8ceoxeahnp168",
            }
    '''
    def post(self, request, format=None):

        getData = request.data
        
        if NewUser.objects.filter(pk=getData["user_id"]).exists():
            user = NewUser.objects.get(pk=getData["user_id"])
            
            if user.user_is_loggedin:
                
                if JobDescriptionModel.objects.filter( user_id=getData["user_id"], job_description_id = getData["job_description_id"]).exists():
                    
                    candidateData = RecruiterResumeCandidateModel.objects.filter(user_id=getData["user_id"] , job_description_id = getData["job_description_id"]).values()

                    # Sort data in descending order based on recruiter_resume_candidate_ai_compare_score
                    # candidateData = sorted(candidateData, key=lambda x: (float(x['recruiter_resume_candidate_ai_compare_score']), x['recruiter_resume_candidate_file_path']), reverse=True)
                    candidateData = sorted(
                        candidateData,
                        key=lambda x: (
                            float(x['recruiter_resume_candidate_ai_compare_score'].replace('%', '')),
                            x['recruiter_resume_candidate_file_path']
                        ),
                        reverse=True
                    )

                    # Format recruiter_resume_candidate_file_path with base URL
                    # for resume in candidateData:
                    #     resume['recruiter_resume_candidate_file_path'] = settings.BASE_URL + '/media' + resume['recruiter_resume_candidate_file_path']

                    res = {
                            "Status": "success",
                            "Code": 201,
                            "Message": "candidate data",
                            "Data": candidateData

                    }

                    return Response(res, status=status.HTTP_201_CREATED)
                else:
                    res = {
                            "Status": "error",
                            "Code": 401,
                            "Message": "Job Description data is not found",
                            "Data": []
                            }
                    return Response(res, status=status.HTTP_401_UNAUTHORIZED)
            
            else:
                res = {
                        "Status": "error",
                        "Code": 401,
                        "Message": "You are not logged in",
                        "Data": []
                        }
                return Response(res, status=status.HTTP_401_UNAUTHORIZED)
        
        else:
            res = {
                    "Status": "error",
                    "Code": 401,
                    "Message": "User is not found",
                    "Data": []
                    }
            return Response(res, status=status.HTTP_401_UNAUTHORIZED)
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]
    
class RecruiterCandidateResumeUpdateAPI(APIView):
    '''
        Recruiter Bulk Resume Analysis API(UPDATE)
        Request : PATCH
        Data : {

            "user_id" : hires_yashpatel1234_yj6mc5kcki,
            "recruiter_resume_candidate_id" : hires_job_description_79qui4q0hbp18iq,
            "recruiter_resume_candidate_bookmark" : true

        }
    
    '''
    def post(self, request ,format=None):
        getData = request.data

        if NewUser.objects.filter(pk = getData["user_id"]).exists():
            user = NewUser.objects.get(pk=getData["user_id"])
            
            if RecruiterResumeCandidateModel.objects.filter(recruiter_resume_candidate_id = getData["recruiter_resume_candidate_id"]).exists():
            
                if user.user_is_loggedin:

                    CandidateResumeUpdateData = RecruiterResumeCandidateModel.objects.get(recruiter_resume_candidate_id = getData["recruiter_resume_candidate_id"])
                    CandidateResumeUpdateData.user_id = getData['user_id']
                    CandidateResumeUpdateData.recruiter_resume_candidate_bookmark = getData["recruiter_resume_candidate_bookmark"]
                    CandidateResumeUpdateData.save()
                    if getData["recruiter_resume_candidate_bookmark"] == True:
                        res = {
                            "Status": "success",
                            "Code": 200,
                            "Message": "Candidate resume bookmarked successfully.",
                            "Data": {
                                "recruiter_resume_candidate_id": getData["recruiter_resume_candidate_id"],
                            }
                        }
                        return Response(res, status=status.HTTP_200_OK)
                    else:
                        res = {
                            "Status": "success",
                            "Code": 200,
                            "Message": "Candidate resume removed from bookmarks.",
                            "Data": {
                                "recruiter_resume_candidate_id": getData["recruiter_resume_candidate_id"],
                            }
                        }
                        return Response(res, status=status.HTTP_200_OK)

                else:
                    res = {
                        "Status": "error",
                        "Code": 401,
                        "Message": "You are not logged in",
                        "Data": []
                        }
                    return Response(res, status=status.HTTP_401_UNAUTHORIZED)

            else:
                res = {
                    "Status": "error",
                    "Code": 401,
                    "Message": "Recruiter Candidate Resume is not found",
                    "Data": []}
                return Response(res, status=status.HTTP_401_UNAUTHORIZED)
            
        else:
                res = {
                    "Status": "error",
                    "Code": 401,
                    "Message": "User data is not found",
                    "Data": []}
                return Response(res, status=status.HTTP_401_UNAUTHORIZED)

    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]
  
class RecruiterCandidateResumeDeleteAPI(APIView):
    
    '''
    Get Recruiter Bulk Resume Delete API(View)
    Request : POST
    Data =  {
                "user_id":"hires_firsetest3_0yyhogjnlh",
                "job_description_id":"hires_job_description_6s8ceoxeahnp168",
            }
    '''
    def post(self, request, format=None):

        getData = request.data
        
        if NewUser.objects.filter(pk=getData["user_id"]).exists():
            user = NewUser.objects.get(pk=getData["user_id"])
            
            if user.user_is_loggedin:
                
                if JobDescriptionModel.objects.filter( user_id=getData["user_id"], job_description_id = getData["job_description_id"]).exists():
                    
                    candidateData = RecruiterResumeCandidateModel.objects.filter(user_id=getData["user_id"] , job_description_id = getData["job_description_id"])
                    candidateData.delete()
                    # for candidate in candidateData:
                    #     if candidate.recruiter_resume_candidate_firstpage_image:
                    #         candidate.recruiter_resume_candidate_firstpage_image.delete(save=False)

                    #     if candidate.recruiter_resume_candidate_file_path:
                    #         file_path = os.path.join(settings.MEDIA_ROOT, candidate.recruiter_resume_candidate_file_path)
                    #         if default_storage.exists(file_path):
                    #             default_storage.delete(file_path)

                    #     candidate.delete()

                    res = {
                            "Status": "success",
                            "Code": 201,
                            "Message": "candidate data delete",
                    }

                    return Response(res, status=status.HTTP_201_CREATED)
                else:
                    res = {
                            "Status": "error",
                            "Code": 401,
                            "Message": "Job Description data is not found",
                            "Data": []
                            }
                    return Response(res, status=status.HTTP_401_UNAUTHORIZED)
            
            else:
                res = {
                        "Status": "error",
                        "Code": 401,
                        "Message": "You are not logged in",
                        "Data": []
                        }
                return Response(res, status=status.HTTP_401_UNAUTHORIZED)
        
        else:
            res = {
                    "Status": "error",
                    "Code": 401,
                    "Message": "User is not found",
                    "Data": []
                    }
            return Response(res, status=status.HTTP_401_UNAUTHORIZED)
    # authentication_classes=[JWTAuthentication]
    # permission_classes=[IsAuthenticated]
    
class RecruiterBulkResumeAnalysisViewAllBookmarkedAPI(APIView):
    '''
    Get Recruiter Bulk Resume Analysis Bookmarked View All Data API(View)
    Request : POST
    Data =  {
                "user_id":"hires_firsetest3_0yyhogjnlh",
                "job_description_id":"hires_job_description_6s8ceoxeahnp168",
                "recruiter_resume_candidate_bookmark": true
            }
    '''
    def post(self, request, format=None):

        getData = request.data
        
        if NewUser.objects.filter(pk=getData["user_id"]).exists(): 
            user = NewUser.objects.get(pk=getData["user_id"])
            
            if user.user_is_loggedin:
                
                if JobDescriptionModel.objects.filter( user_id=getData["user_id"], job_description_id = getData["job_description_id"]).exists():
                    
                    candidateData = RecruiterResumeCandidateModel.objects.filter(user_id=getData["user_id"] , job_description_id = getData["job_description_id"],recruiter_resume_candidate_bookmark = True).values()

                    candidateData = sorted(candidateData, key=lambda x: (float(x['recruiter_resume_candidate_ai_compare_score']), x['recruiter_resume_candidate_file_path']), reverse=True)

                    res = {
                            "Status": "success",
                            "Code": 200,
                            "Message": "candidate bookmarks data",
                            "Data": candidateData

                    }

                    return Response(res, status=status.HTTP_200_OK)
                else:
                    res = {
                            "Status": "error",
                            "Code": 401,
                            "Message": "Job Description data is not found",
                            "Data": []
                            }
                    return Response(res, status=status.HTTP_200_OK)
            
            else:
                res = {
                        "Status": "error",
                        "Code": 401,
                        "Message": "You are not logged in",
                        "Data": []
                        }
                return Response(res, status=status.HTTP_401_UNAUTHORIZED)
        
        else:
            res = {
                    "Status": "error",
                    "Code": 401,
                    "Message": "User is not found",
                    "Data": []
                    }
            return Response(res, status=status.HTTP_401_UNAUTHORIZED)
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]
    
#######################################################################################################
