
def full_profile(customer):
    return {
        "id" :customer.id,
        "username" :customer.username,
        "email" :customer.email,
        "phone_number" :customer.profile.phone_number,
        "city" :customer.profile.city,
        "region" :customer.profile.region,
        "created_at" :customer.created_at
    }

def full_order(new_order, order_item, item):
    return {
                    "orderitem_id": order_item.id,
                    "order_id": new_order.id,
                    "item_id": order_item.item_id,
                    "item_name": item.name,
                    "item_image": item.image,
                    "quantity": order_item.quantity,
                    "total_price": order_item.total_price,
                    "order_date": new_order.order_date
            }

def format_notification(products, prices, _line_items):
    _notification=''
    index=0
    for product in products:
        if product.id == prices[index].product and prices[index].id == _line_items[index]['price']:
            _notification+=f" {product.name} x {_line_items[index]['quantity']}   "
            index+=1
    return _notification

import random
import string

def generate_code(length):
  # create a list of all possible characters (numbers and letters)
  characters = string.digits + string.ascii_letters

  # create an empty string to store the code
  code = ""

  # choose `length` random characters from the list and add them to the code string
  for i in range(length):
    code += random.choice(characters)

  return code

import datetime

def convert_time(time: datetime):
  default_time = datetime.datetime.fromisoformat(time)
  # convert default time to UTC
  utc_time = default_time.astimezone(datetime.timezone.utc)
  current_time = datetime.datetime.now(datetime.timezone.utc)

  time_diff = current_time - utc_time

  if time_diff.total_seconds() < 60:
      return str(int(time_diff.total_seconds())) + "s ago"
  elif time_diff.total_seconds() < 3600:
      return str(int(time_diff.total_seconds() / 60)) + "mins ago"
  elif time_diff.total_seconds() < 86400:
      return str(int(time_diff.total_seconds() / 3600)) + "hr(s) ago"
  elif time_diff.days == 1:
      return "yesterday"
  else:
      return str(time_diff.days) + "days ago"
