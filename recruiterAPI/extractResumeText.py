# import langchain
# from langchain_community.document_loaders import PyMuPDFLoader
# import re
# from groq import Groq
# import json
# import time
# import os
# import spacy
# import sys


# nationality_list = [
#    "Afghan",
#    "Albanian",
#    "Algerian",
#    "American",
#    "Andorran",
#    "Angolan",
#    "Antiguans",
#    "Argentinean",
#    "Armenian",
#    "Australian",
#    "Austrian",
#    "Azerbaijani",
#    "Bahamian",
#    "Bahraini",
#    "Bangladeshi",
#    "Barbadian",
#    "Barbudans",
#    "Batswana",
#    "Belarusian",
#    "Belgian",
#    "Belizean",
#    "Beninese",
#    "Bhutanese",
#    "Bolivian",
#    "Bosnian",
#    "Brazilian",
#    "British",
#    "Bruneian",
#    "Bulgarian",
#    "Burkinabe",
#    "Burmese",
#    "Burundian",
#    "Cambodian",
#    "Cameroonian",
#    "Canadian",
#    "Cape Verdean",
#    "Central African",
#    "Chadian",
#    "Chilean",
#    "Chinese",
#    "Colombian",
#    "Comoran",
#    "Congolese",
#    "Costa Rican",
#    "Croatian",
#    "Cuban",
#    "Cypriot",
#    "Czech",
#    "Danish",
#    "Djibouti",
#    "Dominican",
#    "Dutch",
#    "East Timorese",
#    "Ecuadorean",
#    "Egyptian",
#    "Emirian",
#    "Equatorial Guinean",
#    "Eritrean",
#    "Estonian",
#    "Ethiopian",
#    "Fijian",
#    "Filipino",
#    "Finnish",
#    "French",
#    "Gabonese",
#    "Gambian",
#    "Georgian",
#    "German",
#    "Ghanaian",
#    "Greek",
#    "Grenadian",
#    "Guatemalan",
#    "Guinea-Bissauan",
#    "Guinean",
#    "Guyanese",
#    "Haitian",
#    "Herzegovinian",
#    "Honduran",
#    "Hungarian",
#    "I-Kiribati",
#    "Icelander",
#    "Indian",
#    "Indonesian",
#    "Iranian",
#    "Iraqi",
#    "Irish",
#    "Israeli",
#    "Italian",
#    "Ivorian",
#    "Jamaican",
#    "Japanese",
#    "Jordanian",
#    "Kazakhstani",
#    "Kenyan",
#    "Kittian and Nevisian",
#    "Kuwaiti",
#    "Kyrgyz",
#    "Laotian",
#    "Latvian",
#    "Lebanese",
#    "Liberian",
#    "Libyan",
#    "Liechtensteiner",
#    "Lithuanian",
#    "Luxembourger",
#    "Macedonian",
#    "Malagasy",
#    "Malawian",
#    "Malaysian",
#    "Maldivan",
#    "Malian",
#    "Maltese",
#    "Marshallese",
#    "Mauritanian",
#    "Mauritian",
#    "Mexican",
#    "Micronesian",
#    "Moldovan",
#    "Monacan",
#    "Mongolian",
#    "Moroccan",
#    "Mosotho",
#    "Motswana",
#    "Mozambican",
#    "Namibian",
#    "Nauruan",
#    "Nepalese",
#    "New Zealander",
#    "Nicaraguan",
#    "Nigerian",
#    "Nigerien",
#    "North Korean",
#    "Northern Irish",
#    "Norwegian",
#    "Omani",
#    "Pakistani",
#    "Palauan",
#    "Panamanian",
#    "Papua New Guinean",
#    "Paraguayan",
#    "Peruvian",
#    "Polish",
#    "Portuguese",
#    "Qatari",
#    "Romanian",
#    "Russian",
#    "Rwandan",
#    "Saint Lucian",
#    "Salvadoran",
#    "Samoan",
#    "San Marinese",
#    "Sao Tomean",
#    "Saudi",
#    "Scottish",
#    "Senegalese",
#    "Serbian",
#    "Seychellois",
#    "Sierra Leonean",
#    "Singaporean",
#    "Slovakian",
#    "Slovenian",
#    "Solomon Islander",
#    "Somali",
#    "South African",
#    "South Korean",
#    "Spanish",
#    "Sri Lankan",
#    "Sudanese",
#    "Surinamer",
#    "Swazi",
#    "Swedish",
#    "Swiss",
#    "Syrian",
#    "Taiwanese",
#    "Tajik",
#    "Tanzanian",
#    "Thai",
#    "Togolese",
#    "Tongan",
#    "Trinidadian or Tobagonian",
#    "Tunisian",
#    "Turkish",
#    "Tuvaluan",
#    "Ugandan",
#    "Ukrainian",
#    "Uruguayan",
#    "Uzbekistani",
#    "Venezuelan",
#    "Vietnamese",
#    "Welsh",
#    "Yemenite",
#    "Zambian",
#    "Zimbabwean",
#    "أفغاني",  # Afghan
#     "ألباني",  # Albanian
#     "جزائري",  # Algerian
#     "أمريكي",  # American
#     "أندوري",  # Andorran
#     "أنغولي",  # Angolan
#     "أنتيغوي",  # Antiguans
#     "أرجنتيني",  # Argentinean
#     "أرمني",  # Armenian
#     "أسترالي",  # Australian
#     "نمساوي",  # Austrian
#     "أذربيجاني",  # Azerbaijani
#     "باهامي",  # Bahamian
#     "بحريني",  # Bahraini
#     "بنغالي",  # Bangladeshi
#     "باربادوسي",  # Barbadian
#     "باربوداني",  # Barbudans
#     "بوتسواني",  # Batswana
#     "بيلاروسي",  # Belarusian
#     "بلجيكي",  # Belgian
#     "بليز",  # Belizean
#     "بنيني",  # Beninese
#     "بوتاني",  # Bhutanese
#     "بوليفي",  # Bolivian
#     "بوسني",  # Bosnian
#     "برازيلي",  # Brazilian
#     "بريطاني",  # British
#     "بروني",  # Bruneian
#     "بلغاري",  # Bulgarian
#     "بوركيني",  # Burkinabe
#     "بورمي",  # Burmese
#     "بوروندي",  # Burundian
#     "كمبودي",  # Cambodian
#     "كاميروني",  # Cameroonian
#     "كندي",  # Canadian
#     "كاب فيردي",  # Cape Verdean
#     "أفريقي مركزي",  # Central African
#     "تشادي",  # Chadian
#     "تشيلي",  # Chilean
#     "صيني",  # Chinese
#     "كولومبي",  # Colombian
#     "جزر القمر",  # Comoran
#     "كونغولي",  # Congolese
#     "كوستاريكي",  # Costa Rican
#     "كرواتي",  # Croatian
#     "كوباني",  # Cuban
#     "قبرصي",  # Cypriot
#     "تشيكي",  # Czech
#     "دنماركي",  # Danish
#     "جيبوتي",  # Djibouti
#     "دومينيكي",  # Dominican
#     "هولندي",  # Dutch
#     "تيموري شرقي",  # East Timorese
#     "إكوادوري",  # Ecuadorean
#     "مصري",  # Egyptian
#     "إماراتي",  # Emirian
#     "غيني استوائي",  # Equatorial Guinean
#     "إريتري",  # Eritrean
#     "استوني",  # Estonian
#     "أثيوبي",  # Ethiopian
#     "فيجي",  # Fijian
#     "فلبيني",  # Filipino
#     "فنلندي",  # Finnish
#     "فرنسي",  # French
#     "غابوني",  # Gabonese
#     "غامبي",  # Gambian
#     "جورجي",  # Georgian
#     "ألماني",  # German
#     "غاني",  # Ghanaian
#     "يوناني",  # Greek
#     "غرينادي",  # Grenadian
#     "غواتيمالي",  # Guatemalan
#     "غيني بيساوي",  # Guinea-Bissauan
#     "غيني",  # Guinean
#     "غوياني",  # Guyanese
#     "هايتي",  # Haitian
#     "هرزغوفيني",  # Herzegovinian
#     "هندوراسي",  # Honduran
#     "هنغاري",  # Hungarian
#     "كيريباسي",  # I-Kiribati
#     "آيسلندي",  # Icelander
#     "هندي",  # Indian
#     "إندونيسي",  # Indonesian
#     "إيراني",  # Iranian
#     "عراقي",  # Iraqi
#     "إيرلندي",  # Irish
#     "إسرائيلي",  # Israeli
#     "إيطالي",  # Italian
#     "ساحلي",  # Ivorian
#     "جامايكي",  # Jamaican
#     "ياباني",  # Japanese
#     "أردني",  # Jordanian
#     "كازاخستاني",  # Kazakhstani
#     "كيني",  # Kenyan
#     "كيتيني ونيفيزي",  # Kittian and Nevisian
#     "كويتي",  # Kuwaiti
#     "قرغيزي",  # Kyrgyz
#     "لاوي",  # Laotian
#     "لاتفي",  # Latvian
#     "لبناني",  # Lebanese
#     "ليبيري",  # Liberian
#     "ليبي",  # Libyan
#     "ليختنشتايني",  # Liechtensteiner
#     "لتواني",  # Lithuanian
#     "لوكسمبورغي",  # Luxembourger
#     "مقدوني",  # Macedonian
#     "مدغشقري",  # Malagasy
#     "مالاوي",  # Malawian
#     "ماليزي",  # Malaysian
#     "مالديفي",  # Maldivan
#     "مالي",  # Malian
#     "مالطي",  # Maltese
#     "مارشالي",  # Marshallese
#     "مورتاني",  # Mauritanian
#     "موريشيوسي",  # Mauritian
#     "مكسيكي",  # Mexican
#     "ميكرونيزي",  # Micronesian
#     "مولدافي",  # Moldovan
#     "موناكي",  # Monacan
#     "منغولي",  # Mongolian
#     "مغربي",  # Moroccan
#     "موسوثو",  # Mosotho
#     "موتسوانا",  # Motswana
#     "موزمبيقي",  # Mozambican
#     "ناميبي",  # Namibian
#     "ناوروي",  # Nauruan
#     "نيبالي",  # Nepalese
#     "نيوزيلندي",  # New Zealander
#     "نيكاراغوي",  # Nicaraguan
#     "نيجيري",  # Nigerian
#     "نيجري",  # Nigerien
#     "كوري شمالي",  # North Korean
#     "أيرلندي شمالي",  # Northern Irish
#     "نرويجي",  # Norwegian
#     "عماني",  # Omani
#     "باكستاني",  # Pakistani
#     "بالاواني",  # Palauan
#     "بنمي",  # Panamanian
#     "بابوا غينيا الجديدة",  # Papua New Guinean
#     "باراغواني",  # Paraguayan
#     "بيروفي",  # Peruvian
#     "بولندي",  # Polish
#     "برتغالي",  # Portuguese
#     "قطري",  # Qatari
#     "روماني",  # Romanian
#     "روسي",  # Russian
#     "رواندي",  # Rwandan
#     "سانت لوسيا",  # Saint Lucian
#     "سلفادوري",  # Salvadoran
#     "سامواني",  # Samoan
#     "سان ماريني",  # San Marinese
#     "ساو توميان",  # Sao Tomean
#     "سعودي",  # Saudi
#     "اسكتلندي",  # Scottish
#     "سنغالي",  # Senegalese
#     "صربي",  # Serbian
#     "سيشيلي",  # Seychellois
#     "سيراليوني",  # Sierra Leonean
#     "سنغافوري",  # Singaporean
#     "سلوفاكي",  # Slovakian
#     "سلوفيني",  # Slovenian
#     "جزيري سليمان",  # Solomon Islander
#     "صومالي",  # Somali
#     "جنوب أفريقي",  # South African
#     "كوري جنوبي",  # South Korean
#     "إسباني",  # Spanish
#     "سريلانكي",  # Sri Lankan
#     "سوداني",  # Sudanese
#     "سورينامي",  # Surinamer
#     "سوازي",  # Swazi
#     "سويدي",  # Swedish
#     "سويسري",  # Swiss
#     "سوري",  # Syrian
#     "تايواني",  # Taiwanese
#     "طاجيكي",  # Tajik
#     "تنزاني",  # Tanzanian
#     "تايلاندي",  # Thai
#     "توغولي",  # Togolese
#     "تونغي",  # Tongan
#     "ترينيدادي أو تواغو",  # Trinidadian or Tobagonian
#     "تونسي",  # Tunisian
#     "تركي",  # Turkish
#     "توفالي",  # Tuvaluan
#     "أوغندي",  # Ugandan
#     "أوكراني",  # Ukrainian
#     "أورغوياني",  # Uruguayan
#     "أوزبكستاني",  # Uzbekistani
#     "فنزويلي",  # Venezuelan
#     "فيتنامي",  # Vietnamese
#     "ويلزي",  # Welsh
#     "يمني",  # Yemenite
#     "زامبي",  # Zambian
#     "زيمبابوي"  # Zimbabwean
#     "Afghanistan",
#    "Albania",
#    "Algeria",
#    "United States",
#    "Andorra",
#    "Angola",
#    "Antigua and Barbuda",
#    "Argentina",
#    "Armenia",
#    "Australia",
#    "Austria",
#    "Azerbaijan",
#    "The Bahamas",
#    "Bahrain",
#    "Bangladesh",
#    "Barbados",
#    "Barbuda",
#    "Botswana",
#    "Belarus",
#    "Belgium",
#    "Belize",
#    "Benin",
#    "Bhutan",
#    "Bolivia",
#    "Bosnia and Herzegovina",
#    "Brazil",
#    "United Kingdom",
#    "Brunei",
#    "Bulgaria",
#    "Burkina Faso",
#    "Myanmar",
#    "Burundi",
#    "Cambodia",
#    "Cameroon",
#    "Canada",
#    "Cabo Verde",
#    "Central African Republic",
#    "Chad",
#    "Chile",
#    "China",
#    "Colombia",
#    "Comoros",
#    "Congo",
#    "Costa Rica",
#    "Croatia",
#    "Cuba",
#    "Cyprus",
#    "Czech Republic",
#    "Denmark",
#    "Djibouti",
#    "The Dominican Republic",
#    "The Netherlands",
#    "East Timor",
#    "Ecuador",
#    "Egypt",
#    "United Arab Emirates",
#    "Equatorial Guinea",
#    "Eritrea",
#    "Estonia",
#    "Ethiopia",
#    "Fiji",
#    "The Philippines",
#    "Finland",
#    "France",
#    "Gabon",
#    "Gambia",
#    "Georgia",
#    "Germany",
#    "Ghana",
#    "Greece",
#    "Grenada",
#    "Guatemala",
#    "Guinea-Bissau",
#    "Guinea",
#    "Guyana",
#    "Haiti",
#    "Bosnia and Herzegovina",
#    "Honduras",
#    "Hungary",
#    "Kiribati",
#    "Iceland",
#    "India",
#    "Indonesia",
#    "Iran",
#    "Iraq",
#    "Ireland",
#    "Israel",
#    "Italy",
#    "Côte d'Ivoire",
#    "Jamaica",
#    "Japan",
#    "Jordan",
#    "Kazakhstan",
#    "Kenya",
#    "Saint Kitts and Nevis",
#    "Kuwait",
#    "Kyrgyzstan",
#    "Laos",
#    "Latvia",
#    "Lebanon",
#    "Liberia",
#    "Libya",
#    "Liechtenstein",
#    "Lithuania",
#    "Luxembourg",
#    "North Macedonia",
#    "Madagascar",
#    "Malawi",
#    "Malaysia",
#    "Maldives",
#    "Mali",
#    "Malta",
#    "The Marshall Islands",
#    "Mauritania",
#    "Mauritius",
#    "Mexico",
#    "Micronesia",
#    "Moldova",
#    "Monaco",
#    "Mongolia",
#    "Morocco",
#    "Lesotho",
#    "Botswana",
#    " Mozambique",
#    "Namibia",
#    "Nauru",
#    "Nepal",
#    "New Zealand",
#    "Nicaragua",
#    "Nigeria",
#    "Niger",
#    "North Korea",
#    "Northern Ireland",
#    "Norway",
#    "Oman",
#    "Pakistan",
#    "Palau",
#    "Panama",
#    "Papua New Guinea",
#    "Paraguay",
#    "Peru",
#    "Poland",
#    "Portugal",
#    "Qatar",
#    "Romania",
#    "Russia",
#    "Rwanda",
#    "Saint Lucia",
#    "El Salvador",
#    "Samoa",
#    "San Marino",
#    "Sao Tome and Principe",
#    "Saudi Arabia",
#    "Scotland",
#    "Senegal",
#    "Serbia",
#    "Seychelles",
#    "Sierra Leone",
#    "Singapore",
#    "Slovakia",
#    "Slovenia",
#    "Solomon Islands",
#    "Somalia",
#    "South Africa",
#    "South Korea",
#    "Spain",
#    "Sri Lanka",
#    "Sudan",
#    "Suriname",
#    "Swaziland",
#    "Sweden",
#    "Switzerland",
#    "Syria",
#    "Taiwan",
#    "Tajikistan",
#    "Tanzania",
#    "Thailand",
#    "Togo",
#    "Tonga",
#    "Trinidad and Tobago",
#    "Tunisia",
#    "Turkey",
#    "Tuvalu",
#    "Uganda",
#    "Ukraine",
#    "Uruguay",
#    "Uzbekistan",
#    "Venezuela",
#    "Vietnam",
#    "Wales",
#    "Yemen",
#    "Zambia",
#    "Zimbabwe"
# ]


# sys.path.append(r'recruiterAPI')



# # Load spaCy model for named entity recognition (NER)
# nlp = spacy.load("en_core_web_sm")

# # Keywords in English and Arabic that may indicate nationality
# nationality_keywords = [
#     'nationality', 'citizenship', 'country of origin', 'origin', 'resident of', 'place of birth', 'born in',
#     'الجنسية', 'المواطنة', 'بلد الأصل', 'الأصل', 'مقيم في', 'مكان الميلاد', 'ولد في'
# ]

# def extract_nationality(text):
#     text = re.sub(r'\s+', ' ', text).strip()

#     # Step 1: Keyword-based extraction
#     for keyword in nationality_keywords:
#         pattern = rf'({keyword})\s*[:\-]?\s*([\w\s,-]+)'
#         match = re.search(pattern, text, re.IGNORECASE | re.UNICODE)
#         if match:
#             possible_nationality = match.group(2).strip()
            
#             # Check for matches in nationality list with partial matching enabled
#             for nationality in nationality_list:
#                 if nationality.lower() in possible_nationality.lower() or possible_nationality.lower() in nationality.lower():
#                     return nationality.capitalize()
    
#     # Step 2: Direct matching with nationalities
#     for nationality in nationality_list:
#         if nationality.lower() in text.lower():
#             return nationality.capitalize()
    
#     # Step 3: NER-based fallback
#     doc = nlp(text)
#     for ent in doc.ents:
#         if ent.label_ == "GPE" and any(nationality.lower() == ent.text.lower() for nationality in nationality_list):
#             return ent.text.capitalize()
    
#     return "Nationality not found"

# # Get user input
# def user_input():
#     print("Paste the resume text below (press Enter on an empty line to finish):\n")
#     lines = []
#     while True:
#         line = input()
#         if line == "":
#             break
#         lines.append(line)
#     return " ".join(lines)



# nationality_set = set([n.lower() for n in nationality_list])  # Lowercasing for case-insensitive matching

# # Load spaCy's pre-trained English model outside the functions (avoids reloading for each function call)
# nlp = spacy.load('en_core_web_sm')


# # Set your Groq API key directly in the code
# api_key = "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"

# # Initialize the Groq client with the API key
# client = Groq(api_key=api_key)

# # Step 2: Preprocessing functions
# def preprocess_resume_text(text):
#     return text.strip()

# # Step 3: Email Extraction using regex
# def extract_email(text):
#     email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
#     match = re.search(email_pattern, text)
#     return match.group(0) if match else None


# # Gender Extraction
# def extract_gender(resume_text):
    
#     male_patterns = [r'\b(male|man|guy|boy)\b', r'\b(his|him|he)\b']
#     female_patterns = [r'\b(female|woman|girl)\b', r'\b(hers|her|she)\b']

#     for pattern in male_patterns:
#         if re.search(pattern, resume_text, re.IGNORECASE):
#             return 'Male'

#     for pattern in female_patterns:
#         if re.search(pattern, resume_text, re.IGNORECASE):
#             return 'Female'

#     return "No"

# # Step 4: Extracting details using Groq API

# def extract_details(text):
#     try:
#         processed_text = preprocess_resume_text(text)
#         extracted_email = extract_email(text)
#         extracted_nationality = extract_nationality(text)
#         extracted_gender = extract_gender(text)

#         prompt = f"""
#         Please extract and format the following details from the provided resume text into a JSON object:

#         - **Name**: The full name of the individual.
#         - **Skills**: A list of skills mentioned in the resume. Each skill should be an item in a JSON array. Include all listed skills, and do not truncate.
#         - **TotalExperience**: TotalExperience: Calculate the total professional work experience in months as a numeric value by:
#                 -Identifying full-time, paid professional work experiences that include a start and end date.
#                 -For each role with dates, calculate the duration in months. Use the following steps:
#                 -Convert the duration for each role to months (1 year = 12 months).
#                 -For roles listed as "Present," assume the end date is the current month.
#                 -Add up all individual durations in months to obtain the total.
#                 -Exclude any internships, educational experience, volunteer work, or personal projects, as well as roles without valid dates.
#                 -If no professional work experience is found, return 0.        
#         - **ExperienceDetails**: Include only the **job title** and a **brief description** of the person's responsibilities or work done in that role.
#         - **Education**: Extract only the **degree** (e.g., Bachelor of Science, Master of Business Administration) from the resume. Do not include the institution name, start/end dates, or any additional information.
#         - **Nationality**: {extracted_nationality}
#         - **Gender**: {extracted_gender}
#         - **Email**: {extracted_email if extracted_email else 'Email not found'}

#         Resume Text:
#         {processed_text}

#         Output in JSON format:
#         """

#         while True:
#             # try:
#                 # Make the API call to Groq
#                 chat_completion = client.chat.completions.create(
#                     messages=[{"role": "user", "content": prompt}],
#                     model="llama3-groq-70b-8192-tool-use-preview",
#                 )

#                 generated_text = chat_completion.choices[0].message.content.strip()

#                 # Ensure response is in JSON format
#                 if generated_text.startswith('{'):
#                     return generated_text
#                 else:
#                     json_start = generated_text.find('{')
#                     json_end = generated_text.rfind('}') + 1
#                     return generated_text[json_start:json_end]

#             # except Exception as e:
#             #     if "exceeded token limit" in str(e).lower():
#             #         print("Token limit exceeded, waiting for 3-4 seconds before retrying...")
#             #         time.sleep(4)  # Wait for 3-4 seconds
#             #         continue
#             #     else:
#             #         raise e

#     except Exception as e:
#         print(f"Error during API call: {e}")
#         return None


# nlp = spacy.load("en_core_web_sm")


# # Step 5: Resume Input Validation
# def validate_resume_input(resume_text):
#     if not resume_text or not resume_text.strip():
#         raise ValueError("Resume input is empty or invalid.")

# # Step 6: ATS Calculation using Groq Prompt
# def calculate_ats(job_description, extracted_details):
#     try:
#         prompt = f"""
#         Given the following job description and resume details, provide only the ATS score as a numeric percentage from 0 to 100, without any additional text.

#         Job Description:
#         {job_description}

#         Resume Details:
#         {extracted_details}
#         """

#         # Make the API call to Groq
#         chat_completion = client.chat.completions.create(
#             messages=[{"role": "user", "content": prompt}],
#             model="llama3-groq-70b-8192-tool-use-preview",
#         )

#         ats_score = chat_completion.choices[0].message.content.strip()

#         # Ensure the response is a valid number
#         ats_score = re.search(r'\d+', ats_score)  # Extract numeric value
#         return ats_score.group(0) if ats_score else None

#     except Exception as e:
#         print(f"Error during ATS calculation: {e}")
#         return None



# def getResumeText(resumeText,job_description):

#     # loader = PyMuPDFLoader(filepath)
#     # pages = loader.load()
#     # resume_content = []
#     # for page in pages:
#     #     page_content = page.page_content
#     #     resume_content.append(page_content)


#     # resumeText = " ".join([w for w in resume_content])
#     try:
#         if resumeText or len(resumeText)!=0:
#             extracted_details = extract_details(resumeText)
            
#             if not extracted_details:

#                 data_dict = {'TotalExperience':0,'Gender':'No','Skills':'','Name':'No','ATSScore':'0%'}
#             else:
#                 required_keys = ['nationality', 'gender']
 
#                 data_dict = json.loads(extracted_details)
            
#                 for key in required_keys:
#                     if key.lower() not in data_dict:
#                         data_dict[key] = "No"
                                        
#                 ats_score = calculate_ats(job_description, json.dumps(extracted_details))
                    
#                 data_dict['ATSScore'] = f"{ats_score}%"

#     except:
#         extracted_details = {'TotalExperience':0,'Gender':'No','Skills':'','Name':'No','ATSScore':'0%'}
#         data_dict = json.loads(extracted_details)
    
#     # print(data_dict)
#     return resumeText,data_dict
import re
import json
import os

from groq import Groq
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


# Convert nationality_list to a set for faster lookup
nationality_set = set([n.lower() for n in nationality_list])

# Load spaCy's pre-trained English model outside the functions
nlp = spacy.load('en_core_web_sm')



# Set your Groq API key
api_key = "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"

# Initialize the Groq client with the API key
client = Groq(api_key=api_key)

def preprocess_resume_text(text):
    return text.strip()

def extract_email(text):
    email_pattern = r'\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b'
    match = re.search(email_pattern, text)
    return match.group(0) if match else 'null'

nationality_keywords = [
    'nationality', 'citizenship', 'country of origin', 'origin', 'resident of', 'place of birth', 'born in',
    'الجنسية', 'المواطنة', 'بلد الأصل', 'الأصل', 'مقيم في', 'مكان الميلاد', 'ولد في'
]

def extract_nationality(text):
    text = re.sub(r'\s+', ' ', text).strip()
    
    for keyword in nationality_keywords:
        pattern = rf'({keyword})\s*[:\-]?\s*([\w\s,-]+)'
        match = re.search(pattern, text, re.IGNORECASE | re.UNICODE)
        if match:
            possible_nationality = match.group(2).strip()
            for nationality in nationality_list:
                if nationality.lower() in possible_nationality.lower() or possible_nationality.lower() in nationality.lower():
                    return nationality.capitalize()
    
    for nationality in nationality_list:
        if nationality.lower() in text.lower():
            return nationality.capitalize()
    
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "GPE" and any(nationality.lower() == ent.text.lower() for nationality in nationality_list):
            return ent.text.capitalize()
    
    return "null"

def extract_gender(resume_text):
    male_patterns = [r'\b(male|man|guy|boy)\b', r'\b(his|him|he)\b']
    female_patterns = [r'\b(female|woman|girl)\b', r'\b(hers|her|she)\b']

    for pattern in male_patterns:
        if re.search(pattern, resume_text, re.IGNORECASE):
            return 'Male'

    for pattern in female_patterns:
        if re.search(pattern, resume_text, re.IGNORECASE):
            return 'Female'

    return 'Unknown'

def parse_resume(resume_text, job_description=None):
    system_prompt = """You are an advanced Applicant Tracking System (ATS) parsing expert with deep understanding of semantic matching precise resume and a parsing expert with a focus on accurate experience calculation. Convert diverse experience formats into a clear, consistent representation. Follow these core principles:
    1. Extract information exactly as it appears in the document
    2. Be objective and literal in your interpretation
    3. Use null for missing information
    4. Do not fabricate or assume any details
    5. Prioritize accuracy over completeness"""
    analysis_prompt = f"""Extract resume information with maximum precision:

    Resume Text:
    {resume_text}
    {f'Job Description: {job_description}' if job_description else ''}

    Output strictly following this JSON schema:
    {{
        "candidate_name": "Full legal name (exact from resume)",
        "skills": [
            "List technical skills ONLY from 'Skills' section",
            "Use exact terminology from resume",
            "Lowercase, comma-separated"
        ],
        "ats_matching_score": "Semantic score of matching resume with job description",
        "total_experience": "Cumulative professional experience",
        "email": "Contact email address",
        "gender": "As specified in resume",
        "nationality": "National origin mentioned"
    }}

    Key Parsing Guidelines:
    - Skills: Extract verbatim from dedicated skills section
    - Experience: Calculate without date overlaps
    - Matching Score: Use semantic keyword alignment
    - Precision over comprehensiveness"""
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a expert HR analyst and recuriter."},
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": analysis_prompt}
        ],
        model="llama3-groq-70b-8192-tool-use-preview",
        temperature=0.1,  # Low temperature for more consistent outputs
        max_tokens=4096,
        response_format={"type": "json_object"}
    )
    try:
        parsed_data = json.loads(chat_completion.choices[0].message.content)
        # Extract additional information using regex functions
        email = extract_email(resume_text) or "null"
        gender = extract_gender(resume_text)
        nationality = extract_nationality(resume_text) or "null"
        # Add the additional extracted data to the parsed data
        parsed_data["email"] = email
        parsed_data["gender"] = gender
        parsed_data["nationality"] = nationality
        validate_parsed_data(parsed_data)
        return parsed_data
    except json.JSONDecodeError:
        raise Exception("Failed to parse the response as JSON")
def validate_parsed_data(data):
    """Validate the parsed data for completeness and format"""
    required_fields = ["candidate_name", "skills", "ats_matching_score", "total_experience"]
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
    return parse_resume
def getResumeText(resumeText, job_description):
    try:
        if resumeText and len(resumeText) != 0:
            result = parse_resume(resumeText, job_description)
            print(result)
            if not result:
                data_dict = {'ats_matching_score': '0%', 'Gender': 'No', 'Skills': '', 'candidate_name': 'No', 'total_experience': 0, 'Nationality': 'No'}
            else:
                data_dict = result
        else:
            data_dict = {'ats_matching_score': '0%', 'Gender': 'No', 'Skills': '', 'candidate_name': 'No', 'total_experience': 0, 'Nationality': 'No'}
    except Exception as e:
        print(e, 'error')
        data_dict = {'ats_matching_score': '0%', 'Gender': 'No', 'Skills': '', 'candidate_name': 'No', 'total_experience': 0, 'Nationality': 'No'}
    return resumeText, data_dict

# def parse_resume(resume_text, job_description=None):
#         system_prompt = """You are an expert resume parser specialized in extracting precise information from resumes. 
#         Analyze the provided resume carefully and extract the requested information in JSON format. 
#         Be thorough and precise in your extraction, maintaining the exact information as presented in the resume. Don't extract the skills which is not mentioned in the skill section, extract only skills which is mentioned in the skill section.
#         If certain information is not found, mark it as null rather than making assumptions."""

#         analysis_prompt = f"""Please analyze the following resume and extract key information in a structured JSON format. For the experience calculation, consider overlapping dates only once and calculate total months accurately. If a job description is provided, calculate a matching score based on skill overlap, experience relevance, and education alignment. the Matching score needs to be always end with "%".
#         Calculate the total score accurate without any assumptions and need to be naturally (like 73%, 88%, 92%) based on exact matches, avoiding artificial rounding.if resume is not matching with job description and ATS score is "0%" then show us "0%".

#         Resume Text:
#         {resume_text}

#         {f'Job Description: {job_description}' if job_description else ''}

#         Please provide the information in the following JSON structure:
#         {{
#             "candidate_name": "Full name of the candidate",
#             "skills": ["List of all technical and soft skills mentioned in resume skill sections"],
#             "total_experience_months": "Total work experience in months",
#             "experience": [
#                 {{
#                     "job_title": "Title of the position",
#                     "company": "Company name",
#                     "duration": {{
#                         "start_date": "YYYY-MM",
#                         "end_date": "YYYY-MM or 'Present'",
#                         "months": "Duration in months"
#                     }},
#                     "responsibilities": ["List of key responsibilities and achievements"]
#                 }}
#             ],
#             "education": [
#                 {{
#                     "degree": "Degree name",
#                     "institution": "Institution name",
#                     "duration": {{
#                         "start_date": "YYYY-MM",
#                         "end_date": "YYYY-MM"
#                     }}
#                 }}
#             ],
#             "ats_matching_score": "Percentage score should be always between(0% to 100%) and make sure score should be natural (like 56%, 29%, 87%) generate the proper and perfect matching score, with rounding off.
#             "email": "Email of the candidate",
#             "gender": "Gender of the candidate",
#             "nationality": "Nationality of the candidate"
#         }}"""

#         chat_completion = client.chat.completions.create(
#             messages=[
#                 {"role": "system", "content": system_prompt},
#                 {"role": "user", "content": analysis_prompt}
#             ],
#             model="llama3-groq-70b-8192-tool-use-preview",
#             temperature=0.1,  # Low temperature for more consistent outputs
#             max_tokens=4096,
#             response_format={"type": "json_object"}
#         )
        
#         try:
#             parsed_data = json.loads(chat_completion.choices[0].message.content)
#             # Extract additional information using regex functions
#             email = extract_email(resume_text) or "null"
#             gender = extract_gender(resume_text)
#             nationality = extract_nationality(resume_text) or "null"

#             # Add the additional extracted data to the parsed data
#             parsed_data["email"] = email
#             parsed_data["gender"] = gender
#             parsed_data["nationality"] = nationality
            
#             validate_parsed_data(parsed_data)
#             return parsed_data
#         except json.JSONDecodeError:
#             raise Exception("Failed to parse the response as JSON")

# def validate_parsed_data(data):
#         """Validate the parsed data for completeness and format"""
#         required_fields = ["candidate_name", "skills", "total_experience_months", "experience", "education"]
#         for field in required_fields:
#             if field not in data:
#                 raise ValueError(f"Missing required field: {field}")
        
#         # Validate experience entries
#         for exp in data["experience"]:
#             required_exp_fields = ["job_title", "company", "duration", "responsibilities"]
#             for field in required_exp_fields:
#                 if field not in exp:
#                     raise ValueError(f"Missing required experience field: {field}")

#         return parse_resume


# def getResumeText(resumeText,job_description):

#     try:
#         if resumeText or len(resumeText)!=0:
#             result = parse_resume(resumeText, job_description)
#             print(result)
#             if not result:
#                 data_dict = {'total_experience_months':0,'Gender':'No','Skills':'','candidate_name':'No','ats_matching_score':'0%','Nationality':'No'}
#                 # data_dict = json.loads(extracted_details)
#             else:
#                 data_dict = result
#         else:
#             data_dict = {'total_experience_months':0,'Gender':'No','Skills':'','candidate_name':'No','ats_matching_score':'0%','Nationality':'No'}       
#     except Exception as e:
#         print(e,'error')
#         data_dict = {'total_experience_months':0,'Gender':'No','Skills':'','candidate_name':'No','ats_matching_score':'0%','Nationality':'No'}
#         # data_dict = json.loads(extracted_details)

#     return resumeText,data_dict
