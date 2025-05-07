
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
# from candidateresumeAPI.models import *
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
# from userloginAPI.views import APIKeyAuthentication
import zipfile
import json
from PIL import Image
import fitz
from langchain_community.document_loaders import PyMuPDFLoader
from multiprocessing import Pool, cpu_count
from concurrent.futures import ThreadPoolExecutor
import django
from django.db import connection

# from .extractResumeTextcopy import getResumeText
from .extractResumeText import getResumeText

# import spacy

# nlp = spacy.load("en_core_web_sm")

def convert_keys_to_lowercase(data):
    if isinstance(data, dict):
        return {k.lower(): convert_keys_to_lowercase(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_keys_to_lowercase(item) for item in data]
    else:
        return data

def process_single_resume(args):
    """
    Process a single resume file with the given parameters
    """
    try:
        # Close the database connection for this thread
        connection.close()
        
        file_name, target_directory, bulk_upload_id, job_description_text, user_id, job_description_id = args
        
        file_path = os.path.join(target_directory, file_name)
        if not file_path.lower().endswith('.pdf'):
            return None
            
        # Create document object
        doc = fitz.open(file_path)
        page = doc.load_page(0)
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # Generate unique ID for this resume's image
        randomstr = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))
        image_unique_id = "img_" + randomstr
        
        # Save first page image
        image_directory = os.path.join(settings.MEDIA_ROOT, 'resume_firstpage_images')
        os.makedirs(image_directory, exist_ok=True)
        image_path = os.path.join(image_directory, f"{image_unique_id}.jpg")
        img.save(image_path)
        
        # Generate unique ID for this resume
        resume_randomstr = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))
        resume_unique_id = "hires_recruiter_resume_candidate_" + resume_randomstr
        
        # Extract resume text and details
        try:
            resumeText, extracted_details = getResumeText(file_path, job_description_text)
        except Exception as e:
            resumeText = ''
            extracted_details = {
                'TotalExperience': 0,
                'Gender': 'No',
                'Skills': '',
                'Name': 'No',
                'ATSScore': 0
            }
        
        lowercase_data = convert_keys_to_lowercase(extracted_details)
        
        # Create database record
        from recruiterAPI.models import RecruiterResumeCandidateModel
        
        recZipfile = RecruiterResumeCandidateModel(
            recruiter_resume_candidate_id=resume_unique_id,
            recruiter_bulk_resume_upload_id=bulk_upload_id,
            user_id=user_id,
            job_description_id=job_description_id,
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
        
        return {
            "recruiter_resume_candidate_file_path": file_path.split("media")[1].replace("\\", "/"),
            "recruiter_resume_candidate_name": lowercase_data.get('name', 'NO'),
            "aiCompPercentageScore": lowercase_data.get('atsscore', 'NO'),
            "recruiter_resume_candidate_experience": lowercase_data.get('totalexperience', 'NO'),
            "recruiter_resume_candidate_gender": lowercase_data.get('gender', 'NO'),
            "recruiter_resume_tech_stack": lowercase_data.get('skills', 'NO'),
            "recruiter_resume_candidate_nationality": lowercase_data.get('nationality', 'NO'),
        }
        
    except Exception as e:
        print(f"Error processing {file_name}: {str(e)}")
        return None

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
     

#####################################################

# Recruiter Bulk Resume Analysis

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
#                     with zipfile.ZipFile(fullpath, 'r') as zip_ref:
#                         for file_name in zip_ref.namelist():
#                             file_info = zip_ref.getinfo(file_name)
#                             if file_info.is_dir():
#                                 continue
                            
#                             file_path = os.path.join(target_directory, file_name)
#                             if file_path.lower().endswith('.pdf'):
#                                 zip_ref.extract(file_name, target_directory)
#                                 doc = fitz.open(file_path)
#                                 page = doc.load_page(0)
#                                 pix = page.get_pixmap()
#                                 img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
#                                 image_directory = os.path.join(settings.MEDIA_ROOT, 'resume_firstpage_images')
#                                 os.makedirs(image_directory, exist_ok=True)
#                                 image_path = os.path.join(image_directory, f"{uniqueID}.jpg")
#                                 img.save(image_path)

#                                 randomstr = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))
#                                 uniqueID = "hires_recruiter_resume_candidate_" + randomstr

#                                 try:
#                                     resumeText,extracted_details = getResumeText(file_path)
#                                     extracted_details_json = json.loads(extracted_details)
                                    
#                                 except Exception as e:
#                                     resumeText = ''
#                                     extracted_details_json = {'TotalExperience':0,'Gender':'No','Skills':'','Name':'No'}
                                
#                                 lowercase_data = convert_keys_to_lowercase(extracted_details_json)
                                
#                                 recZipfile = RecruiterResumeCandidateModel(
#                                     recruiter_resume_candidate_id=uniqueID,
#                                     recruiter_bulk_resume_upload_id=data.recruiter_bulk_resume_upload_id,
#                                     user_id=getData["user_id"],
#                                     job_description_id=getData["job_description_id"],
#                                     recruiter_resume_candidate_firstpage_image=image_path.replace(settings.MEDIA_ROOT, '').replace('\\', '/'),
#                                     recruiter_resume_candidate_file_path=file_path.split("media")[1].replace("\\","/"),
#                                     recruiter_resume_candidate_experience = lowercase_data['totalexperience'],
#                                     recruiter_resume_candidate_gender = lowercase_data['gender'],
#                                     recruiter_resume_candidate_name = lowercase_data['name'],
#                                     recruiter_resume_tech_stack = lowercase_data['skills'],
#                                     recruiter_resume_candidate_extracted_text=resumeText
#                                 )
#                                 recZipfile.save()
#                                 doc.close()
#                             else:
#                                 return Response({"Status": "error", "Code": 401, "Message": "Invalid file format", "Data": []}, status=status.HTTP_401_UNAUTHORIZED)
                    
#                     if JobDescriptionModel.objects.filter(user_id=getData["user_id"], job_description_id=getData["job_description_id"]).exists():
#                         uploadedjd = JobDescriptionModel.objects.get(user_id=getData["user_id"], job_description_id=getData["job_description_id"])
#                         jdpath = os.path.join(settings.MEDIA_ROOT, str(uploadedjd.job_description_upload_file))

#                         jdtext,extracted_details = getResumeText(jdpath)
#                         extracted_details_json = json.loads(extracted_details)

#                         resumeText = RecruiterResumeCandidateModel.objects.filter(user_id=getData["user_id"], recruiter_bulk_resume_upload_id=data.recruiter_bulk_resume_upload_id).values()
#                         extracted_text = {}
#                         resume_list = []
#                         # extracted_details = extracted_details.replace("\\n", "").replace("\\\"", "\"")

#                         # Convert JSON string to Python dictionary
#                         # data = json.loads(extracted_details)
#                         for resume in resumeText:
#                             try:
#                                 json_compliant_string = resume['recruiter_resume_tech_stack'].replace("'", '"')
#                                 tech_list = json.loads(json_compliant_string)
#                             except:
#                                 tech_list = []
#                             person = ""

#                             extracted_text = {
#                                 "recruiter_resume_candidate_file_path": resume['recruiter_resume_candidate_file_path'],
#                                 "recruiter_resume_candidate_name": person,
#                                 "aiCompPercentageScore": float(aiComperision(jdtext, resume['recruiter_resume_candidate_extracted_text'])),
#                                 "recruiter_resume_candidate_experience": resume['recruiter_resume_candidate_experience'],
#                                 "recruiter_resume_candidate_gender": resume['recruiter_resume_candidate_gender'],
#                                 "recruiter_resume_candidate_name": resume['recruiter_resume_candidate_name'],
#                                 "recruiter_resume_tech_stack": tech_list,
#                             }
#                             bulk_resume_instance = RecruiterResumeCandidateModel.objects.get(pk=resume["recruiter_resume_candidate_id"])
#                             bulk_resume_instance.recruiter_resume_candidate_file_path=resume['recruiter_resume_candidate_file_path']
#                             bulk_resume_instance.recruiter_resume_candidate_name=resume['recruiter_resume_candidate_name']
#                             bulk_resume_instance.recruiter_resume_candidate_gender = resume['recruiter_resume_candidate_gender']
#                             bulk_resume_instance.recruiter_resume_candidate_experience =resume['recruiter_resume_candidate_experience']
#                             bulk_resume_instance.recruiter_resume_tech_stack =resume['recruiter_resume_tech_stack']
#                             bulk_resume_instance.recruiter_resume_candidate_nationality = "" 
#                             bulk_resume_instance.recruiter_resume_candidate_url = resume['recruiter_resume_candidate_file_path']
#                             bulk_resume_instance.recruiter_resume_candidate_ai_compare_score=float(aiComperision(jdtext, resume['recruiter_resume_candidate_extracted_text']))
#                             bulk_resume_instance.save()
#                             resume_list.append(extracted_text)
#                         sorted_resumes = sorted(resume_list, key=operator.itemgetter('aiCompPercentageScore'), reverse=True)
#                         return Response({"Status": "success", "Code": 201, "Message": "Bulk Resumes uploaded successfully", "Data": sorted_resumes}, status=status.HTTP_201_CREATED)
#                     else:
#                         return Response({"Status": "error", "Code": 401, "Message": "Job description file is not found", "Data": []}, status=status.HTTP_401_UNAUTHORIZED)
#                 except Exception as e:
#                     return Response({"Status": "error", "Code": 401, "Message": str(e), "Data": []}, status=status.HTTP_401_UNAUTHORIZED)
#             else:
#                 return Response({"Status": "error", "Code": 400, "Message": list(serializer.errors.values())[0][0], "Data": []}, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({"Status": "error", "Code": 401, "Message": str(e), "Data": []}, status=status.HTTP_401_UNAUTHORIZED)# class RecruiterBulkResumeAnalysisAPI(APIView):
#     # authentication_classes=[JWTAuthentication]
#     # permission_classes=[IsAuthenticated]



#@@@@@@@@@@@@@@@@@@@



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
#                     extracted_text = {}
#                     resume_list = []
                    
#                     with zipfile.ZipFile(fullpath, 'r') as zip_ref:
#                         for file_name in zip_ref.namelist():
                            
#                             file_info = zip_ref.getinfo(file_name)
#                             if file_info.is_dir():
#                                 continue
                            
#                             file_path = os.path.join(target_directory, file_name)
#                             if file_path.lower().endswith('.pdf'):
#                                 zip_ref.extract(file_name, target_directory)
#                                 doc = fitz.open(file_path)
#                                 page = doc.load_page(0)
#                                 pix = page.get_pixmap()
#                                 img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
#                                 image_directory = os.path.join(settings.MEDIA_ROOT, 'resume_firstpage_images')
#                                 os.makedirs(image_directory, exist_ok=True)
#                                 image_path = os.path.join(image_directory, f"{uniqueID}.jpg")
#                                 img.save(image_path)

#                                 randomstr = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))
#                                 uniqueID = "hires_recruiter_resume_candidate_" + randomstr
#                                 try:
#                                     if JobDescriptionModel.objects.filter(user_id=getData["user_id"], job_description_id=getData["job_description_id"]).exists():
#                                         uploadedjd = JobDescriptionModel.objects.get(user_id=getData["user_id"], job_description_id=getData["job_description_id"])
#                                         jdpath = os.path.join(settings.MEDIA_ROOT, str(uploadedjd.job_description_upload_file))
#                                         loader = PyMuPDFLoader(jdpath)
#                                         pages = loader.load()

#                                         jobdescription = []
#                                         for page in pages:
#                                             page_content = page.page_content
#                                             jobdescription.append(page_content)


#                                         jobdescriptionText = " ".join([w for w in jobdescription])
#                                 except Exception as e:
#                                     return Response({"Status": "error", "Code": 401, "Message": str(e) + "Job Description", "Data": []}, status=status.HTTP_401_UNAUTHORIZED)


#                                 try:
#                                     resumeText,extracted_details = getResumeText(file_path,jobdescriptionText)

#                                 except Exception as e:
#                                     resumeText = ''
#                                     extracted_details = {'TotalExperience':0,'Gender':'No','Skills':'','Name':'No','ATSScore':0}
#                                 lowercase_data = convert_keys_to_lowercase(extracted_details)

#                                 recZipfile = RecruiterResumeCandidateModel(
#                                     recruiter_resume_candidate_id=uniqueID,
#                                     recruiter_bulk_resume_upload_id=data.recruiter_bulk_resume_upload_id,
#                                     user_id=getData["user_id"],
#                                     job_description_id=getData["job_description_id"],
#                                     recruiter_resume_candidate_firstpage_image=image_path.replace(settings.MEDIA_ROOT, '').replace('\\', '/'),
#                                     recruiter_resume_candidate_file_path=file_path.split("media")[1].replace("\\", "/"),
#                                     recruiter_resume_candidate_experience=lowercase_data.get('totalexperience', 'NO'),
#                                     recruiter_resume_candidate_gender=lowercase_data.get('gender', 'NO'),
#                                     recruiter_resume_candidate_name=lowercase_data.get('name', 'NO'),
#                                     recruiter_resume_tech_stack=lowercase_data.get('skills', 'NO'),
#                                     recruiter_resume_candidate_nationality=lowercase_data.get('nationality', 'NO'),
#                                     recruiter_resume_candidate_ai_compare_score=lowercase_data.get('atsscore', 'NO'),
#                                     recruiter_resume_candidate_extracted_text=resumeText
#                                 )
#                                 recZipfile.save()
#                                 doc.close()

#                                 print(lowercase_data)

#                                 extracted_text = {
#                                     "recruiter_resume_candidate_file_path": file_path.split("media")[1].replace("\\", "/"),
#                                     "recruiter_resume_candidate_name": lowercase_data.get('name', 'NO'),
#                                     "aiCompPercentageScore": lowercase_data.get('atsscore', 'NO'),
#                                     "recruiter_resume_candidate_experience": lowercase_data.get('totalexperience', 'NO'),
#                                     "recruiter_resume_candidate_gender": lowercase_data.get('gender', 'NO'),
#                                     "recruiter_resume_tech_stack": lowercase_data.get('skills', 'NO'),
#                                     "recruiter_resume_candidate_nationality": lowercase_data.get('nationality', 'NO'),
#                                 }
#                                 resume_list.append(extracted_text)

                                
#                                 # lowercase_data = convert_keys_to_lowercase(extracted_details)
#                                 # recZipfile = RecruiterResumeCandidateModel(
#                                 #     recruiter_resume_candidate_id=uniqueID,
#                                 #     recruiter_bulk_resume_upload_id=data.recruiter_bulk_resume_upload_id,
#                                 #     user_id=getData["user_id"],
#                                 #     job_description_id=getData["job_description_id"],
#                                 #     recruiter_resume_candidate_firstpage_image=image_path.replace(settings.MEDIA_ROOT, '').replace('\\', '/'),
#                                 #     recruiter_resume_candidate_file_path=file_path.split("media")[1].replace("\\","/"),
#                                 #     recruiter_resume_candidate_experience = lowercase_data['totalexperience'],
#                                 #     recruiter_resume_candidate_gender = lowercase_data['gender'],
#                                 #     recruiter_resume_candidate_name = lowercase_data['name'],
#                                 #     recruiter_resume_tech_stack = lowercase_data['skills'],
#                                 #     recruiter_resume_candidate_nationality = lowercase_data['nationality'],
#                                 #     recruiter_resume_candidate_ai_compare_score = lowercase_data['atsscore'],
#                                 #     recruiter_resume_candidate_extracted_text=resumeText
#                                 # )
#                                 # recZipfile.save()
#                                 # doc.close()
#                                 # print(lowercase_data)
#                                 # extracted_text = {
#                                 #     "recruiter_resume_candidate_file_path": file_path.split("media")[1].replace("\\","/"),
#                                 #     "recruiter_resume_candidate_name": lowercase_data['name'],
#                                 #     "aiCompPercentageScore": lowercase_data['atsscore'],
#                                 #     "recruiter_resume_candidate_experience": lowercase_data['totalexperience'],
#                                 #     "recruiter_resume_candidate_gender": lowercase_data['gender'],
#                                 #     "recruiter_resume_candidate_name": lowercase_data['name'],
#                                 #     "recruiter_resume_tech_stack": lowercase_data['skills'],
#                                 #     "recruiter_resume_candidate_nationality": lowercase_data['nationality'],
#                                 # }
#                                 # resume_list.append(extracted_text)

#                             else:
#                                 return Response({"Status": "error", "Code": 401, "Message": "Invalid file format", "Data": []}, status=status.HTTP_401_UNAUTHORIZED)
#                         sorted_candidates = sorted(resume_list, key=lambda x: int((str(x['aiCompPercentageScore'])).strip('%')), reverse=True)

#                         return Response({"Status": "success", "Code": 201, "Message": "Bulk Resumes uploaded successfully", "Data": sorted_candidates}, status=status.HTTP_201_CREATED)

#                 except Exception as e:
#                     return Response({"Status": "error", "Code": 401, "Message": str(e), "Data": []}, status=status.HTTP_401_UNAUTHORIZED)
#             else:
#                 return Response({"Status": "error", "Code": 400, "Message": list(serializer.errors.values())[0][0], "Data": []}, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({"Status": "error", "Code": 401, "Message": str(e), "Data": []}, status=status.HTTP_401_UNAUTHORIZED)# class RecruiterBulkResumeAnalysisAPI(APIView):
#     # authentication_classes=[JWTAuthentication]
#     # permission_classes=[IsAuthenticated]
                   
#@@@@@@@@@@@@@@@@@@@

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

            # Generate unique ID for bulk upload
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
            
            if not userRes.pk:
                return Response({"Status": "error", "Code": 400, "Message": list(serializer.errors.values())[0][0], "Data": []}, status=status.HTTP_400_BAD_REQUEST)

            try:
                # Get the uploaded zip file path
                data = RecruiterBulkResumeUploadModel.objects.get(
                    recruiter_bulk_resume_upload_id=resp["recruiter_bulk_resume_upload_id"], 
                    user_id=resp["user_id"]
                )
                original_path = str(data.recruiter_bulk_resume_upload)
                fullpath = os.path.join(settings.MEDIA_ROOT, original_path)

                if not os.path.exists(fullpath):
                    return Response({"Status": "error", "Code": 404, "Message": f"File not found: {fullpath}", "Data": []}, status=status.HTTP_404_NOT_FOUND)

                # Get job description text
                uploadedjd = JobDescriptionModel.objects.get(
                    user_id=getData["user_id"], 
                    job_description_id=getData["job_description_id"]
                )
                jdpath = os.path.join(settings.MEDIA_ROOT, str(uploadedjd.job_description_upload_file))
                loader = PyMuPDFLoader(jdpath)
                pages = loader.load()
                jobdescription = [page.page_content for page in pages]
                jobdescriptionText = " ".join(jobdescription)

                target_directory = os.path.join(settings.MEDIA_ROOT, 'extracted_resumes')
                os.makedirs(target_directory, exist_ok=True)
                resume_list = []
                
                with zipfile.ZipFile(fullpath, 'r') as zip_ref:
                    # Extract all PDF files
                    pdf_files = [
                        file_name for file_name in zip_ref.namelist()
                        if not zip_ref.getinfo(file_name).is_dir() and file_name.lower().endswith('.pdf')
                    ]
                    
                    for file_name in pdf_files:
                        zip_ref.extract(file_name, target_directory)
                    
                    # Prepare arguments for processing
                    process_args = [
                        (file_name, target_directory, resp["recruiter_bulk_resume_upload_id"],
                         jobdescriptionText, getData["user_id"], getData["job_description_id"])
                        for file_name in pdf_files
                    ]
                    
                    # Use ThreadPoolExecutor instead of ProcessPool
                    with ThreadPoolExecutor(max_workers=min(len(process_args), 10)) as executor:
                        results = list(executor.map(process_single_resume, process_args))
                    
                    # Filter out None results and add successful ones to resume_list
                    resume_list = [result for result in results if result is not None]
                
                # Sort candidates by score
                sorted_candidates = sorted(resume_list, 
                                        key=lambda x: int((str(x['aiCompPercentageScore'])).strip('%')), 
                                        reverse=True)
                
                return Response({
                    "Status": "success",
                    "Code": 201,
                    "Message": "Bulk Resumes uploaded successfully",
                    "Data": sorted_candidates
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({"Status": "error", "Code": 401, "Message": str(e), "Data": []}, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            return Response({"Status": "error", "Code": 401, "Message": str(e), "Data": []}, status=status.HTTP_401_UNAUTHORIZED)

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
    
