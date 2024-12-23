import random
import re
import time
from typing import List, Callable
import uuid
import datetime
from io import BytesIO
from django.conf import settings
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.db.models import Lookup
from django.apps import apps

from gporjukti_backend_v2.settings import BASE_URL
from human_resource_management.models.employee import EmployeeInformation
from location.models import OfficeLocation
from product_management.models.product import Product, ProductAttributeValue
from user.models import UserInformation
from utils.calculate import offer_check
from django.db.models import Q

import aiohttp
import asyncio


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return result.getvalue()
    return None

def parent_product_attribute_value_list(product, product_attribute_list):
    product_attribute_values = []

    product_attribute_qs = product_attribute_list

    if product_attribute_qs:
        for product_attribute in product_attribute_qs:
            attribute_values = []

            product_attribute_value_qs = ProductAttributeValue.objects.filter(
                Q(product_attribute=product_attribute, products__slug=product.slug) |
                Q(product_attribute=product_attribute, products__product_parent__slug=product.slug)
            ).distinct('value')

            for product_attribute_value in product_attribute_value_qs:
                attribute_values.append({
                    "id": product_attribute_value.id,
                    "slug": product_attribute_value.slug,
                    "value": product_attribute_value.value,
                })

            product_attribute_values.append({
                "id": product_attribute.id,
                "name": product_attribute.name,
                "slug": product_attribute.slug,
                "attribute_values": attribute_values,
            })

    return product_attribute_values


def product_attribute_value_list(product, product_attribute_list):
    product_attribute_value = []
    
    attribute_value = None
    
    product_attribute_qs = product_attribute_list
    
    if product_attribute_qs:
        for product_attribute in product_attribute_qs:
            
            product_attribute_value_qs = ProductAttributeValue.objects.filter(
                Q(product_attribute = product_attribute, products__slug = product.slug)
                | Q(product_attribute = product_attribute, products__product_parent__slug = product.slug)
                ).last()
            
            if product_attribute_value_qs:
                attribute_value = {
                    "id": product_attribute_value_qs.id,
                    "slug": product_attribute_value_qs.slug,
                    "value": product_attribute_value_qs.value,
                }
                
            product_attribute_value.append({
                "id": product_attribute.id,
                "name": product_attribute.name,
                "slug": product_attribute.slug,
                
                "attribute_value": attribute_value,
                
                
            })
    
    return product_attribute_value

def product_image(product):
    image_url = settings.NOT_FOUND_IMAGE
        
    image_list = product.images
    
    if product.images:
        # image_url = random.choice(product.images)
        # print(f"First Image = {image_list[0]}")
        
        # image_url = random.choice(image_list)
        image_url = image_list[0]
        
    return image_url

def product_price_details(product, product_price_type):
    context = {}
        
    msp = 0.0
    mrp = 0.0
    discount_amount = 0.0
    after_discount_price = mrp
    tax_amount = 0.0
    tax_value = 0.0
    gsheba_amount = 0.0
    advance_amount = 0.0
    tax_value_title = None
    discount_title = None
    promo_code_discount_title = "-"
    promo_code_discount_amount = 0.0
    
    if product.is_out_of_stock:
        context['is_out_of_stock'] = True
        return context
    
    # if product.status in ["STANDALONE", "PARENT"]:
    
    product_variant_qs = Product.objects.filter(
        product_parent = product, status__in = ["CHILD", "CHILD_OF_CHILD"]
    ).last()
    
    
    if product_variant_qs:
        product = product_variant_qs
    
    price_qs = product.product_price_infos.filter(product_price_type=product_price_type).last()
    
    if price_qs:
        msp = price_qs.msp
        mrp = price_qs.mrp
        gsheba_amount = price_qs.gsheba_amount
        advance_amount = price_qs.advance_amount
        
        discount_qs = price_qs.discount
        promo_code_qs = price_qs.promo_code
        
        
        if discount_qs:
            discount = offer_check(discount_qs)
            discount_status = discount.get('valid_status')
            discount_amount = discount.get('discount_value')
            
            if discount_status == 'Active':
                if discount_qs.amount_type == 'FLAT':
                    discount_amount = discount_qs.discount_amount
                else:
                    discount_amount = round(((mrp * discount_qs.discount_amount) / 100), 2)
                
                discount_title = discount_qs.name
                
        if promo_code_qs:
            discount = offer_check(promo_code_qs)
            discount_status = discount.get('valid_status')
            discount_amount = discount.get('discount_value')
            
            if discount_status == 'Active':
                if promo_code_qs.amount_type == 'FLAT':
                    promo_code_discount_amount = promo_code_qs.discount_amount
                else:
                    promo_code_discount_amount = round(((mrp * promo_code_qs.discount_amount) / 100), 2)
                
                promo_code_discount_title = promo_code_qs.promo_code
        
        after_discount_price = mrp - discount_amount
        
        if product.selling_tax_category:
            tax_value = product.selling_tax_category.value_in_percentage
            
            tax_amount = (after_discount_price * tax_value) / 100
            tax_value_title = product.selling_tax_category.name
    
    if after_discount_price > mrp:
        after_discount_price = 0.0
        discount_amount = 0.0
        discount_title = None
        
    if msp > mrp and product_price_type == 'POINT_OF_SELL':
        msp = mrp
        
    if product_price_type == 'POINT_OF_SELL':
        advance_amount = msp
        after_discount_price = mrp
        
    
    if product_price_type == 'ECOMMERCE' and mrp < 1:
        context['is_out_of_stock'] = True
        return context 
    
    if product_price_type == 'ECOMMERCE' and mrp < 1:
        context['is_out_of_stock'] = True
        return context 
    
    if product_price_type == 'ECOMMERCE':
        advance_amount = abs(price_qs.advance_amount)
    
    context = {
        'msp': int(msp),
        'mrp': int(mrp),
        'gsheba_amount': int(gsheba_amount),
        'after_discount_price': int(after_discount_price),
        'discount_amount': int(discount_amount),
        'discount_title': discount_title,
        'tax_amount': int(tax_amount),
        'advance_amount': int(advance_amount),
        'tax_value': int(tax_value),
        'tax_value_title': tax_value_title,
        'promo_code_discount_amount': int(promo_code_discount_amount),
        'promo_code': promo_code_discount_title,
    }
            
    return context


def get_user_store_list(request_user):
    store_list_qs = OfficeLocation.objects.all().order_by('name')
    
    user_information_qs = UserInformation.objects.filter(user__email = request_user.email).last()
    
    employee_qs = EmployeeInformation.objects.filter(user__email = request_user.email).last()
    
    
    if request_user.is_superuser == True:
        qs = store_list_qs
    elif user_information_qs.user_type.name == 'Shop':
        qs = store_list_qs.filter(employee_informations__work_station__slug = employee_qs.work_station.slug).distinct()

    elif user_information_qs.user_type.name == 'Shop User':
        qs = store_list_qs.filter(employee_informations__work_station__slug = employee_qs.work_station.slug).distinct()
        
    elif employee_qs.pos_reason:
        qs = store_list_qs.filter(pos_region_name = employee_qs.pos_reason.name, is_active = True).distinct()
        
    elif employee_qs.pos_area:
        qs = store_list_qs.filter(pos_area_name = employee_qs.pos_area.name, is_active = True).distinct()
        
    elif employee_qs.work_station.name == "GProjukti.com - Warehouse":
        qs = store_list_qs.filter(employee_informations__work_station__slug = employee_qs.work_station.slug).distinct()
        
    else:
        qs = store_list_qs
 
    return qs

