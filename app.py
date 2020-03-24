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
recipes = db.recipes 

app = Flask(__name__, static_url_path='')

ApiKey = os.getenv("RECIPE_API_KEY") #set the api key #get it from our invisible .ENV file

@app.route('/')
def home():
    #Home
    return render_template('index.html')

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/results')
def results():
    search_term = request.args.get('user_input')


    params = {
        'query': search_term,
        'apiKey': ApiKey,
        'number': 7
    }

    url = "https://api.spoonacular.com/recipes/search"


    r = requests.get(url, params=params)
    if r.status_code == 200:
        json_recipes = json.loads(r.content)
        recipes = json_recipes['results']
        return render_template('results.html', recipes=recipes)

@app.route('/results/<id>')
def display(id):
    params = {
        'id': id,
        "apiKey": ApiKey
    }
    url = f"https://api.spoonacular.com/recipes/{id}/information"
    r = requests.get(url, params=params)
    if r.status_code == 200:
        json_recipe = json.loads(r.content)
        ingredients = json_recipe['extendedIngredients']
        image = json_recipe['image']
    else:
        return "error"

    for ingredient in ingredients:
        ingredient['amount'] = str(ingredient['amount']).rstrip('.0')
        ingredient['amount'] = str(ingredient['amount']).strip('0')

    instructions_params = {
        'apiKey': ApiKey
    }
    instructions_url = f"https://api.spoonacular.com/recipes/{id}/analyzedInstructions"

    req = requests.get(instructions_url, params=instructions_params)
    if req.status_code == 200:
        json_instructions = json.loads(req.content)
        steps = json_instructions[0]["steps"]
    else:
        return "error"
    return render_template('single_recipe.html', ingredients=ingredients, steps=steps, recipe_id=id, image=image)

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
    return render_template('shoppinglist_show.html', lists=lists.find(), prices=prices)

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
    return render_template('shoppinglist_new.html', list={}, title='New List', products=[None])

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


# Routes Pertaining to the Sales Calculator/Kitchen Timer
@app.route('/tools')
def tools():
    return render_template('tools.html')

# Routes pertaining to the About Page
@app.route('/about')
def about():
    return render_template('about.html')

#Routes for Recipe 

@app.route('/Myrecipes')
def recipes_index():
    return render_template('own_recipes.html', recipes=recipes.find())

@app.route('/Myrecipes/new')
def add_recipe():
    """Create new recipe"""
    return render_template('recipe_new.html', recipe={}, title='Want a new recipe?')

@app.route('/Myrecipes/<recipe_id>')
def show_recipe(recipe_id):
     "Shows recipes in detail"
     recipe = recipes.find_one({'_id': ObjectId(recipe_id)})
     return render_template('show_recipe.html', recipe=recipe)

@app.route('/Myrecipes/<recipe_id>/edit')
def recipe_edit(recipe_id):
    """Edit recipes if needed."""
    recipe = recipes.find_one({'_id': ObjectId(recipe_id)})
    return render_template('recipe_edit.html', recipe=recipe, title="Edit current recipe")

@app.route('/Myrecipes', methods=['POST'])
def submit_recipe():
    new_recipe = {
        'name': request.form.get('name'),
        'url': request.form.get('url'),
        'ingredients': request.form.get('ingredients'),
        'steps': request.form.get('steps')
    }
    recipe_id = recipes.insert_one(new_recipe).inserted_id
    return redirect(url_for('show_recipe', recipe_id=recipe_id))

@app.route('/Myrecipes/<recipe_id>', methods=['POST'])
def update_recipe(recipe_id):
    """Submit edited recipe."""
    update_recipe = {
        'name': request.form.get('name'),
        'url': request.form.get('url'),
        'ingredients': request.form.get('ingredients'),
        'steps': request.form.get('steps'),
    }
    recipes.update_one(
        {'_id': ObjectId(recipe_id)},
        {'$set': update_recipe})
    return redirect(url_for('show_recipe', recipe_id=recipe_id))

@app.route('/Myrecipes/<recipe_id>/delete', methods=['POST'])
def recipe_del(recipe_id):
    """Deletes recipes."""
    recipes.delete_one({'_id': ObjectId(recipe_id)})
    return redirect(url_for('recipes_index'))




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))
