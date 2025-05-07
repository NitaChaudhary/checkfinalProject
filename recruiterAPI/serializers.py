from rest_framework import serializers
from .models import *
from userloginAPI.models import *
from databaseAPI.models import *

import re
import os
link_regex_pattern = r'^https?://[^\s]+$'


class JobDescriptionSerializer(serializers.ModelSerializer):
    

    user_id = serializers.PrimaryKeyRelatedField(queryset=NewUser.objects.all(), source='user')

    class Meta:
        model = JobDescriptionModel
        fields = ["job_description_upload_file","user_id","job_level_name","job_tilte", "job_description_action"]

    def validate(self, data):

        job_tilte = data["job_tilte"]
        jd_file = data["job_description_upload_file"]


        if job_tilte == None or job_tilte =="": 
            raise serializers.ValidationError({'errorMsg' : 'Job title is required'})

        # if JobDescriptionModel.objects.filter(job_tilte = job_tilte).exists():
        #     raise serializers.ValidationError({'errorMsg' : 'Name of the Job title is already exist'})
        
        # if not jd_file:
        #     raise serializers.ValidationError({"errorMsg": 'File is required'})
        
        # if not jd_file.name.lower().endswith('.pdf') and not jd_file.name.lower().endswith('.doc') and not jd_file.name.lower().endswith('.docx'):
            
        #     raise serializers.ValidationError({"errorMsg": "unsupported file extension. Only PDF and DOC files are allowed."})


        return data

class RecruiterBulkResumeUploadSerializer(serializers.ModelSerializer):
    
    user_id = serializers.PrimaryKeyRelatedField(queryset=NewUser.objects.all(), source='user')

    class Meta:
        model = RecruiterBulkResumeUploadModel
        fields = ['recruiter_bulk_resume_upload_id', 'user_id', 'recruiter_bulk_resume_upload', 'recruiter_bulk_resume_upload_registration_date']

    def validate(self, data):
        resume_file = data["recruiter_bulk_resume_upload"]

        if not resume_file:
            raise serializers.ValidationError({"errorMsg": 'File is required'})
        
        if not resume_file.name.lower().endswith('.zip'):
            raise serializers.ValidationError({"errorMsg": "Unsupported file extension. Only ZIP files are allowed."})

        return data
    
# class RecruiterExtractedZipFileSerializer(serializers.ModelSerializer):
#     recruiter_bulk_resume_upload_id = serializers.PrimaryKeyRelatedField(queryset=RecruiterBulkResumeUploadModel.objects.all(), source='recruiter_bulk_resume_upload')
#     recruiter_user_id = serializers.PrimaryKeyRelatedField(queryset=NewUser.objects.all(), source='recruiter_user')

#     class Meta:
#         model = RecruiterResumeCandidateModel
#         fields = [ 'recruiter_bulk_resume_upload_id','recruiter_user_id', 'resume_file_path', 'recruiter_resume_extracted_file_registration_date']

#     def validate(self, data):
#         # resume_file_path = data.get("resume_file_path", None)

#         # if not resume_file_path:
#         #     raise serializers.ValidationError({"errorMsg": 'File is required'})
        
#         # if not resume_file_path.name.lower().endswith('.pdf'):
#         #     raise serializers.ValidationError({"errorMsg": "Unsupported file extension. Only Pdf files are allowed."})

#         return data