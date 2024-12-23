from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.templatetags.static import static
from product_management.models.product import ProductPriceInfo, ProductStock, Product
from reportlab.lib.units import inch
from reportlab.graphics.barcode import code128
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.http import FileResponse

from utils.response_wrapper import ResponseWrapper

def generate_single_line_barcode_for_pos(data_list):
    response = None
    unique_barcode_list = []
    
    for product in data_list:
        product_code = product.get('product_code')
        quantity = product.get('quantity')
        
        if not quantity:
            return ResponseWrapper(error_msg='Quantity Is Not Given', error_code=400)
        if quantity < 0:
            return ResponseWrapper(error_msg='Quantity Number is Not valid', error_code=400)
        
        if not product_code:
            return ResponseWrapper(error_msg='Product Is Not Given', error_code=400)
        
        product_qs = Product.objects.filter(product_code=product_code).last()
        
        if not product_qs:
            return ResponseWrapper(error_msg='Product is Not Found', error_code=404)   
        
        product_price_qs = ProductPriceInfo.objects.filter(id=product_qs.product_price_infos.filter(product_price_type="POINT_OF_SELL").last().id).last()
        
        if not product_price_qs:
            return ResponseWrapper(error_msg='Product Price is Not Add', error_code=404)
        
        product_stock_qs = ProductStock.objects.filter(product_price_info__id=product_qs.product_price_infos.filter(product_price_type="POINT_OF_SELL").last().id).last()
        
        last_barcode_serial_number = f"{product_code}-0{product_qs.serial_no}"
        
        product_price = product_qs.product_price_infos.filter(product_price_type="POINT_OF_SELL").last().mrp
        
        last_serial_number = int(last_barcode_serial_number.split('-')[-1])
        
        for i in range(last_serial_number + 1, last_serial_number + quantity + 1):
            new_barcode = f"{int(product_code):05d}-{i:05d}"
            
            product_stock_qs = ProductStock.objects.filter(barcode=new_barcode).last()
            
            if not product_stock_qs:
                total_price = product_price * quantity
                unique_barcode_list.append((new_barcode, product_price, total_price))
                
                product_qs.serial_no += 1
                product_qs.save() 
                
            else:
                product_qs.serial_no =+ 1
                product_qs.save()
                continue
            
    barcode_width = 7 * inch  # Width of the barcode
    barcode_height = 0 * inch  # Height of the barcode
    x = 2.18 * inch   # x-coordinate for the barcode
    y_start = 10 * inch  # Starting y-coordinate for the barcode
    
    buffer = BytesIO()
    barcode_canvas = canvas.Canvas(buffer, pagesize=letter)

    for record, product_price, total_price in unique_barcode_list:
        y = y_start
        barcode = code128.Code128(record, barWidth=.019 * inch, barHeight=.8 * inch)

        barcode.drawOn(barcode_canvas, x, y)

        barcode_canvas.drawString((x + .90 * inch), (y - .15 * inch), record)
        barcode_canvas.drawString((x + .95 * inch), (y - .3 * inch), "Tk. " + str(product_price).split('.')[0])

        barcode_canvas.showPage()

    barcode_canvas.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f'{product_code}-barcode.pdf')

# Same Barcode Print In Same Page. In  One Page can Print Total 27 . 

def generate_multiple_line_barcode_for_pos(data_list):
    response = None
    unique_barcode_list = []

    for product in data_list:
        product_code = product.get('product_code')
        quantity = product.get('quantity')
        
        if not quantity:
            return ResponseWrapper(error_msg='Quantity Is Not Given', error_code=400)
        if quantity < 0:
            return ResponseWrapper(error_msg='Quantity Number is Not valid', error_code=400)
        if not product_code:
            return ResponseWrapper(error_msg='Product Is Not Given', error_code=400)
        
        product_qs = Product.objects.filter(product_code=product_code).last()
        if not product_qs:
            return ResponseWrapper(error_msg='Product is Not Found', error_code=404)   
        
        product_price_info = product_qs.product_price_infos.filter(product_price_type="POINT_OF_SELL").last()
        # product_price_info = product_qs.product_price_infos.filter(product_price_type="ECOMMERCE").last()
        
        if not product_price_info:
            return ResponseWrapper(error_msg='Product Price is Not Added', error_code=404)

        product_price = product_price_info.mrp
        
        last_serial_number = int(f"{product_code}-0{product_qs.serial_no}".split('-')[-1])

        for i in range(last_serial_number + 1, last_serial_number + quantity + 1):
            new_barcode = f"{int(product_code):05d}-{i:05d}"
            product_stock_qs = ProductStock.objects.filter(barcode=new_barcode).last()
            
            print('ffff', product_stock_qs)
            
            if not product_stock_qs:
                unique_barcode_list.append((new_barcode, product_price))
            else:
                product_qs.serial_no =+ 1
                product_qs.save()
                continue
            
            product_qs.serial_no = i
            product_qs.save()
            
        print('ffff', unique_barcode_list)
        
        # Barcode rendering setup
        barcode_width = 7 * inch
        barcode_height = 0 * inch
        buffer = BytesIO()
        barcode_canvas = canvas.Canvas(buffer, pagesize=letter)
        
        # X and Y coordinates calculation
        x_coords = [round(i * 2.5, 4) for i in range(4)]
        y_coords = [round(10 - i * 1.21, 4) for i in range(9)]
        xy_coords = [(x * inch, y * inch) for x in x_coords for y in y_coords]
        
        c = 0  # Coordinate counter
        
        for record, price in unique_barcode_list:
            x, y = xy_coords[c]
            barcode = code128.Code128(record, barWidth=.015 * inch, barHeight=.4 * inch)
            barcode.drawOn(barcode_canvas, x, y)
            barcode_canvas.drawString((x + .70 * inch), (y - .15 * inch), record)
            barcode_canvas.drawString((x + .90 * inch), (y - .3 * inch), "Tk " + str(price).split('.')[0])
            if c < len(xy_coords) - 1:
                c += 1
            else:
                c = 0
                barcode_canvas.showPage()
        
        barcode_canvas.save()
        buffer.seek(0)
    
    return FileResponse(buffer, as_attachment=True, filename=f'{product_code}-barcode.pdf')


def generate_same_barcode_for_pos(data_list):
    buffer = BytesIO()
    barcode_canvas = canvas.Canvas(buffer, pagesize=letter)

    x_coords = 2.18 * inch
    y_start = 10 * inch
    
    for index, product in enumerate(data_list):
        barcode = product.get('barcode')
        
        if not barcode:
            return ResponseWrapper(error_msg='Barcode Is Not Given', error_code=400)
        barcode_qs = ProductStock.objects.filter(barcode = barcode).last()
        
        if not barcode_qs:
            return ResponseWrapper(error_msg='Barcode is Not Found', error_code=404)   
        
        if not barcode_qs.product_price_info:
            return ResponseWrapper(error_msg='Product Price is Not Add', error_code=404)
        
        product_price = barcode_qs.product_price_info.mrp
        
        if index > 0:
            barcode_canvas.showPage()

        x_coords = 2.18 * inch  # Reset x-coordinate for each page
        y_coords = y_start

        # Create a new barcode object
        barcode_obj = code128.Code128(barcode, barWidth=.019 * inch, barHeight=.8 * inch)

        # Draw the barcode on the current page
        barcode_obj.drawOn(barcode_canvas, x_coords, y_coords)

        # Add additional information if needed, e.g., price
        barcode_canvas.drawString((x_coords + .90 * inch), (y_coords - .15 * inch), barcode)
        barcode_canvas.drawString((x_coords + .90 * inch), (y_coords - .3 * inch), "Tk " + str(product_price).split('.')[0])

    barcode_canvas.save()
    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename='same-barcode.pdf')


def generate_multiple_same_barcode_for_pos(data_list):
    unique_barcode_list = []

    for item in data_list:
        barcode = item.get('barcode')

        product_stock_qs = ProductStock.objects.filter(barcode=barcode).last()

        if not product_stock_qs:
            return ResponseWrapper(error_msg = "Product Stock is Not Found", error_code = 404)
        
        product_price = product_stock_qs.product_price_info.mrp
        unique_barcode_list.append((barcode, product_price))

        buffer=BytesIO()
        barcode_canvas = canvas.Canvas(buffer, pagesize=letter)

        #x coordinates
        x_coords = []
        x_start = .0
        for i in range(4):
            x_coords.append(round(x_start, 4))
            x_start += 2.5
        y_coords = []
        y_start = 10
        for i in range(9):
            y_coords.append(round(y_start, 4))
            y_start -= 1.21
        xy_coords = []
        for x_coord in x_coords:
            for y_coord in y_coords:
                xy_coords.append((x_coord*inch, y_coord*inch))
        c = 0
        
        # x = xy_coords[c][0]
        # y = xy_coords[c][1]
            
        for record, price in unique_barcode_list:
            x = xy_coords[c][0]
            y = xy_coords[c][1]
            barcode = code128.Code128(record, barWidth=.015 * inch, barHeight=.4 * inch)
            barcode.drawOn(barcode_canvas, x, y)
            barcode_canvas.drawString((x + .70 * inch), (y - .15 * inch), record)
            barcode_canvas.drawString((x + .90 * inch), (y - .3 * inch), "Tk " + str(price).split('.')[0])
            if c < ((3 * 9) - 1):
                c += 1
            else:
                c = 0
                barcode_canvas.showPage()

            
        barcode_canvas.save()
        buffer.seek(0)
        barcode_canvas.drawString((x + .01 * inch), (y - .5 * inch), "..................")
        
    return FileResponse(buffer, as_attachment=True, filename='barcode.pdf')