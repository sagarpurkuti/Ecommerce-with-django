from django.shortcuts import render, redirect, get_object_or_404
# from django.http import HttpResponse, JsonResponse
from carts.models import CartItem, Cart
from .forms import OrderForm
from .models import Order, Payment, OrderProduct
from store.models import Product
import datetime
import json
import requests
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

#yt reference
from django.views import View
import hmac
import hashlib
import uuid
import base64
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from django.contrib import messages



def payment_success(request):

    data = request.GET.get('data')
    if not data:
        return redirect('payment_failure')
        
    try:
        decoded_data_str = base64.b64decode(data).decode("utf-8")
        decoded_data = json.loads(decoded_data_str)
    except (base64.binascii.Error, json.JSONDecodeError):
        return redirect('payment_failure')
    
    product_code = 'EPAYTEST'
    data_to_sign = (
        f"transaction_code={decoded_data.get('transaction_code')},"
        f"status={decoded_data.get('status')},"
        f"total_amount={str(decoded_data.get('total_amount')).replace(',', '')},"
        f"transaction_uuid={decoded_data.get('transaction_uuid')},"
        f"product_code={product_code},"
        f"signed_field_names=transaction_code,status,total_amount,transaction_uuid,product_code,signed_field_names"
    )
    computed_signature = gensignature(data_to_sign)
    
    # Check if the signature matches
    if str(decoded_data.get('signature')) != computed_signature:
        return redirect('payment_failure')
    
    # Optionally, you can set a success message here
    messages.success(request, "Payment successful")
    
    # Extract necessary fields from the decoded data
    transaction_uuid = decoded_data.get('transaction_uuid')
    total_amount = decoded_data.get('total_amount')
    status = decoded_data.get('status')
    
    if not all([transaction_uuid, total_amount, status]):
        return redirect('payment_failure')
    
    if status.upper() in ["COMPLETE", "SUCCESS"]:
        try:
            with transaction.atomic():
                # Save payment
                payment = Payment.objects.create(
                    user=request.user,
                    payment_id=transaction_uuid,
                    payment_method="eSewa",
                    amount_paid=total_amount,
                    status="Completed"
                )
    
                # Update order
                order = Order.objects.get(user=request.user, is_ordered=False)
                order.payment = payment
                order.is_ordered = True
                order.status = 'New'
                order.save()


                #move the cart items to order product table
                cart_items = CartItem.objects.filter(user = request.user)
                for item in cart_items:
                    orderproduct = OrderProduct()
                    orderproduct.order_id = order.id
                    orderproduct.payment = payment
                    orderproduct.user_id = request.user.id
                    orderproduct.product_id = item.product_id
                    orderproduct.quantity = item.quantity
                    orderproduct.product_price = item.product.price
                    orderproduct.ordered = True
                    orderproduct.save()


                    cart_item = CartItem.objects.get(id=item.id)
                    product_variation = cart_item.variations.all()
                    orderproduct = OrderProduct.objects.get(id=orderproduct.id)
                    orderproduct.variation.set(product_variation)
                    orderproduct.save()
                    
                    #reduce the quantity of sold product
                    product = Product.objects.get(id= item.product_id)
                    product.stock -=item.quantity
                    product.save()
 
                # Clear cart
                CartItem.objects.filter(user=request.user).delete()

                #send order recevied email to customer
                mail_subject = 'Order Recevied'
                message      = render_to_string('orders/order_received_email.html',{
                    'user'   : request.user,
                    'order'  : order,
                })
                to_email    = request.user.email
                send_email  = EmailMessage(mail_subject, message, to=[to_email])
                send_email.send()

                # send order number and transaction id back to sendData method via JsonResponse
                data = {
                    'order_number'  :   order.order_number,
                    'transID'       :   payment.payment_id
                }


                try:
                    order = Order.objects.get(order_number=order.order_number, is_ordered=True)
                    ordered_products = OrderProduct.objects.filter(order_id=order.id)

                    subtotal = 0

                    for i in ordered_products:
                        subtotal += i.product_price*i.quantity
                    # payment = Payment.objects.get(payment_id=transID)

                    context = {
                        'order' : order,
                        'ordered_products' : ordered_products,
                        'order_number'     : order.order_number,
                        'transID'          : payment.payment_id,
                        'payment'          : payment,
                        'subtotal'         : subtotal,
                    }
                    return render(request, 'orders/payment_success.html', context)
                except(Payment.DoesNotExist, Order.DoesNotExist):
                    return redirect('home')

    
        except ObjectDoesNotExist:
            return redirect('payment_failure')
    
    return redirect('payment_failure')


def payment_failure(request):
    # You might want to log failed attempts here
    return render(request, 'orders/payment_failure.html')


def gensignature(data_to_sign):
   
    SECRET_KEY = '8gBm/:&EnhH.1/q'
    key = SECRET_KEY.encode("utf-8")
    message = data_to_sign.encode("utf-8")
    hmac_sha256 = hmac.new(key, message, hashlib.sha256)
    digest = hmac_sha256.digest()
    signature = base64.b64encode(digest).decode("utf-8")
    
    return signature


def place_order(request,total=0, quantity=0,):
    current_user  = request.user
    # if the cart count is less than or equal to then redirect back to shop

    cart_items  = CartItem.objects.filter(user=current_user)
    cart_count  = cart_items.count()
    if cart_count<=0:
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total = (cart_item.product.price*cart_item.quantity)
        quantity += cart_item.quantity

    tax = (13 * total)/100
    grand_total = total + tax

  
    if request.method=='POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            #store all the billing informaion inside order table
            data            = Order()
            data.user       = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name  = form.cleaned_data['last_name']
            data.phone      = form.cleaned_data['phone']
            data.email      = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country    = form.cleaned_data['country']
            data.state      = form.cleaned_data['state']
            data.city       = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total= grand_total
            data.tax        = tax
            data.ip         = request.META.get('REMOTE_ADDR')
            data.save()
            # Generate Order Number
            yr = int(datetime.date.today().strftime('%Y'))  # ✅ Gives full year (e.g., 2025)
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d  = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")
            order_number    = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)

            uuid_val = uuid.uuid4()



            secret_key = '8gBm/:&EnhH.1/q'
            # data_to_sign = f"{grand_total}, {uuid_val}, EPAYTEST"
            total_amount = order.order_total
            transaction_uuid = str(uuid_val)
            product_code = 'EPAYTEST'
            # data_to_sign=f"{total_amount},{transaction_uuid},{product_code}"
            data_to_sign = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"


            # data_to_sign = f"total_amount={order.order_total}, transaction_uuid={uuid_val}, product_code=EPAYTEST"
            # data_to_sign = f"{order.order_total},{uuid_val},EPAYTEST"  # Comma-separated without parameter names

            result = gensignature(data_to_sign)

            data = {
            'total_amount': order.order_total,
            'transaction_uuid': str(uuid_val),
            'product_code': 'EPAYTEST',
            'signature': result,
            }

            context ={
                'order':order,
                'cart_items': cart_items,
                'total':total,
                'tax':tax,
                'grand_total':grand_total,
                'data':data,
            }

            return render (request, 'orders/payments.html', context)
    else:
        return redirect('checkout')



