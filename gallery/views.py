from sys import prefix
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.shortcuts import render,redirect
import boto3
from boto3.session import Session
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import  User
from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .models import fileMeta
import datetime
from django.conf import settings
from gallery.cookiegen import generate_signed_cookies


# Create your views here.

def register(request):
    form=CreateUserForm()
    if request.method== "POST":
        form=CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user=form.cleaned_data.get('username')
            messages.success(request,'Account was created for'+user)
            return redirect('login')

    context={"form":form}
    return render(request,'base/register.html',context)

def login_view(request):
    
    if request.method=='POST':
       username= request.POST.get('username')
       password= request.POST.get('password')
       user= authenticate(request, username=username,password=password)
       print(user)
       if user is not None:
            login(request, user)
            return redirect('base/gallery.html')
       else:
            messages.info(request, 'Username or password incorrect')
    context={}
    return render(request, 'base/login.html',context )

def logout_view(request):
    logout(request)
    print("User session cleared!!!")
    return redirect('login.html')
    
def getDisplayFileName(actualFileName):
    return actualFileName.split("/")[-1]

def getUserFromFileName(filename):
    return filename.split("/")[0].split("_")[0]

def isAdmin(userName):
    return  (userName == "CloudAdmin")


@login_required
def gallerylist(request):
    app_user_name = str(request.user)
    user_obj = User.objects.get(username=app_user_name)
    firstname=user_obj.first_name
    lastname= user_obj.last_name

    print("From gallery: " +app_user_name)
    session=Session(aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    s3=session.resource('s3')
    my_bucket=s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
    tmp_dict={}   
    if (isAdmin(app_user_name)):
        prefix_val = ""
    else:
        prefix_val = app_user_name+"_files/"
    for s3_file in my_bucket.objects.filter(Prefix=prefix_val):
            print(s3_file.key)
            if(s3_file.key[-1]=='/'):
                continue
            if(isAdmin(app_user_name)):
                tmp_dict.update({s3_file.key:s3_file.key})
            else:
                tmp_dict.update({s3_file.key:getDisplayFileName(s3_file.key)})
    context={"msg":tmp_dict,"name":app_user_name,"firstname":firstname,"lastname":lastname}
    user_url = "https://images.cloudgallery.space/{}_files/*".format(app_user_name)
    if (isAdmin(app_user_name)):
        user_url = "https://images.cloudgallery.space/*"
    cookies = generate_signed_cookies(user_url ,settings.CF_KEY_PAIR_ID, str(settings.PRIVATE_KEY_PATH))
    response  = render(request, 'base/gallery.html', context)
    for i,j in cookies.items():
        if (isAdmin(app_user_name)):
            response.set_cookie(i,value=j,domain='.cloudgallery.space',path = "/".format(app_user_name))
        else:
            response.set_cookie(i,value=j,domain='.cloudgallery.space',path = "/{}_files/".format(app_user_name))
        response.cookies[i]['samesite'] = 'None'
        response.cookies[i]['secure'] = True
    return response


@login_required
def viewDetails(request):
    username = str(request.user)
    filename = request.GET.get('file','')
    if(isAdmin(username)):
        fileObject =fileMeta.objects.get(user_name__exact=getUserFromFileName(filename),file_name__exact=getDisplayFileName(filename))
    else:
        fileObject = fileMeta.objects.get(user_name__exact=username, file_name__exact=getDisplayFileName(filename))
    description=fileObject.description
    upload_t = fileObject.created_at
    update_t = fileObject.updated_at
    file_size = fileObject.file_size
    firstname = fileObject.owner_first_name
    lastname = fileObject.owner_last_name
        

    context = {"username":str(username),"filename":getDisplayFileName(filename),"actual_filename":filename,
                "description":description, "upload_t":upload_t, "update_t":update_t,"firstname":firstname,"lastname":lastname,
                "file_size":file_size }
    
    user_url = "https://images.cloudgallery.space/{}_files/*".format(username)
    cookies = generate_signed_cookies(user_url ,settings.CF_KEY_PAIR_ID, str(settings.PRIVATE_KEY_PATH))
    response = render(request,'base/viewdetails.html',context)
    for i,j in cookies.items():
        response.set_cookie(i,value=j,domain='.cloudgallery.space',path = "/{}_files/".format(username))
        response.cookies[i]['samesite'] = 'None'
        response.cookies[i]['secure'] = True
    return response

@login_required
def uploadFile(request):
    username = str(request.user)
    user_obj = User.objects.get(username=username)
    firstname=user_obj.first_name
    lastname= user_obj.last_name
    message=""
    if request.method=='POST':

        prefix = str(request.user)+"_files/"
        file_upload = request.FILES['filename']
        print(file_upload.name)
        if (int(file_upload.size)<=10485760):
            s3_name = prefix+file_upload.name
            s3=boto3.resource('s3',aws_access_key_id=settings.AWS_ACCESS_KEY_ID,aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
            s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME).put_object(Key=s3_name,Body=file_upload)
            record = fileMeta(user_name=str(request.user))
            record.file_name = str(file_upload.name)
            record.owner_first_name=firstname
            record.owner_last_name=lastname
            record.file_size = int(file_upload.size)
            record.description=str(request.POST.get('description'))
            record.created_at = datetime.datetime.now()
            record.updated_at = record.created_at
            record.save()
            message = "Upload Successful!"
        else:
            print("File size too large!")
            message = ""

    return render(request,'base/add.html',context={"message":message})

def delete_object(request):
    if request.method=='GET':
        filename = request.GET.get('file','')
        username = str(request.user)

        s3 = boto3.resource('s3',aws_access_key_id=settings.AWS_ACCESS_KEY_ID,aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        obj = s3.Object(settings.AWS_STORAGE_BUCKET_NAME, filename)
        response = obj.delete()
        print(response)

        if(isAdmin(username)):
            fileObject =fileMeta.objects.get(user_name__exact=getUserFromFileName(filename),file_name__exact=getDisplayFileName(filename))
            fileObject.delete()
        else:
            fileObject = fileMeta.objects.get(user_name__exact=username, file_name__exact=getDisplayFileName(filename))
            fileObject.delete()
    return redirect('gallery')

def edit_object(request):
    username = str(request.user)
    if request.method=='GET':
        filename = request.GET.get('file','')
        context = {"filename":str(filename)}
        return render(request,'base/edit.html',context)
    elif request.method=='POST':
        filename = request.POST.get('file','')
        print("The filename we got in edit section is "+filename)
        if(isAdmin(username)):
            fileObject =fileMeta.objects.get(user_name__exact=getUserFromFileName(filename),file_name__exact=getDisplayFileName(filename))
            fileObject.description=str(request.POST.get('description'))
            fileObject.updated_at=datetime.datetime.now()
            fileObject.save()
        else:
            fileObject = fileMeta.objects.get(user_name__exact=username, file_name__exact=getDisplayFileName(filename))
            fileObject.description=str(request.POST.get('description'))
            fileObject.updated_at=datetime.datetime.now()
            fileObject.save()
        return redirect('gallery')
        




    
