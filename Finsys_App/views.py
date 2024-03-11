#Finsys Final
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render,redirect
from django.contrib.auth.models import User, auth
from . models import *
from django.contrib import messages
from django.utils.crypto import get_random_string
from datetime import date
from datetime import timedelta
import random
import string
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.core.mail import send_mail, EmailMessage
from io import BytesIO
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import datetime
from datetime import date,datetime
from django.db.models import Sum,F,IntegerField,Q
from django.db.models.functions import ExtractMonth,ExtractYear,Cast
from django.core.mail import EmailMessage
from django.urls import reverse
from django.http import HttpResponse
from django.db import IntegrityError
from django.shortcuts import get_object_or_404

def Fin_index(request):
    return render(request,'Fin_index.html')


def Fin_login(request):
    if request.method == 'POST':
        user_name = request.POST['username']
        passw = request.POST['password']
    
        log_user = auth.authenticate(username = user_name,
                                  password = passw)
    
        if log_user is not None:
            auth.login(request, log_user)

        # ---super admin---

            if request.user.is_staff==1:
                return redirect('Fin_Adminhome') 
            
        # -------distributor ------    
            
        if Fin_Login_Details.objects.filter(User_name = user_name,password = passw).exists():
            data =  Fin_Login_Details.objects.get(User_name = user_name,password = passw)  
            if data.User_Type == 'Distributor':
                did = Fin_Distributors_Details.objects.get(Login_Id=data.id) 
                if did.Admin_approval_status == 'Accept':
                    request.session["s_id"]=data.id
                    if 's_id' in request.session:
                        if request.session.has_key('s_id'):
                            s_id = request.session['s_id']
                            print(s_id)
                            
                            current_day=date.today() 
                            if current_day == did.End_date:
                                print("wrong")
                                   
                                return redirect('Fin_Wrong')
                            else:
                                return redirect('Fin_DHome')
                            
                    else:
                        return redirect('/')
                else:
                    messages.info(request, 'Approval is Pending..')
                    return redirect('Fin_DistributorReg')
                      
            if data.User_Type == 'Company':
                cid = Fin_Company_Details.objects.get(Login_Id=data.id) 
                if cid.Admin_approval_status == 'Accept' or cid.Distributor_approval_status == 'Accept':
                    request.session["s_id"]=data.id
                    if 's_id' in request.session:
                        if request.session.has_key('s_id'):
                            s_id = request.session['s_id']
                            print(s_id)
                            com = Fin_Company_Details.objects.get(Login_Id = s_id)
                            

                            current_day=date.today() 
                            if current_day >= com.End_date:
                                print("wrong")
                                   
                                return redirect('Fin_Wrong')
                            else:
                                return redirect('Fin_Com_Home')
                    else:
                        return redirect('/')
                else:
                    messages.info(request, 'Approval is Pending..')
                    return redirect('Fin_CompanyReg')  
            if data.User_Type == 'Staff': 
                cid = Fin_Staff_Details.objects.get(Login_Id=data.id)   
                if cid.Company_approval_status == 'Accept':
                    request.session["s_id"]=data.id
                    if 's_id' in request.session:
                        if request.session.has_key('s_id'):
                            s_id = request.session['s_id']
                            print(s_id)
                            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
                            

                            current_day=date.today() 
                            if current_day >= com.company_id.End_date:
                                print("wrong")
                                messages.info(request, 'Your Account Temporary blocked')
                                return redirect('Fin_StaffReg') 
                            else:
                                return redirect('Fin_Com_Home')
                    else:
                        return redirect('/')
                else:
                    messages.info(request, 'Approval is Pending..')
                    return redirect('Fin_StaffReg') 
        else:
            messages.info(request, 'Invalid Username or Password. Try Again.')
            return redirect('Fin_CompanyReg')  
    else:  
        return redirect('Fin_CompanyReg')   
  

def logout(request):
    request.session["uid"] = ""
    auth.logout(request)
    return redirect('Fin_index')  

                    


 
    
# ---------------------------start admin ------------------------------------   


def Fin_Adminhome(request):
    noti = Fin_ANotification.objects.filter(status = 'New')
    n = len(noti)
    context = {
        'noti':noti,
        'n':n
    }
    return render(request,'Admin/Fin_Adminhome.html',context)

def Fin_PaymentTerm(request):
    terms = Fin_Payment_Terms.objects.all()
    noti = Fin_ANotification.objects.filter(status = 'New')
    n = len(noti)
    return render(request,'Admin/Fin_Payment_Terms.html',{'terms':terms,'noti':noti,'n':n})

def Fin_add_payment_terms(request):
  if request.method == 'POST':
    num=int(request.POST['num'])
    select=request.POST['select']
    if select == 'Years':
      days=int(num)*365
      pt = Fin_Payment_Terms(payment_terms_number = num,payment_terms_value = select,days = days)
      pt.save()
      messages.success(request, 'Payment term is added')
      return redirect('Fin_PaymentTerm')

    else:  
      days=int(num*30)
      pt = Fin_Payment_Terms(payment_terms_number = num,payment_terms_value = select,days = days)
      pt.save()
      messages.success(request, 'Payment term is added')
      return redirect('Fin_PaymentTerm')


  return redirect('Fin_PaymentTerm')

def Fin_ADistributor(request):
    noti = Fin_ANotification.objects.filter(status = 'New')
    n = len(noti)
    return render(request,"Admin/Fin_ADistributor.html",{'noti':noti,'n':n})

def Fin_Distributor_Request(request):
   data = Fin_Distributors_Details.objects.filter(Admin_approval_status = "NULL")
   print(data)
   noti = Fin_ANotification.objects.filter(status = 'New')
   n = len(noti)
   return render(request,"Admin/Fin_Distributor_Request.html",{'data':data,'noti':noti,'n':n})

def Fin_Distributor_Req_overview(request,id):
    data = Fin_Distributors_Details.objects.get(id=id)
    noti = Fin_ANotification.objects.filter(status = 'New')
    n = len(noti)
    return render(request,"Admin/Fin_Distributor_Req_overview.html",{'data':data,'noti':noti,'n':n})

def Fin_DReq_Accept(request,id):
   data = Fin_Distributors_Details.objects.get(id=id)
   data.Admin_approval_status = 'Accept'
   data.save()
   return redirect('Fin_Distributor_Request')

def Fin_DReq_Reject(request,id):
   data = Fin_Distributors_Details.objects.get(id=id)
   data.Login_Id.delete()
   data.delete()
   return redirect('Fin_Distributor_Request')

def Fin_Distributor_delete(request,id):
   data = Fin_Distributors_Details.objects.get(id=id)
   data.Login_Id.delete()
   data.delete()
   return redirect('Fin_All_distributors')

def Fin_All_distributors(request):
   data = Fin_Distributors_Details.objects.filter(Admin_approval_status = "Accept")
   print(data)
   noti = Fin_ANotification.objects.filter(status = 'New')
   n = len(noti)
   return render(request,"Admin/Fin_All_distributors.html",{'data':data,'noti':noti,'n':n})

def Fin_All_Distributor_Overview(request,id):
   data = Fin_Distributors_Details.objects.get(id=id)
   noti = Fin_ANotification.objects.filter(status = 'New')
   n = len(noti)
   return render(request,"Admin/Fin_All_Distributor_Overview.html",{'data':data,'noti':noti,'n':n})  

def Fin_AClients(request):
    noti = Fin_ANotification.objects.filter(status = 'New')
    n = len(noti)
    return render(request,"Admin/Fin_AClients.html",{'noti':noti,'n':n})


def Fin_AClients_Request(request):
    data = Fin_Company_Details.objects.filter(Registration_Type = "self", Admin_approval_status = "NULL")
    print(data)
    noti = Fin_ANotification.objects.filter(status = 'New')
    n = len(noti)
    return render(request,"Admin/Fin_AClients_Request.html",{'data':data,'noti':noti,'n':n})

def Fin_AClients_Request_OverView(request,id):
    data = Fin_Company_Details.objects.get(id=id)
    allmodules = Fin_Modules_List.objects.get(company_id = id,status = "New")
    noti = Fin_ANotification.objects.filter(status = 'New')
    n = len(noti)
    return render(request,'Admin/Fin_AClients_Request_OverView.html',{'data':data,'allmodules':allmodules,'noti':noti,'n':n})

def Fin_Client_Req_Accept(request,id):
   data = Fin_Company_Details.objects.get(id=id)
   data.Admin_approval_status = 'Accept'
   data.save()
   return redirect('Fin_AClients_Request')

def Fin_Client_Req_Reject(request,id):
   data = Fin_Company_Details.objects.get(id=id)
   data.Login_Id.delete()
   data.delete()
   return redirect('Fin_AClients_Request')

def Fin_Client_delete(request,id):
   data = Fin_Company_Details.objects.get(id=id)
   data.Login_Id.delete()
   data.delete()
   return redirect('Fin_Admin_clients')

def Fin_Admin_clients(request):
   data = Fin_Company_Details.objects.filter(Admin_approval_status = "Accept")
   print(data)
   noti = Fin_ANotification.objects.filter(status = 'New')
   n = len(noti)
   return render(request,"Admin/Fin_Admin_clients.html",{'data':data,'noti':noti,'n':n})

def Fin_Admin_clients_overview(request,id):
   data = Fin_Company_Details.objects.get(id=id)
   allmodules = Fin_Modules_List.objects.get(company_id = id,status = "New")
   noti = Fin_ANotification.objects.filter(status = 'New')
   n = len(noti)
   return render(request,"Admin/Fin_Admin_clients_overview.html",{'data':data,'allmodules':allmodules,'noti':noti,'n':n})   

def Fin_Anotification(request):
    noti = Fin_ANotification.objects.filter(status = 'New')
    n = len(noti)
    context = {
        'noti':noti,
        'n':n
    }
    return render(request,'Admin/Fin_Anotification.html',context) 

def  Fin_Anoti_Overview(request,id):
    noti = Fin_ANotification.objects.filter(status = 'New')
    n = len(noti)

    

    data = Fin_ANotification.objects.get(id=id)

    if data.Login_Id.User_Type == "Company":

        if data.Modules_List :
            allmodules = Fin_Modules_List.objects.get(Login_Id = data.Login_Id,status = "New")
            allmodules1 = Fin_Modules_List.objects.get(Login_Id = data.Login_Id,status = "pending")

        
            context = {
                'noti':noti,
                'n':n,
                'data':data,
                'allmodules':allmodules,
                'allmodules1':allmodules1,
            }
            return render(request,'Admin/Fin_Anoti_Overview.html',context)
        else:
            data1 = Fin_Company_Details.objects.get(Login_Id = data.Login_Id)
            context = {
                'noti':noti,
                'n':n,
                'data1':data1,
                'data':data,
                
            }
            return render(request,'Admin/Fin_Anoti_Overview.html',context)
    else:
        data1 = Fin_Distributors_Details.objects.get(Login_Id = data.Login_Id)
        context = {
                'noti':noti,
                'n':n,
                'data1':data1,
                'data':data,
                
            }

        return render(request,'Admin/Fin_Anoti_Overview.html',context)


def  Fin_Module_Updation_Accept(request,id):
    data = Fin_ANotification.objects.get(id=id)
    allmodules = Fin_Modules_List.objects.get(Login_Id = data.Login_Id,status = "New")
    allmodules.delete()

    allmodules1 = Fin_Modules_List.objects.get(Login_Id = data.Login_Id,status = "pending")
    allmodules1.status = "New"
    allmodules1.save()

    data.status = 'old'
    data.save()

    return redirect('Fin_Anotification')

def  Fin_Module_Updation_Reject(request,id):
    data = Fin_ANotification.objects.get(id=id)
    allmodules = Fin_Modules_List.objects.get(Login_Id = data.Login_Id,status = "pending")
    allmodules.delete()

    data.delete()

    return redirect('Fin_Anotification')

def  Fin_payment_terms_Updation_Accept(request,id):
    data = Fin_ANotification.objects.get(id=id)
    com = Fin_Company_Details.objects.get(Login_Id = data.Login_Id)
    terms=Fin_Payment_Terms.objects.get(id=data.PaymentTerms_updation.Payment_Term.id)
    
    
    com.Start_Date =date.today()
    days=int(terms.days)

    end= date.today() + timedelta(days=days)
    com.End_date = end
    com.Payment_Term = terms
    com.save()

    data.status = 'old'
    data.save()

    upt = Fin_Payment_Terms_updation.objects.get(id = data.PaymentTerms_updation.id)
    upt.status = 'old'
    upt.save()

    cnoti = Fin_CNotification.objects.filter(Company_id = com)
    for c in cnoti:
        c.status = 'old'
        c.save()    

    return redirect('Fin_Anotification')

def  Fin_payment_terms_Updation_Reject(request,id):
    data = Fin_ANotification.objects.get(id=id)

    upt = Fin_Payment_Terms_updation.objects.get(id = data.PaymentTerms_updation.id)

    upt.delete()
    data.delete()

    return redirect('Fin_Anotification')


def  Fin_ADpayment_terms_Updation_Accept(request,id):
    data = Fin_ANotification.objects.get(id=id)
    com = Fin_Distributors_Details.objects.get(Login_Id = data.Login_Id)
    terms=Fin_Payment_Terms.objects.get(id=data.PaymentTerms_updation.Payment_Term.id)
    
    
    com.Start_Date =date.today()
    days=int(terms.days)

    end= date.today() + timedelta(days=days)
    com.End_date = end
    com.Payment_Term = terms
    com.save()

    data.status = 'old'
    data.save()

    upt = Fin_Payment_Terms_updation.objects.get(id = data.PaymentTerms_updation.id)
    upt.status = 'old'
    upt.save()

    cnoti = Fin_DNotification.objects.filter(Distributor_id = com)
    for c in cnoti:
        c.status = 'old'
        c.save()    

    return redirect('Fin_Anotification')

def  Fin_ADpayment_terms_Updation_Reject(request,id):
    data = Fin_ANotification.objects.get(id=id)

    upt = Fin_Payment_Terms_updation.objects.get(id = data.PaymentTerms_updation.id)

    upt.delete()
    data.delete()

    return redirect('Fin_Anotification')

 
# ---------------------------end admin ------------------------------------ 






# ---------------------------start distributor------------------------------------   

 
def Fin_DHome(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Distributors_Details.objects.get(Login_Id = s_id)
        current_day=date.today() 
        diff = (data.End_date - current_day).days
        num = 20
        print(diff)
        if diff <= 20:
            n=Fin_DNotification(Login_Id = data.Login_Id,Distributor_id = data,Title = "Payment Terms Alert",Discription = "Your Payment Terms End Soon")
            n.save() 

        noti = Fin_DNotification.objects.filter(status = 'New',Distributor_id = data.id)
        n = len(noti)
        context = {
            'noti':noti,
            'n':n,
            'data':data
        }
        return render(request,'Distributor/Fin_DHome.html',context)
    else:
       return redirect('/')   

def Fin_DistributorReg(request):
    terms = Fin_Payment_Terms.objects.all()
    context = {
       'terms':terms
    }
    return render(request,'Distributor/Fin_DistributorReg.html',context)

def Fin_DReg_Action(request):
    if request.method == 'POST':
      first_name = request.POST['first_name']
      last_name = request.POST['last_name']
      email = request.POST['email']
      user_name = request.POST['username']
      password = request.POST['dpassword']

      if Fin_Login_Details.objects.filter(User_name=user_name).exists():
        messages.info(request, 'This username already exists. Sign up again')
        return redirect('Fin_DistributorReg')
      
      elif Fin_Distributors_Details.objects.filter(Email=email).exists():
        messages.info(request, 'This email already exists. Sign up again')
        return redirect('Fin_DistributorReg')
      else:
        dlog = Fin_Login_Details(First_name = first_name,Last_name = last_name,
                                User_name = user_name,password = password,
                                User_Type = 'Distributor')
        dlog.save()

        code_length = 8  
        characters = string.ascii_letters + string.digits  # Letters and numbers

        while True:
            unique_code = ''.join(random.choice(characters) for _ in range(code_length))
        
            # Check if the code already exists in the table
            if not Fin_Company_Details.objects.filter(Company_Code = unique_code).exists():
              break 

        ddata = Fin_Distributors_Details(Email = email,Login_Id = dlog,Distributor_Code = unique_code,Admin_approval_status = "NULL")
        ddata.save()
        return redirect('Fin_DReg2',dlog.id)    

        # code=get_random_string(length=6)
        # if Fin_Distributors_Details.objects.filter( Distributor_Code = code).exists():
        #     code2=get_random_string(length=6)

        #     ddata = Fin_Distributors_Details(Email = email,Login_Id = dlog,Distributor_Code = code2,Admin_approval_status = "NULL")
        #     ddata.save()
        #     return redirect('Fin_DReg2',dlog.id)
        # else:
        #     ddata = Fin_Distributors_Details(Email = email,Login_Id = dlog,Distributor_Code = code,Admin_approval_status = "NULL")
        #     ddata.save()
        #     return redirect('Fin_DReg2',dlog.id)
 
    return redirect('Fin_DistributorReg')

def Fin_DReg2(request,id):
    dlog = Fin_Login_Details.objects.get(id = id)
    ddata = Fin_Distributors_Details.objects.get(Login_Id = id)
    terms = Fin_Payment_Terms.objects.all()
    context = {
       'terms':terms,
       'dlog':dlog,
       'ddata':ddata
    }
    return render(request,'Distributor/Fin_DReg2.html',context)

def Fin_DReg2_Action2(request,id):
   if request.method == 'POST':
      ddata = Fin_Distributors_Details.objects.get(Login_Id = id)

      ddata.Contact = request.POST['phone']
      ddata.Image=request.FILES.get('img')

      payment_term = request.POST['payment_term']
      terms=Fin_Payment_Terms.objects.get(id=payment_term)
    
      start_date=date.today()
      days=int(terms.days)

      end= date.today() + timedelta(days=days)
      End_date=end

      ddata.Payment_Term  = terms
      ddata.Start_Date = start_date
      ddata.End_date = End_date

      ddata.save()
      return redirect('Fin_DistributorReg')
   return render('Fin_DReg2',id)  

def Fin_DClient_req(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Distributors_Details.objects.get(Login_Id = s_id)
        data1 = Fin_Company_Details.objects.filter(Registration_Type = "distributor",Distributor_approval_status = "NULL",Distributor_id = data.id)
        noti = Fin_DNotification.objects.filter(status = 'New',Distributor_id = data.id)
        n = len(noti)
        return render(request,'Distributor/Fin_DClient_req.html',{'data':data,'data1':data1,'noti':noti,'n':n})
    else:
       return redirect('/') 
    
def Fin_DClient_req_overview(request,id):
    data = Fin_Company_Details.objects.get(id=id)
    allmodules = Fin_Modules_List.objects.get(company_id = id,status = "New")
    noti = Fin_DNotification.objects.filter(status = 'New',Distributor_id = data.id)
    n = len(noti)
    return render(request,'Distributor/Fin_DClient_req_overview.html',{'data':data,'allmodules':allmodules,'noti':noti,'n':n})    
    
def Fin_DClient_Req_Accept(request,id):
   data = Fin_Company_Details.objects.get(id=id)
   data.Distributor_approval_status = 'Accept'
   data.save()
   return redirect('Fin_DClient_req')

def Fin_DClient_Req_Reject(request,id):
   data = Fin_Company_Details.objects.get(id=id)
   data.Login_Id.delete()
   data.delete()
   return redirect('Fin_DClient_req')   

def Fin_DClients(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Distributors_Details.objects.get(Login_Id = s_id)
        data1 = Fin_Company_Details.objects.filter(Registration_Type = "distributor",Distributor_approval_status = "Accept",Distributor_id = data.id)
        noti = Fin_DNotification.objects.filter(status = 'New',Distributor_id = data.id)
        n = len(noti)
        return render(request,'Distributor/Fin_DClients.html',{'data':data,'data1':data1,'noti':noti,'n':n})
    else:
       return redirect('/')  
   
def Fin_DClients_overview(request,id):
    data = Fin_Company_Details.objects.get(id=id)
    allmodules = Fin_Modules_List.objects.get(company_id = id,status = "New")
    noti = Fin_DNotification.objects.filter(status = 'New',Distributor_id = data.id)
    n = len(noti)
    return render(request,'Distributor/Fin_DClients_overview.html',{'data':data,'allmodules':allmodules,'noti':noti,'n':n})

def Fin_DClient_remove(request,id):
   data = Fin_Company_Details.objects.get(id=id)
   data.Login_Id.delete()
   data.delete()
   return redirect('Fin_DClients') 
    
def Fin_DProfile(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Distributors_Details.objects.get(Login_Id = s_id)
        data1 = Fin_Company_Details.objects.filter(Registration_Type = "distributor",Distributor_approval_status = "Accept",Distributor_id = data.id)
        terms = Fin_Payment_Terms.objects.all()
        noti = Fin_DNotification.objects.filter(status = 'New',Distributor_id = data.id)
        n = len(noti)
        return render(request,'Distributor/Fin_DProfile.html',{'data':data,'data1':data1,'terms':terms,'noti':noti,'n':n})
    else:
       return redirect('/')  
    
def Fin_Dnotification(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Distributors_Details.objects.get(Login_Id = s_id)

        noti = Fin_DNotification.objects.filter(status = 'New',Distributor_id = data.id)
        n = len(noti)
        context = {
            'noti':noti,
            'n':n,
            'data':data
        }
        return render(request,'Distributor/Fin_Dnotification.html',context)  
    else:
       return redirect('/') 
    
def  Fin_Dnoti_Overview(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        d = Fin_Distributors_Details.objects.get(Login_Id = s_id)
        noti = Fin_DNotification.objects.filter(status = 'New',Distributor_id = d.id)
        n = len(noti)

        

        data = Fin_DNotification.objects.get(id=id)

        if data.Modules_List :
            allmodules = Fin_Modules_List.objects.get(Login_Id = data.Login_Id,status = "New")
            allmodules1 = Fin_Modules_List.objects.get(Login_Id = data.Login_Id,status = "pending")

        
            context = {
                'noti':noti,
                'n':n,
                'data':data,
                'allmodules':allmodules,
                'allmodules1':allmodules1,
            }
            return render(request,'Distributor/Fin_Dnoti_Overview.html',context)
        else:
            data1 = Fin_Company_Details.objects.get(Login_Id = data.Login_Id)
            context = {
                'noti':noti,
                'n':n,
                'data1':data1,
                'data':data,
                
            }
            return render(request,'Distributor/Fin_Dnoti_Overview.html',context)    
    else:
       return redirect('/') 
    
def  Fin_DModule_Updation_Accept(request,id):
    data = Fin_DNotification.objects.get(id=id)
    allmodules = Fin_Modules_List.objects.get(Login_Id = data.Login_Id,status = "New")
    allmodules.delete()

    allmodules1 = Fin_Modules_List.objects.get(Login_Id = data.Login_Id,status = "pending")
    allmodules1.status = "New"
    allmodules1.save()

    data.status = 'old'
    data.save()

    return redirect('Fin_Dnotification')

def  Fin_DModule_Updation_Reject(request,id):
    data = Fin_DNotification.objects.get(id=id)
    allmodules = Fin_Modules_List.objects.get(Login_Id = data.Login_Id,status = "pending")
    allmodules.delete()

    data.delete()

    return redirect('Fin_Dnotification')

def  Fin_Dpayment_terms_Updation_Accept(request,id):
    data = Fin_DNotification.objects.get(id=id)
    com = Fin_Company_Details.objects.get(Login_Id = data.Login_Id)
    terms=Fin_Payment_Terms.objects.get(id=data.PaymentTerms_updation.Payment_Term.id)
    
    
    com.Start_Date =date.today()
    days=int(terms.days)

    end= date.today() + timedelta(days=days)
    com.End_date = end
    com.Payment_Term = terms
    com.save()

    data.status = 'old'
    data.save()

    upt = Fin_Payment_Terms_updation.objects.get(id = data.PaymentTerms_updation.id)
    upt.status = 'old'
    upt.save()

    return redirect('Fin_Dnotification')

def  Fin_Dpayment_terms_Updation_Reject(request,id):
    data = Fin_DNotification.objects.get(id=id)

    upt = Fin_Payment_Terms_updation.objects.get(id = data.PaymentTerms_updation.id)

    upt.delete()
    data.delete()

    return redirect('Fin_Dnotification')    

def Fin_DChange_payment_terms(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        
        if request.method == 'POST':
            data = Fin_Login_Details.objects.get(id = s_id)
            com = Fin_Distributors_Details.objects.get(Login_Id = s_id)
            pt = request.POST['payment_term']

            pay = Fin_Payment_Terms.objects.get(id=pt)

            data1 = Fin_Payment_Terms_updation(Login_Id = data,Payment_Term = pay)
            data1.save()

            
            noti = Fin_ANotification(Login_Id = data,PaymentTerms_updation = data1,Title = "Change Payment Terms",Discription = com.Login_Id.First_name + " is change Payment Terms")
            noti.save()
              


        
            return redirect('Fin_DProfile')
    else:
       return redirect('/') 
    

def Fin_Edit_Dprofile(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        com = Fin_Distributors_Details.objects.get(Login_Id = s_id)
        data = Fin_Distributors_Details.objects.get(Login_Id = s_id)

        noti = Fin_DNotification.objects.filter(status = 'New',Distributor_id = data.id)
        n = len(noti)

        context ={
            'com':com,
            'data':data,
            'n':n,
            'noti':noti
        }

        return render(request,"Distributor/Fin_Edit_Dprofile.html",context)    
    else:
       return redirect('/')    
    
def Fin_Edit_Dprofile_Action(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        com = Fin_Distributors_Details.objects.get(Login_Id = s_id)
        if request.method == 'POST':
            com.Login_Id.First_name = request.POST['first_name']
            com.Login_Id.Last_name = request.POST['last_name']
            com.Email = request.POST['email']
            com.Contact = request.POST['contact']
            
            com.Image  = request.FILES.get('img')
            

            com.Login_Id.save()
            com.save()

            return redirect('Fin_DProfile')
        return redirect('Fin_Edit_Dprofile')     
    else:
       return redirect('/')     

      
# ---------------------------end distributor------------------------------------  


             
# ---------------------------start staff------------------------------------   
    

def Fin_StaffReg(request):
    return render(request,'company/Fin_StaffReg.html')

def Fin_staffReg_action(request):
   if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        user_name = request.POST['cusername']
        password = request.POST['cpassword'] 
        cid = request.POST['Company_Code']
        if Fin_Company_Details.objects.filter(Company_Code = cid ).exists():
            com =Fin_Company_Details.objects.get(Company_Code = cid )

            if Fin_Staff_Details.objects.filter(company_id=com,Login_Id__User_name=user_name).exists():
                messages.info(request, 'This username already exists. Sign up again')
                return redirect('Fin_StaffReg')

            if Fin_Login_Details.objects.filter(User_name=user_name,password = password).exists():
                messages.info(request, 'This username and password already exists. Sign up again')
                return redirect('Fin_StaffReg')
        
            elif Fin_Staff_Details.objects.filter(Email=email).exists():
                messages.info(request, 'This email already exists. Sign up again')
                return redirect('Fin_StaffReg')
            else:
                dlog = Fin_Login_Details(First_name = first_name,Last_name = last_name,
                                    User_name = user_name,password = password,
                                    User_Type = 'Staff')
                dlog.save()

                ddata = Fin_Staff_Details(Email = email,Login_Id = dlog,Company_approval_status = "NULL",company_id = com)
                ddata.save()
                return redirect('Fin_StaffReg2',dlog.id)
        else:
            messages.info(request, 'This company code  not exists. Sign up again')  
            return redirect('Fin_StaffReg')    
        
def Fin_StaffReg2(request,id):
    dlog = Fin_Login_Details.objects.get(id = id)
    ddata = Fin_Staff_Details.objects.get(Login_Id = id)
    context = {
       'dlog':dlog,
       'ddata':ddata
    }
    return render(request,'company/Fin_StaffReg2.html',context)

def Fin_StaffReg2_Action(request,id):
    if request.method == 'POST':
        
        staff = Fin_Staff_Details.objects.get(Login_Id = id)
        log = Fin_Login_Details.objects.get(id = id)

        staff.Login_Id = log
           
        staff.contact = request.POST['phone']
        staff.img=request.FILES.get('img')
        staff.Company_approval_status = "Null"
        staff.save()
        print("Staff Registration Complete")
    
        return redirect('Fin_StaffReg')
        
    else:
        return redirect('Fin_StaffReg2',id)
# ---------------------------end staff------------------------------------ 


    
# ---------------------------start company------------------------------------ 

def Fin_Com_Home(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')

            current_day=date.today() 
            diff = (com.End_date - current_day).days
            num = 20
            print(diff)
            if diff <= 20:
                n=Fin_CNotification(Login_Id = data,Company_id = com,Title = "Payment Terms Alert",Discription = "Your Payment Terms End Soon")
                n.save()    

            noti = Fin_CNotification.objects.filter(status = 'New',Company_id = com)
            n = len(noti)

            context = {
                'allmodules':allmodules,
                'com':com,
                'data':data,
                'noti':noti,
                'n':n
                }

            return render(request,'company/Fin_Com_Home.html',context)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            return render(request,'company/Fin_Com_Home.html',{'allmodules':allmodules,'com':com,'data':data})
    else:
       return redirect('/') 
    
def Fin_Cnotification(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')

            noti = Fin_CNotification.objects.filter(status = 'New',Company_id = com)
            n = len(noti)
            context = {
                'allmodules':allmodules,
                'com':com,
                'data':data,
                'noti':noti,
                'n':n
            }
            return render(request,'company/Fin_Cnotification.html',context)  
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            context = {
                'allmodules':allmodules,
                'com':com,
                'data':data,
                
            }
            return render(request,'company/Fin_Cnotification.html',context)
    else:
       return redirect('/')     
     

def Fin_CompanyReg(request):
    return render(request,'company/Fin_CompanyReg.html')

def Fin_companyReg_action(request):
   if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        user_name = request.POST['cusername']
        password = request.POST['cpassword']


        if Fin_Login_Details.objects.filter(User_name=user_name).exists():
            messages.info(request, 'This username already exists. Sign up again')
            return redirect('Fin_CompanyReg')
      
        elif Fin_Company_Details.objects.filter(Email=email).exists():
            messages.info(request, 'This email already exists. Sign up again')
            return redirect('Fin_CompanyReg')
        else:
            dlog = Fin_Login_Details(First_name = first_name,Last_name = last_name,
                                User_name = user_name,password = password,
                                User_Type = 'Company')
            dlog.save()

        code_length = 8  
        characters = string.ascii_letters + string.digits  # Letters and numbers

        while True:
            unique_code = ''.join(random.choice(characters) for _ in range(code_length))
        
            # Check if the code already exists in the table
            if not Fin_Company_Details.objects.filter(Company_Code = unique_code).exists():
              break  

        ddata = Fin_Company_Details(Email = email,Login_Id = dlog,Company_Code = unique_code,Admin_approval_status = "NULL",Distributor_approval_status = "NULL")
        ddata.save()
        return redirect('Fin_CompanyReg2',dlog.id)      

        # code=get_random_string(length=6)
        # if Fin_Company_Details.objects.filter( Company_Code = code).exists():
        #     code2=get_random_string(length=6)

        #     ddata = Fin_Company_Details(Email = email,Login_Id = dlog,Company_Code = code2,Admin_approval_status = "NULL",Distributor_approval_status = "NULL")
        #     ddata.save()
        #     return redirect('Fin_CompanyReg2',dlog.id)
        # else:
        #     ddata = Fin_Company_Details(Email = email,Login_Id = dlog,Company_Code = code,Admin_approval_status = "NULL",Distributor_approval_status = "NULL")
        #     ddata.save()
        #     return redirect('Fin_CompanyReg2',dlog.id)
 
   return redirect('Fin_DistributorReg')

def Fin_CompanyReg2(request,id):
    data = Fin_Login_Details.objects.get(id=id)
    terms = Fin_Payment_Terms.objects.all()
    return render(request,'company/Fin_CompanyReg2.html',{'data':data,'terms':terms})

def Fin_CompanyReg2_action2(request,id):
    if request.method == 'POST':
        data = Fin_Login_Details.objects.get(id=id)
        com = Fin_Company_Details.objects.get(Login_Id=data.id)

        com.Company_name = request.POST['cname']
        com.Address = request.POST['caddress']
        com.City = request.POST['city']
        com.State = request.POST['state']
        com.Pincode = request.POST['pincode']
        com.Country = request.POST['ccountry']
        com.Image  = request.FILES.get('img1')
        com.Business_name = request.POST['bname']
        com.Industry = request.POST['industry']
        com.Company_Type = request.POST['ctype']
        com.Accountant = request.POST['staff']
        com.Payment_Type = request.POST['paid']
        com.Registration_Type = request.POST['reg_type']
        com.Contact = request.POST['phone']

        dis_code = request.POST['dis_code']
        if dis_code != '':
            if Fin_Distributors_Details.objects.filter(Distributor_Code = dis_code).exists():
                com.Distributor_id = Fin_Distributors_Details.objects.get(Distributor_Code = dis_code)
            else :
                messages.info(request, 'Sorry, distributor id does not exists')
                return redirect('Fin_CompanyReg2',id)
            
        
        payment_term = request.POST['payment_term']
        terms=Fin_Payment_Terms.objects.get(id=payment_term)
        com.Payment_Term =terms
        com.Start_Date=date.today()
        days=int(terms.days)

        end= date.today() + timedelta(days=days)
        com.End_date=end

        com.save()
        return redirect('Fin_Modules',id)
   
def Fin_Modules(request,id):
    data = Fin_Login_Details.objects.get(id=id)
    return render(request,'company/Fin_Modules.html',{'data':data})   

def Fin_Add_Modules(request,id):
    if request.method == 'POST':
        data = Fin_Login_Details.objects.get(id=id)
        com = Fin_Company_Details.objects.get(Login_Id=data.id)

        # -----ITEMS----

        Items = request.POST.get('c1')
        Price_List = request.POST.get('c2')
        Stock_Adjustment = request.POST.get('c3')


        # --------- CASH & BANK-----
        Cash_in_hand = request.POST.get('c4')
        Offline_Banking = request.POST.get('c5')
        # Bank_Reconciliation = request.POST.get('c6')
        UPI = request.POST.get('c7')
        Bank_Holders = request.POST.get('c8')
        Cheque = request.POST.get('c9')
        Loan_Account = request.POST.get('c10')

        #  ------SALES MODULE -------
        Customers = request.POST.get('c11')
        Invoice  = request.POST.get('c12')
        Estimate = request.POST.get('c13')
        Sales_Order = request.POST.get('c14')
        Recurring_Invoice = request.POST.get('c15')
        Retainer_Invoice = request.POST.get('c16')
        Credit_Note = request.POST.get('c17')
        Payment_Received = request.POST.get('c18')
        Delivery_Challan = request.POST.get('c19')

        #  ---------PURCHASE MODULE--------- 
        Vendors = request.POST.get('c20') 
        Bills  = request.POST.get('c21')
        Recurring_Bills = request.POST.get('c22')
        Debit_Note = request.POST.get('c23')
        Purchase_Order = request.POST.get('c24')
        Expenses = request.POST.get('c25')
        Payment_Made = request.POST.get('c27')

        #  ---------EWay_Bill---------
        EWay_Bill = request.POST.get('c28')

        #  -------ACCOUNTS--------- 
        Chart_of_Accounts = request.POST.get('c29') 
        Manual_Journal = request.POST.get('c30')
        # Reconcile  = request.POST.get('c36')


        # -------PAYROLL------- 
        Employees = request.POST.get('c31')
        Employees_Loan = request.POST.get('c32')
        Holiday = request.POST.get('c33') 
        Attendance = request.POST.get('c34')
        Salary_Details = request.POST.get('c35')

        modules = Fin_Modules_List(Items = Items,Price_List = Price_List,Stock_Adjustment = Stock_Adjustment,
            Cash_in_hand = Cash_in_hand,Offline_Banking = Offline_Banking,
            UPI = UPI,Bank_Holders = Bank_Holders,Cheque = Cheque,Loan_Account = Loan_Account,
            Customers = Customers,Invoice = Invoice,Estimate = Estimate,Sales_Order = Sales_Order,
            Recurring_Invoice = Recurring_Invoice,Retainer_Invoice = Retainer_Invoice,Credit_Note = Credit_Note,
            Payment_Received = Payment_Received,Delivery_Challan = Delivery_Challan,
            Vendors = Vendors,Bills = Bills,Recurring_Bills = Recurring_Bills,Debit_Note = Debit_Note,
            Purchase_Order = Purchase_Order,Expenses = Expenses,
            Payment_Made = Payment_Made,EWay_Bill = EWay_Bill,
            Chart_of_Accounts = Chart_of_Accounts,Manual_Journal = Manual_Journal,
            Employees = Employees,Employees_Loan = Employees_Loan,Holiday = Holiday,
            Attendance = Attendance,Salary_Details = Salary_Details,
            Login_Id = data,company_id = com)
        
        modules.save()

        #Adding Default Units under company
        Fin_Units.objects.create(Company=com, name='BOX')
        Fin_Units.objects.create(Company=com, name='NUMBER')
        Fin_Units.objects.create(Company=com, name='PACK')

        # Adding default accounts for companies

        created_date = date.today()
        account_info = [
            {"company_id": com, "Login_Id": data, "account_type": "Accounts Payable", "account_name": "Accounts Payable", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "This is an account of all the money which you owe to others like a pending bill payment to a vendor,etc.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Accounts Receivable", "account_name": "Accounts Receivable", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "The money that customers owe you becomes the accounts receivable. A good example of this is a payment expected from an invoice sent to your customer.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Asset", "account_name": "Advance Tax", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Any tax which is paid in advance is recorded into the advance tax account. This advance tax payment could be a quarterly, half yearly or yearly payment", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Advertising and Marketing", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Your expenses on promotional, marketing and advertising activities like banners, web-adds, trade shows, etc. are recorded in advertising and marketing account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Automobile Expense", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Transportation related expenses like fuel charges and maintenance charges for automobiles, are included to the automobile expense account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Bad Debt", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Any amount which is lost and is unrecoverable is recorded into the bad debt account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Bank Fees and Charges", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": " Any bank fees levied is recorded into the bank fees and charges account. A bank account maintenance fee, transaction charges, a late payment fee are some examples.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Consultant Expense", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Charges for availing the services of a consultant is recorded as a consultant expenses. The fees paid to a soft skills consultant to impart personality development training for your employees is a good example.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Cost Of Goods Sold", "account_name": "Cost of Goods Sold", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An expense account which tracks the value of the goods sold.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Credit Card Charges", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": " Service fees for transactions , balance transfer fees, annual credit fees and other charges levied on a credit card are recorded into the credit card account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Depreciation Expense", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Any depreciation in value of your assets can be captured as a depreciation expense.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Income", "account_name": "Discount", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Any reduction on your selling price as a discount can be recorded into the discount account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Equity", "account_name": "Drawings", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "The money withdrawn from a business by its owner can be tracked with this account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Asset", "account_name": "Employee Advance", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Money paid out to an employee in advance can be tracked here till it's repaid or shown to be spent for company purposes", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Liability", "account_name": "Employee Reimbursements", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "This account can be used to track the reimbursements that are due to be paid out to employees.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Expense", "account_name": "Exchange Gain or Loss", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Changing the conversion rate can result in a gain or a loss. You can record this into the exchange gain or loss account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Fixed Asset", "account_name": "Furniture and Equipment", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Purchases of furniture and equipment for your office that can be used for a long period of time usually exceeding one year can be tracked with this account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Income", "account_name": "General Income", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "A general category of account where you can record any income which cannot be recorded into any other category", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Income", "account_name": "Interest Income", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "A percentage of your balances and deposits are given as interest to you by your banks and financial institutions. This interest is recorded into the interest income account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Stock", "account_name": "Inventory Asset", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An account which tracks the value of goods in your inventory.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "IT and Internet Expenses", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Money spent on your IT infrastructure and usage like internet connection, purchasing computer equipment etc is recorded as an IT and Computer Expense", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Janitorial Expense", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "All your janitorial and cleaning expenses are recorded into the janitorial expenses account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Income", "account_name": "Late Fee Income", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Any late fee income is recorded into the late fee income account. The late fee is levied when the payment for an invoice is not received by the due date", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Lodging", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Any expense related to putting up at motels etc while on business travel can be entered here.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Meals and Entertainment", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Expenses on food and entertainment are recorded into this account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Office Supplies", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "All expenses on purchasing office supplies like stationery are recorded into the office supplies account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Other Current Liability", "account_name": "Opening Balance Adjustments", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "This account will hold the difference in the debits and credits entered during the opening balance.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Equity", "account_name": "Opening Balance Offset", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "This is an account where you can record the balance from your previous years earning or the amount set aside for some activities. It is like a buffer account for your funds.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Income", "account_name": "Other Charges", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Miscellaneous charges like adjustments made to the invoice can be recorded in this account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Other Expenses", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": " Any minor expense on activities unrelated to primary business operations is recorded under the other expense account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Equity", "account_name": "Owner's Equity", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "The owners rights to the assets of a company can be quantified in the owner's equity account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Cash", "account_name": "Petty Cash", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "It is a small amount of cash that is used to pay your minor or casual expenses rather than writing a check.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Postage", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Your expenses on ground mails, shipping and air mails can be recorded under the postage account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Asset", "account_name": "Prepaid Expenses", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An asset account that reports amounts paid in advance while purchasing goods or services from a vendor.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Printing and Stationery", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": " Expenses incurred by the organization towards printing and stationery.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Rent Expense", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "The rent paid for your office or any space related to your business can be recorded as a rental expense.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Repairs and Maintenance", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "The costs involved in maintenance and repair of assets is recorded under this account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Equity", "account_name": "Retained Earnings", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "The earnings of your company which are not distributed among the share holders is accounted as retained earnings.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Salaries and Employee Wages", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Salaries for your employees and the wages paid to workers are recorded under the salaries and wages account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Income", "account_name": "Sales", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": " The income from the sales in your business is recorded under the sales account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Income", "account_name": "Shipping Charge", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Shipping charges made to the invoice will be recorded in this account.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Other Liability", "account_name": "Tag Adjustments", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": " This adjustment account tracks the transfers between different reporting tags.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Liability", "account_name": "Tax Payable", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "The amount of money which you owe to your tax authority is recorded under the tax payable account. This amount is a sum of your outstanding in taxes and the tax charged on sales.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Telephone Expense", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "The expenses on your telephone, mobile and fax usage are accounted as telephone expenses.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Travel Expense", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": " Expenses on business travels like hotel bookings, flight charges, etc. are recorded as travel expenses.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Uncategorized", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "This account can be used to temporarily track expenses that are yet to be identified and classified into a particular category.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Cash", "account_name": "Undeposited Funds", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "Record funds received by your company yet to be deposited in a bank as undeposited funds and group them as a current asset in your balance sheet.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Liability", "account_name": "Unearned Revenue", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "A liability account that reports amounts received in advance of providing goods or services. When the goods or services are provided, this account balance is decreased and a revenue account is increased.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Equity", "account_name": "Capital Stock", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": " An equity account that tracks the capital introduced when a business is operated through a company or corporation.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Long Term Liability", "account_name": "Construction Loans", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An expense account that tracks the amount you repay for construction loans.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Contract Assets", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An asset account to track the amount that you receive from your customers while you're yet to complete rendering the services.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Depreciation And Amortisation", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An expense account that is used to track the depreciation of tangible assets and intangible assets, which is amortization.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Equity", "account_name": "Distributions", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An equity account that tracks the payment of stock, cash or physical products to its shareholders.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Equity", "account_name": "Dividends Paid", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An equity account to track the dividends paid when a corporation declares dividend on its common stock.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Other Current Liability", "account_name": "GST Payable", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Liability", "account_name": "Output CGST", "credit_card_no": "", "sub_account": True, "parent_account": "GST Payable", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Liability", "account_name": "Output IGST", "credit_card_no": "", "sub_account": True, "parent_account": "GST Payable", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Liability", "account_name": "Output SGST", "credit_card_no": "", "sub_account": True, "parent_account": "GST Payable", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Other Current Asset", "account_name": "GST TCS Receivable", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Asset", "account_name": "GST TDS Receivable", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Other Current Asset", "account_name": "Input Tax Credits", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Asset", "account_name": "Input CGST", "credit_card_no": "", "sub_account": True, "parent_account": "Input Tax Credits", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Asset", "account_name": "Input IGST", "credit_card_no": "", "sub_account": True, "parent_account": "Input Tax Credits", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Asset", "account_name": "Input SGST", "credit_card_no": "", "sub_account": True, "parent_account": "Input Tax Credits", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Equity", "account_name": "Investments", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An equity account used to track the amount that you invest.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Cost Of Goods Sold", "account_name": "Job Costing", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An expense account to track the costs that you incur in performing a job or a task.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Cost Of Goods Sold", "account_name": "Labor", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An expense account that tracks the amount that you pay as labor.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Cost Of Goods Sold", "account_name": "Materials", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An expense account that tracks the amount you use in purchasing materials.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Merchandise", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An expense account to track the amount spent on purchasing merchandise.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Long Term Liability", "account_name": "Mortgages", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An expense account that tracks the amounts you pay for the mortgage loan.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Raw Materials And Consumables", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An expense account to track the amount spent on purchasing raw materials and consumables.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Asset", "account_name": "Reverse Charge Tax Input but not due", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "The amount of tax payable for your reverse charge purchases can be tracked here.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Asset", "account_name": "Sales to Customers (Cash)", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Cost Of Goods Sold", "account_name": "Subcontractor", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": " An expense account to track the amount that you pay subcontractors who provide service to you.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Other Current Liability", "account_name": "TDS Payable", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Other Current Asset", "account_name": "TDS Receivable", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Expense", "account_name": "Transportation Expense", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "An expense account to track the amount spent on transporting goods or providing services.", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},

            {"company_id": com, "Login_Id": data, "account_type": "Bank", "account_name": "Bank Account", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Cash", "account_name": "Cash Account", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Credit Card", "account_name": "Credit Card Account", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
            {"company_id": com, "Login_Id": data, "account_type": "Payment Clearing Account", "account_name": "Payment Clearing Account", "credit_card_no": "", "sub_account": "", "parent_account": "", "bank_account_no": None, "account_code": "", "description": "", "balance":0.0, "balance_type" : "", "date" : created_date, "create_status": "default", "status": "active"},
        ]

        for account in account_info:
            if not Fin_Chart_Of_Account.objects.filter(Company = com,account_name=account['account_name']).exists():
                new_account = Fin_Chart_Of_Account(Company=account['company_id'],LoginDetails=account['Login_Id'],account_name=account['account_name'],account_type=account['account_type'],credit_card_no=account['credit_card_no'],sub_account=account['sub_account'],parent_account=account['parent_account'],bank_account_no=account['bank_account_no'],account_code=account['account_code'],description=account['description'],balance=account['balance'],balance_type=account['balance_type'],create_status=account['create_status'],status=account['status'],date=account['date'])
                new_account.save()

        #Adding Default Customer payment under company
        Fin_Company_Payment_Terms.objects.create(Company=com, term_name='Due on Receipt', days=0)
        Fin_Company_Payment_Terms.objects.create(Company=com, term_name='NET 30', days=30)
        Fin_Company_Payment_Terms.objects.create(Company=com, term_name='NET 60', days=60)

        print("add modules")
        return redirect('Fin_CompanyReg')
    return redirect('Fin_Modules',id)

def Fin_Edit_Modules(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        
        com = Fin_Company_Details.objects.get(Login_Id = s_id)
        allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
        return render(request,'company/Fin_Edit_Modules.html',{'allmodules':allmodules,'com':com})
       
    else:
       return redirect('/') 
def Fin_Edit_Modules_Action(request): 
    if 's_id' in request.session:
        s_id = request.session['s_id']
        
        if request.method == 'POST':
            data = Fin_Login_Details.objects.get(id = s_id)
        
            com = Fin_Company_Details.objects.get(Login_Id = s_id)

            # -----ITEMS----

            Items = request.POST.get('c1')
            Price_List = request.POST.get('c2')
            Stock_Adjustment = request.POST.get('c3')


            # --------- CASH & BANK-----
            Cash_in_hand = request.POST.get('c4')
            Offline_Banking = request.POST.get('c5')
            # Bank_Reconciliation = request.POST.get('c6')
            UPI = request.POST.get('c7')
            Bank_Holders = request.POST.get('c8')
            Cheque = request.POST.get('c9')
            Loan_Account = request.POST.get('c10')

            #  ------SALES MODULE -------
            Customers = request.POST.get('c11')
            Invoice  = request.POST.get('c12')
            Estimate = request.POST.get('c13')
            Sales_Order = request.POST.get('c14')
            Recurring_Invoice = request.POST.get('c15')
            Retainer_Invoice = request.POST.get('c16')
            Credit_Note = request.POST.get('c17')
            Payment_Received = request.POST.get('c18')
            Delivery_Challan = request.POST.get('c19')

            #  ---------PURCHASE MODULE--------- 
            Vendors = request.POST.get('c20') 
            Bills  = request.POST.get('c21')
            Recurring_Bills = request.POST.get('c22')
            Debit_Note = request.POST.get('c23')
            Purchase_Order = request.POST.get('c24')
            Expenses = request.POST.get('c25')
            
            Payment_Made = request.POST.get('c27')

            # ----------EWay_Bill-----
            EWay_Bill = request.POST.get('c28')

            #  -------ACCOUNTS--------- 
            Chart_of_Accounts = request.POST.get('c29') 
            Manual_Journal = request.POST.get('c30')
            # Reconcile  = request.POST.get('c36')


            # -------PAYROLL------- 
            Employees = request.POST.get('c31')
            Employees_Loan = request.POST.get('c32')
            Holiday = request.POST.get('c33') 
            Attendance = request.POST.get('c34')
            Salary_Details = request.POST.get('c35')

            modules = Fin_Modules_List(Items = Items,Price_List = Price_List,Stock_Adjustment = Stock_Adjustment,
                Cash_in_hand = Cash_in_hand,Offline_Banking = Offline_Banking,
                UPI = UPI,Bank_Holders = Bank_Holders,Cheque = Cheque,Loan_Account = Loan_Account,
                Customers = Customers,Invoice = Invoice,Estimate = Estimate,Sales_Order = Sales_Order,
                Recurring_Invoice = Recurring_Invoice,Retainer_Invoice = Retainer_Invoice,Credit_Note = Credit_Note,
                Payment_Received = Payment_Received,Delivery_Challan = Delivery_Challan,
                Vendors = Vendors,Bills = Bills,Recurring_Bills = Recurring_Bills,Debit_Note = Debit_Note,
                Purchase_Order = Purchase_Order,Expenses = Expenses,
                Payment_Made = Payment_Made,EWay_Bill = EWay_Bill,
                Chart_of_Accounts = Chart_of_Accounts,Manual_Journal = Manual_Journal,
                Employees = Employees,Employees_Loan = Employees_Loan,Holiday = Holiday,
                Attendance = Attendance,Salary_Details = Salary_Details,
                Login_Id = data,company_id = com,status = 'pending')
            
            modules.save()
            data1=Fin_Modules_List.objects.filter(company_id = com).update(update_action=1)

            if com.Registration_Type == 'self':
                noti = Fin_ANotification(Login_Id = data,Modules_List = modules,Title = "Module Updation",Discription = com.Company_name + " is change Modules")
                noti.save()
            else:
                noti = Fin_DNotification(Distributor_id = com.Distributor_id,Login_Id = data,Modules_List = modules,Title = "Module Updation",Discription = com.Company_name + " is change Modules")
                noti.save()   

            print("edit modules")
            return redirect('Fin_Company_Profile')
        return redirect('Fin_Edit_Modules')
       
    else:
       return redirect('/')    
    


def Fin_Company_Profile(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            terms = Fin_Payment_Terms.objects.all()
            noti = Fin_CNotification.objects.filter(status = 'New',Company_id = com)
            n = len(noti)
            return render(request,'company/Fin_Company_Profile.html',{'allmodules':allmodules,'com':com,'data':data,'terms':terms,'noti':noti,'n':n})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            return render(request,'company/Fin_Company_Profile.html',{'allmodules':allmodules,'com':com,'data':data})
        
    else:
       return redirect('/') 
    
def Fin_Staff_Req(request): 
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        com = Fin_Company_Details.objects.get(Login_Id = s_id)
        data1 = Fin_Staff_Details.objects.filter(company_id = com.id,Company_approval_status = "NULL")
        allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
        noti = Fin_CNotification.objects.filter(status = 'New',Company_id = com)
        n = len(noti)
        return render(request,'company/Fin_Staff_Req.html',{'com':com,'data':data,'allmodules':allmodules,'data1':data1,'noti':noti,'n':n})
    else:
       return redirect('/') 

def Fin_Staff_Req_Accept(request,id):
   data = Fin_Staff_Details.objects.get(id=id)
   data.Company_approval_status = 'Accept'
   data.save()
   return redirect('Fin_Staff_Req')

def Fin_Staff_Req_Reject(request,id):
   data = Fin_Staff_Details.objects.get(id=id)
   data.Login_Id.delete()
   data.delete()
   return redirect('Fin_Staff_Req')  

def Fin_Staff_delete(request,id):
   data = Fin_Staff_Details.objects.get(id=id)
   data.Login_Id.delete()
   data.delete()
   return redirect('Fin_All_Staff')  

def Fin_All_Staff(request): 
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        com = Fin_Company_Details.objects.get(Login_Id = s_id)
        data1 = Fin_Staff_Details.objects.filter(company_id = com.id,Company_approval_status = "Accept")
        allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
        noti = Fin_CNotification.objects.filter(status = 'New',Company_id = com)
        n = len(noti)
        return render(request,'company/Fin_All_Staff.html',{'com':com,'data':data,'allmodules':allmodules,'data1':data1,'noti':noti,'n':n})
    else:
       return redirect('/') 


def Fin_Change_payment_terms(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        
        if request.method == 'POST':
            data = Fin_Login_Details.objects.get(id = s_id)
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            pt = request.POST['payment_term']

            pay = Fin_Payment_Terms.objects.get(id=pt)

            data1 = Fin_Payment_Terms_updation(Login_Id = data,Payment_Term = pay)
            data1.save()

            if com.Registration_Type == 'self':
                noti = Fin_ANotification(Login_Id = data,PaymentTerms_updation = data1,Title = "Change Payment Terms",Discription = com.Company_name + " is change Payment Terms")
                noti.save()
            else:
                noti = Fin_DNotification(Distributor_id = com.Distributor_id,Login_Id = data,PaymentTerms_updation = data1,Title = "Change Payment Terms",Discription = com.Company_name + " is change Payment Terms")
                noti.save()    


        
            return redirect('Fin_Company_Profile')
    else:
       return redirect('/') 
    
def Fin_Wrong(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
           com = Fin_Distributors_Details.objects.get(Login_Id = s_id)     
        terms = Fin_Payment_Terms.objects.all()
        context= {
            'com':com,
            'terms':terms
        }
        return render(request,"company/Fin_Wrong.html",context)    
    else:
       return redirect('/') 
    
def Fin_Wrong_Action(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        
        if request.method == 'POST':
            data = Fin_Login_Details.objects.get(id = s_id)

            if data.User_Type == "Company":
                com = Fin_Company_Details.objects.get(Login_Id = s_id)
                pt = request.POST['payment_term']

                pay = Fin_Payment_Terms.objects.get(id=pt)

                data1 = Fin_Payment_Terms_updation(Login_Id = data,Payment_Term = pay)
                data1.save()

                if com.Registration_Type == 'self':
                    noti = Fin_ANotification(Login_Id = data,PaymentTerms_updation = data1,Title = "Change Payment Terms",Discription = com.Company_name + " is change Payment Terms")
                    noti.save()
                else:
                    noti = Fin_DNotification(Distributor_id = com.Distributor_id,Login_Id = data,PaymentTerms_updation = data1,Title = "Change Payment Terms",Discription = com.Company_name + " is change Payment Terms")
                    noti.save()    


            
                return redirect('Fin_CompanyReg')
            else:
                com = Fin_Distributors_Details.objects.get(Login_Id = s_id)
                pt = request.POST['payment_term']

                pay = Fin_Payment_Terms.objects.get(id=pt)

                data1 = Fin_Payment_Terms_updation(Login_Id = data,Payment_Term = pay)
                data1.save()

                noti = Fin_ANotification(Login_Id = data,PaymentTerms_updation = data1,Title = "Change Payment Terms",Discription = com.Login_Id.First_name + com.Login_Id.Last_name + " is change Payment Terms")
                noti.save()

                return redirect('Fin_DistributorReg')



    else:
       return redirect('/')  

def Fin_Edit_Company_profile(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        com = Fin_Company_Details.objects.get(Login_Id = s_id)
        noti = Fin_CNotification.objects.filter(status = 'New',Company_id = com)
        n = len(noti)

        context ={
            'com':com,
            'data':data,
            'n':n,
            'noti':noti


        }

        return render(request,"company/Fin_Edit_Company_profile.html",context)    
    else:
       return redirect('/') 
    

def Fin_Edit_Company_profile_Action(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        com = Fin_Company_Details.objects.get(Login_Id = s_id)
        if request.method == 'POST':
            com.Login_Id.First_name = request.POST['first_name']
            com.Login_Id.Last_name = request.POST['last_name']
            com.Email = request.POST['email']
            com.Contact = request.POST['contact']
            com.Company_name = request.POST['cname']
            com.Address = request.POST['caddress']
            com.City = request.POST['city']
            com.State = request.POST['state']
            com.Pincode = request.POST['pincode']
            com.Business_name = request.POST['bname']
            com.Pan_NO = request.POST['pannum']
            com.GST_Type = request.POST.get('gsttype')
            com.GST_NO = request.POST['gstnum']
            com.Industry = request.POST['industry']
            com.Company_Type = request.POST['ctype']
            com.Image = request.FILES.get('img')
            

            com.Login_Id.save()
            com.save()

            return redirect('Fin_Company_Profile')
        return redirect('Fin_Edit_Company_profile')     
    else:
       return redirect('/') 
    
def Fin_Edit_Staff_profile(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        com = Fin_Staff_Details.objects.get(Login_Id = s_id)

        context ={
            'com':com
        }

        return render(request,"company/Fin_Edit_Staff_profile.html",context)    
    else:
       return redirect('/')    
    
def Fin_Edit_Staff_profile_Action(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        com = Fin_Staff_Details.objects.get(Login_Id = s_id)
        if request.method == 'POST':
            com.Login_Id.First_name = request.POST['first_name']
            com.Login_Id.Last_name = request.POST['last_name']
            com.Email = request.POST['email']
            com.contact = request.POST['contact']
            
            com.img = request.FILES.get('img')
            

            com.Login_Id.save()
            com.save()

            return redirect('Fin_Company_Profile')
        return redirect('Fin_Edit_Staff_profile')     
    else:
       return redirect('/')     
      
    
# ---------------------------end company------------------------------------     
import calendar
from calendar import monthrange,month_name

def Fin_Attendance(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        log = Fin_Login_Details.objects.get(id = s_id)
        
        if log.User_Type == 'Staff':
            event_counts = {}
            formatted_event_counts = {}
            staff =Fin_Staff_Details.objects.get(Login_Id =log)
            allmodules = Fin_Modules_List.objects.get(company_id = staff.company_id)

            all_events = Fin_Attendances.objects.filter(company=staff.company_id)
            for event in all_events:
                month_year = event.start_date.strftime('%Y-%m')  # Format: 'YYYY-MM'
                year, month = map(int, month_year.split('-'))

                event_duration = (event.end_date - event.start_date).days + 1 if event.end_date else 1

                if month_year not in event_counts:
                    event_counts[month_year] = event_duration
                else:
                    event_counts[month_year] += event_duration
            for key, value in event_counts.items():
                year, month = map(int, key.split('-'))
                total_days = monthrange(year, month)[1]
                month_name = calendar.month_name[int(month)]
                formatted_month_year = f"{month_name}-{year}"
                formatted_event_counts[formatted_month_year] = {'count': value, 'total_days': total_days, 'month': month_name,
                                                         'year': year}
                
            attendance_data = Fin_Attendances.objects.filter(company=staff.company_id)
            employee_attendance = {}

            for entry in attendance_data:
                year = entry.start_date.year
                month = entry.start_date.month

                key = (entry.employee.id, year, month)
               
                if key not in employee_attendance:
                    formatted_month_year = f"{calendar.month_name[int(month)]}-{year}"
                    employee_attendance[key] = {
                    'formatted_month_year': formatted_month_year,
                    'e_id':entry.employee.id,
                    'employee': entry.employee.first_name + ' ' + entry.employee.last_name,
                    'year': year,
                    'month': calendar.month_name[int(month)],
                    'working_days': 0,
                    'holidays': 0,
                    'absent_days': 0,
                }

                if entry.status == 'Leave':
                    absent_days = (entry.end_date - entry.start_date).days + 1 if entry.end_date else 1
                    employee_attendance[key]['absent_days'] += absent_days

                    _, last_day = monthrange(year, month)

                holidays_data = Holiday.objects.filter(
                    company=staff.company_id,
                    start_date__year=year,
                    start_date__month=month
                )
                total_holidays = 0
                for holiday in holidays_data:
                    total_holidays += (holiday.end_date - holiday.start_date).days + 1

                employee_attendance[key]['holidays'] = total_holidays
                employee_attendance[key]['working_days'] = last_day - total_holidays - employee_attendance[key]['absent_days']
            

        if log.User_Type == 'Company':
            event_counts = {}
            formatted_event_counts = {}
            com = Fin_Company_Details.objects.get(Login_Id = log)
            allmodules = Fin_Modules_List.objects.get(company_id = com.id)
            all_events = Fin_Attendances.objects.filter(company=com.id)
            for event in all_events:
                month_year = event.start_date.strftime('%Y-%m')  # Format: 'YYYY-MM'
                year, month = map(int, month_year.split('-'))

                event_duration = (event.end_date - event.start_date).days + 1 if event.end_date else 1

                if month_year not in event_counts:
                    event_counts[month_year] = event_duration
                else:
                    event_counts[month_year] += event_duration
            for key, value in event_counts.items():
                year, month = map(int, key.split('-'))
                total_days = monthrange(year, month)[1]
                month_name = calendar.month_name[int(month)]
                formatted_month_year = f"{month_name}-{year}"
                formatted_event_counts[formatted_month_year] = {'count': value, 'total_days': total_days, 'month': month_name,
                                                         'year': year}
                
            attendance_data = Fin_Attendances.objects.filter(company=com.id)
            employee_attendance = {}

            for entry in attendance_data:
                year = entry.start_date.year
                month = entry.start_date.month

                key = (entry.employee.id, year, month)
               
                if key not in employee_attendance:
                    formatted_month_year = f"{calendar.month_name[int(month)]}-{year}"
                    employee_attendance[key] = {
                    'formatted_month_year': formatted_month_year,
                    'e_id':entry.employee.id,
                    'employee': entry.employee.first_name + ' ' + entry.employee.last_name,
                    'year': year,
                    'month': calendar.month_name[int(month)],
                    'working_days': 0,
                    'holidays': 0,
                    'absent_days': 0,
                }
            

                if entry.status == 'Leave':
                    absent_days = (entry.end_date - entry.start_date).days + 1 if entry.end_date else 1
                    employee_attendance[key]['absent_days'] += absent_days

                    _, last_day = monthrange(year, month)

                holidays_data = Holiday.objects.filter(
                    company=com.id,
                    start_date__year=year,
                    start_date__month=month
                )
                total_holidays = 0
                for holiday in holidays_data:
                    total_holidays += (holiday.end_date - holiday.start_date).days + 1

                employee_attendance[key]['holidays'] = total_holidays
                employee_attendance[key]['working_days'] = last_day - total_holidays - employee_attendance[key]['absent_days']
            

        context = {
            "events": all_events,
            "event_counts_json": formatted_event_counts,
            'employee_attendance': list(employee_attendance.values()),
            'allmodules':allmodules
        }   
        return render(request,'company/Fin_Attendance.html',context)

def Fin_Add_Attendance(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        log = Fin_Login_Details.objects.get(id = s_id)
        if log.User_Type == 'Staff':
            staff =Fin_Staff_Details.objects.get(Login_Id =log)
            allmodules = Fin_Modules_List.objects.get(company_id = staff.company_id)
            emp = Employee.objects.filter(company = staff.company_id,employee_status = 'active')
            bgroup = Employee_Blood_Group.objects.filter(company = staff.company_id)
        if log.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = log)
            allmodules = Fin_Modules_List.objects.get(company_id = com.id)
            emp = Employee.objects.filter(company = com.id,employee_status = 'active')
            bgroup = Employee_Blood_Group.objects.filter(company = com.id)

        context ={
            'emp':emp,'bloodgroup':bgroup,'allmodules':allmodules
        }
        return render(request,'company/Fin_add_attendance.html',context)
    return redirect('Fin_Attendance')

#from django.http import JsonResponse

def Fin_Holiday_check_for_attendance(request):
    date = request.POST.get('sdate')
    empid = request.POST.get('empid')
    if 's_id' in request.session:
        s_id = request.session['s_id']
        log = Fin_Login_Details.objects.get(id = s_id)
        if log.User_Type == 'Staff':
            staff =Fin_Staff_Details.objects.get(Login_Id =log)
            exists = Holiday.objects.filter(company = staff.company_id,start_date__lte=date, end_date__gte=date).exists()
            atndance = Fin_Attendances.objects.filter(employee = empid, company = staff.company_id,start_date__lte=date,end_date__gte=date).exists()
        if log.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = log)
            exists = Holiday.objects.filter(company = com.id,start_date__lte=date, end_date__gte=date).exists()
            atndance = Fin_Attendances.objects.filter(employee = empid, company = com.id,start_date__lte=date,end_date__gte=date).exists()

        return JsonResponse({'exists': exists,'atndance':atndance})
    


def Fin_attendance_save(request):
    if 's_id' in request.session:
        if request.method == 'POST':
            s_id = request.session['s_id']
            emp = request.POST['emp']
            empid = Employee.objects.get(id = emp)
            log = Fin_Login_Details.objects.get(id = s_id)
            if log.User_Type == 'Staff':
                staff =Fin_Staff_Details.objects.get(Login_Id =log)
                attendance = Fin_Attendances(employee = empid,start_date= request.POST['sdate'],end_date = request.POST['edate'],status = request.POST['status'],reason = request.POST['reason'],company = staff.company_id,login_id = log)
                attendance.save()
                att_history = Fin_Attendance_history(company = staff.company_id,login_id = log,attendance = attendance,action = "Created")
                att_history.save()
                return redirect('Fin_Attendance')

            if log.User_Type == 'Company':
                com = Fin_Company_Details.objects.get(Login_Id = log)
                attendance = Fin_Attendances(start_date= request.POST['sdate'],end_date = request.POST['edate'],status = request.POST['status'],reason = request.POST['reason'],company = com,login_id = log,employee = empid)
                attendance.save()
                att_history = Fin_Attendance_history(company = com,login_id = log,attendance = attendance,action = "Created")
                att_history.save()
                return redirect('Fin_Attendance')
        return redirect('Fin_Add_Attendance')
    return redirect('Fin_Add_Attendance')

def chumma(request):
    return render(request,'company/chumma.html')



def fin_employee_save_atndnce(request):

    if request.method == 'POST':

        title = request.POST['Title']
        firstname = request.POST['First_Name'].capitalize()
        lastname = request.POST['Last_Name'].capitalize()
        image = request.FILES.get('Image', None)
        if image:
            image = request.FILES['Image']
        else:
            image = ''
        alias = request.POST['Alias']
        joiningdate = request.POST['Joining_Date']
        salarydate = request.POST['Salary_Date']
        salary_type = request.POST['Salary_Type']

        amountperhour = request.POST['perhour']
        if amountperhour == '' or amountperhour == '0':
            amountperhour = 0
        else:
            amountperhour = request.POST['perhour']

        workinghour = request.POST['workhour']
        if workinghour == '' or workinghour == '0':
            workinghour = 0
        else:
            workinghour = request.POST['workhour']

        salaryamount = request.POST['Salary_Amount']
        if request.POST['Salary_Amount'] == '':
            salaryamount = None
        else:
            salaryamount = request.POST['Salary_Amount']

        employeenumber = request.POST['Employee_Number']
        designation = request.POST['Designation']
        location = request.POST['Location']
        gender = request.POST['Gender']
        dob = request.POST['DOB']
        blood = request.POST['Blood']
        contact = request.POST['Contact_Number']
        emergencycontact = request.POST['Emergency_Contact']
        email = request.POST['Email']
        parent = request.POST['Parent'].capitalize()
        spouse = request.POST['Spouse'].capitalize()
        file = request.FILES.get('File', None)
        if file:
            file = request.FILES['File']
        else:
            file=''
        street = request.POST['street']
        city = request.POST['city']
        state = request.POST['state']
        pincode = request.POST['pincode']
        country = request.POST['country']
        tempStreet = request.POST['tempStreet']
        tempCity = request.POST['tempCity']
        tempState = request.POST['tempState']
        tempPincode = request.POST['tempPincode']
        tempCountry = request.POST['tempCountry']
        
        bankdetails = request.POST['Bank_Details']
        if bankdetails == "Yes":
            accoutnumber = request.POST['Account_Number']
            ifsc = request.POST['IFSC']
            bankname = request.POST['BankName']
            branchname = request.POST['BranchName']
            transactiontype = request.POST['Transaction_Type']
        else:
            accoutnumber = ''
            ifsc = ''
            bankname = ''
            branchname = ''
            transactiontype = ''

        if request.POST['tds_applicable'] == 'Yes':
            tdsapplicable = request.POST['tds_applicable']
            tdstype = request.POST['TDS_Type']
            
            if tdstype == 'Amount':
                tdsvalue = request.POST['TDS_Amount']
            elif tdstype == 'Percentage':
                tdsvalue = request.POST['TDS_Percentage']
            else:
                tdsvalue = 0
        elif request.POST['tds_applicable'] == 'No':
            tdsvalue = 0
            tdstype = ''
            tdsapplicable = request.POST['tds_applicable']
        else:
            tdsvalue = 0
            tdstype = ''
            tdsapplicable = ''

        incometax = request.POST['Income_Tax']
        aadhar = request.POST['Aadhar']
        uan = request.POST['UAN']
        pf = request.POST['PF']
        pan = request.POST['PAN']
        pr = request.POST['PR']

        if dob == '':
            age = 2
        else:
            dob2 = date.fromisoformat(dob)
            today = date.today()
            age = int(today.year - dob2.year - ((today.month, today.day) < (dob2.month, dob2.day)))
        
        sid = request.session['s_id']
        employee = Fin_Login_Details.objects.get(id=sid)
        
        if employee.User_Type == 'Company':
            companykey =  Fin_Company_Details.objects.get(Login_Id_id=sid)
        elif employee.User_Type == 'Staff':
            staffkey = Fin_Staff_Details.objects.get(Login_Id=sid)
            companykey = Fin_Company_Details.objects.get(id=staffkey.company_id_id)
        else:
            distributorkey = Fin_Distributors_Details.objects.get(login_Id=sid)
            companykey = Fin_Company_Details.objects.get(id=distributorkey.company_id_id)

        
        if Employee.objects.filter(employee_mail=email,mobile = contact,employee_number=employeenumber,company_id = companykey.id).exists():
            messages.error(request,'user exist')
            return redirect('Fin_Add_Attendance')
        
        elif Employee.objects.filter(mobile = contact,company_id = companykey.id).exists():
            messages.error(request,'phone number exist')
            return redirect('Fin_Add_Attendance')
        
        elif Employee.objects.filter(emergency_contact = emergencycontact,company_id = companykey.id).exists():
            messages.error(request,'emergency phone number exist')
            return redirect('Fin_Add_Attendance')
        
        elif Employee.objects.filter(employee_mail=email,company_id = companykey.id).exists():
            messages.error(request,'email exist')
            return redirect('Fin_Add_Attendance')
        
        elif Employee.objects.filter(employee_number=employeenumber,company_id = companykey.id).exists():
            messages.error(request,'employee id exist')
            return redirect('Fin_Add_Attendance')
        
        elif incometax != '' and Employee.objects.filter(income_tax_number = incometax,company_id = companykey.id).exists():
            messages.error(request,'Income Tax Number exist')
            return redirect('Fin_Add_Attendance')
        
        elif pf != '' and Employee.objects.filter(pf_account_number = pf,company_id = companykey.id).exists():
            messages.error(request,'PF account number exist')
            return redirect('Fin_Add_Attendance')
        
        elif aadhar != '' and Employee.objects.filter(aadhar_number = aadhar,company_id = companykey.id).exists():
            messages.error(request,'Aadhar number exist')
            return redirect('Fin_Add_Attendance')
        
        elif pan != '' and Employee.objects.filter(pan_number = pan,company_id = companykey.id).exists():
            messages.error(request,'PAN number exist')
            return redirect('Fin_Add_Attendance')
        
        elif uan != '' and Employee.objects.filter(universal_account_number = uan,company_id = companykey.id).exists():
            messages.error(request,'Universal account number exist')
            return redirect('Fin_Add_Attendance')
        
        elif pr != '' and Employee.objects.filter(pr_account_number = pr,company_id = companykey.id).exists():
            messages.error(request,'PR account number exist')
            return redirect('Fin_Add_Attendance')
        
        elif bankdetails.lower() == 'yes':
            if accoutnumber != '' and Employee.objects.filter(account_number=accoutnumber,company_id = companykey.id).exists():
                messages.error(request,'Bank account number already exist')
                return redirect('Fin_Add_Attendance')
            
            else:
                if employee.User_Type == 'Company':
                    

                    new = Employee(upload_image=image,title = title,first_name = firstname,last_name = lastname,alias = alias,
                            employee_mail = email,employee_number = employeenumber,employee_designation = designation,
                            employee_current_location = location,mobile = contact,date_of_joining = joiningdate,
                            employee_status = 'Active' ,company_id = companykey.id,login_id=sid,salary_amount = salaryamount ,
                            amount_per_hour = amountperhour ,total_working_hours = workinghour,gender = gender ,date_of_birth = dob ,
                            age = age,blood_group = blood,fathers_name_mothers_name = parent,spouse_name = spouse,
                            emergency_contact = emergencycontact,provide_bank_details = bankdetails,account_number = accoutnumber,
                            ifsc = ifsc,name_of_bank = bankname,branch_name = branchname,bank_transaction_type = transactiontype,
                            tds_applicable = tdsapplicable, tds_type = tdstype,percentage_amount = tdsvalue,pan_number = pan,
                            income_tax_number = incometax,aadhar_number = aadhar,universal_account_number = uan,pf_account_number = pf,
                            pr_account_number = pr,upload_file = file,employee_salary_type =salary_type,salary_effective_from=salarydate,
                            city=city,street=street,state=state,country=country,pincode=pincode,temporary_city=tempCity,
                            temporary_street=tempStreet,temporary_state=tempState,temporary_pincode=tempPincode,temporary_country=tempCountry)
                    new.save()

                    history = Employee_History(company_id = companykey.id,login_id=sid,employee_id = new.id,date = date.today(),action = 'Created')
                    history.save()
            
                elif employee.User_Type == 'Staff':
                    

                    new =  Employee(upload_image=image,title = title,first_name = firstname,last_name = lastname,alias = alias,
                                employee_mail = email,employee_number = employeenumber,employee_designation = designation,
                                employee_current_location = location,mobile = contact,date_of_joining = joiningdate,
                                employee_salary_type = salary_type,employee_status = 'Active' ,company_id = companykey.id,login_id=sid ,
                                amount_per_hour = amountperhour ,total_working_hours = workinghour,gender = gender ,date_of_birth = dob ,
                                age = age,blood_group = blood,fathers_name_mothers_name = parent,spouse_name = spouse,
                                emergency_contact = emergencycontact,provide_bank_details = bankdetails,account_number = accoutnumber,
                                ifsc = ifsc,name_of_bank = bankname,branch_name = branchname,bank_transaction_type = transactiontype,
                                tds_applicable = tdsapplicable, tds_type = tdstype,percentage_amount = tdsvalue,pan_number = pan,
                                income_tax_number = incometax,aadhar_number = aadhar,universal_account_number = uan,pf_account_number = pf,
                                pr_account_number = pr,upload_file = file,salary_amount = salaryamount,salary_effective_from=salarydate,
                                city=city,street=street,state=state,country=country,pincode=pincode,temporary_city=tempCity,
                                temporary_street=tempStreet,temporary_state=tempState,temporary_pincode=tempPincode,temporary_country=tempCountry)
                    
                    new.save()

                    history = Employee_History(company_id = companykey.id,login_id=sid,employee_id = new.id,date = date.today(),action = 'Created')
                    history.save()
        
        else:
            if employee.User_Type == 'Company':
                

                new = Employee(upload_image=image,title = title,first_name = firstname,last_name = lastname,alias = alias,
                        employee_mail = email,employee_number = employeenumber,employee_designation = designation,
                        employee_current_location = location,mobile = contact,date_of_joining = joiningdate,
                        employee_status = 'Active' ,company_id = companykey.id,login_id=sid,salary_amount = salaryamount ,
                        amount_per_hour = amountperhour ,total_working_hours = workinghour,gender = gender ,date_of_birth = dob ,
                        age = age,blood_group = blood,fathers_name_mothers_name = parent,spouse_name = spouse,
                        emergency_contact = emergencycontact,provide_bank_details = bankdetails,account_number = accoutnumber,
                        ifsc = ifsc,name_of_bank = bankname,branch_name = branchname,bank_transaction_type = transactiontype,
                        tds_applicable = tdsapplicable, tds_type = tdstype,percentage_amount = tdsvalue,pan_number = pan,
                        income_tax_number = incometax,aadhar_number = aadhar,universal_account_number = uan,pf_account_number = pf,
                        pr_account_number = pr,upload_file = file,employee_salary_type =salary_type,salary_effective_from=salarydate,
                        city=city,street=street,state=state,country=country,pincode=pincode,temporary_city=tempCity,
                        temporary_street=tempStreet,temporary_state=tempState,temporary_pincode=tempPincode,temporary_country=tempCountry)
                new.save()

                history = Employee_History(company_id = companykey.id,login_id=sid,employee_id = new.id,date = date.today(),action = 'Created')
                history.save()
        
            elif employee.User_Type == 'Staff':
                

                new =  Employee(upload_image=image,title = title,first_name = firstname,last_name = lastname,alias = alias,
                            employee_mail = email,employee_number = employeenumber,employee_designation = designation,
                            employee_current_location = location,mobile = contact,date_of_joining = joiningdate,
                            employee_salary_type = salary_type,employee_status = 'Active' ,company_id = companykey.id,login_id=sid ,
                            amount_per_hour = amountperhour ,total_working_hours = workinghour,gender = gender ,date_of_birth = dob ,
                            age = age,blood_group = blood,fathers_name_mothers_name = parent,spouse_name = spouse,
                            emergency_contact = emergencycontact,provide_bank_details = bankdetails,account_number = accoutnumber,
                            ifsc = ifsc,name_of_bank = bankname,branch_name = branchname,bank_transaction_type = transactiontype,
                            tds_applicable = tdsapplicable, tds_type = tdstype,percentage_amount = tdsvalue,pan_number = pan,
                            income_tax_number = incometax,aadhar_number = aadhar,universal_account_number = uan,pf_account_number = pf,
                            pr_account_number = pr,upload_file = file,salary_amount = salaryamount,salary_effective_from=salarydate,
                            city=city,street=street,state=state,country=country,pincode=pincode,temporary_city=tempCity,
                            temporary_street=tempStreet,temporary_state=tempState,temporary_pincode=tempPincode,temporary_country=tempCountry)
                
                new.save()

                history = Employee_History(company_id = companykey.id,login_id=sid,employee_id = new.id,date = date.today(),action = 'Created')
                history.save()

        sid = request.session['s_id']
        loginn = Fin_Login_Details.objects.get(id=sid)
        if loginn.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = sid)
            allmodules = Fin_Modules_List.objects.get(company_id = com.id)
            employee = Employee.objects.filter(company_id=com.id)
            
        elif loginn.User_Type == 'Staff' :
            com = Fin_Staff_Details.objects.get(Login_Id = sid)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)
            employee = Employee.objects.filter(company_id=com.company_id_id)
        return redirect('Fin_Add_Attendance')
    



def Fin_Attendanceview(request,mn,yr,id):
    if 's_id' in request.session:
        month_name = mn
        months = list(calendar.month_name).index(month_name) 
        month = months - 1

        year = yr
    
        sid = request.session['s_id']
        loginn = Fin_Login_Details.objects.get(id=sid)
        if loginn.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = sid)
            events = Holiday.objects.filter(start_date__month=months,start_date__year=year,company_id=com.id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.id)
            attendance = Fin_Attendances.objects.filter(employee = id,company = com.id,start_date__month=months,start_date__year =year)
            emp =Employee.objects.get(id=id)
        
        elif loginn.User_Type == 'Staff' :
            com = Fin_Staff_Details.objects.get(Login_Id = sid)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id)
            events = Holiday.objects.filter(start_date__month=months,start_date__year=year,company_id=com.company_id)
            attendance = Fin_Attendances.objects.filter(employee = id,company = com.company_id,start_date__month=months,start_date__year =year)
            emp =Employee.objects.get(id=id)

        return render(request,'company/Fin_AttendanceView.html',{'events':events,'month':month,'year':year,'attendance':attendance,'emp':emp,'month_name':month_name,'allmodules':allmodules})


def Fin_editAttendance(request,id,mn,yr,pk):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        log = Fin_Login_Details.objects.get(id = s_id)
        leave = Fin_Attendances.objects.get(id=id)
    
        if log.User_Type == 'Staff':
            staff =Fin_Staff_Details.objects.get(Login_Id =log)
            allmodules = Fin_Modules_List.objects.get(company_id = staff.company_id)
            emp = Employee.objects.filter(company = staff.company_id,employee_status = 'active')
            bgroup = Employee_Blood_Group.objects.filter(company = staff.company_id)
            
        if log.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = log)
            allmodules = Fin_Modules_List.objects.get(company_id = com.id)
            emp = Employee.objects.filter(company = com.id,employee_status = 'active')
            bgroup = Employee_Blood_Group.objects.filter(company = com.id)
            
        context ={
            'emp':emp,'bloodgroup':bgroup,'leave':leave,'allmodules':allmodules,'mn':mn,'yr':yr,'pk':pk
        }
        return render(request,'company/Fin_attendanceEdit.html',context)

def Fin_editAttendanceVIEW(request,id,mn,yr,pk):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        log = Fin_Login_Details.objects.get(id = s_id)
        leave = Fin_Attendances.objects.get(id=id)
    
        if log.User_Type == 'Staff':
            staff =Fin_Staff_Details.objects.get(Login_Id =log)
            if request.method == 'POST':
                emps = request.POST['empS']
                empid = Employee.objects.get(id = emps)
                leave.employee = empid
                leave.start_date = request.POST['sdate']
                leave.end_date = request.POST['edate']
                leave.reason = request.POST['reason']
                leave.status = request.POST['status']
                leave.save()
                att_history = Fin_Attendance_history(company = staff.company_id,login_id = log,attendance = leave,action = "Edited")
                att_history.save()
                return redirect('Fin_Attendanceview',mn,yr,pk)
        if log.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = log)
            if request.method == 'POST':
                emps = request.POST['empS']
                empid = Employee.objects.get(id = emps)
                leave.employee = empid
                leave.start_date = request.POST['sdate']
                leave.end_date = request.POST['edate']
                leave.reason = request.POST['reason']
                leave.status = request.POST['status']
                leave.save()
                att_history = Fin_Attendance_history(company = com,login_id = log,attendance = leave,action = "Edited")
                att_history.save()
                return redirect('Fin_Attendanceview',mn,yr,pk)
            
def fin_employee_save_atndnce_EDIT(request,mn,yr,pk):

    if request.method == 'POST':

        title = request.POST['Title']
        firstname = request.POST['First_Name'].capitalize()
        lastname = request.POST['Last_Name'].capitalize()
        image = request.FILES.get('Image', None)
        if image:
            image = request.FILES['Image']
        else:
            image = ''
        alias = request.POST['Alias']
        joiningdate = request.POST['Joining_Date']
        salarydate = request.POST['Salary_Date']
        salary_type = request.POST['Salary_Type']

        amountperhour = request.POST['perhour']
        if amountperhour == '' or amountperhour == '0':
            amountperhour = 0
        else:
            amountperhour = request.POST['perhour']

        workinghour = request.POST['workhour']
        if workinghour == '' or workinghour == '0':
            workinghour = 0
        else:
            workinghour = request.POST['workhour']

        salaryamount = request.POST['Salary_Amount']
        if request.POST['Salary_Amount'] == '':
            salaryamount = None
        else:
            salaryamount = request.POST['Salary_Amount']

        employeenumber = request.POST['Employee_Number']
        designation = request.POST['Designation']
        location = request.POST['Location']
        gender = request.POST['Gender']
        dob = request.POST['DOB']
        blood = request.POST['Blood']
        contact = request.POST['Contact_Number']
        emergencycontact = request.POST['Emergency_Contact']
        email = request.POST['Email']
        parent = request.POST['Parent'].capitalize()
        spouse = request.POST['Spouse'].capitalize()
        file = request.FILES.get('File', None)
        if file:
            file = request.FILES['File']
        else:
            file=''
        street = request.POST['street']
        city = request.POST['city']
        state = request.POST['state']
        pincode = request.POST['pincode']
        country = request.POST['country']
        tempStreet = request.POST['tempStreet']
        tempCity = request.POST['tempCity']
        tempState = request.POST['tempState']
        tempPincode = request.POST['tempPincode']
        tempCountry = request.POST['tempCountry']
        
        bankdetails = request.POST['Bank_Details']
        if bankdetails == "Yes":
            accoutnumber = request.POST['Account_Number']
            ifsc = request.POST['IFSC']
            bankname = request.POST['BankName']
            branchname = request.POST['BranchName']
            transactiontype = request.POST['Transaction_Type']
        else:
            accoutnumber = ''
            ifsc = ''
            bankname = ''
            branchname = ''
            transactiontype = ''

        if request.POST['tds_applicable'] == 'Yes':
            tdsapplicable = request.POST['tds_applicable']
            tdstype = request.POST['TDS_Type']
            
            if tdstype == 'Amount':
                tdsvalue = request.POST['TDS_Amount']
            elif tdstype == 'Percentage':
                tdsvalue = request.POST['TDS_Percentage']
            else:
                tdsvalue = 0
        elif request.POST['tds_applicable'] == 'No':
            tdsvalue = 0
            tdstype = ''
            tdsapplicable = request.POST['tds_applicable']
        else:
            tdsvalue = 0
            tdstype = ''
            tdsapplicable = ''

        incometax = request.POST['Income_Tax']
        aadhar = request.POST['Aadhar']
        uan = request.POST['UAN']
        pf = request.POST['PF']
        pan = request.POST['PAN']
        pr = request.POST['PR']

        if dob == '':
            age = 2
        else:
            dob2 = date.fromisoformat(dob)
            today = date.today()
            age = int(today.year - dob2.year - ((today.month, today.day) < (dob2.month, dob2.day)))
        
        sid = request.session['s_id']
        employee = Fin_Login_Details.objects.get(id=sid)
        
        if employee.User_Type == 'Company':
            companykey =  Fin_Company_Details.objects.get(Login_Id_id=sid)
        elif employee.User_Type == 'Staff':
            staffkey = Fin_Staff_Details.objects.get(Login_Id=sid)
            companykey = Fin_Company_Details.objects.get(id=staffkey.company_id_id)
        else:
            distributorkey = Fin_Distributors_Details.objects.get(login_Id=sid)
            companykey = Fin_Company_Details.objects.get(id=distributorkey.company_id_id)

        
        if Employee.objects.filter(employee_mail=email,mobile = contact,employee_number=employeenumber,company_id = companykey.id).exists():
            messages.error(request,'user exist')
            return redirect('Fin_editAttendance',mn,yr,pk)
        
        elif Employee.objects.filter(mobile = contact,company_id = companykey.id).exists():
            messages.error(request,'phone number exist')
            return redirect('Fin_editAttendance',mn,yr,pk)
        
        elif Employee.objects.filter(emergency_contact = emergencycontact,company_id = companykey.id).exists():
            messages.error(request,'emergency phone number exist')
            return redirect('Fin_editAttendance',mn,yr,pk)
        
        elif Employee.objects.filter(employee_mail=email,company_id = companykey.id).exists():
            messages.error(request,'email exist')
            return redirect('Fin_editAttendance',mn,yr,pk)
        
        elif Employee.objects.filter(employee_number=employeenumber,company_id = companykey.id).exists():
            messages.error(request,'employee id exist')
            return redirect('Fin_editAttendance',mn,yr,pk)
        
        elif incometax != '' and Employee.objects.filter(income_tax_number = incometax,company_id = companykey.id).exists():
            messages.error(request,'Income Tax Number exist')
            return redirect('Fin_editAttendance',mn,yr,pk)
        
        elif pf != '' and Employee.objects.filter(pf_account_number = pf,company_id = companykey.id).exists():
            messages.error(request,'PF account number exist')
            return redirect('Fin_editAttendance',mn,yr,pk)
        
        elif aadhar != '' and Employee.objects.filter(aadhar_number = aadhar,company_id = companykey.id).exists():
            messages.error(request,'Aadhar number exist')
            return redirect('Fin_editAttendance',mn,yr,pk)
        
        elif pan != '' and Employee.objects.filter(pan_number = pan,company_id = companykey.id).exists():
            messages.error(request,'PAN number exist')
            return redirect('Fin_editAttendance',mn,yr,pk)
        
        elif uan != '' and Employee.objects.filter(universal_account_number = uan,company_id = companykey.id).exists():
            messages.error(request,'Universal account number exist')
            return redirect('Fin_editAttendance',mn,yr,pk)
        
        elif pr != '' and Employee.objects.filter(pr_account_number = pr,company_id = companykey.id).exists():
            messages.error(request,'PR account number exist')
            return redirect('Fin_editAttendance',mn,yr,pk)
        
        elif bankdetails.lower() == 'yes':
            if accoutnumber != '' and Employee.objects.filter(account_number=accoutnumber,company_id = companykey.id).exists():
                messages.error(request,'Bank account number already exist')
                return redirect('Fin_editAttendance',mn,yr,pk)
            
            else:
                if employee.User_Type == 'Company':
                    

                    new = Employee(upload_image=image,title = title,first_name = firstname,last_name = lastname,alias = alias,
                            employee_mail = email,employee_number = employeenumber,employee_designation = designation,
                            employee_current_location = location,mobile = contact,date_of_joining = joiningdate,
                            employee_status = 'Active' ,company_id = companykey.id,login_id=sid,salary_amount = salaryamount ,
                            amount_per_hour = amountperhour ,total_working_hours = workinghour,gender = gender ,date_of_birth = dob ,
                            age = age,blood_group = blood,fathers_name_mothers_name = parent,spouse_name = spouse,
                            emergency_contact = emergencycontact,provide_bank_details = bankdetails,account_number = accoutnumber,
                            ifsc = ifsc,name_of_bank = bankname,branch_name = branchname,bank_transaction_type = transactiontype,
                            tds_applicable = tdsapplicable, tds_type = tdstype,percentage_amount = tdsvalue,pan_number = pan,
                            income_tax_number = incometax,aadhar_number = aadhar,universal_account_number = uan,pf_account_number = pf,
                            pr_account_number = pr,upload_file = file,employee_salary_type =salary_type,salary_effective_from=salarydate,
                            city=city,street=street,state=state,country=country,pincode=pincode,temporary_city=tempCity,
                            temporary_street=tempStreet,temporary_state=tempState,temporary_pincode=tempPincode,temporary_country=tempCountry)
                    new.save()

                    history = Employee_History(company_id = companykey.id,login_id=sid,employee_id = new.id,date = date.today(),action = 'Created')
                    history.save()
            
                elif employee.User_Type == 'Staff':
                    

                    new =  Employee(upload_image=image,title = title,first_name = firstname,last_name = lastname,alias = alias,
                                employee_mail = email,employee_number = employeenumber,employee_designation = designation,
                                employee_current_location = location,mobile = contact,date_of_joining = joiningdate,
                                employee_salary_type = salary_type,employee_status = 'Active' ,company_id = companykey.id,login_id=sid ,
                                amount_per_hour = amountperhour ,total_working_hours = workinghour,gender = gender ,date_of_birth = dob ,
                                age = age,blood_group = blood,fathers_name_mothers_name = parent,spouse_name = spouse,
                                emergency_contact = emergencycontact,provide_bank_details = bankdetails,account_number = accoutnumber,
                                ifsc = ifsc,name_of_bank = bankname,branch_name = branchname,bank_transaction_type = transactiontype,
                                tds_applicable = tdsapplicable, tds_type = tdstype,percentage_amount = tdsvalue,pan_number = pan,
                                income_tax_number = incometax,aadhar_number = aadhar,universal_account_number = uan,pf_account_number = pf,
                                pr_account_number = pr,upload_file = file,salary_amount = salaryamount,salary_effective_from=salarydate,
                                city=city,street=street,state=state,country=country,pincode=pincode,temporary_city=tempCity,
                                temporary_street=tempStreet,temporary_state=tempState,temporary_pincode=tempPincode,temporary_country=tempCountry)
                    
                    new.save()

                    history = Employee_History(company_id = companykey.id,login_id=sid,employee_id = new.id,date = date.today(),action = 'Created')
                    history.save()
        
        else:
            if employee.User_Type == 'Company':
                

                new = Employee(upload_image=image,title = title,first_name = firstname,last_name = lastname,alias = alias,
                        employee_mail = email,employee_number = employeenumber,employee_designation = designation,
                        employee_current_location = location,mobile = contact,date_of_joining = joiningdate,
                        employee_status = 'Active' ,company_id = companykey.id,login_id=sid,salary_amount = salaryamount ,
                        amount_per_hour = amountperhour ,total_working_hours = workinghour,gender = gender ,date_of_birth = dob ,
                        age = age,blood_group = blood,fathers_name_mothers_name = parent,spouse_name = spouse,
                        emergency_contact = emergencycontact,provide_bank_details = bankdetails,account_number = accoutnumber,
                        ifsc = ifsc,name_of_bank = bankname,branch_name = branchname,bank_transaction_type = transactiontype,
                        tds_applicable = tdsapplicable, tds_type = tdstype,percentage_amount = tdsvalue,pan_number = pan,
                        income_tax_number = incometax,aadhar_number = aadhar,universal_account_number = uan,pf_account_number = pf,
                        pr_account_number = pr,upload_file = file,employee_salary_type =salary_type,salary_effective_from=salarydate,
                        city=city,street=street,state=state,country=country,pincode=pincode,temporary_city=tempCity,
                        temporary_street=tempStreet,temporary_state=tempState,temporary_pincode=tempPincode,temporary_country=tempCountry)
                new.save()

                history = Employee_History(company_id = companykey.id,login_id=sid,employee_id = new.id,date = date.today(),action = 'Created')
                history.save()
        
            elif employee.User_Type == 'Staff':
                

                new =  Employee(upload_image=image,title = title,first_name = firstname,last_name = lastname,alias = alias,
                            employee_mail = email,employee_number = employeenumber,employee_designation = designation,
                            employee_current_location = location,mobile = contact,date_of_joining = joiningdate,
                            employee_salary_type = salary_type,employee_status = 'Active' ,company_id = companykey.id,login_id=sid ,
                            amount_per_hour = amountperhour ,total_working_hours = workinghour,gender = gender ,date_of_birth = dob ,
                            age = age,blood_group = blood,fathers_name_mothers_name = parent,spouse_name = spouse,
                            emergency_contact = emergencycontact,provide_bank_details = bankdetails,account_number = accoutnumber,
                            ifsc = ifsc,name_of_bank = bankname,branch_name = branchname,bank_transaction_type = transactiontype,
                            tds_applicable = tdsapplicable, tds_type = tdstype,percentage_amount = tdsvalue,pan_number = pan,
                            income_tax_number = incometax,aadhar_number = aadhar,universal_account_number = uan,pf_account_number = pf,
                            pr_account_number = pr,upload_file = file,salary_amount = salaryamount,salary_effective_from=salarydate,
                            city=city,street=street,state=state,country=country,pincode=pincode,temporary_city=tempCity,
                            temporary_street=tempStreet,temporary_state=tempState,temporary_pincode=tempPincode,temporary_country=tempCountry)
                
                new.save()

                history = Employee_History(company_id = companykey.id,login_id=sid,employee_id = new.id,date = date.today(),action = 'Created')
                history.save()

        sid = request.session['s_id']
        loginn = Fin_Login_Details.objects.get(id=sid)
        if loginn.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = sid)
            allmodules = Fin_Modules_List.objects.get(company_id = com.id)
            employee = Employee.objects.filter(company_id=com.id)
            
        elif loginn.User_Type == 'Staff' :
            com = Fin_Staff_Details.objects.get(Login_Id = sid)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id_id)
            employee = Employee.objects.filter(company_id=com.company_id_id)
        return redirect('Fin_editAttendance',mn,yr,pk)
    

def Fin_deleteAttendance(request,id,mn,yr,pk):
    month_name = mn
    year = yr
    leave = Fin_Attendances.objects.get(id = id)
    leave.delete()
    return redirect('Fin_Attendanceview',month_name,year,pk)


def Fin_attendance_history(request):
    hid = request.GET.get('hid')
    
    if 's_id' in request.session:
        s_id = request.session['s_id']
        log = Fin_Login_Details.objects.get(id = s_id)
        if log.User_Type == 'Staff':
            staff =Fin_Staff_Details.objects.get(Login_Id =log)
            exists = Fin_Attendance_history.objects.filter(company = staff.company_id,attendance = hid)
            data = [{'action': item.action, 'date': item.date, 'first_name': item.login_id.First_name, 'last_name': item.login_id.Last_name} for item in exists]
        if log.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = log)
            exists = Fin_Attendance_history.objects.filter(company = com.id,attendance = hid)
            data = [{'action': item.action, 'date': item.date, 'first_name': item.login_id.First_name, 'last_name': item.login_id.Last_name} for item in exists]

        return JsonResponse({'data': data})
    
def Fin_addcommentstoleave(request,id,mn,yr,pk):
    month_name = mn
    year = yr
    data = Fin_Attendances.objects.get(id=id)
    if 's_id' in request.session:
        if request.method == 'POST':
            s_id = request.session['s_id']
            log = Fin_Login_Details.objects.get(id = s_id)
            if log.User_Type == 'Staff':
                staff =Fin_Staff_Details.objects.get(Login_Id =log)
                comment = Fin_attendance_comment(company = staff.company_id, login_id = log, attendance = data, comment = request.POST['comment'])
                comment.save()
            if log.User_Type == 'Company':
                com = Fin_Company_Details.objects.get(Login_Id = log)
                comment = Fin_attendance_comment(company = com, login_id = log, attendance = data, comment = request.POST['comment'])
                comment.save()
            return redirect('Fin_Attendanceview',month_name,year,pk)
        return redirect('Fin_Attendanceview',month_name,year,pk)


def Fin_attendancecomments(request):
    hid = request.GET.get('hid')
    
    if 's_id' in request.session:
        s_id = request.session['s_id']
        log = Fin_Login_Details.objects.get(id = s_id)
        if log.User_Type == 'Staff':
            staff =Fin_Staff_Details.objects.get(Login_Id =log)
            exists = Fin_attendance_comment.objects.filter(company = staff.company_id,attendance = hid)
            data = [{'action': item.comment} for item in exists]
        if log.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = log)
            exists = Fin_attendance_comment.objects.filter(company = com.id,attendance = hid)
            data = [{'action': item.comment} for item in exists]
        return JsonResponse({'data': data})


def Fin_shareLeaveStatementToEmail(request,id,mn,yr):
    if 's_id' in request.session:
      
        if request.method == 'POST':
            emails_string = request.POST['email_ids']

            # Split the string by commas and remove any leading or trailing whitespace
            emails_list = [email.strip() for email in emails_string.split(',')]
            email_message = request.POST['email_message']
            # print(emails_list)
            month_name = mn
            months = list(calendar.month_name).index(month_name) 

            year = yr
            s_id = request.session['s_id']
            log = Fin_Login_Details.objects.get(id = s_id)
            emp = Employee.objects.get(id =id)

            if log.User_Type == 'Staff':
                staff =Fin_Staff_Details.objects.get(Login_Id =log)
                att = Fin_Attendances.objects.filter(employee = id,company = staff.company_id,start_date__month=months,start_date__year =year)
                context = {'att': att, 'emp': emp ,'month_name':month_name, 'year':year}
            if log.User_Type == 'Company':
                com = Fin_Company_Details.objects.get(Login_Id = log)
                att = Fin_Attendances.objects.filter(employee = id,company = com.id,start_date__month=months,start_date__year =year)
                context = {'att': att, 'emp': emp,'month_name':month_name, 'year':year}
            template_path = 'company/FIn_LeaveTransaction.html'
            template = get_template(template_path)

            html  = template.render(context)
            result = BytesIO()
            pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)#, link_callback=fetch_resources)
            pdf = result.getvalue()
            filename = f'Leave Statement - {emp.first_name} {emp.last_name}-{month_name},{year}.pdf'
            subject = f"Leave Statement - {emp.first_name} {emp.last_name}-{month_name},{year}"
            email = EmailMessage(subject, f"Hi,\nPlease find the attached Leave Statement - of-{emp.first_name} {emp.last_name}. \n{email_message}", from_email=settings.EMAIL_HOST_USER,to=emails_list)
            email.attach(filename, pdf, "application/pdf")
            email.send(fail_silently=False)

            msg = messages.success(request, 'Bill has been shared via email successfully..!')
            return redirect('Fin_Attendanceview',month_name,year,id)
        
def employee_blood_group(request):
    if request.method == 'POST':
        bloodGroup = request.POST.get('bloodGroup', '').upper()
        sid = request.session.get('s_id')
        loginn = Fin_Login_Details.objects.get(id=sid)
        invalid_group = ['A+', 'A-', 'B+', 'O+']

        if loginn.User_Type == 'Company' and bloodGroup not in invalid_group:
            com = Fin_Company_Details.objects.get(Login_Id=sid)
            
            allmodules = Fin_Modules_List.objects.get(company_id=com.id)
            group = Employee_Blood_Group(blood_group=bloodGroup, company_id=com.id, login_id=sid)
            group.save()
            bloodgroup = Employee_Blood_Group.objects.filter(company_id=com.id,login_id=sid).values('blood_group').distinct()
            return JsonResponse({'success': True,'bloodgroup': list(bloodgroup)})

        elif loginn.User_Type == 'Staff' and bloodGroup not in invalid_group:
            com = Fin_Staff_Details.objects.get(Login_Id = sid)
            allmodules = Fin_Modules_List.objects.get(company_id=com.company_id)
            group = Employee_Blood_Group(blood_group=bloodGroup, company_id=com.company_id, login_id=sid)
            group.save()
            bloodgroup = Employee_Blood_Group.objects.filter(company_id=com.company_id,login_id=sid).values('blood_group').distinct()
            return JsonResponse({'success': True,'bloodgroup': list(bloodgroup)})

    return JsonResponse({'success': False, 'error': 'Invalid blood group or user type'})