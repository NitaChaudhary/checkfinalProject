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
resume_list = []

import re

def clean_text(text):
    # Remove non-ASCII characters
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    # Replace newlines and tabs with space
    text = re.sub(r'\s+', ' ', text)
    # Remove multiple spaces
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()



def process_single_resume(resume):
    try:
        file_path = resume['file_path']
        file_name = resume['file_name']
        fullpath = os.path.join(settings.MEDIA_ROOT, file_path)
        print(fullpath)
        print(f"Full file path: {str(file_path)}")

        randomstr = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))
        unique_resumeID = "hires_recruiter_resume_candidate_" + randomstr

        loader = PyMuPDFLoader(resume['job_description_file'])
        pages = loader.load()

        jobdescription = []
        for page in pages:
            page_content = page.page_content
            jobdescription.append(page_content)

        jobdescriptionText = " ".join([w for w in jobdescription])
        jobcleaned_text = clean_text(jobdescriptionText)
        # Extract resume text using getResumeText
        resumeText, extracted_details = getResumeText(resume['resumeText'], jobcleaned_text)
        lowercase_data = convert_keys_to_lowercase(extracted_details)
        
        randomstr = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))
        uniqueID = "hires_recruiter_resume_candidate_" + randomstr
        
        recZipfile = RecruiterResumeCandidateModel(
                recruiter_resume_candidate_id=uniqueID,
                recruiter_bulk_resume_upload_id=resume['recruiter_bulk_resume_upload_id'],
                user_id=resume['user_id'],
                job_description_id=resume['job_description_id'],
                recruiter_resume_candidate_firstpage_image=resume['imgpath'].split("media")[1].replace("\\","/"),
                recruiter_resume_candidate_file_path=file_path.split("media")[1].replace("\\","/"),
                recruiter_resume_candidate_experience = lowercase_data.get('total_experience_months','No'),
                recruiter_resume_candidate_gender = lowercase_data.get('gender','No'),
                recruiter_resume_candidate_name = lowercase_data.get('candidate_name','No'),
                recruiter_resume_tech_stack = lowercase_data.get('skills','No'),
                recruiter_resume_candidate_nationality = lowercase_data.get('nationality', 'No'),
                recruiter_resume_candidate_ai_compare_score = lowercase_data.get('ats_matching_score','No'),
                recruiter_resume_candidate_extracted_text=resume['resumeText']
            )
        recZipfile.save()
        return {
            "recruiter_resume_candidate_file_path": resume['recruiter_resume_candidate_file_path'],
            "recruiter_resume_candidate_name": lowercase_data.get('candidate_name','No'),
            "aiCompPercentageScore": lowercase_data.get('ats_matching_score','No'),
            "recruiter_resume_candidate_experience": lowercase_data.get('total_experience_months','No'),
            "recruiter_resume_candidate_gender": lowercase_data.get('gender','No'),
            "recruiter_resume_tech_stack": lowercase_data.get('skills','No'),
            "recruiter_resume_candidate_nationality": lowercase_data.get('nationality', 'No')
        }
    except Exception as e:
        print(f"Error processing resume: {e}")
        return {
            "recruiter_resume_candidate_file_path": resume['recruiter_resume_candidate_file_path'],
            "recruiter_resume_candidate_name": 'No',
            "aiCompPercentageScore": '0%',
            "recruiter_resume_candidate_experience": 0,
            "recruiter_resume_candidate_gender": 'No',
            "recruiter_resume_tech_stack": '',
            "recruiter_resume_candidate_nationality": "No"
            
        }

# Main function for processing resume chunks
def process_resume_chunk(resume_chunk, getResumeText, uniqueID):
    

    # Use ProcessPoolExecutor for multiprocessing
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
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

# # core
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
            else:
                return Response({"Status": "error", "Code": 401, "Message": "Invalid file format", "Data": []}, status=status.HTTP_401_UNAUTHORIZED)
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

                    # resume_chunk_size = 5
                    resume_chunk_list = []
                    with zipfile.ZipFile(fullpath, 'r') as zip_ref:
                        
                        
                        for file_name in zip_ref.namelist():
                            file_path = os.path.join(target_directory, file_name)
                            file_info = zip_ref.getinfo(file_name)
                             # Extract the file and save it to the specified path
                            with open(file_path, 'wb') as file:
                                file.write(zip_ref.read(file_name))
                            loader = PyMuPDFLoader(file_path)
                            
                            doc = fitz.open(file_path)
                            page = doc.load_page(0)
                            pix = page.get_pixmap()
                            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                            image_directory = os.path.join(settings.MEDIA_ROOT, 'resume_firstpage_images')
                            os.makedirs(image_directory, exist_ok=True)
                            image_path = os.path.join(image_directory, f"{file_name}.jpg")
                            img.save(image_path)
                            
                            pages = loader.load()
                            resume_content = []
                            for page in pages:
                                page_content = page.page_content
                                resume_content.append(page_content)
                                
                            #     
                            resumeText = " ".join([w for w in resume_content])
                            cleaned_text = clean_text(resumeText)    
                            if not file_info.is_dir() and file_name.lower().endswith('.pdf'):
                                resume_chunk_list.append({
                                    '':uniqueID,
                                    'imgpath':image_path,
                                    'resumeText':cleaned_text,
                                    'file_path': file_path,
                                    'file_name': file_name,
                                    'recruiter_resume_candidate_file_path': "extracted_resumes/"+ file_name,
                                    'recruiter_bulk_resume_upload_id': data.recruiter_bulk_resume_upload_id,
                                    'user_id': getData["user_id"],
                                    'job_description_id': getData["job_description_id"],
                                    'job_description_file': os.path.join(settings.MEDIA_ROOT, str(JobDescriptionModel.objects.get(user_id=getData["user_id"], job_description_id=getData["job_description_id"]).job_description_upload_file)),
                                })

                    fff = []
                    current_group = []
                    current_count = 0

                    for rec in resume_chunk_list:

                        word_count = len(rec['resumeText'].split(' '))
                        if current_count + word_count <= 8000:
                            current_group.append(rec)
                            current_count += word_count
                        else:
                            fff.append(current_group)
                            current_group = [rec]
                            current_count = word_count

                    if current_group:
                        fff.append(current_group)

                    final_chunks = []

                    # Sort records by descending word count for greedy allocation
                    sorted_records = sorted(resume_chunk_list, key=lambda rec: len(rec['resumeText'].split(' ')), reverse=True)

                    for rec in sorted_records:
                        word_count = len(rec['resumeText'].split(' '))
                        # Try to fit the record into an existing chunk
                        placed = False
                        for chunk in final_chunks:
                            if sum(len(r['resumeText'].split(' ')) for r in chunk) + word_count <= 8000:
                                chunk.append(rec)
                                placed = True
                                break
                        # If no existing chunk can fit the record, create a new chunk
                        if not placed:
                            final_chunks.append([rec])
    
                    global resume_list  # Declare the global variable
                    resume_list.clear()
                    for chunk in final_chunks:
                        time.sleep(10)
                        results = process_resume_chunk(chunk, getData, uniqueID)
                        
                 
                    sorted_candidates = sorted(resume_list, key=lambda x: int((str(x['aiCompPercentageScore'])).strip('%')), reverse=True)
                    return Response({"Status": "success", "Code": 201, "Message": "Bulk Resumes uploaded successfully", "Data": sorted_candidates}, status=status.HTTP_201_CREATED)
                except Exception as e:
                    return Response({"Status": "error", "Code": 401, "Message": str(e), "Data": []}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({"Status": "error", "Code": 400, "Message": list(serializer.errors.values())[0][0], "Data": []}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"Status": "error", "Code": 401, "Message": str(e), "Data": []}, status=status.HTTP_401_UNAUTHORIZED)


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

class RecruiterBulkResumeAnalysisNewAPI(APIView):
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
                    cleaned_text = clean_text(jobdescriptionText)
                    print(jobdescriptionText)
                    print('-------------------------------------------------------')
                    print(cleaned_text)
                    print('#############################@@@@@@@@@@@@@@@@@@@@@@#################################')
                    print()
                    print()
                    print()
                    print()
            else:
                return Response({"Status": "error", "Code": 401, "Message": "Invalid file format", "Data": []}, status=status.HTTP_401_UNAUTHORIZED)
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

                    # resume_chunk_size = 5
                    resume_chunk_list = []
                    with zipfile.ZipFile(fullpath, 'r') as zip_ref:
                        
                        
                        for file_name in zip_ref.namelist():
                            file_path = os.path.join(target_directory, file_name)
                            file_info = zip_ref.getinfo(file_name)
                                # Extract the file and save it to the specified path
                            with open(file_path, 'wb') as file:
                                file.write(zip_ref.read(file_name))
                            loader = PyMuPDFLoader(file_path)
                            
                            doc = fitz.open(file_path)
                            page = doc.load_page(0)
                            pix = page.get_pixmap()
                            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                            image_directory = os.path.join(settings.MEDIA_ROOT, 'resume_firstpage_images')
                            os.makedirs(image_directory, exist_ok=True)
                            image_path = os.path.join(image_directory, f"{file_name}.jpg")
                            img.save(image_path)
                            
                            pages = loader.load()
                            resume_content = []
                            for page in pages:
                                page_content = page.page_content
                                resume_content.append(page_content)

                            resumeText = " ".join([w for w in resume_content])
                            cleaned_text = clean_text(resumeText)
                            print(resumeText)
                            print('-------------------------------------------------------')
                            print(cleaned_text)
                            print('##############################################################')
                            print()
                            print()
                            print()
                            if not file_info.is_dir() and file_name.lower().endswith('.pdf'):
                                resume_chunk_list.append({
                                    '':uniqueID,
                                    'imgpath':image_path,
                                    'resumeText':resumeText,
                                    'file_path': file_path,
                                    'file_name': file_name,
                                    'recruiter_resume_candidate_file_path': "extracted_resumes/"+ file_name,
                                    'recruiter_bulk_resume_upload_id': data.recruiter_bulk_resume_upload_id,
                                    'user_id': getData["user_id"],
                                    'job_description_id': getData["job_description_id"],
                                    'job_description_file': os.path.join(settings.MEDIA_ROOT, str(JobDescriptionModel.objects.get(user_id=getData["user_id"], job_description_id=getData["job_description_id"]).job_description_upload_file)),
                                })
                        return Response({"Status": "success", "Code": 201, "Message": "Bulk Resumes uploaded successfully", "Data": []}, status=status.HTTP_201_CREATED)
                except Exception as e:
                    return Response({"Status": "error", "Code": 401, "Message": str(e), "Data": []}, status=status.HTTP_401_UNAUTHORIZED)
            
        except Exception as e:
            return Response({"Status": "error", "Code": 401, "Message": str(e), "Data": []}, status=status.HTTP_401_UNAUTHORIZED)
