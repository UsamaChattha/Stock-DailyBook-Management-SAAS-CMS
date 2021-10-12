from bson import ObjectId
from datetime import datetime
import pymongo
from werkzeug.security import generate_password_hash

import db_mongo


def insert_user(name, email, password, mongo):
    hashpass = generate_password_hash(password, method='sha256')
    mongo.db.user.insert_one({
        'Name': name,
        'Email': email,
        'Password': hashpass,
        'Type': 'Admin',
    })


def insert_buyer(name, address, email, contact, city, type, mongo):
    mongo.db.buyers.insert_one({
        'Name': name,
        'Address': address,
        'Email': email,
        'Contact': contact,
        'City': city,
        'Type': type,
    })


def insert_item(name, item_group,default_supplier, carton_size, pack_size, net_price, discount, tax, retail, mongo):
    mongo.db.items.insert_one({
        'Name': name,
        'Item_Group': item_group,
        'Default_Supplier': default_supplier,
        'Carton_Size': carton_size,
        'Pack_Size': pack_size,
        'Net_Price': net_price,
        'Discount': discount,
        'Tax': tax,
        'Retail': retail
    })


def insert_Production(doc_no, expiry_date, item_id, pack_size, manufacture_batch, quantity, bonus, company, mongo):
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y")
    product = db_mongo.retrieve_one_product(mongo, item_id)
    mongo.db.production.insert_one({
        'Name': product['Name'],
        'Doc_No': doc_no,
        'Expiry_Date': expiry_date,
        'Product_Name': item_id,
        'Pack_Size': pack_size,
        'Manufacture_Batch': manufacture_batch,
        'Quantity': quantity,
        'Net_Price': product['Net_Price'],
        'Discount': product['Discount'],
        'Bonus': bonus,
        'Company': company,
        'Date_Time': dt_string,
        'Status': 'Available'
    })


def insert_items_debit_credit(item_id, item_name, pack_size, manufacture_batch, quantity, net_price, user_id,
                             pay_type, type, mongo):
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y")
    mongo.db.items_debit_credit.insert_one({
        'Item_Id': item_id,
        'Product_Name': item_name,
        'Pack_Size': pack_size,
        'Manufacture_Batch': manufacture_batch,
        'Quantity': quantity,
        'Net_Price': net_price,
        'Date_Time': dt_string,
        'Pay_Type': pay_type,
        'Type': type,
        'Date_Time': dt_string,
        'User_Id': user_id
    })


def insert_sales_debit_credit(buyer_id, sale_id, net_price, mongo):
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y")
    mongo.db.items_debit_credit.insert_one({
        'Date_Time': dt_string,
        'Pay_Type': "Debit",
        'Type': "Sale",
        'Date_Time': dt_string,
        'User_Id': buyer_id,
        'Sales_Id': sale_id,
        'Amount': net_price,
    })


def delete_sale_return_debit_credit(id, pay_type, type, mongo):
    mongo.db.items_debit_credit.delete_many(
        {"$and":
            [
                {"Pay_Type": pay_type},
                {"Type": type},
                {"Sales_Id": id}
            ]
        }
    )


def delete_date_debit_credit(date, mongo):
    mongo.db.items_debit_credit.delete_many(
        {"$and":
            [
                {"Type": "Day_Book"},
                {"Date_Time": date}
            ]
        }
    )


def insert_book(pay_type, type, user_id, amount, remarks, name, date, mongo):
    dt_string = date
    mongo.db.items_debit_credit.insert_one({
        'Name': name,
        'Date_Time': dt_string,
        'Pay_Type': pay_type,
        'Type': type,
        'User_Id': user_id,
        'Amount': amount,
        'Remarks': remarks,
    })


def get_trail_balance_data(start_date, end_date, mongo):

    data = mongo.db.items_debit_credit.find({
                "$or":
                    [
                        {"Type": "Day_Book"},
                        {"Type": "Sale"}
                    ]
            })

    final_data = []
    st_date = datetime.strptime(start_date, "%d/%m/%Y")
    en_date = datetime.strptime(end_date, "%d/%m/%Y")
    for d in data:
        current_date = datetime.strptime(d['Date_Time'], "%d/%m/%Y")
        if current_date >= st_date and current_date <= en_date:
            final_data.append(d)

    return final_data


def get_ledger_data(start_date, end_date, id, mongo):

    data = mongo.db.items_debit_credit.find({
                "$or":
                    [
                        {"Type": "Day_Book"},
                        {"Type": "Sale"}
                    ]
            })

    final_data = []
    st_date = datetime.strptime(start_date, "%d/%m/%Y")
    en_date = datetime.strptime(end_date, "%d/%m/%Y")
    for d in data:
        current_date = datetime.strptime(d['Date_Time'], "%d/%m/%Y")
        if current_date >= st_date and current_date <= en_date and d['User_Id'] == id:
            final_data.append(d)

    return final_data


def insert_Sales(buyer_id, all_data, net_price, mongo):
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y")
    mongo.db.sales.insert_one({
        'Date_Time': dt_string,
        'Buyer_Id': buyer_id,
        'Sales': all_data,
        'Net_Price': net_price
    })

    Sales = mongo.db.sales.find_one(sort=[('_id', pymongo.DESCENDING)])

    return str(Sales['_id'])


def update_buyer(id, name, address, email, contact, city, type, mongo):
    mongo.db.buyers.update_one({'_id': ObjectId(id)},
                               {'$set':
                                   {
                                       'Name': name,
                                       'Address': address,
                                       'Email': email,
                                       'Contact': contact,
                                       'City': city,
                                       'Type': type,
                                   }
                               })


def update_production(id, doc_no, expiry_date, item_id, pack_size, manufacture_batch, quantity, bonus, mongo):
    mongo.db.production.update_one({'_id': ObjectId(id)},
                               {'$set':
                                   {
                                       'Doc_No': doc_no,
                                       'Expiry_Date': expiry_date,
                                       'Product_Name': item_id,
                                       'Pack_Size': pack_size,
                                       'Manufacture_Batch': manufacture_batch,
                                       'Quantity': quantity,
                                       'Bonus': bonus,
                                   }
                               })


def update_product(id, name, item_group, default_supplier, carton_size, pack_size, net_price, discount, tax, retail, mongo):
    mongo.db.items.update_one({'_id': ObjectId(id)},
                               {'$set':
                                   {
                                       'Name': name,
                                       'Item_Group': item_group,
                                       'Default_Supplier': default_supplier,
                                       'Carton_Size': carton_size,
                                       'Pack_Size': pack_size,
                                       'Net_Price': net_price,
                                       'Discount': discount,
                                       'Tax': tax,
                                       'Retail': retail
                                   }
                               })


def update_sales(id, buyer_id, all_data, net_price, mongo):

    mongo.db.sales.update_one({'_id': ObjectId(id)},
                               {'$set':
                                   {
                                       'Date_Time': datetime.now().strftime("%d/%m/%Y"),
                                       'Buyer_Id': buyer_id,
                                       'Sales': all_data,
                                       'Net_Price': net_price
                                   }
                               })


def update_production_quantity(id, quantity, pack_size, mongo):
    production = mongo.db.production.find_one({'_id': ObjectId(id)})

    if production != None:
        old_quantity = production['Quantity']
        old_packsize = production['Pack_Size']

        mongo.db.production.update_one({'_id': ObjectId(id)},
                                   {'$set':
                                       {
                                           'Quantity': int(old_quantity) - int(quantity),
                                           'Pack_Size': int(old_packsize) - int(pack_size)
                                       }
                                   })


def get_buyers_list(mongo):
    buyers = mongo.db.buyers.find()
    return list(buyers)


def get_buyers(mongo):
    buyers = mongo.db.buyers.find({'Type': {'$ne': 'own'}})
    return list(buyers)


def get_day_book(mongo, date):
    book = mongo.db.items_debit_credit.find(
        {"$and":
             [
                 {"Type": "Day_Book"},
                 {"Date_Time": date}
             ]
        })
    return list(book)


def delete_one_buyer(mongo, id):
    mongo.db.buyers.delete_one({'_id': ObjectId(id)})


def delete_one_product(id, mongo):
    mongo.db.items.delete_one({'_id': ObjectId(id)})


def retrieve_one_buyer(mongo, id):
    buyer = mongo.db.buyers.find_one({'_id': ObjectId(id)})
    return buyer


def retrieve_own(mongo):
    buyer = mongo.db.buyers.find({'Type': 'own'})
    return list(buyer)


def retrieve_supplier(mongo):
    supplier = mongo.db.buyers.find({'Type': 'Suppliers'})
    return list(supplier)


def retrieve_product(mongo):
    products = mongo.db.items.find()
    return list(products)


def retrieve_sale(mongo):
    sale = mongo.db.sales.find()
    return list(sale)


def retrieve_one_sale(mongo, id):
    sale = mongo.db.sales.find_one({'_id': ObjectId(id)})
    return sale


def retrieve_one_product(mongo, id):
    product = mongo.db.items.find_one({'_id': ObjectId(id)})
    return product


def retrieve_production(mongo):
    production = mongo.db.production.find()
    return list(production)


def retrieve_available_production(mongo):
    production = mongo.db.production.find({'Status': 'Available'})
    return list(production)


def retrieve_one_production(mongo, id):
    production = mongo.db.production.find_one({'_id': ObjectId(id)})
    return production


def retrieve_address(mongo, address):
    address = mongo.db.buyers.find_one({'_id': ObjectId(address)})
    return address


def retrieve_name_production(mongo, item_id):
    item_id = mongo.db.production.find({'Product_Name': item_id})
    return item_id


def get_user_by_mail(email, mongo):
    user = mongo.db.user.find_one({'Email': email})
    return user
