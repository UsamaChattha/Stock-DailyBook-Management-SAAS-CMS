from flask import Flask, request, render_template, session, redirect, url_for, flash, jsonify, make_response
from flask_pymongo import PyMongo
import json

from werkzeug.security import check_password_hash

import db_mongo
from datetime import datetime
from dateutil.relativedelta import *

from trail_balance_print import create_trail_balance_pdf
from ledger_details_print import create_ledger_details_pdf

app = Flask('__name__')
app.config['MONGO_URI'] = '<---YOUR_Mongo DB Connection String--->'
app.config['SECRET_KEY'] = '<---YOUR_SECRET_FORM_KEY--->'
mongo = PyMongo(app)



@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/logout', methods=['GET'])
def logout():
    if 'user' in session:
        session.pop('user', None)
    return redirect(url_for('login'))


@app.route('/index')
def index():
    if 'user' not in session:
        return  redirect(url_for('login'))
    user = session['user']
    return render_template('index.html', user=user)


@app.route('/error')
def error():
    return render_template('500.html')


@app.route('/buyers')
def buyers():
    if 'user' not in session:
        return  redirect(url_for('login'))
    user = session['user']
    try:
        # read file
        cities = get_cities_from_file()
        buyers = db_mongo.get_buyers(mongo)

        edit_id = request.args.get('id')
        edit_buyer = None
        if edit_id != None:
            edit_buyer = db_mongo.retrieve_one_buyer(mongo, edit_id)

        return render_template('buyers.html', user=user, cities=cities, buyers=buyers, edit_buyer=edit_buyer)
    except:
        return redirect(url_for('error'))


@app.route('/production')
def production():
    if 'user' not in session:
        return  redirect(url_for('login'))
    user = session['user']

    own = db_mongo.retrieve_own(mongo)
    products = db_mongo.retrieve_product(mongo)
    productions = db_mongo.retrieve_production(mongo)

    edit_id = request.args.get('id')
    edit_production = None
    if edit_id != None or edit_id == '':
        edit_production = db_mongo.retrieve_one_production(mongo, edit_id)
    return render_template('production.html', user=user, products=products, productions=productions, edit_production=edit_production, own=own[0])


@app.route('/items')
def items():
    if 'user' not in session:
        return  redirect(url_for('login'))
    user = session['user']
    products = db_mongo.retrieve_product(mongo)
    edit_id = request.args.get('id')
    edit_product = None
    if edit_id != None or edit_id == '':
        edit_product = db_mongo.retrieve_one_product(mongo, edit_id)
    return render_template('items.html', user=user, products=products, edit_product=edit_product)


@app.route('/')
@app.route('/sales')
def sales():
    if 'user' not in session:
        return  redirect(url_for('login'))

    user = session['user']
    sales = db_mongo.retrieve_sale(mongo)
    buyers = db_mongo.get_buyers(mongo)
    own = db_mongo.retrieve_own(mongo)
    items = db_mongo.retrieve_product(mongo)
    edit_id = request.args.get('id')
    productions = db_mongo.retrieve_available_production(mongo)

    edit_sales = None
    buyer = None
    if edit_id != None:
        edit_sales = db_mongo.retrieve_one_sale(mongo, edit_id)
        buyer = db_mongo.retrieve_one_buyer(mongo, edit_sales['Buyer_Id'])

    return render_template('sales.html', user=user, buyers=buyers, buyer=buyer, edit_sales=edit_sales, sales=sales,
                           items=items, own=own[0], productions=productions)


@app.route('/DayBook')
def DayBook():
    if 'user' not in session:
        return  redirect(url_for('login'))
    user = session['user']
    buyer = db_mongo.get_buyers_list(mongo)
    edit_date = request.args.get('inputdate')
    edit_new_date = None
    if edit_date != None:
        edit_new_date = edit_date.split('-')[2] + '/' + edit_date.split('-')[1] + '/' + edit_date.split('-')[0]
        edit_new_date = db_mongo.get_day_book(mongo, edit_new_date)
    return render_template('DayBook.html', user=user, buyer=buyer, edit_date=edit_date, edit_new_date=edit_new_date)


@app.route('/trail_balance')
def trail_balance():
    if 'user' not in session:
        return  redirect(url_for('login'))
    user = session['user']
    if request.args.get('from') is None or request.args.get('to') is None:
        now = datetime.now()
        to_date = now.strftime("%d/%m/%Y")
        to_ui_date = to_date.split('/')[2] + '-' + to_date.split('/')[1] + '-' + to_date.split('/')[0]
        from_date = now + relativedelta(months=-1)
        from_date = from_date.strftime("%d/%m/%Y")
        from_ui_date = from_date.split('/')[2] + '-' + from_date.split('/')[1] + '-' + from_date.split('/')[0]
    else:
        date = request.args.get('from')
        from_ui_date = date
        from_date = date.split('-')[2] + '/' + date.split('-')[1] + '/' + date.split('-')[0]
        date = request.args.get('to')
        to_ui_date = date
        to_date = date.split('-')[2] + '/' + date.split('-')[1] + '/' + date.split('-')[0]

    final_data = db_mongo.get_trail_balance_data(from_date, to_date, mongo)
    buyers = db_mongo.get_buyers_list(mongo)

    return render_template('trail_balance.html', user=user, to_date=to_ui_date, from_date=from_ui_date,
                           data=final_data, buyers=buyers)


@app.route('/trail_balance_print')
def trail_balance_print():
    if 'user' not in session:
        return  redirect(url_for('login'))
    user = session['user']
    if request.args.get('from') is not None and request.args.get('to') is not None:
        date = request.args.get('from')
        from_ui_date = date
        from_date = date.split('-')[2] + '/' + date.split('-')[1] + '/' + date.split('-')[0]
        date = request.args.get('to')
        to_ui_date = date
        to_date = date.split('-')[2] + '/' + date.split('-')[1] + '/' + date.split('-')[0]

        final_data = db_mongo.get_trail_balance_data(from_date, to_date, mongo)
        buyers = db_mongo.get_buyers_list(mongo)

        now = datetime.now()
        dt_string = now.strftime("%d-%m-%Y")

        pdf = create_trail_balance_pdf("Trail Balance", from_date.replace("/", "-"), to_date.replace("/", "-"), dt_string, final_data, buyers)

        response = make_response(pdf.output(dest='S').encode('latin-1'))
        response.headers.set('Content-Disposition', 'attachment', filename='Trail_Balance_' + from_ui_date + "_to_" + to_ui_date + ".pdf")
        response.headers.set('Content-Type', 'application/pdf')
        return response

    return redirect(url_for('trail_balance', user=user))


@app.route('/ledger')
def ledger():
    if 'user' not in session:
        return  redirect(url_for('login'))
    user = session['user']
    buyers = db_mongo.get_buyers_list(mongo)
    return render_template('ledger.html', user=user, buyers=buyers)


@app.route('/ledger_details')
def ledger_details():
    if 'user' not in session:
        return  redirect(url_for('login'))

    user = session['user']

    if request.args.get('BuyerId') is None or request.args.get('StartDate') is None or request.args.get('EndDate') is None:
        return redirect(url_for('ledger'))

    buyer_id = request.args.get('BuyerId')
    start_date = request.args.get('StartDate')
    end_date = request.args.get('EndDate')

    start_date = start_date.split('-')[2] + '/' + start_date.split('-')[1] + '/' + start_date.split('-')[0]
    end_date = end_date.split('-')[2] + '/' + end_date.split('-')[1] + '/' + end_date.split('-')[0]

    start_ui_date = start_date.split('/')[2] + '-' + start_date.split('/')[1] + '-' + start_date.split('/')[0]
    end_ui_date = end_date.split('/')[2] + '-' + end_date.split('/')[1] + '-' + end_date.split('/')[0]

    buyer = db_mongo.retrieve_one_buyer(mongo, buyer_id)
    final_data = db_mongo.get_ledger_data(start_date, end_date, buyer_id, mongo)

    return render_template('ledger_details.html', user=user, start_date=start_ui_date, end_date=end_ui_date,
                           buyer=buyer, data=final_data, start_date_print=start_date, end_date_print=end_date)



@app.route('/ledger_details_print')
def ledger_details_print():
    if 'user' not in session:
        return  redirect(url_for('login'))

    id = request.args.get('id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    final_data = db_mongo.get_ledger_data(start_date, end_date, id, mongo)
    buyer = db_mongo.retrieve_one_buyer(mongo, id)

    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y")

    pdf = create_ledger_details_pdf("General Ledger", start_date.replace("/", "-"), end_date.replace("/", "-"),
                                    dt_string, final_data, buyer)

    response = make_response(pdf.output(dest='S').encode('latin-1'))
    response.headers.set('Content-Disposition', 'attachment', filename='Ledger_Details_' + start_date.replace("/", "-")
                                                                       + "_to_" + end_date.replace("/", "-") + ".pdf")
    response.headers.set('Content-Type', 'application/pdf')
    return response


@app.route('/daily_transaction')
def daily_transaction():
    if 'user' not in session:
        return  redirect(url_for('login'))
    user = session['user']
    return render_template('daily_transaction.html', user=user)


@app.route('/register_user', methods=['POST'])
def register_user():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    if password != confirm_password:
        flash('Password and Confirm Password are Not Same!')
        return redirect(url_for('register'))

    if db_mongo.get_user_by_mail(email, mongo) != None:
        flash('Email Already Exists!')
        return redirect(url_for('register'))

    db_mongo.insert_user(name, email, password, mongo)

    return redirect(url_for('login'))


@app.route('/login_user', methods=['POST'])
def login_user():
    email = request.form['email']
    password = request.form['password']

    user = db_mongo.get_user_by_mail(email, mongo)
    if user == None:
        flash('Email/Password is not Correct!')
        return redirect(url_for('login'))

    if check_password_hash(user['Password'], password) and user['Type'] == 'Admin':
        user['_id'] = str(user['_id'])
        session['user'] = user
        return redirect(url_for('sales'))

    flash('Email/Password is not Correct!')
    return redirect(url_for('login'))


@app.route('/insert_buyer', methods=["POST"])
def insert_buyer():
    name = request.form['name']
    email = request.form['email']
    address = request.form['address']
    contact = request.form['contact']
    city = request.form['city']
    type = request.form['type']


    db_mongo.insert_buyer(name, address, email,contact, city, type, mongo)
    flash('Buyer/Supplier is inserted successfully')
    return redirect(url_for('buyers'))


@app.route('/insert_item', methods=["POST"])
def insert_item():
    name = request.form['name']
    item_group = request.form['group']
    default_supplier = request.form['DefaultSupplier']
    carton_size = request.form['CartonSize']
    pack_size = request.form['PackSize']
    net_price = request.form['NetPrice']
    discount = request.form['discount']
    tax = request.form['tax']
    retail = request.form['RetailPrice']

    db_mongo.insert_item(name, item_group,default_supplier, carton_size, pack_size, net_price, discount, tax, retail, mongo)

    flash('Item/Product is inserted successfully')
    return redirect(url_for('items'))


@app.route('/insert_production', methods=["POST"])
def insert_production():
    item_id = request.form['ProductName']
    user_id = request.form['company_id']
    doc_no = request.form['DocNo']
    expiry_date = request.form['ExpiryDate']
    pack_size = request.form['PackSize']
    manufacture_batch = request.form['batch']
    quantity = request.form['quantity']
    bonus = request.form['bonus']
    company = request.form['company_id']

    product = db_mongo.retrieve_one_product(mongo, item_id)
    item_name = product['Name']

    db_mongo.insert_Production(doc_no, expiry_date, item_id, pack_size, manufacture_batch, quantity, bonus, company, mongo)
    db_mongo.insert_items_debit_credit(item_id, item_name, pack_size, manufacture_batch, quantity, "0", user_id,
                                       "Credit", "Production", mongo)

    flash('Production is inserted successfully')
    return redirect(url_for('production'))


@app.route('/insert_sales', methods=["POST"])
def insert_sales():
    table = request.form.getlist('table')
    item_ids = request.form.getlist('item_id')
    production_ids = request.form.getlist('production_id')

    buyer_id = request.form['BuyerId']

    net_price = 0

    all_data = []
    for i, row in enumerate(table):
        row_data = row.split('%')
        net_price = net_price + int(row_data[5].strip())
        all_data.append(
            {
                'item_id': item_ids[i],
                'item_name': row_data[0].strip(),
                'batch_no': row_data[1].strip(),
                'sale_price': row_data[2].strip(),
                'pack_size': row_data[3].strip(),
                'quantity': row_data[4].strip(),
                'net_price': row_data[5].strip(),
                'discount': row_data[6].strip(),
                'expiry_date': row_data[7].strip(),
                'production_id': production_ids[i]
            }
        )

        db_mongo.insert_items_debit_credit(item_ids[i], row_data[0].strip(), row_data[3].strip(),
                                           row_data[1].strip(), row_data[4].strip(), row_data[5].strip(), buyer_id,
                                           "Debit", "Production", mongo)
        db_mongo.update_production_quantity(production_ids[i], int(row_data[4].strip()), int(row_data[3].strip()), mongo)

    sale_id = db_mongo.insert_Sales(buyer_id, all_data, net_price, mongo)
    db_mongo.insert_sales_debit_credit(buyer_id, sale_id, net_price, mongo)

    flash('Sale is Inserted Successfully!')
    return redirect(url_for('sales'))


@app.route('/insert_book', methods=["POST"])
def insert_book():
    debit_table = request.form.getlist('debit_table')
    credit_table = request.form.getlist('credit_table')

    date = request.form['book_date']
    date = date.split('-')[2] + '/' + date.split('-')[1] + '/' + date.split('-')[0]

    db_mongo.delete_date_debit_credit(date, mongo)

    for i, row in enumerate(debit_table):
        row_data1 = row.split('%')
        if row_data1[1].strip() != '' and row_data1[0].strip() != '' and row_data1[2].strip() != '':
            user = db_mongo.retrieve_one_buyer(mongo, row_data1[2].strip())
            db_mongo.insert_book("Debit", "Day_Book", row_data1[2].strip(), row_data1[0].strip(), row_data1[1].strip(),
                                 user['Name'], date, mongo)

    for i, row in enumerate(credit_table):
        row_data2 = row.split('%')
        if row_data2[1].strip() != '' and row_data2[0].strip() != '' and row_data2[2].strip() != '':
            user = db_mongo.retrieve_one_buyer(mongo, row_data2[2].strip())
            db_mongo.insert_book("Credit", "Day_Book", row_data2[2].strip(), row_data2[0].strip(), row_data2[1].strip(),
                                 user['Name'], date, mongo)

    flash('DayBook is inserted successfully')
    return redirect(url_for('DayBook'))


@app.route('/edit_buyer', methods=["POST"])
def edit_buyer():
    name = request.form['name']
    email = request.form['email']
    address = request.form['address']
    contact = request.form['contact']
    city = request.form['city']
    type = request.form['type']

    id = request.form['id']

    db_mongo.update_buyer(id, name, address, email,contact, city,type, mongo)

    flash('Buyer/Supplier is Updated Successfully')
    return redirect(url_for('buyers'))


@app.route('/delete_item', methods=["GET"])
def delete_item():
    id = request.args.get('id')

    db_mongo.delete_one_product(id, mongo)

    flash('Item is Deleted Successfully!')
    return redirect(url_for('items'))


@app.route('/edit_product', methods=["POST"])
def edit_product():
    name = request.form['name']
    item_group = request.form['group']
    default_supplier = request.form['DefaultSupplier']
    carton_size = request.form['CartonSize']
    pack_size = request.form['PackSize']
    net_price = request.form['NetPrice']
    discount = request.form['discount']
    tax = request.form['tax']
    retail = request.form['RetailPrice']

    id = request.form['id']

    db_mongo.update_product(id, name, item_group, default_supplier, carton_size, pack_size, net_price, discount, tax, retail, mongo)

    flash('Buyer/Supplier is Updated Successfully')
    return redirect(url_for('items'))


@app.route('/edit_production', methods=["POST"])
def edit_production():
    item_id = request.form['ProductName']
    doc_no = request.form['DocNo']
    expiry_date = request.form['ExpiryDate']
    pack_size = request.form['PackSize']
    manufacture_batch = request.form['batch']
    quantity = request.form['quantity']
    bonus = request.form['bonus']
    id = request.form['id']
    user_id = request.form['company_id']


    product = db_mongo.retrieve_one_product(mongo, item_id)
    production = db_mongo.retrieve_one_production(mongo, id)

    db_mongo.insert_items_debit_credit(production['Product_Name'], production['Name'], production['Pack_Size'],
                                       production['Manufacture_Batch'], production['Quantity'], "0", user_id,
                                       "Debit", "Production", mongo)

    db_mongo.insert_items_debit_credit(item_id, product['Name'], pack_size, manufacture_batch, quantity, "0", user_id,
                                       "Credit", "Production", mongo)

    db_mongo.update_production(id, doc_no, expiry_date, item_id, pack_size, manufacture_batch, quantity, bonus, mongo)

    flash('production is Updated Successfully')
    return redirect(url_for('production'))


@app.route('/edit_sales', methods=["POST"])
def edit_sales():
    table = request.form.getlist('table')
    item_ids = request.form.getlist('item_id')
    production_ids = request.form.getlist('production_id')

    buyer_id = request.form['BuyerId']
    id = request.form['id']

    sales = db_mongo.retrieve_one_sale(mongo, id)
    for sale in sales['Sales']:
        db_mongo.insert_items_debit_credit(sale['item_id'], sale['item_name'], sale['pack_size'],
                                           sale['batch_no'], sale['quantity'], sale['net_price'], buyer_id,
                                           "Credit", "Production", mongo)

        quantity = -1 * int(sale['quantity'])
        pack_size = -1 * int(sale['pack_size'])
        db_mongo.update_production_quantity(sale['production_id'], quantity, pack_size, mongo)

    db_mongo.delete_sale_return_debit_credit(id, 'Debit', 'Sale', mongo)

    net_price = 0

    all_data = []
    for i, row in enumerate(table):
        row_data = row.split('%')
        net_price = net_price + int(row_data[5].strip())
        all_data.append(
            {
                'item_id': item_ids[i],
                'item_name': row_data[0].strip(),
                'batch_no': row_data[1].strip(),
                'sale_price': row_data[2].strip(),
                'pack_size': row_data[3].strip(),
                'quantity': row_data[4].strip(),
                'net_price': row_data[5].strip(),
                'discount': row_data[6].strip(),
                'expiry_date': row_data[7].strip(),
                'production_id': production_ids[i]
            }
        )

        db_mongo.insert_items_debit_credit(item_ids[i], row_data[0].strip(), row_data[3].strip(),
                                           row_data[1].strip(), row_data[4].strip(), row_data[5].strip(), buyer_id,
                                           "Debit", "Production", mongo)
        db_mongo.update_production_quantity(production_ids[i], int(row_data[4].strip()), int(row_data[3].strip()),
                                            mongo)


    db_mongo.update_sales(id, buyer_id, all_data, net_price, mongo)
    db_mongo.insert_sales_debit_credit(buyer_id, id, net_price, mongo)

    flash('Item/Product is updated successfully')
    return redirect(url_for('sales'))


def get_cities_from_file():
    with open('static/citiesName.json', 'r', encoding='utf-8', errors='ignore') as myfile:
        data = myfile.read()
        # parse file
        return json.loads(data)['cities']


@app.route('/delete_buyer', methods=["GET"])
def delete_buyer():
    id = request.args.get('id')
    db_mongo.delete_one_buyer(mongo, id)
    flash('Buyer is deleted Successfully.')
    return redirect(url_for('buyers'))


@app.route('/get_item_group', methods=['POST'])
def get_item_group():
    default_supplier = request.form['DefaultSupplier']
    if default_supplier == 'Medicine':
        own = db_mongo.retrieve_own(mongo)

        new_list = []
        for o in own:
            new_list.append(encode(o))

        return jsonify({'OWN': new_list})
    else:
        Supplier = db_mongo.retrieve_supplier(mongo)
        new_list = []
        for o in Supplier:
            new_list.append(encode(o))

        return jsonify({'Supplier': new_list})


@app.route('/get_buyer', methods=['POST'])
def get_buyer():
    address = request.form['address']
    Address = db_mongo.retrieve_address(mongo, address)
    Address['_id'] = str(Address['_id'])
    return jsonify({'success': Address})


@app.route('/get_items', methods=['POST'])
def get_items():
    item_id = request.form['ProductName']
    ProductName = db_mongo.retrieve_name_production(mongo, item_id)
    new_list = []
    for o in ProductName:
        new_list.append(encode(o))
    return jsonify({'success': new_list})


def encode(o):
    if '_id' in o:
        o['_id'] = str(o['_id'])
    return o


if __name__ == '__main__':
    app.run(debug=True)