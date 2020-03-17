from flask import Flask, render_template, request, redirect, url_for
import requests
import json
from bson.objectid import ObjectId
from pymongo import MongoClient
import os

# Databases
host = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/beepupper')
client = MongoClient(host=f'{host}?retryWrites=false')
db = client.get_default_database()
lists = db.lists
products = db.products

app = Flask(__name__)

@app.route('/')
def home():
    #Home
    return render_template('index.html')