from base.models import PaymentType
from discount.models import Discount, PromoCode
from django.utils import timezone
from datetime import timedelta
from gporjukti_backend_v2.settings import TODAY

from human_resource_management.models.employee import EmployeeInformation
from location.models import OfficeLocation
from location.serializers import OfficeLocationSerializer
from order.models import Order, OrderItem, OrderItemStatusLog, OrderItemWarrantyLog, OrderPaymentLog, OrderStatusLog, ServicingOrder, ServicingOrderItem
# from order.serializers import OrderItemListSerializer
from product_management.models.product import Product, ProductStock, ProductStockLog, ShopWiseZeroStockLog
# from product_management.utils import barcode_status_log
from user.models import UserInformation
from user.serializers import BaseSerializer
from utils.generates import unique_slug_generator
from utils.response_wrapper import ResponseWrapper
from django.db.models import Q

from typing import Dict
import logging

from django.conf import settings

import requests

from user.models import User

logger = logging.getLogger('django')




def offer_check(obj):
    context = {}
    
    schedule_type = obj.schedule_type
    valid_from_str = None
    valid_to_str = None
    discount_value = 0.0
    
    valid_status = 'Active'
    
    today = timezone.now() + timedelta(hours=6)
    current_time = today.time()
    
    if obj.is_for_lifetime:
        schedule_type_display = 'Date Wise'
        
        context = {
            'schedule_type' : obj.schedule_type,
            'schedule_type_display' : schedule_type_display,
            'valid_from' : valid_from_str,
            'valid_to' : valid_to_str,
            'valid_status' : valid_status,
            'discount_value' : discount_value,
        }
    
    elif schedule_type == 'DATE_WISE':
        schedule_type = schedule_type
        schedule_type_display = 'Date Wise'
        
        valid_from = obj.start_date + timedelta(hours=6)
        if obj.end_date:
            end_date = obj.end_date
        else:
            end_date = timezone.now()
            
        valid_to = end_date + timedelta(hours=6)
        
        if valid_from:
            valid_from_str = valid_from.strftime("%b %d, %Y at %I:%M %p")
        if valid_to:
            valid_to_str = valid_to.strftime("%b %d, %Y at %I:%M %p")
        
        if valid_from <= today <= valid_to:
            valid_status = valid_status
            
        elif today <= valid_from:
            valid_status = 'Upcoming'
            
        elif valid_to <= today:
            valid_status = 'Inactive'
        
    elif schedule_type == 'TIME_WISE':
        schedule_type = schedule_type
        schedule_type_display = 'Time Wise'
        
        valid_from = obj.start_time 
        valid_to = obj.end_time 
        
        if valid_from:
            valid_from_str = valid_from.strftime("%I:%M %p")
        if valid_to:
            valid_to_str = valid_to.strftime("%I:%M %p")
            
        if valid_from and valid_to:
            if valid_from <= current_time <= valid_to:
                valid_status = valid_status
                
            elif current_time <= valid_from:
                valid_status = 'Upcoming'
                
            elif valid_to <= current_time:
                valid_status = 'Inactive'

    if valid_status == 'Active':
        if obj.amount_type ==  'FLAT':
            discount_value = obj.discount_amount
        else:
            discount_value = round(obj.discount_amount/100, 2)
            
    context = {
        'schedule_type' : obj.schedule_type,
        'schedule_type_display' : schedule_type_display,
        'valid_from' : valid_from_str,
        'valid_to' : valid_to_str,
        'valid_status' : valid_status,
        'discount_value' : discount_value,
    }
    
    return context

def calculate_promo_code(promo_code, order_type, product_list):
    is_for_lifetime = False
    is_for_all = False
    
    mrp = 0.0 
    total_product_price = 0.0 
    after_discount_total_product_price = 0.0 
    after_discount_product_price = 0.0 
    total_discount_amount = 0.0 
    applied_discount_amount = 0.0 
    promo_discount_amount = 0.0 
    
    total_promo_discount_amount = 0.0
    promo_discount_value = 0.0
    product_price_qs = None
    product_price_list_qs = None
    valid_status = None
    discount_qs = None
    error_msg_list = []
    
    
    promo_qs = PromoCode.objects.filter(promo_code = promo_code).last()
    if not promo_qs:
        return ResponseWrapper(error_msg='Promo Code is Not Found', error_code=404)
    
    is_for_lifetime = promo_qs.is_for_lifetime
    is_for_all = promo_qs.is_for_all
    
    if not is_for_lifetime:
        check_promo_code = offer_check(promo_qs)
        promo_code_status = check_promo_code.get('valid_status')
        
    elif is_for_lifetime:
        promo_code_status = 'Active'
    
    if promo_code_status != 'Active':
        return ResponseWrapper(error_msg=f"Currently '{promo_code}' is Not Valid", error_code=404)
    
    if not is_for_all and not (promo_qs.promo_type == order_type):
        return ResponseWrapper(error_msg=f"This '{promo_code}' Promo Code is Only Valid for '{promo_qs.get_promo_type_display()}'", error_code=404)
    
    is_promo_valid = True

    for product in product_list:
        product_slug = product.get('product_slug')
        quantity = product.get('quantity')
        
        product_qs = Product.objects.filter(slug = product_slug).last()
        
        if not product_qs:
            error_message = f'{product_slug} Product is Not Found'
            error_msg_list.append(error_message)
            is_promo_valid = False
            break
        
        try:
            product_price_list_qs = product_qs.product_price_infos.all()
        except:
            product_price_list_qs = None
        
        if product_price_list_qs is None:
            error_message = f'{product_slug} Product Price is Not Found'
            error_msg_list.append(error_message)
            is_promo_valid = False
            break
            
        # if not is_for_all
        
        if order_type in ['ECOMMERCE_SELL', 'RETAIL_ECOMMERCE_SELL']:
            product_price_qs = product_price_list_qs.filter(
                product__slug = product_qs.slug, product_price_type = 'ECOMMERCE').last()
            
        elif order_type in ['POINT_OF_SELL', 'ON_THE_GO']:
            product_price_qs = product_price_list_qs.filter(
                product__slug = product_qs.slug, product_price_type = 'POINT_OF_SELL').last()
            
        elif order_type in ['CORPORATE_SELL']:
            product_price_qs = product_price_list_qs.filter(
                product__slug = product_qs.slug, product_price_type = 'CORPORATE').last()
            
        elif order_type in ['B2B_SELL']:
            product_price_qs = product_price_list_qs.filter(
                product__slug = product_qs.slug, product_price_type = 'B2B').last()
        
        if product_price_qs.promo_code:
            
            #print(f'Product = {product_price_qs.promo_code.promo_code}, COde = {promo_code}')
            
            if not product_price_qs.promo_code.promo_code == promo_code:
                
                error_message = f"'{promo_code}' is Not Valid for '{product_qs.name}'"
                error_msg_list.append(error_message)
                is_promo_valid = False
        
        if not product_price_qs:
            error_message = f"For This '{product_qs.name}' Product Price Does Not Found"
            error_msg_list.append(error_message)
            is_promo_valid = False
        
        mrp = product_price_qs.mrp
    
        discount_qs = product_price_qs.discount
        promo_qs = product_price_qs.promo_code
        
        total_product_price += (mrp*quantity)
            
        if discount_qs:
            discount = offer_check(discount_qs)
        
            discount_status = discount.get('valid_status')
            
            total_product_price += (mrp*quantity)
                
            if discount_status == 'Active':
                
                discount_amount = discount_qs.discount_amount
                if discount_qs.amount_type == 'FLAT':
                    applied_discount_amount = discount_amount
                    
                else:
                    applied_discount_amount = round((mrp*discount_amount/100), 2)
                    
                total_discount_amount += applied_discount_amount
                    
            after_discount_product_price = total_product_price - total_discount_amount
            
            after_discount_total_product_price += after_discount_product_price
            
        if promo_qs:
            
            if promo_qs.promo_code == promo_code:
                discount = offer_check(promo_qs)
            
                discount_status = discount.get('valid_status')
            
                if discount_status == 'Active':
                    
                    discount_amount = promo_qs.discount_amount
                    
                    if promo_qs.amount_type == 'FLAT':
                        applied_discount_amount = discount_amount
                        
                    else:
                        applied_discount_amount = round((mrp*discount_amount/100), 2)
                        
                    promo_discount_value += applied_discount_amount
                        
                    total_promo_discount_amount = total_product_price - promo_discount_value
                
                    promo_discount_value += after_discount_product_price
                    
                    total_promo_discount_amount = promo_discount_value
            
            
    # if len(product_list) > 1:
    #     if is_promo_valid == True:  
    #         if promo_qs:
    #             promo_discount_value = promo_qs.discount_amount

    #             if promo_qs.amount_type == 'FLAT':
    #                 promo_discount_amount = promo_discount_value
                    
    #             else:
    #                 promo_discount_amount = round((after_discount_total_product_price*promo_discount_value/100), 2)       
                
    #             total_promo_discount_amount = after_discount_product_price - promo_discount_amount 
                    
    #     elif not is_promo_valid :  
    #         #print('bbbbbbbbbb')
    #         promo_discount_value = promo_qs.discount_amount

    #         if promo_qs.amount_type == 'FLAT':
    #             promo_discount_amount = promo_discount_value
                
    #         else:
    #             promo_discount_amount = round((after_discount_total_product_price*promo_discount_value/100), 2)       
            
    #         total_promo_discount_amount = after_discount_product_price - promo_discount_amount 
            
        
    # if is_promo_valid == True: 
    #     promo_discount_value = promo_qs.discount_amount

    #     if promo_qs.amount_type == 'FLAT':
    #         promo_discount_amount = promo_discount_value
            
    #     else:
    #         promo_discount_amount = round((after_discount_total_product_price*promo_discount_value/100), 2)   
            
    #         #print(f"after_discount_total_product_price ={after_discount_total_product_price}, promo_discount_value= {promo_discount_value} promo_discount_amount= {promo_discount_amount}")    
        
    #     total_promo_discount_amount = after_discount_product_price - promo_discount_amount 
        
    
    price_info_details = {
        'total_product_price': total_product_price,
        'total_discount_amount': total_discount_amount,
        'after_discount_product_price': after_discount_product_price,
        'promo_discount_value': promo_discount_value,
        'promo_discount_amount': promo_discount_amount,
        'total_promo_discount_amount': abs(total_promo_discount_amount),
    }
    context= {
        'price_info_details':price_info_details, 
        'error_msg_list': error_msg_list,
    }
    
        
    return context

def calculate_order_price(order_obj, **kwargs): 
    order_qs = Order.objects.filter(invoice_no = order_obj.invoice_no).last()
    
    
    #print(f'In Start Invoice No is = {order_obj.invoice_no}, Order ID = {order_obj.id}')
    
    context = {}

    today = timezone.now() + timedelta(hours=6)
    current_time = today.time()
    
    # Order 
    total_order_product_price = 0.0
    total_order_discount_amount = 0.0
    total_order_net_payable_amount = 0.0
    total_order_gsheba_amount = 0.0
    total_order_tax_amount = 0.0
    total_order_promo_discount = 0.0
    total_order_delivery_charge = 0.0
    total_order_payable_amount = 0.0
    total_order_advance_amount = 0.0
    total_order_paid_amount = 0.0
    total_order_due_amount = 0.0
    total_order_return_amount = 0.0
    total_order_expense_amount = 0.0
    total_order_balance_amount = 0.0
    total_promo_discount_amount = 0.0
    
    payment_status = order_qs.payment_status
    
    # Order Item
    unit_msp_price = 0.0
    unit_mrp_price = 0.0
    total_product_price = 0.0
    total_tax_amount = 0.0
    total_discount_amount = 0.0
    discount_value = 0.0
    discount_type = None
    total_net_price = 0.0
    commission_amount = 0.0
    gsheba_amount = 0.0
    commission_amount = 0.0
    tax_amount = 0.0
    discount_amount = 0.0
    
    unit_msp_price = 0.0
    unit_mrp_price = 0.0
    selling_price = unit_mrp_price
    
    # Order Item List
    
    order_item_list = order_qs.order_items.filter(
        is_gift_item = False
    ).exclude(
        status__in = ["CANCELLED", "RETURNED","GSHEBA_RETURNED", "REFUNDED"]
    )
    # 
    # #print(f"This is in Calculate.py File, Total Order Item  = {order_item_list.count()}, Order Item ID is = {order_item_list.last().id}, GSheba Amount is ={order_item_list.last().gsheba_amount}")
    
    for order_item in order_item_list:
            
        #  Promo Code
        promo_code = ''
        total_promo_discount_amount = 0.0
        promo_discount_value = 0.0
        promo_discount_type = ''
        
        is_commission_enable = True
        
        
        
        order_item_qs =  OrderItem.objects.filter(id = order_item.id)
        
        #print(f"Order Item Price = {order_item.selling_price}")
        
        if not order_item_qs:
            return context
        
        product_qs = order_item.product
        quantity = 1
        
        # quantity = order_item.quantity
        
        product_price_qs = None
        
        if product_qs:
            if order_qs.order_type in ['ECOMMERCE_SELL', 'RETAIL_ECOMMERCE_SELL', 'PC_BUILDER_SELL']:
                product_price_qs = product_qs.product_price_infos.filter(product_price_type = 'ECOMMERCE').last()
                
            elif order_qs.order_type in ['POINT_OF_SELL', 'ON_THE_GO']:
                product_price_qs = product_qs.product_price_infos.filter(product_price_type = 'POINT_OF_SELL').last()
                
            elif order_qs.order_type == 'CORPORATE_SELL':
                product_price_qs = product_qs.product_price_infos.filter(product_price_type = 'CORPORATE').last()
                
            elif order_qs.order_type == 'B2B_SELL':
                product_price_qs = product_qs.product_price_infos.filter(product_price_type = 'B2B').last()
                
                
            if product_price_qs:
                try:
                    unit_msp_price = product_price_qs.msp
                    unit_mrp_price = product_price_qs.mrp
                except:
                    unit_msp_price = 0.0
                    unit_mrp_price = 0.0
        
        if order_item.selling_price == 0.0:
            selling_price = unit_mrp_price - discount_amount
        elif order_item.selling_price > 0.0:
            selling_price = order_item.selling_price
        
        total_product_price = quantity * selling_price
        
        # TAX Calculation
        if product_qs:
            selling_tax_category_qs = product_qs.selling_tax_category or 0
        
            if selling_tax_category_qs:
                tax_amount = product_qs.selling_tax_category.value_in_percentage
        
        total_tax_amount = round(((total_product_price * tax_amount) / 100), 2)
        
        # Discount Calculation
        
        #print(f"DIscount = {product_price_qs.discount}, {product_price_qs.product_price_type}")

        try:
            discount_qs = product_price_qs.discount
        except:
            discount_qs = None
        
        if discount_qs:
            discount_offer = offer_check(obj = discount_qs)
            valid_status =  discount_offer.get('valid_status')
            
            if valid_status == 'Active':
                discount_type = discount_qs.amount_type
                discount_value = discount_qs.discount_amount
                
                if discount_type == 'FLAT':
                    discount_amount = discount_value
                else:
                    discount_amount = (total_product_price * discount_value)/100
                    
                
            total_discount_amount = discount_amount * quantity
            
            total_net_price = total_product_price - total_discount_amount
            
        
        try:
            promo_qs = product_price_qs.promo_code
        except:
            promo_qs = None
        
        #print(f"Promo Code = {product_price_qs.promo_code}, {order_qs.promo_code}")
        
        if order_qs.promo_code:
            if promo_qs:
                discount_offer = offer_check(obj = promo_qs)
                valid_status =  discount_offer.get('valid_status')
                
                if valid_status == 'Active':
                    
                    is_commission_enable = False
                    total_product_price = unit_mrp_price
                    
                    promo_code = order_qs.promo_code
                    
                    promo_discount_type = promo_qs.amount_type
                    promo_discount_value = promo_qs.discount_amount
                    
                    if promo_discount_type == 'FLAT':
                        total_promo_discount_amount = promo_discount_value
                        
                    else:
                        total_promo_discount_amount = (total_product_price * promo_discount_value)/100
                        
                    # total_order_promo_discount = total_promo_discount_amount
                        
                    
                total_discount_amount = discount_amount * quantity 
                
                total_net_price = total_product_price - total_discount_amount
                
        print(f"Promo Code = {promo_code}, Type = {promo_discount_type}, Value = {promo_discount_value}, Total Promo Discount = {total_order_promo_discount}")
            
                
        # gsheba_amount = 37
        
        selling_price = unit_mrp_price - discount_amount
        
        if order_qs.order_type in ['POINT_OF_SELL']:
            selling_price = order_item.selling_price
            gsheba_amount = order_item.gsheba_amount
            
        if is_commission_enable == True:
            if not order_qs.order_type in ['ECOMMERCE_SELL', 'RETAIL_ECOMMERCE_SELL', 'PC_BUILDER_SELL']:
                commission_amount =  total_net_price - (unit_msp_price * quantity)
            
        
        if order_qs.order_type in ['POINT_OF_SELL'] and not order_qs.promo_code:
            selling_price = order_item.selling_price
            total_product_price = selling_price
            
        else:
            selling_price = order_item.selling_price
            total_product_price = unit_mrp_price
        
        # total_product_price = selling_price + gsheba_amount
        
        #print('yyyyyyyyyyy', gsheba_amount)
        
        order_item_qs.update(
            unit_msp_price = unit_msp_price,
            unit_mrp_price = unit_mrp_price,
            total_product_price = total_product_price,
            total_tax_amount = total_tax_amount,
            total_discount_amount = total_discount_amount,
            discount_value = discount_value,
            discount_type = discount_type,
            total_net_price = total_net_price,
            gsheba_amount = gsheba_amount,
            commission_amount = commission_amount,
            selling_price = selling_price,
            promo_code = promo_code,
            total_promo_discount_amount = total_promo_discount_amount,
            promo_discount_value = promo_discount_value,
            promo_discount_type = promo_discount_type,
        )
        
        total_order_product_price += total_product_price
        total_order_discount_amount += total_discount_amount
        total_order_gsheba_amount += gsheba_amount
        total_order_tax_amount += total_tax_amount
        
        
    #print(f"total_promo_discount_amount= {total_promo_discount_amount}, ")
    
    total_order_net_payable_amount = total_order_product_price - total_order_discount_amount
    
    
    total_order_promo_discount += total_promo_discount_amount
    
    print(f"total_order_promo_discount = {total_order_promo_discount}, total_promo_discount_amount = {total_promo_discount_amount}")
    
    if order_qs.order_type=='POINT_OF_SELL':
        total_order_delivery_charge = 0.0
    else:
        total_order_delivery_charge =  order_qs.delivery_method.delivery_charge
    
    total_order_payable_amount = (total_order_net_payable_amount + total_order_gsheba_amount +  total_order_tax_amount + total_order_delivery_charge 
    - total_order_promo_discount)
    
    total_order_advance_amount = sum(order_qs.order_payment_logs.values_list('received_amount', flat = True))
    
    total_order_paid_amount = total_order_advance_amount
    
    total_order_due_amount = total_order_payable_amount - total_order_advance_amount
    
    if total_order_due_amount == 0.0:
        payment_status = 'PAID'
        
    # if order_qs.order_payment_logs.all(): 
    #     total_order_advance_amount = sum(order_qs.order_payment_logs.all().values_list('received_amount', flat=True))
    #print('vvvvvvvvvvvvvvvv', total_order_delivery_charge)
    
    if total_order_payable_amount > 4999:
        total_order_payable_amount = total_order_payable_amount - total_order_delivery_charge
        total_order_due_amount = total_order_due_amount - total_order_delivery_charge
        
        total_order_delivery_charge = 0.0
    
    order_qs.total_product_price = total_order_product_price
    order_qs.total_discount_amount = total_order_discount_amount
    order_qs.total_net_payable_amount = total_order_net_payable_amount
    order_qs.total_gsheba_amount = total_order_gsheba_amount
    order_qs.total_tax_amount = total_order_tax_amount
    order_qs.total_promo_discount = total_order_promo_discount
    order_qs.total_delivery_charge = total_order_delivery_charge
    order_qs.total_payable_amount = total_order_payable_amount
    order_qs.total_advance_amount = total_order_advance_amount
    order_qs.total_paid_amount = total_order_paid_amount
    order_qs.total_due_amount = total_order_due_amount
    order_qs.total_return_amount = total_order_return_amount
    # order_qs.total_expense_amount = total_order_expense_amount
    order_qs.payment_status = payment_status
    
    order_qs.save()
    
    print(f"total_payable_amount = {order_qs.total_payable_amount}")
    
    return context



def generate_order_item_status_log(order_item_obj, status, status_display,order_item_status_reason, status_change_by, order_item_status_change_at, created_by):
    context = {
        'msg': 'Success'
    }
    
    order_status_log_qs = OrderItemStatusLog.objects.filter(order_item__id = order_item_obj.id, status = status ).last()
    
    if order_status_log_qs:
        return context
    
    order_status_log_qs = OrderItemStatusLog.objects.create(order_item= order_item_obj, status = status, status_display = status_display,  order_status_reason = order_item_status_reason,status_change_by = status_change_by, order_status_change_at= order_item_status_change_at,  created_by = created_by)
    
    if order_status_log_qs:
        order_status_log_qs.order_status_change_at = order_status_log_qs.created_at
        order_status_log_qs.save()

    return context



def generate_order_status_log(order_obj, status, status_display,order_status_reason, status_change_by, order_status_change_at, created_by):
    context = {
        'msg': 'Success'
    }
    order_status_log_qs = OrderStatusLog.objects.filter(order__invoice_no = order_obj.invoice_no, status = status ).last()
    
    if order_status_log_qs:
        return context

    status_log_slug = unique_slug_generator(name=order_obj.invoice_no) if order_obj.invoice_no else None
    
    order_status_log_qs = OrderStatusLog.objects.create(slug=status_log_slug,order= order_obj, status = status, status_display = status_display,  order_status_reason = order_status_reason,status_change_by = status_change_by, order_status_change_at= order_status_change_at,  created_by = created_by)
    
    if order_status_log_qs:
        order_status_log_qs.order_status_change_at = order_status_log_qs.created_at
        order_status_log_qs.save()
        
        
    order_item_list = order_obj.order_items.filter(status = status)
    
    for order_item in order_item_list:
        order_item_status_reason = order_status_reason
        
        order_item_status_log_qs = OrderItemStatusLog.objects.filter(order_item__id= order_item.id, status = order_item.status).last()
        
        if not order_item_status_log_qs:
            order_item_log_qs = generate_order_item_status_log(order_item_obj= order_item, status = order_item.status, status_display =status_display, order_item_status_reason=order_item_status_reason , status_change_by = status_change_by, order_item_status_change_at = order_status_log_qs.order_status_change_at, created_by = created_by)

    return context

def order_item_create(barcode_status,order_item_qs, order_qs, product_slug, quantity, selling_price, gsheba_amount, barcode_number, created_by, status, status_change_reason):
    
    # selling_price = 0.0
    product_qs = None
    error_msg = None
    is_valid = True
    
    context = {
        'is_valid': is_valid,
        'error_msg': error_msg
    } 
    
    # #print(F'Barcode Current Status = {barcode_status}, Order Item Qs = {order_item_qs}, Order Item status = {status},GSheba Amount = {gsheba_amount}, barcode_number = {barcode_number}')
    
    if barcode_number:
        product_stock_qs = ProductStock.objects.filter(barcode = barcode_number).last()

        if not product_stock_qs.status in ['RETURNED', 'GSHEBA_FAUlLY', 'COMPANY_WARRANTY_FAUlLY', 'PACKET_DAMAGE', 'REPLACEMENT_WARRANTY_FAULTY', 'SERVICE_WARRANTY_FAULTY']:
            # pass
            if not product_stock_qs:
                error_msg = f"This '{barcode_number}' Barcode is Not Found"
                is_valid = False
                
                context = {
                    'is_valid': is_valid,
                    'error_msg': error_msg
                }
                
                return context
        
        elif product_stock_qs.status in ['RETURNED', 'GSHEBA_FAUlLY', 'COMPANY_WARRANTY_FAUlLY', 'PACKET_DAMAGE', 'REPLACEMENT_WARRANTY_FAULTY', 'SERVICE_WARRANTY_FAULTY'] and not order_item_qs.status in ["GSHEBA_RETURNED", "RETURNED", "REFUNDED"]:
            
            # if not product_stock_qs.status == 'ACTIVE':
            error_msg = f"This '{barcode_number}' Barcode is {product_stock_qs.get_status_display()}"
            is_valid = False
            
            # order_qs.delete()

            context = {
                'is_valid': is_valid,
                'error_msg': error_msg
            }
            
            return context
        
        product_qs = product_stock_qs.product_price_info.product
        
        if order_item_qs:
            if not order_item_qs.barcode_number == barcode_number:
                
                if not product_stock_qs.status == 'ACTIVE':
                    previous_barcode_status = product_stock_qs.get_status_display()
                    
                    error_msg = f"This '{barcode_number}' Barcode Can't Sell, Because of, This Barcode Status is '{previous_barcode_status}"
                    
                    is_valid = False
                    
                    context = {
                        'is_valid': is_valid,
                        'error_msg': error_msg
                    }
                    
                    return context
        
        
        today = timezone.now()
        
        previous_status = product_stock_qs.status
        
        previous_status_display = product_stock_qs.get_status_display()
        
        # print('barcode_number', order_item_qs.barcode_number)
        
        if barcode_status == "ACTIVE":
            product_stock_qs.status = 'SOLD'
            
            if product_stock_qs.stock_in_date:
                delta = today - product_stock_qs.stock_in_date
                days = delta.days
                hours, remainder = divmod(delta.seconds, 3600)
                minutes, _ = divmod(remainder, 60)

                stock_in_age = f'{days} Days {hours} Hours {minutes} Minutes'
                product_stock_qs.stock_in_age = stock_in_age 
        
        elif order_item_qs:
            if order_item_qs.status in ['RETURNED', 'GSHEBA_RETURNED', 'CANCELLED', 'REFUNDED']:
                
                if order_item_qs.status == 'GSHEBA_RETURNED':
                    product_stock_qs.status = "GSHEBA_FAUlLY"
                    
                elif order_item_qs.status == "RETURNED":
                    product_stock_qs.status = 'RETURN'
                    
                elif order_item_qs.status in ["CANCELLED", "REFUNDED"]:
                    product_stock_qs.status = 'ACTIVE'
            
            # try:
            employee_qs = EmployeeInformation.objects.filter(user = created_by).last()
            
            stock_location_qs = None
            
            if employee_qs:
                if order_qs.order_type == ["ECOMMERCE_SELL"]:
                    
                    stock_location_qs = OfficeLocation.objects.filter(name__icontains = "GProjukti.com - E commerce Shop").last()
                
                else:
                    stock_location_qs = employee_qs.work_station
            
                if stock_location_qs:
                    product_stock_qs.save()
                
            # except:
            #     pass
                    
        else:
            if order_qs.approved_status == 'APPROVED':
                product_stock_qs.status = barcode_status
        
        product_stock_qs.save()
        
        stock_status_change_by_info = BaseSerializer(created_by).data
        
        stock_location_info = OfficeLocationSerializer(product_stock_qs.stock_location).data
        # product_stock_log_qs = ProductStockLog.objects.filter(
        #     product_stock = product_stock_qs, 
        # )
        current_status_display = product_stock_qs.get_status_display()
        
        if barcode_status:
            current_status_display = barcode_status
            
        try:
            reason = f"This '{product_stock_qs.barcode}' Barcode Status Change From '{previous_status_display}' To '{current_status_display}' By '{order_item_qs.created_by.first_name} {order_item_qs.created_by.last_name}' at {today.strftime('%b %d, %Y at %I:%M %p')}"
        except:
            reason = f"This '{product_stock_qs.barcode}' Barcode Status Change at {today.strftime('%b %d, %Y at %I:%M %p')}"
        
        
        product_stock_log_qs = ProductStockLog.objects.create(
                product_stock = product_stock_qs, 
                previous_status = previous_status,
                previous_status_display = previous_status_display,
                current_status = product_stock_qs.status,
                current_status_display = product_stock_qs.get_status_display(),
                remarks = reason,
                is_active = product_stock_qs.is_active,
                stock_status_change_by_info = stock_status_change_by_info,
                stock_location_info = stock_location_info,
                created_by = created_by,
                stock_in_date = today,
            )
        
        try:
            product_code = product_stock_qs.product_price_info.product.product_code
            shop_slug = product_stock_qs.stock_location.slug
            
            current_stock_qs = ProductStock.objects.filter(
                product_price_info__product__product_code = product_code, 
                stock_location__slug  = shop_slug, 
                status = "ACTIVE"
                )
            
            #print(f"Current Stock = ", current_stock_qs, current_stock_qs.count(), product_code, shop_slug)
            
            
            if current_stock_qs.count() == 0:
                remarks = f"This '{product_stock_qs.product_price_info.product.name}' Product, Become '0' Stock at {today.strftime('%b %d, %Y at %I:%M %p')}, From '{product_stock_qs.stock_location.name}"
                
                shop_wise_zero_stock_qs = ShopWiseZeroStockLog.objects.create(
                    product = product_stock_qs.product_price_info.product,
                    office_location  = product_stock_qs.stock_location,
                    zero_stock_date = today, remarks = remarks,
                    created_by = created_by
                )
                
            
        except:
            pass
        
    elif product_slug:
        product_qs = Product.objects.filter(slug = product_slug).last()

        if not product_qs:
            error_msg = f"This '{product_slug}' Product is Not Found"
            
            is_valid = False
            
            context = {
                'is_valid': is_valid,
                'error_msg': error_msg
            }
        
    else:
        product_qs = order_item_qs.product
    
    
    if int(selling_price) > 0:
        selling_price = selling_price
        
    elif not selling_price and product_qs:
        if product_qs.product_price_infos:
            try:
                selling_price = product_qs.product_price_infos.last().mrp
            except:
                selling_price = 0.0
        
    
    if not order_item_qs:
        
        for _ in range(quantity):
            order_item_qs = OrderItem.objects.create(
                order=order_qs,
                status=status,
                quantity=1,  # Each created OrderItem will have a quantity of 1
                product=product_qs,
                selling_price=selling_price,
                gsheba_amount=gsheba_amount,
                barcode_number=barcode_number,
                created_by=created_by
            )
            
            status_display = order_item_qs.get_status_display()
            profile_image_url = None
            
            status_change_by = {}
            
            if order_item_qs.created_by:
                user_information_qs =  UserInformation.objects.filter(
                    user__id = order_item_qs.created_by.id
                ).last()
                
                if user_information_qs:
                    status_change_by = BaseSerializer(order_item_qs.created_by).data
                    
            if not status_change_reason:
                order_item_status_reason = f'Order Item Status Change For - '
            else:
                order_item_status_reason = status_change_reason
                

            order_item_status_log_qs = OrderItemStatusLog.objects.filter(order_item__id= order_item_qs.id, status = order_item_qs.status).last()
    
            if not order_item_status_log_qs:
                order_item_log_qs = generate_order_item_status_log(order_item_obj= order_item_qs, status = order_item_qs.status, status_display =status_display, order_item_status_reason=order_item_status_reason , status_change_by = status_change_by, order_item_status_change_at = order_item_qs.created_at, created_by = created_by)
        
        #print(f"After Create GSheba Amount is = {gsheba_amount}")
        
    else:
        print('gggggggggggggg', quantity)
        
        if not quantity:
            quantity = order_item_qs.quantity 
            
        if quantity > 1:
            new_quantity = quantity - 1
            
            for _ in range(new_quantity):
                order_item_qs = OrderItem.objects.create(
                    order=order_qs,
                    status=status,
                    quantity=1,  # Each created OrderItem will have a quantity of 1
                    product=product_qs,
                    selling_price=selling_price,
                    gsheba_amount=gsheba_amount,
                    barcode_number=barcode_number,
                    created_by=created_by
                )
                
                today = TODAY
        
                if status == 'RETURNED':
                    order_item_warranty_log_qs = order_item_qs.order_item_warranty_logs.filter(end_date__gte = today, warranty_type = '1_GSHEBA_WARRANTY')
                    if order_item_warranty_log_qs:
                        status = 'GSHEBA_RETURNED'
                    
                order_item_qs.quantity = 1
                order_item_qs.status = status
                order_item_qs.product = product_qs
                order_item_qs.selling_price = selling_price
                order_item_qs.gsheba_amount = gsheba_amount
                order_item_qs.barcode_number = barcode_number
                order_item_qs.updated_by = created_by
                order_item_qs.save()
            
        elif quantity == 1:
            
            today = TODAY
            
            if status == 'RETURNED':
                order_item_warranty_log_qs = order_item_qs.order_item_warranty_logs.filter(end_date__gte = today, warranty_type = '1_GSHEBA_WARRANTY')
                if order_item_warranty_log_qs:
                    status = 'GSHEBA_RETURNED'
                
            order_item_qs.quantity = 1
            order_item_qs.status = status
            order_item_qs.product = product_qs
            order_item_qs.selling_price = selling_price
            order_item_qs.gsheba_amount = gsheba_amount
            order_item_qs.barcode_number = barcode_number
            order_item_qs.updated_by = created_by
            order_item_qs.save()
        
    if product_qs:
        gift_product_qs = product_qs.gift_product
        
        if gift_product_qs:
            gift_order_item_qs = OrderItem.objects.create(
                order = order_qs, status = status,
                quantity = 1, product = gift_product_qs, 
                selling_price = 0.0, gsheba_amount = 0.0,
                is_gift_item = True, order_item_id = order_item_qs.id,
                created_by = created_by
            )
        
        
    status_display = order_item_qs.get_status_display()
    profile_image_url = None
    
    status_change_by = {}
    
    if order_item_qs.created_by:
        user_information_qs =  UserInformation.objects.filter(
            user__id = order_item_qs.created_by.id
        ).last()
        
        if user_information_qs:
            profile_image_url = user_information_qs.image
            
            status_change_by = BaseSerializer(order_item_qs.created_by).data
            
    if not status_change_reason:
        order_item_status_reason = f'Order Item Status Change For - '
    else:
        order_item_status_reason = status_change_reason
        
    order_item_status_log_qs = OrderItemStatusLog.objects.filter(order_item__id= order_item_qs.id, status = order_item_qs.status).last()
    
    if not order_item_status_log_qs:
        order_item_log_qs = generate_order_item_status_log(order_item_obj= order_item_qs, status = order_item_qs.status, status_display =status_display, order_item_status_reason=order_item_status_reason , status_change_by = status_change_by, order_item_status_change_at = order_item_qs.created_at, created_by = created_by)
    
    
    # Product Warranty Add
    
    product_warranty_list = product_qs.product_warrantys.all().order_by('warranty_type')
    
    
    if product_warranty_list:
        for product_warranty in product_warranty_list:
            
            warranty_type = product_warranty.warranty_type
            warranty_duration = product_warranty.warranty_duration
            value = product_warranty.value
            
            start_date = order_item_qs.created_at
            
            
            if warranty_type == "1_GSHEBA_WARRANTY" and gsheba_amount == 0.0:
                pass
            
            elif order_item_qs.order.order_type in ["ECOMMERCE_SELL", "RETAIL_ECOMMERCE_SELL"] and warranty_type == "1_GSHEBA_WARRANTY":
                
                pass
            
            else:
                order_item_warranty_qs = order_item_qs.order_item_warranty_logs.all().last()
                
                if order_item_warranty_qs:
                    start_date = order_item_warranty_qs.end_date
                    
                if warranty_duration == 'DAY':
                    end_date = start_date + timedelta(days=int(value))
                elif warranty_duration == 'MONTH':
                    end_date = start_date + timedelta(days=30 * int(value))  # Assuming 1 month = 30 days
                elif warranty_duration == 'YEAR':
                    end_date = start_date + timedelta(days=365 * int(value)) 
                
                if order_item_warranty_qs:
                    order_item_warranty_log_qs = order_item_qs.order_item_warranty_logs.filter(warranty_type = warranty_type)
                    if not order_item_warranty_log_qs:
                        order_item_warranty_qs = OrderItemWarrantyLog.objects.create(
                            order_item = order_item_qs,
                            warranty_type = warranty_type,
                            warranty_duration = warranty_duration,
                            value = value,
                            start_date = start_date,
                            end_date = end_date,
                            created_by = created_by
                        )
                elif not order_item_warranty_qs:
                    order_item_warranty_qs = OrderItemWarrantyLog.objects.create(
                            order_item = order_item_qs,
                            warranty_type = warranty_type,
                            warranty_duration = warranty_duration,
                            value = value,
                            start_date = start_date,
                            end_date = end_date,
                            created_by = created_by
                        )
            
    return context


def order_payment_log(slug, order_qs, payment_slug, payment_qs, order_status, received_amount, transaction_no, request_user, status):
    
    # order_payment_log_qs = OrderPaymentLog.objects.filter(
    #         order = order_qs, order_payment = payment_qs, status = status).last()
    
    if slug:
        order_payment_log_qs = OrderPaymentLog.objects.filter(
            slug = slug).last()
    
    else:
        order_payment_log_qs = OrderPaymentLog.objects.filter(
            order = order_qs, status = status, received_amount = received_amount, slug = payment_slug).last()
    
    if order_payment_log_qs:
        print('update', payment_qs )
        order_payment_log_qs.received_amount = received_amount
        order_payment_log_qs.transaction_no = transaction_no
        order_payment_log_qs.order_status = order_status
        order_payment_log_qs.updated_by = request_user
        order_payment_log_qs.status = status
        order_payment_log_qs.save()
    
    else:
        print('Createing', payment_qs )
        slug = unique_slug_generator(name = f"{order_qs}-{payment_slug}")
        
        order_payment_log_qs = OrderPaymentLog.objects.create(
            order = order_qs,
            slug = slug,
            order_payment = payment_qs,
            order_status = order_qs.status,
            received_amount = received_amount,
            transaction_no = transaction_no,
            created_by = request_user,
            status = status
        )
    
    
    return order_payment_log_qs

def service_order_create_or_update(invoice_no,servicing_type, order, request_user, status, order_date):
    
    service_order_qs = ServicingOrder.objects.filter(
            invoice_no = invoice_no).last()
    
    if service_order_qs:
        service_order_qs.status = status,
        service_order_qs.servicing_type = servicing_type,
        service_order_qs.order = order,
        service_order_qs.order_date = order_date,
        service_order_qs.updated_by = request_user
        service_order_qs.save()
    
    else:
        service_order_qs = ServicingOrder.objects.create(
            invoice_no = invoice_no,
            status = status,
            servicing_type = servicing_type,
            order = order,
            created_by = request_user,
            order_date = timezone.now()
        )
        # order_item_list =  order.order_items.filter(status = 'WAREHOUSE_TO_SERVICE_POINT')
        
        order_item_list =  order.order_items.filter()
        
        for order_item in order_item_list:
            quantity = order_item.quantity
            status = order_item.status
            product = order_item.product
            barcode_number = order_item.barcode_number
            servicing_order = service_order_qs
            
            service_order_item_qs = ServicingOrderItem.objects.create(
                servicing_order = servicing_order,
                status = service_order_qs.status,
                quantity =quantity,
                product =product,
                barcode_number = barcode_number,
                created_by = request_user
            )
    
    return service_order_qs


def generate_service_order_status_log(order_obj, status, status_display,order_status_reason, status_change_by, order_status_change_at, created_by):
    context = {
        'msg': 'Success'
    }
    order_status_log_qs = OrderStatusLog.objects.filter(order__invoice_no = order_obj.invoice_no, status = status ).last()
    
    if order_status_log_qs:
        return context

    status_log_slug = unique_slug_generator(name=order_obj.invoice_no) if order_obj.invoice_no else None
    
    order_status_log_qs = OrderStatusLog.objects.create(slug=status_log_slug,order= order_obj, status = status, status_display = status_display,  order_status_reason = order_status_reason,status_change_by = status_change_by, order_status_change_at= order_status_change_at,  created_by = created_by)
    
    if order_status_log_qs:
        order_status_log_qs.order_status_change_at = order_status_log_qs.created_at
        order_status_log_qs.save()
        
        
    order_item_list = order_obj.order_items.filter(status = status)
    
    for order_item in order_item_list:
        order_item_status_reason = order_status_reason
        
        order_item_status_log_qs = OrderItemStatusLog.objects.filter(order_item__id= order_item.id, status = order_item.status).last()
        
        if not order_item_status_log_qs:
            order_item_log_qs = generate_order_item_status_log(order_item_obj= order_item, status = order_item.status, status_display =status_display, order_item_status_reason=order_item_status_reason , status_change_by = status_change_by, order_item_status_change_at = order_status_log_qs.order_status_change_at, created_by = created_by)

    return context



def sslcommerz_payment_create(data: Dict, customer: User) -> Dict:
    """
    :param data:
    :param customer:
    :return:
    """
    customer_name = 'GProjukti Customer'
    if customer.first_name and customer.last_name:
        customer_name = f'{customer.first_name} {customer.last_name}'
    try:
        body = {
            'store_id': settings.SSL_STORE_ID,
            'store_passwd': settings.SSL_STORE_PASSWORD,
            'currency': 'BDT',
            'cus_name': customer_name,
            'cus_add1': 'Dhaka',
            # 'cus_add1': customer.address if customer.address else 'Dhaka',
            'cus_city': 'Dhaka',
            'cus_country': 'Bangladesh',
            'cus_phone': '09876543',
            'cus_email': 'no-email@gprojukti.com.bd',
            'shipping_method': 'YES',
            'ship_name': 'Dhaka',
            'ship_city': 'Dhaka',
            'ship_country': 'Bangladesh',
            'ship_postcode': 1000,
            'ship_add1': 'Dhaka',
        }
        body.update(data)
        response = requests.post(
            url=f'https://securepay.sslcommerz.com/gwprocess/v4/api.php',
            data=body,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            # timeout=5,
        )
        resp: Dict = response.json()
        #print(resp)
        if resp.get('status') == 'SUCCESS':
            return resp
        # logger.error('SSL_COMMERZ_PAYMENT_ERROR_RESPONSE: ', str(data['failedreason']))
        return {}
    
    except requests.exceptions.Timeout as e:
        logger.error('SSL_COMMERZ_PAYMENT_TIMEOUT_ERROR: ', str(e))
    except requests.exceptions.HTTPError as e:
        logger.error('SSL_COMMERZ_PAYMENT_HTTP_ERROR: ', str(e))
    except requests.exceptions.ConnectionError as e:
        logger.error('SSL_COMMERZ_PAYMENT_CONNECTION_ERROR: ', str(e))
    return {}


def show_wise_day_end_calculation(shop_qs, request_user):
    today = timezone.now().date()
    # today = today.date() - timedelta(days=1)
    
    shop_name = '-'
    shop_slug = '-'
    retail_sell_amount = 0.0
    opening_balance_amount = 0.0
    total_retail_gsheba_amount = 0.0
    total_e_retail_sell_amount = 0.0
    total_ecommerce_collection = 0.0
    total_e_retail_collection = 0.0
    total_advance_collection = 0.0
    total_corporate_collection = 0.0
    total_b2b_collection = 0.0
    total_mfs_collection = 0.0
    
    total_gsheba_claim_quantity = 0.0
    total_warranty_claim_quantity = 0.0
    total_refund_amount = 0.0
        

    if shop_qs:
        shop_name = shop_qs.name
        shop_slug = shop_qs.slug
    
    elif not shop_qs.office_type == 'STORE':
        return ResponseWrapper(error_msg=f"You Must Be Selected a Shop", error_code=404)
        
    shop_order_qs = Order.objects.filter(order_date__date = today).filter(
                                            Q(created_by = request_user)
                                            )
    
    pos_order_qs = shop_order_qs.filter(order_type = 'POINT_OF_SELL', status = 'DELIVERED')
    
    retail_sell_amount = sum(pos_order_qs.values_list('total_payable_amount', flat=True))
    
    total_retail_gsheba_amount = sum(pos_order_qs.values_list('total_gsheba_amount', flat=True))
        
    
    e_retail_order_qs = shop_order_qs.filter(
        order_type = 'RETAIL_ECOMMERCE_SELL').exclude(
            status__in = ["CANCELLED", "RETURNED", "GSHEBA_RETURNED", "REFUNDED"]
            )
        
    total_e_retail_sell_amount = sum(e_retail_order_qs.values_list('total_payable_amount', flat=True))
    
    try:
        qs = OrderPaymentLog.objects.filter(order__shop__slug = shop_slug, status = 'RECEIVED', created_at__date =  today)
        
        total_e_retail_collection = sum(qs.filter(order__order_type = "RETAIL_ECOMMERCE_SELL").values_list('received_amount', flat=True))
        
    
        total_advance_collection = sum(amount for amount in shop_order_qs.values_list('received_amount', flat=True) if amount is not None)
        
        
        shop_received_amount_qs = qs
        shop_refunded_amount_qs = shop_order_qs.filter(status = 'REFUNDED')
        
        total_refund_amount = sum(shop_refunded_amount_qs.values_list('received_amount', flat=True))
    
        shop_return_order_qs = shop_order_qs.filter(status = 'GSHEBA_RETURNED')
        
        total_gsheba_claim_quantity = shop_return_order_qs.count()
        
        shop_warranty_order_qs = shop_order_qs.filter(status__in = ['RETURNED'])
        
        total_warranty_claim_quantity = shop_warranty_order_qs.count()
        
    except:
        pass
    
    ecommerce_collection_qs = OrderPaymentLog.objects.filter(
        created_by = request_user, 
        created_at__date= today, status = "RECEIVED", 
        order__order_type = "ECOMMERCE_SELL"
    )
    
    if ecommerce_collection_qs:
        try:
            total_ecommerce_collection = sum(
                ecommerce_collection_qs.values_list('received_amount', flat = True)
            )
        except:
            pass
    
    payment_qs = PaymentType.objects.all()
    
    payment_list = []
    
    for payment_type in payment_qs:
        payment_type_logo = None
        total_amount = 0.0
        
        payment_type_name = payment_type.name
        payment_type_slug = payment_type.slug
        
        if payment_type.logo:
            payment_type_logo = payment_type.logo
            
        shop_order_qs = OrderPaymentLog.objects.filter(created_by = request_user, status = 'RECEIVED',created_at__date =  today)
        
        order_payment_log = shop_order_qs.filter(order_payment__slug = payment_type_slug, status = 'RECEIVED')
        
        total_amount = sum(order_payment_log.values_list('received_amount', flat = True))
        
        context = {
            'name': payment_type_name,
            'slug': payment_type_slug,
            'logo': payment_type_logo,
            'total_amount': total_amount,
        }
        payment_list.append(context)
        
    # payment_serializer = ShopWisePaymentCollectionListSerializer(instance=payment_qs, many = True)
    
    #TODO MFS Collection Amount Check
    
    # total_advance_collection = (retail_sell_amount + total_e_retail_collection + total_ecommerce_collection)
    
    # qs = OrderPaymentLog.objects.filter(created_by = request_user, status = 'RECEIVED', created_at__date =  today).exclude(order__order_type = "POINT_OFF_SELL")
    
    # total_advance_collection = sum(qs.values_list('received_amount', flat = True)) - total_e_retail_sell_amount
    
    # qs = OrderPaymentLog.objects.filter(
    #     order__shop__slug = shop_slug, status = 'RECEIVED', created_at__date =  today).exclude(order__order_type = "POINT_OFF_SELL")
    
    qs = OrderPaymentLog.objects.filter(order__order_date__date =  today,
        order__shop__slug = shop_slug, status = 'RECEIVED', created_at__date =  today).exclude(order__order_type = "POINT_OFF_SELL")
    
    # if qs:
    #     print('tttttttttttt',qs.count(), qs.first().order.order_date, today.date())
    
    total_advance_collection = sum(qs.values_list('received_amount', flat = True))
    
    # - total_e_retail_sell_amount
    
    context = { 
        'today':today,
        'shop_name':shop_name,
        'shop_slug':shop_slug,
        'retail_sell_amount':retail_sell_amount,
        'total_retail_gsheba_amount':total_retail_gsheba_amount,
        'total_e_retail_sell_amount':total_e_retail_sell_amount,
        'total_e_retail_collection':total_e_retail_collection,
        'total_advance_collection':total_advance_collection,
        'total_corporate_collection':total_corporate_collection,
        'total_ecommerce_collection':total_ecommerce_collection,
        'total_b2b_collection':total_b2b_collection,
        'total_gsheba_claim_quantity':total_gsheba_claim_quantity,
        'total_refund_amount':total_refund_amount,
        'total_warranty_claim_quantity':total_warranty_claim_quantity,
        'total_mfs_collection':total_mfs_collection,
        'opening_balance_amount':opening_balance_amount,
        'payment_collection_amount':payment_list,
        # 'payment_collection_amount':payment_serializer.data,
    }

    return context