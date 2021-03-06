import urllib.parse

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import action, api_view, permission_classes, parser_classes
from rest_framework import permissions, viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, FormParser
from rest_framework_jwt.settings import api_settings

from gala.pharmacy.models import Staff, Pharmacy, Drug, Disease
from gala.pharmacy.serializers import PharmacySerializer, StaffSerializer
from . import serializers as sz

# @api_view(["post"])
# @permission_classes([permissions.AllowAny])
# @parser_classes([FormParser, JSONParser])
@csrf_exempt
def ussd_callback(request):
    body=request.body.decode("utf-8")
    print(body)
    body=urllib.parse.unquote(body)
    body=body.split("&")
    phoneNumber=None
    serviceCode=None
    text=None
    resp=None
    print(body)
    for key in body:
        if "phoneNumber" in key:
            phoneNumber = key.replace("phoneNumber=", "")
            continue
        if "serviceCode" in key:
            serviceCode=key.replace("serviceCode=", "")
            continue
        if "text" in key:
            text=key.replace("text=", "").replace(" ", "")
            continue
        if "sessionId" in key:
            sessionId=key.replace("sessionId=", "")
            continue
        if "networkCode" in key:
            networkCode=key.replace("networkCode=", "")
            continue
    resp = f"END Invalid option, please try again"
    if text == "":
        resp = "CON What would you want to check \n1. Diseases \n2. Covid19"
    else:
        if text == "1":
                resp = "CON Get information on\n1. Diabetes\n2. Hypertesion\n3. Kidney issues\n4.Heart Issues"
        elif text == "2":
            resp = "END Covid19 is a respiratory disease that has claimed 209,234 lives and 3,109,103 cases"
        elif text == "1*1":
            resp = "CON Diabetes\n1. Nutrition/Diet\n2.Food near you\3. Pharmacies"
        elif text == "1*2":
            resp = "CON Hypertesion\n1. Nutrition/Diet\n2.Food near you\3. Pharmacies"
        elif text == "1*3":
            resp = "CON Kidney issues\n1. Nutrition/Diet\n2.Food near you\3. Pharmacies"
        elif text == "1*4":
            resp = "CON Heart Issues\n1. Nutrition/Diet\n2.Food near you\3. Pharmacies"
        elif text in ["1*5*1", "1*4*1", "1*3*1", "1*2*1", "1*1*1", "1*5*2", "1*4*2", "1*3*2", "1*2*2", "1*1*2", "1*2"]:
            resp = "END The information will be sent to you shortly"
    print(resp)
    return HttpResponse(resp)


class UserAuthViewset(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()
    serializer_class = sz.UserSerializer

    @action(methods=['post'], detail=False, permission_classes=[permissions.AllowAny])
    def login(self, request) -> '[{Response Object}]':
        serializer = sz.LoginSerializer(
            data=request.data, context={'request': request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        username = serializer.data['username']
        password = serializer.data['password']
        login_as = serializer.data["login_as"]
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({
                "error": "Please check your username or password"
            }, status=status.HTTP_404_NOT_FOUND)
        obj = sz.UserSerializer(user).data
        obj["login_as"] = login_as
        obj["staff"] = {}
        if login_as!="user":
            staff = get_object_or_404(Staff.objects.all(), user=user)
            obj["staff"] = sz.StaffSerializer(staff).data
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        obj['token'] = jwt_encode_handler(payload)
        return Response(obj)

class StaffViewset(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer


class PharmacyViewset(viewsets.ModelViewSet):
    queryset = Pharmacy.objects.all()
    serializer_class = PharmacySerializer

class DrugViewset(viewsets.ModelViewSet):
    queryset = Drug.objects.all()
    serializer_class = sz.DrugSerializer

class DiseaseViewset(viewsets.ModelViewSet):
    queryset = Disease.objects.all()
    serializer_class = sz.DiseaseSerializer
