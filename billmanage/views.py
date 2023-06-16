from django.core import paginator
from django.db import models
from django.http import request,HttpResponseRedirect
from django.http.response import HttpResponse
from django.shortcuts import render,redirect
from .models import bill, item
from django.db.models import Count

from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.models import  User
from django.contrib.auth.decorators import login_required

import math
# Create your views here.
from django.core.paginator import Paginator, EmptyPage,PageNotAnInteger


@login_required(login_url ='/')
def dashboard(request):
    return render(request, 'billmanage/dashboard.html')

def loginview(request):
    user =request.user
    if user.is_authenticated:
        return redirect("dashboard")

    if request.method =="POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
    return render(request,'billmanage/login.html') 


def logout_view(request):
    logout(request)

    # Redirect to a success page.


# @login_required(login_url ='/')
def addbill(request):
    billno = bill.objects.count() + 1
    return render(request, 'billmanage/addbill.html', {'billno': billno})


# @login_required(login_url ='/')
def addbill_submitted(request):
    if request.method == "POST":
        amount = []
        amountwithtax = []
        total = 0
        grandtotal = 0
        # gst =int(request.POST['CGST'])+int(request.POST['SGST'])
        gst =int(request.POST['CGST'])
        rate = request.POST.getlist('rate[]',False)
        qty = request.POST.getlist('qty[]',False)
        itname = request.POST.getlist('ItemName[]',False)
        hsn = request.POST.getlist('hsn[]',False)
        delivery =request.POST.get('delivery')
        notice =request.POST.get('notice')
        email =request.POST.get('email')
        phone =request.POST.get('phone')

        try:
            invoice_type = request.POST['invoice_type']
        except KeyError:
            # Handle the case when invoice_type is not present in request.POST
            # You can show an error message, redirect the user, or take any other appropriate action
            return HttpResponse('Invoice type is missing')

        # Map the invoice types to their display names
        invoice_type_mapping = {
            'quotation': 'Quotation',
            'proforma': 'Proforma Invoice',
            'sales': 'Sales Invoice',
        }

        # Get the display name for the selected invoice type
        invoice_type_display = invoice_type_mapping.get(invoice_type, 'Invoice')


        # hsn = request.POST.getlist('hsn[]',False)
        for i in range(len(rate)):
            amt = int(rate[i])*int(qty[i])
            total += amt
            gmt = amt+(amt*gst/100)
            grandtotal += gmt
            amount.append(amt)
            amountwithtax.append(gmt)
        billno = bill.objects.count() + 1

        newbill = bill( 
            invoice_type=invoice_type_display,  # Use the display name instead of the raw value   
            notice=notice,
            #delivery = delivery,
            email=email,
            phone=phone,
            billno = billno,
            recipient = request.POST['rname'],
            address = request.POST['address'],
            delivery = request.POST.get('delivery', ''),
            #hsncode = request.POST.get('hsncode[]', ''),
            date = request.POST.get('date', ''),
            # GSTno = request.POST['gst'],
            cgst = int(request.POST['CGST']),
            # sgst = int(request.POST['SGST']),
            total = total,
            grandtotal = grandtotal,
        )
        newbill.save()

        print(len(rate))
       
        for i in range(len(rate)):
            newitem = item( 
                itemname = itname[i],
                #hsncode = hsn[i],
                qty = qty[i],
                rate = rate[i],
                amount = amount[i],
                billno = bill.objects.get(billno=billno), 
            )
            newitem.save()
        return invoice(request, billno)
    else:
        return render(request, 'billmanage/addbill.html')


# @login_required(login_url ='/')
def records(request):
    if request.method=='POST':
        startingdate = request.POST['start']
        enddate = request.POST['end']
        if startingdate and enddate:
            
            billobj = bill.objects.filter(date__range=[startingdate, enddate])
        else:
            
            billobj = bill.objects.all()
    else:
        billobj = bill.objects.all()
    paginator = Paginator(billobj, 10)
    page_number = request.GET.get('page')
    try:
        bills = paginator.page(page_number)
    except PageNotAnInteger:
        bills = paginator.page(1)
    except EmptyPage:
        bills = paginator.page(paginator.num_pages)
    return render(request, 'billmanage/records.html', {'bills': bills})



# @login_required(login_url ='/')
def invoice(request, billno):
    billobj = bill.objects.get(billno=billno)
    itemobj = item.objects.filter(billno=billno)
    amount = billobj.grandtotal
    amountwithouttax = billobj.total
    amount = float(amount)
    amountwithouttax = float(amountwithouttax)
    gst = round((amount - amountwithouttax), 2)
    rs = num2words(int(str(amount).split(".")[0]))
    if (int(str(amount).split(".")[1])>0):
        paisa = num2words(int(str(amount).split(".")[1]))
    else:
        paisa = False
    return render(request, 'billmanage/newinvoice.html', {'bill': billobj, 'items': itemobj, 'rs': rs, 'paisa': paisa, 'gst': gst, 'range':6})



# @login_required(login_url ='/')
# @login_required(login_url='/login/')
def delete(request, billno):
    deletebill = bill.objects.get(billno=billno)
    deletebill.delete()
    return records(request)



# @login_required(login_url ='/')
# @login_required(login_url='/login/')
def num2words(num):
    under_20 = ['Zero','One','Two','Three','Four','Five','Six','Seven','Eight','Nine','Ten','Eleven','Twelve','Thirteen','Fourteen','Fifteen','Sixteen','Seventeen','Eighteen','Nineteen']
    tens = ['Twenty','Thirty','Forty','Fifty','Sixty','Seventy','Eighty','Ninety']
    above_100 = {100: 'Hundred',1000:'Thousand', 100000:'Lakhs', 10000000:'Crores'}

    if num < 20:
         return under_20[(int)(num)]

    if num < 100:
        return tens[(int)(num/10)-2] + ('' if num%10==0 else ' ' + under_20[(int)(num%10)])

    # find the appropriate pivot - 'Million' in 3,603,550, or 'Thousand' in 603,550
    pivot = max([key for key in above_100.keys() if key <= num])

    return num2words((int)(num/pivot)) + ' ' + above_100[pivot] + ('' if num%pivot==0 else ' ' + num2words(num%pivot))
