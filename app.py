import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import stripe

stripe_keys = {
  'secret_key': os.environ.get('STRIPE_SECRET_KEY'),
  'publishable_key': os.environ.get('PUBLISHABLE_KEY')
}

stripe.api_key = stripe_keys['secret_key']

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

if os.environ.get('ENV') == 'production':
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://localhost/bitcoin-db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Purchaser(db.Model):

    __tablename__ = "purchasers"

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.Text)
    tokenType = db.Column(db.Text)
    email = db.Column(db.Text)

    billing_name = db.Column(db.Text)
    billing_country = db.Column(db.Text)
    billing_country_code = db.Column(db.Text)
    billing_zip = db.Column(db.Integer)
    billing_address_line_1 = db.Column(db.Text)
    billing_city = db.Column(db.Text)
    billing_state = db.Column(db.Text)

    shipping_name = db.Column(db.Text)
    shipping_country = db.Column(db.Text)
    shipping_country_code = db.Column(db.Text)
    shipping_zip = db.Column(db.Integer)
    shipping_address_line_1 = db.Column(db.Text)
    shipping_city = db.Column(db.Text)
    shipping_state = db.Column(db.Text)

    price_paid = db.Column(db.Text)
    order_quantity = db.Column(db.Integer)
    has_shipped = db.Column(db.Boolean)

    def __init__(self, token, tokenType, email, billing_name, billing_country, billing_country_code, billing_zip, billing_address_line_1, billing_city, billing_state, shipping_name, shipping_country, shipping_country_code, shipping_zip, shipping_address_line_1, shipping_city, shipping_state, price_paid, order_quanity, has_shipped):
        self.token = token
        self.tokenType = tokenType
        self.email = email
        self.billing_name = billing_name
        self.billing_country = billing_country
        self.billing_country_code = billing_country_code
        self.billing_zip = billing_zip
        self.billing_address_line_1 = billing_address_line_1
        self.billing_city = billing_city
        self.billing_state = billing_state
        self.shipping_name = shipping_name
        self.shipping_country = shipping_country
        self.shipping_country_code = shipping_country_code
        self.shipping_zip = shipping_zip
        self.shipping_address_line_1 = shipping_address_line_1
        self.shipping_city = shipping_city
        self.shipping_state = shipping_state
        self.price_paid = price_paid
        self.order_quantity = order_quanity
        self.has_shipped = has_shipped

    def __repr__(self):
        return f"This is {self.name} and they bought your book."

@app.route('/')
def index():
    return render_template('index.html', key=stripe_keys['publishable_key'])

@app.route('/charge', methods=['POST'])
def charge():

    print(request.form)

    cost = request.form['bookAmount']
    
    order_quanity = int(cost) / 2500
    dollars = int(cost) / 100
    price_paid = str('${:,.2f}'.format(dollars))

    print(price_paid)
    # Amount in cents
    amount = int(cost)

    customer = stripe.Customer.create(
        email=request.form['stripeEmail'],
        source=request.form['stripeToken']
    )

    charge = stripe.Charge.create(
        customer=customer.id,
        amount=amount,
        currency='usd',
        description='Flask Charge'
    )

    new_purchaser = Purchaser(
        request.form['stripeToken'],
        request.form['stripeTokenType'],
        request.form['stripeEmail'],
        request.form['stripeBillingName'],
        request.form['stripeBillingAddressCountry'],
        request.form['stripeBillingAddressCountryCode'],
        request.form['stripeBillingAddressZip'],
        request.form['stripeBillingAddressLine1'],
        request.form['stripeBillingAddressCity'],
        request.form['stripeBillingAddressState'],
        request.form['stripeShippingName'],
        request.form['stripeShippingAddressCountry'],
        request.form['stripeShippingAddressCountryCode'],
        request.form['stripeShippingAddressZip'],
        request.form['stripeShippingAddressLine1'],
        request.form['stripeShippingAddressCity'],
        request.form['stripeShippingAddressState'],
        price_paid,
        order_quanity,
        False
        )
    db.session.add(new_purchaser)
    db.session.commit()
    flash("Thank you! You have successfully purchased the book.")
    return redirect(url_for('index'))

if __name__ == '__main__':
  app.run(debug=True, port=5000)