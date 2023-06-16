from datetime import datetime, timedelta
from django.utils import timezone
from datetime import date
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, FloatField, F, IntegerField, Avg
from django.db.models.functions import Coalesce
from django.shortcuts import render
from products.models import Product, Category
from sales.models import Sale, SaleDetail
import json


@login_required(login_url="/accounts/login/")
def index(request):
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)
    year = today.year
    month = today.month

    monthly_earnings = []
    monthly_sales = []
    current_month_profit = 0.0

    products = Product.objects.all().order_by('-date')
    grand_product_total =  grand_product_total = products.aggregate(total=Sum('quantity'))['total']
    grand_total_amount = products.aggregate(total_amount_sum=Sum('total_amount'))['total_amount_sum'] or 0


    # Calculate overall profit
    overall_profit = Product.objects.annotate(
        profit=(F('price') - F('buying_price')) * F('quantity')
    ).aggregate(total_profit=Sum('profit'))['total_profit']


     # Calculate daily profit before sales
    start_date = today - timedelta(days=1)
    daily_profit_before_sales = Product.objects.filter(date__date=today).aggregate(total_profit=Sum((F('price') - F('buying_price')) * F('quantity')))['total_profit']
    

    # Calculate weekly profit before sales
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    weekly_profit_before_sales = Product.objects.filter(date__date__range=[start_of_week, end_of_week]).aggregate(total_profit=Sum((F('price') - F('buying_price')) * F('quantity')))['total_profit']
    

    # Calculate monthly profit before sales
    start_of_month = date(today.year, today.month, 1)
    end_of_month = date(today.year, today.month, 1) + timedelta(days=32)
    monthly_profit_before_sales = Product.objects.filter(date__date__range=[start_of_month, end_of_month]).aggregate(total_profit=Sum((F('price') - F('buying_price')) * F('quantity')))['total_profit']
    


    # Calculate sales count for the current month
    current_month_sales = Sale.objects.filter(date__year=year, date__month=month)
    monthly_sales.append(current_month_sales.count())

    # Calculate earnings and profits for the current month
    sales = current_month_sales
    earning = sales.aggregate(total_variable=Coalesce(Sum(F('grand_total')), 0.0, output_field=FloatField())).get('total_variable')
    buying_price = sales.aggregate(total_variable=Coalesce(Sum(F('saledetail__product__buying_price') * F('saledetail__quantity')), 0.0, output_field=FloatField())).get('total_variable')
    current_month_profit = earning - buying_price

    # Calculate earnings and profits per month
    for m in range(1, 13):
        sales = Sale.objects.filter(date__year=year, date__month=m)
        earning = sales.aggregate(total_variable=Coalesce(Sum(F('grand_total')), 0.0, output_field=FloatField())).get('total_variable')
        buying_price = sales.aggregate(total_variable=Coalesce(Sum(F('saledetail__product__buying_price') * F('saledetail__quantity')), 0.0, output_field=FloatField())).get('total_variable')
        profit = earning - buying_price  # Calculate the profit
        monthly_earnings.append({
            'earning': earning,
            'profit': profit,
        })
        if m != month:
            monthly_sales.append(0)
        else:
            monthly_sales.append(current_month_sales.count())

    # Calculate annual earnings and profit
    sales = Sale.objects.filter(date__year=year)
    annual_earnings = sales.aggregate(total_variable=Coalesce(Sum(F('grand_total')), 0.0, output_field=FloatField())).get('total_variable')
    annual_buying_price = sales.aggregate(total_variable=Coalesce(Sum(F('saledetail__product__buying_price') * F('saledetail__quantity')), 0.0, output_field=FloatField())).get('total_variable')
    annual_profit = annual_earnings - annual_buying_price
    annual_earnings = format(annual_earnings, '.2f')
    annual_profit = format(annual_profit, '.2f')

    # Calculate daily and weekly sales
    seven_days_ago = today - timedelta(days=7)
    today_sales = Sale.objects.filter(date=today).count()
    weekly_sales = Sale.objects.filter(date__range=[seven_days_ago, today]).count()

    # Calculate average earnings per month (continued)
    avg_month = Sale.objects.filter(date__year=year).aggregate(
        avg_variable=Coalesce(Avg(F('grand_total')), 0.0, output_field=FloatField())).get('avg_variable')
    avg_month = format(avg_month, '.2f')


    # Top selling products
    top_products = Product.objects.annotate(quantity_sum=Sum(
        'saledetail__quantity')).order_by('-quantity_sum')[:3]

    top_products_names = []
    top_products_quantity = []

    for p in top_products:
        top_products_names.append(p.name)
        top_products_quantity.append(p.quantity_sum)

    # Calculate daily sales and profits
    today_sales = Sale.objects.filter(date__date=today).aggregate(
        total_sales=Coalesce(Sum(F('grand_total')), 0.0, output_field=FloatField())).get('total_sales')
    daily_profit = SaleDetail.objects.filter(sale__date__date=today).aggregate(
        total_profits=Coalesce(Sum(F('profit')), 0.0, output_field=FloatField())).get('total_profits')
    today_sales = format(today_sales, '.2f')
    daily_profit = format(daily_profit, '.2f')

    # Calculate weekly sales and profits
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    current_month_sales = Sale.objects.filter(date__month=today.month)
   
    weekly_sales = current_month_sales.filter(date__date__range=[start_of_week, end_of_week])
    weekly_sales_total = weekly_sales.aggregate(total_sales=Coalesce(Sum('grand_total'), 0.0))['total_sales']
    
    weekly_sale_details = SaleDetail.objects.filter(sale__in=weekly_sales)
    weekly_profits = weekly_sale_details.aggregate(
        total_profits=Coalesce(Sum(F('profit')), 0.0, output_field=FloatField())).get('total_profits')
    weekly_profits = format(weekly_profits, '.2f')

    monthly_sales = current_month_sales.aggregate(total_sales=Coalesce(Sum('grand_total'), 0.0))['total_sales']
    

    context = {
        "active_icon": "dashboard",
        "products": Product.objects.all().count(),
        "categories": Category.objects.all().count(),
        "annual_earnings": annual_earnings,
        "annual_profit": annual_profit,
        "monthly_earnings": json.dumps(monthly_earnings),
        "monthly_sales": monthly_sales,
        "monthly_profits": current_month_profit,  # Display only the current month profit
        "avg_month": avg_month,
        "top_products_names": json.dumps(top_products_names),
        "top_products_names_list": top_products_names,
        "top_products_quantity": json.dumps(top_products_quantity),
        "today_sales": today_sales,
        "weekly_sales": weekly_sales_total,
        "weekly_profits": weekly_profits,
        'sales': sales,
        'daily_profit': daily_profit,
        'daily_profit_before_sales': daily_profit_before_sales,
        'weekly_profit_before_sales': weekly_profit_before_sales,
        'monthly_profit_before_sales': monthly_profit_before_sales,
        'overall_profit': overall_profit or 0 ,
        "products": products,
        "grand_product_total": grand_product_total,
        "grand_total_amount": grand_total_amount,
    }

    return render(request, "pos/index.html", context)
