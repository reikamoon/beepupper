from flask import Flask, render_template, request, redirect, url_for
import requests
import json
from bson.objectid import ObjectId
from pymongo import MongoClient
import os
from dotenv import load_dotenv #needed for .env
load_dotenv() #needed for .env

# Databases
host = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/beepupper')
client = MongoClient(host=f'{host}?retryWrites=false')
db = client.get_default_database()
lists = db.lists
products = db.products

app = Flask(__name__, static_url_path='')

# RECIPE_API_KEY = os.getenv("RECIPE_API_KEY") #set the api key #get it from our invisible .ENV file

@app.route('/')
def home():
    #Home
    return render_template('index.html')

# def index(): #homepage
#     limit = request.args.get("search_limit",10) #set limit, if none then put 10
#     search_term = request.args.get("search_result", "random") #search_term will contain search_result, else it will be random

#     recipe_json = get_recipe_json(search_term, RECIPE_API_KEY, limit)

#     return render_template('index.html', recipe_json = recipe_json)

# def get_recipe_json(search_term, apiKey, limit):
#     r = requests.get("https://api.spoonacular.com/recipes/search" % (search_term, apiKey, limit)) #get our gifs and applying our parameters
#     if r.status_code == 200:
#         return r.json() #return json
#     else:
#         return None

@app.route('/today')
def todo():
    #Show To Do List
    return render_template('today.html')

@app.route('/mylists')
def view_lists():
    #View all lists along with budget, total spent, and budget difference.
    list_list = lists.find()
    prices = {}

    for list in list_list: #list_list is all lists
        product_list = list['products']
        listsum = 0 #sum of everything on the lists is by default, 0.
        for products in product_list: #For every product on the shopping list, add up all the prices to get the total.
            listsum += float(products['price'])
        prices[list['_id']] = listsum
    return render_template('Ashow_shoppinglist.html', lists=lists.find(), prices=prices)

@app.route('/mylists/<list_id>', methods=['GET'])
def show_list(list_id):
    #Show a single List
    list = lists.find_one({'_id': ObjectId(list_id)})
    product_list = list['products']
    print(list)
    listsum = 0
    for products in product_list:
        listsum += float(products['price'])

    budget = float(list['budget'])
    budgetdiff = round(budget - listsum, 2)
    print(budgetdiff)
    return render_template('list_view.html', list=list, listsum=listsum, budgetdiff=budgetdiff)

@app.route('/mylists/new/list')
def new_list():
    #Create a New List
    return render_template('Anew_shoppinglist.html', list={}, title='New List', products=[None])

@app.route('/mylists', methods=['POST'])
def submit_list():
    #Submit a new list to the db.lists.
    new_list = {
    'title': request.form.get('title'),
    'budget': request.form.get('budget'),
    'products': [{'name': request.form.get('name'),'price': request.form.get('price'),'URL': request.form.get('url'),'image_url': request.form.get('image_url')}]
    }
    lists_id = lists.insert_one(new_list).inserted_id
    return redirect(url_for('view_lists', lists_id=lists_id))

@app.route('/mylists/<list_id>/edit', methods = ['GET'])
def edit_list(list_id):
    # Edit my shopping list
    product_list = lists.find_one({'_id': ObjectId(list_id)})
    return render_template('Aedit_shoppinglist.html', list=product_list, list_id=list_id, products=product_list['products'])

@app.route('/mylists/<list_id>/edit', methods=['POST'])
def list_update(list_id):
    # Save Edits to list and Update list in the database.
    product_list = lists.find_one({'_id': ObjectId(list_id)})['products']
    product_list.append({'name': request.form.get('name'),'price': request.form.get('price'),'URL': request.form.get('url'),'image_url': request.form.get('image_url')})
    updated_list = {
        'title': request.form.get('title'),
        'budget': request.form.get('budget'),
        'products': product_list,
        }
    lists.update_one(
        {'_id': ObjectId(list_id)},
        {'$set': updated_list})
    return redirect(url_for('view_lists', list_id=list_id))

@app.route('/mylists/<list_id>/delete')
def list_delete(list_id):
    #Delete a product from the list
    lists.delete_one({'_id': ObjectId(list_id)})
    return redirect(url_for('view_lists'))

# Routes for Products
@app.route('/mylists/<list_id>/new')
def new_product(list_id):
    #Create a new product
    list = lists.find_one({'_id': ObjectId(list_id)})
    return render_template('Bnew_product.html', list=list, product=None)

@app.route('/mylists/<list_id>', methods=['POST'])
def submit_product(list_id):
    #Submit Product to Database and add to list
    product_list = lists.find_one({'_id': ObjectId(list_id)})['products']
    print("Product list: ", product_list)
    new_product = {
        'name': request.form.get('name'),
        'price': request.form.get('price'),
        'URL': request.form.get('url'),
        'image_url': request.form.get('image_url')
    }
    print("New product: ", new_product)
    product_list.append(new_product)
    lists.update_one(
    {'_id': ObjectId(list_id)},
    {'$set': {'products': product_list}})
    return redirect(url_for('show_list', list_id=list_id))


@app.route('/mylists/<list_id>/delete/<product_name>')
def product_delete(list_id, product_name):
    #Delete a product
    product_list = lists.find_one({'_id': ObjectId(list_id)})['products']
    for product in product_list:
        if product['name'] == product_name:
            product_list.remove(product)
            break
    lists.update_one(
    {'_id': ObjectId(list_id)},
    {'$set': {'products': product_list}})
    return redirect(url_for('view_lists'))

# # Routes for Recipes
# @app.route('/mylists/<list_id>/new')
# def new_recipe(list_id):
#     #Create a new recipe
#     list = lists.find_one({'_id': ObjectId(list_id)})
#     return render_template('Bnew_recipe.html', list=list, product=None)

# @app.route('/mylists/<list_id>', methods=['POST'])
# def submit_recipe(list_id):
#     #Submit Recipe to Database and add to list
#     recipe_list = lists.find_one({'_id': ObjectId(list_id)})['recipes']
#     print("Recipe list: ", recipe_list)
#     new_recipe = {
#         'name': request.form.get('name'),
#         'servings': request.form.get('serving'),
#         'ingredients': request.form.get('ingredients'),
#         'directions': request.form.get('dorections'),
#         # 'URL': request.form.get('url'),
#         # 'image_url': request.form.get('image_url')
#     }
#     print("New recipe: ", new_recipe)
#     recipe_list.append(new_recipe)
#     lists.update_one(
#     {'_id': ObjectId(list_id)},
#     {'$set': {'recipes': recipe_list}})
#     return redirect(url_for('show_list', list_id=list_id))

# @app.route('/mylists/<list_id>/delete/<recipe_name>')
# def recipe_delete(list_id, recipe_name):
#     #Delete a product
#     recipe_list = lists.find_one({'_id': ObjectId(list_id)})['recipes']
#     for product in recipe_list:
#         if recipe['name'] == recipe_name:
#             recipe_list.remove(recipe)
#             break
#     lists.update_one(
#     {'_id': ObjectId(list_id)},
#     {'$set': {'recipes': recipe_list}})
#     return redirect(url_for('view_lists'))

# Routes Pertaining to the Sales Calculator
@app.route('/salescalculator')
def calculator():
    return render_template('salescalculator.html')

# Routes pertaining to the About Page
@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))
