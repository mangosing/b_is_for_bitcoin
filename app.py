import os
from flask import Flask, render_template, request
import stripe

app = Flask(__name__, static_url_path='/static')

@app.route('/')
def index():
    return render_template('index.html')