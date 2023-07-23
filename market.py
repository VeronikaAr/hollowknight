import re
from random import randint
from datetime import datetime, timedelta
from flask import Flask, render_template, request, url_for, redirect, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from kodland_db import db

app = Flask(__name__)

all_orders = []

app.config.update(
    SECRET_KEY='WOW SUCH SECRET'
)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class User(UserMixin):
    def __init__(self, id):
        self.id = id


@login_manager.user_loader
def load_user(login):
    if login == 'Doll':
        return User(login)


@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/order', methods=['GET', 'POST'])
@login_required
def order():
    if request.method == 'POST':
        for key in request.form:
            if request.form[key] == '':
                return render_template('order.html', error='Не все поля заполнены!')
            if key == 'email':
                if not re.match('\w+@\w+\.(ru|com)', request.form[key]):
                    return render_template('order.html', error='Неправильный формат почты')
            if key == 'phone_number':
                if not re.match('\+7\d{9}', request.form[key]):
                    return render_template('order.html', error='Неправильный формат номера телефона')
        
        cart_data = db.cart.get_all()
        order_data = db.orders.get_all()

        id_ = order_data[-1].id + 1 if order_data else 1
        for row in cart_data:
            item = {'id': id_, 'item_id': row.item_id, 'amount': row.amount}
            db.orders.put(item)

        for row in cart_data:
            db.cart.delete('item_id', row.item_id)
        return redirect(url_for('cart'))

    return render_template('order.html')

@app.route('/api/orders')
def api_orders():
    return jsonify(all_orders)

@app.route('/regist', methods=['GET', 'POST'])
def regist():
    if request.method == 'POST':
        for key in request.form:
            if request.form[key] == '':
                return render_template('regist.html', message='Все поля должны быть заполнены!')

        row = db.users.get('login', request.form['login'])
        if row:
            return render_template('regist.html', message='Такой пользователь уже существует!')
            
        if request.form['password'] != request.form['password_check']:
            return render_template('regist.html', message='Пароли не совпадают')
        data = dict(request.form)
        data.pop('password_check')
        db.users.put(data=data)
        return render_template('regist.html', message='Регистрация прошла успешно')
    return render_template('regist.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    login = 'Doll'
    password = '123467'
    if request.method == 'POST':
        if request.form['login'] == login and request.form['password'] == password:
            user = User(login) # Создаем пользователя
            login_user(user) # Логинем пользователя
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Неправильный логин или пароль')
    return render_template('login.html')

@app.route('/order_list')
@login_required
def order_list():
    return render_template('order_list.html')

@app.route('/products', methods=['GET', 'POST'])
def products():
    if request.method == 'POST':
        item_id = request.form['item_id']
        row = db.cart.get('item_id', item_id)
        if not row:
            data = {'item_id':item_id, 'amount':1}
            db.cart.put(data)
        else:
            data = {'item_id':item_id, 'amount':row.amount+1}
            db.cart.delete('item_id', item_id)
            db.cart.put(data)

    data = db.items.get_all()
    return render_template('products.html', data=data) 

@app.route('/contacts')
@login_required
def contacts():
    return render_template('contacts.html')

@app.route('/about')
@login_required
def about():
    return render_template('about.html')

@app.route('/cart', methods=['GET', 'POST'])
def cart():
    if request.method == 'POST':
        # Дополнительная логика
        return redirect(url_for('order'))
    
    data = db.cart.get_all()
    total_sum = 0
    for row in data:
        item_row = db.items.get('id', row.item_id)
        row.name = item_row.name
        row.description = item_row.description
        row.price = item_row.price
        row.total = row.amount * item_row.price
        total_sum += row.total
    return render_template('cart.html', data=data, total_sum=total_sum)
    


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return render_template('end.html')

if __name__ == "__main__":
    app.run()