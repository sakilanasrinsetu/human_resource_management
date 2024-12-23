import os
import random
import string
import time
from django.utils.text import slugify
import re


def random_string_generator(size=4, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def random_number_generator(size=4, chars='1234567890'):
    return ''.join(random.choice(chars) for _ in range(size))


# def unique_slug_generator():
#     timestamp_m = time.strftime("%Y")
#     timestamp_d = time.strftime("%m")
#     timestamp_y = time.strftime("%d")
#     timestamp_now = time.strftime("%H%M%S")
#     random_str = random_string_generator()
#     random_num = random_number_generator()
#     bindings = (
#         random_str + timestamp_d + random_num + timestamp_now +
#         timestamp_y + random_num + timestamp_m
#     )
#     return bindings

def unique_slug_generator(name):
    timestamp_m = time.strftime("%Y")
    timestamp_d = time.strftime("%m")
    timestamp_y = time.strftime("%d")
    timestamp_now = time.strftime("%H%M%S")
    random_str = random_string_generator()
    random_num = random_number_generator() 
    bindings = f"{random_str}-{timestamp_d}-{random_num}-{timestamp_now}-{timestamp_y}-{random_num}-{timestamp_m}"
    
    slug = bindings
    if name:
        cleaned_name = re.sub(r'[^a-zA-Z0-9\s]', '', name) 
        
        converted_name = cleaned_name.lower().replace(' ', '-')
        slug = f"{converted_name}-{bindings}" 
    return slug


def unique_slug_generator_for_product_category(name):
    if name:
        # Remove non-alphanumeric characters except spaces
        cleaned_name = re.sub(r'[^a-zA-Z0-9\s]', '', name)
        # Convert to lowercase and replace spaces with hyphens
        converted_name = cleaned_name.lower().replace(' ', '-')
        slug = f"{converted_name}"
    else:
        slug = ""
        
    return slug

def generate_requisition_no(last_requisition_no):
    prefix = 'REG000'
    last_requisition_no = last_requisition_no.replace('REG000', '')
    if len(last_requisition_no) < 9:
        random_num = random.randint(10000, 99999)
    else:
        random_num = last_requisition_no
    
    random_num = int(random_num)+1
    new_requisition_no = f"{prefix}{random_num}"
    
    return new_requisition_no

def generate_invoice_no(last_invoice_no):
    prefix = 'ONL00'
    last_invoice_no = last_invoice_no.replace('ONL00', '')
    
    if len(last_invoice_no) < 9:
        random_num = random.randint(1000000, 9999999)
    else:
        random_num = last_invoice_no
    
    random_num = int(random_num) + 1
    new_invoice_no = f"{prefix}{random_num}"
    
    return new_invoice_no

def generate_service_invoice_no(last_invoice_no):
    prefix = 'SER00'
    last_invoice_no = last_invoice_no.replace('SER00', '')
    
    if len(last_invoice_no) < 10:
        random_num = random.randint(1000000, 9999999)
    else:
        random_num = last_invoice_no
    
    random_num = int(random_num) + 1
    new_invoice_no = f"{prefix}{random_num}"
    
    return new_invoice_no


def generate_transaction_number(last_transaction_no):
    prefix = 'OSL'
    
    # Remove any prefix like 'OSL00' from last_transaction_no
    last_transaction_no = last_transaction_no.replace('OSL00', '')
    
    # Check if the remaining string is shorter than 7 characters
    if len(last_transaction_no) < 10:
        random_num = random.randint(1000000, 9999999)
    else:
        try:
            random_num = int(last_transaction_no)
        except ValueError:
            random_num = random.randint(1000000, 9999999)
    
    random_num += 1
    new_invoice_no = f"{prefix}{random_num}"
    
    return new_invoice_no




# def generate_transaction_number(last_transaction_no):
#     prefix = 'OSL'
#     last_transaction_no = last_transaction_no.replace('OSL00', '')
    
#     if len(last_transaction_no) < 10:
#         random_num = random.randint(1000000, 9999999)
#     else:
#         random_num = last_transaction_no
    
#     random_num = int(random_num) + 1
#     new_invoice_no = f"{prefix}{random_num}"
    
#     return new_invoice_no

def generate_task_no(task_no):
    prefix = 'TASK000'
    task_no = task_no.replace('TASK000', '')
    if len(task_no) < 9:
        random_num = random.randint(10000, 99999)
    else:
        random_num = task_no
    
    random_num = int(random_num)+1
    new_task_no = f"{prefix}{random_num}"
    
    return new_task_no
