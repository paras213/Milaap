import os
import sqlite3
from django.template.loader import render_to_string
import cv2
from django.contrib.auth.models import User
import numpy as np
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from PIL import Image
from django.core.mail import send_mail
from django.template import Template,Context
from .models import Member
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
import requests
from django.contrib.auth import authenticate,login,logout
from django.urls import reverse
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def train():
  recognizer=cv2.face.LBPHFaceRecognizer_create();
  path='DataSet'
  def getImageWithID(path):
    imagePaths=[os.path.join(path,f) for f in os.listdir(path)]
    faces=[]
    IDs=[]
    for imagePath in imagePaths:
      faceImg=Image.open(imagePath).convert('L')
      facenp=np.array(faceImg,'uint8')
      ID=int(os.path.split(imagePath)[-1].split('.')[1])
      faces.append(facenp)
      IDs.append(ID)
      cv2.waitKey(10)
    return IDs,faces
  Ids,faces=getImageWithID(path)
  recognizer.train(faces,np.array(Ids))
  try:
    os.mkdir(settings.BASE_DIR+'/recognizer')
  except:
    None
  recognizer.write('recognizer/trainningData.yml')
  return None

def register(request):
  if request.method=='POST':
    username=request.POST['username']
    password=request.POST['password']
    cpassword=request.POST['password1']
    mobilenumber=request.POST['number']
    email=request.POST['email']
    if password==cpassword:
      user=User.objects.create_user(username,email,password)
      user.first_name=request.POST['firstname'] 
      user.last_name=request.POST['lastname']
      user.save()
      messages.success(request,'%s has been Registered Successfully'%user.username)
      return redirect('/child/login')
    else:
      messages.error(request,"Your password didn't match!")
      return redirect('/register')
  return render(request,'child/register.html')

def login1(request):
  if request.method=='POST':
    lusername=request.POST['username']
    lpassword=request.POST['password']
    user=authenticate(username=lusername,password=lpassword)
    if user is not None:
      login(request,user)
      messages.success(request,"%s has been logged Successfully"%user.username)
      return redirect('/child/dashboard')
    else:
      messages.error(request,'Invalid Username or Password')
      return redirect('/child/login')
  return render(request,'child/login.html')

@login_required
def logout1(request):
  logout(request)
  messages.success(request,'You have been logout Successfully')
  return redirect('/child')

@login_required
def congrats(request):
  faceDetect=cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
  cam=cv2.VideoCapture(0)
  mem=list(Member.objects.all())[-1]
  id=mem.id
  sample=0
  try:
    os.mkdir(settings.BASE_DIR+"/DataSet")
  except:
    None
  while(True):
    ret,img=cam.read()
    gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    faces=faceDetect.detectMultiScale(gray,1.3,5)
    for(x,y,w,h) in faces:
        sample=sample+1
        cv2.imwrite('DataSet/User.'+str(id)+"."+str(sample)+'.jpg',gray[y:y+h,x:x+w])
        cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
        cv2.waitKey(100)
    if(sample>20):
        break
  cam.release()
  cv2.destroyAllWindows()
  train()
  x=Member.objects.filter(id=id).update(trained=True)
  return render(request,'child/congrats.html')

@login_required
def laststep(request):
  return render(request,'child/laststep.html')

def home(request):
  return render(request,'child/index.html')

def success(request): 
    return HttpResponse('successfuly uploaded')

@login_required
def addmember(request):
  if request.method=="POST":
    name=request.POST['name']
    number=request.POST['number']
    gender=request.POST['gender']
    address=request.POST['address']
    code=request.POST['pincode']
    img=request.FILES['image']
    mem=Member()
    mem.user=request.user
    mem.name=name
    mem.mobilenumber=number
    mem.gender=gender
    mem.address=address
    mem.zip1=code
    mem.image=img
    mem.save()
    return redirect('/child/laststep')
  return render(request,'child/addmember.html')

@login_required
def dashboard(request):
  return render(request,'child/dashboard.html')

@login_required
def allmembers(request):
  members=Member.objects.filter(user=request.user)
  return render(request,'child/allmembers.html',{'members':members,'len':len(members)})

@login_required
def searchmember(request):
  return render(request,'child/searchmember.html')

def display_ip():
    """  Function To Print GeoIP Latitude & Longitude """
    ip_request = requests.get('https://get.geojs.io/v1/ip.json')
    my_ip = ip_request.json()['ip']
    geo_request = requests.get('https://get.geojs.io/v1/ip/geo/' +my_ip + '.json')
    geo_data = geo_request.json()
    a=[geo_data['region'],geo_data['latitude'],geo_data['longitude']]
    return a

@login_required
def searchresult(request):
  faceDetect=cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
  def getans(Id):
    profile=None
    try:
      profile=Member.objects.get(id=Id)
    except:
      None
    return profile
  cam=cv2.VideoCapture(0)
  rec=cv2.face.LBPHFaceRecognizer_create();
  try:
    rec.read('recognizer\\trainningData.yml')
  except:
    return HttpResponse("There are no Members in our database to search with")
  id=0
  flag=0
  font=cv2.FONT_HERSHEY_COMPLEX_SMALL
  while(True):
    ret,img=cam.read()
    gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    faces=faceDetect.detectMultiScale(gray,1.3,5)
    for(x,y,w,h) in faces:
        cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
        id,conf=rec.predict(gray[y:y+h,x:x+w])
        profile = getans(id)
        if profile!=None:
          cv2.destroyAllWindows()
          flag=1
          break
        #cv2.putText(img,str(id),(x,y+h), font, 4,(255,255,255),2,cv2.LINE_AA)
    cv2.imshow("Face",img);
    if(cv2.waitKey(1)==ord('q') or flag==1):
        break;
  cam.release()
  cv2.destroyAllWindows()
  current_site=get_current_site(request)
  to_email = profile.user.email
  Member.objects.filter(id=profile.id).update(missing = {'user':request.user.id,'Given':False})
  subject='Verify You Family Member Absence'
  r=display_ip()
  html_message = render_to_string('child/acc_active_email.html',context={'user':request.user,'profile':profile,'uid':urlsafe_base64_encode(force_bytes(id)),'url':"http://%s/child/allowuser/%s"%(current_site.domain,profile.id),'region':r[0],'long':r[1],'lat':r[2]})
  plain_message = strip_tags(html_message)
  x = send_mail(subject,plain_message,settings.EMAIL_HOST_USER,[to_email], html_message=html_message,fail_silently = True)
  if x==1:
    messages.success(request,f'We have sent the confirmation mail')
  return redirect('/child')
  #return render(request,'child/searchresult.html',{'profile':profile})'token':account_activation_token.make_token(request.user)


@login_required
def deletemember(request,memberid):
  s=Member.objects.get(id=memberid)
  t=s.name
  image=s.image
  s.delete()
  for sample in range(1,22):
    try:
      os.remove('DataSet/User.'+str(memberid)+"."+str(sample)+'.jpg')
    except:
      None
  os.remove('child/media/'+str(image))
  if len(Member.objects.filter(trained=True))!=0:
    train()
  else:
    try:
      os.remove('recognizer/trainningData.yml')
    except:
      None
  msg="%s has been removed successfully."%t;
  messages.success(request,'%s has been Removed Successfully'%t)
  return render(request,'child/allmembers.html')


def allowuser(request,id):
  x = Member.objects.get(id=id).missing
  x['Given'] = True
  print(x)
  Member.objects.filter(id=id).update(missing=x)
  return HttpResponse("We have give him access, we will inform him to connect you, we wish your member will be back to you safely as soon as possible.")

def alloweduser(request):
  profiles = Member.objects.all()
  accessed = []
  for pro in profiles:
    if pro.missing['user'] == request.user.id and pro.missing['Given']:
      accessed.append(pro)
  return render(request,'child/allowedusers.html',{'accessed':accessed})
#http://{{domain}}{% url 'activate' uidb64=uid token=token year=user.id %}
