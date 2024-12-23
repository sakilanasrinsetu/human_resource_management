from base.serializers import UserInformationBaseSerializer
from location.serializers import OfficeLocationListSerializer
from product_management.models.product import ProductStockLog, ProductStockTransferLog

def product_stock_transfer_log(product_stock_transfer_qs, request_user, status_change_reason):
    stock_status_change_by_info = UserInformationBaseSerializer(request_user).data
    from_shop_info = OfficeLocationListSerializer(product_stock_transfer_qs.from_shop).data
    to_shop_info = OfficeLocationListSerializer(product_stock_transfer_qs.to_shop).data
    status = product_stock_transfer_qs.status
    status_display = product_stock_transfer_qs.get_status_display()
    stock_transfer_type = product_stock_transfer_qs.stock_transfer_type
    stock_transfer_type_display = product_stock_transfer_qs.get_stock_transfer_type_display()
    
    product_transfer_log_qs = ProductStockTransferLog.objects.create(
                product_stock= product_stock_transfer_qs,
                from_shop_info= from_shop_info,
                to_shop_info= to_shop_info,
                status= status,
                status_display= status_display,
                stock_transfer_type= stock_transfer_type,
                stock_transfer_type_display= stock_transfer_type_display,
                remarks= status_change_reason,
                is_active= product_stock_transfer_qs.is_active,
                stock_status_change_by_info= stock_status_change_by_info,
                status_changed_date= product_stock_transfer_qs.updated_by,
                created_by = request_user
                )
    
    product_stock_list_qs = product_stock_transfer_qs.product_stock.all()
    
    for product_stock in product_stock_list_qs:
        previous_status = 'ACTIVE'
        previous_status_display = 'Active'
        
        product_stock_log_qs = ProductStockLog.objects.create(
                product_stock = product_stock, 
                previous_status = previous_status,
                previous_status_display = previous_status_display,
                current_status = product_stock.status,
                current_status_display = product_stock.get_status_display(),
                remarks = status_change_reason,
                is_active = product_stock.is_active,
                stock_status_change_by_info = stock_status_change_by_info,
                stock_location_info = to_shop_info,
                created_by = product_transfer_log_qs.created_by,
                stock_in_date = product_transfer_log_qs.created_at,
            )
    
    return True