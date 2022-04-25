import hashlib

import pandas
from flask import Flask, render_template, request
import sqlite3 as sql
import pandas as pd
import datetime

app = Flask(__name__)
host = 'http://127.0.0.1:5000/'

currentUserNameGlobal = '0'


@app.route('/')
def mainPage():  # put application's code here
    popData()
    #print(len(getProductsInCategory('Cell Phones')))
    return render_template('mainPage.html')

#asks for login info and verifies user
@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        # popData()
        userName = request.form['UserName']
        password = request.form['Password']
        result = userExist(userName, password)
        if result:
            global currentUserNameGlobal
            currentUserNameGlobal = userName
            return render_template('successfulLogin.html', error=error, result=result)
        else:
            return render_template('unSuccLogin.html', error=error)
    return render_template('loginPage.html')

#shows personal info and gives option for password change
#verifies user entered correct password and also hashes it
@app.route('/UserInfo', methods=['POST', 'GET'])
def userInfo():
    error = None
    global currentUserNameGlobal
    result = getPersonalInfo(currentUserNameGlobal)
    # print(type(result))
    # print(result)
    # result = [['arubertelli0@nsu.edu'],['Ileana']]
    if request.method == 'POST':
        newPassword = request.form['newPassword']
        reNewPassword = request.form['reNewPassword']
        if newPassword == reNewPassword:
            db = sql.connect('Phase2.db')
            hashedPw = hashPass(newPassword)
            # print(hashedPw)
            db.execute('UPDATE Users SET password = ? WHERE email = ?;', (hashedPw, currentUserNameGlobal))
            db.commit()
            db.close()
            return render_template('pwChangeSucc.html', error=error)
        else:
            return render_template('pwChangeUnSucc.html', error=error)
    else:
        return render_template('UserInfo.html', error=error, result=result)

#Page for buyer options
@app.route('/buyerPage', methods=['POST', 'GET'])
def buyerPage():
    error = None
    return render_template('buyerPage.html', error=error, result=getFirstLastName(currentUserNameGlobal))

#Page for seller actions
#verifies that user is a valid seller
@app.route('/sellerPage', methods=['POST', 'GET'])
def sellerPage():
    error = None
    global currentUserNameGlobal
    if sellerExist(currentUserNameGlobal):
        return render_template('sellerPage.html', error=error, result=getFirstLastName(currentUserNameGlobal))
    else:
        return render_template('noSeller.html', error=error)

#Allows a seller to list a new product
#gets necessary info and updates database
#gives message whether it was successful
@app.route('/productList', methods=['POST', 'GET'])
def productList():
    error = None
    if request.method == 'POST':
        title = request.form['title']
        productName = request.form['productName']
        category = request.form['category']
        productDesc = request.form['productDesc']
        price = request.form['price']
        quantity = request.form['quantity']
        global currentUserNameGlobal
        sellerEmail = currentUserNameGlobal
        listingId = getNextListingId()
        if categoryExists(category):
            db = sql.connect('Phase2.db')
            cursor = db.execute('INSERT INTO Product_Listings (Seller_Email, Listing_ID, Category, Title, Product_Name,'
                                ' Product_Description, Price, Quantity, List_Date) VALUES (?,?,?,?,?,?,?,?,?);',
                                (sellerEmail, listingId,
                                 category, title,
                                 productName,
                                 productDesc, price,
                                 quantity, getCurrentDate()))
            db.commit()
            db.close()
            return render_template('succProdList.html', error=error)
        else:
            return render_template('unSuccProdList.html', error=error)
    else:
        return render_template('productList.html', error=error)

# allows users to browse available products
#result is products in the category
#newResult is category selection
@app.route('/browseProducts', methods=['POST', 'GET'])
def browseProducts():
    error = None
    #gets all possible categories for selection purposes
    db = sql.connect('Phase2.db')
    cursor = db.execute('SELECT DISTINCT c.category_name FROM CATEGORIES c')
    result1 = cursor.fetchall()
    newResult = []
    #converts to strings
    for thing in result1:
        for thing1 in thing:
            thing1 = thing1.replace(",", "")
            thing1 = thing1.replace("'", "")
            newValue = thing1
        newResult.append((newValue))
    #print(type(result1[0][0]))
    #print(result1[0][0])
    db.close()
    if request.method == 'POST':
        category = request.form['category']
        #print(category)
        #print(category)
        result = getProductsInCategory(category)
        return render_template('browseProducts.html', error=error, result=result, result1=newResult)
    else:
        return render_template('browseProducts.html', error=error, result=getProductsInCategory('Root'), result1=newResult)

# helper function to get products
# takes the category for the products
#clenses some database miss matches
def getProductsInCategory(category):
    if category == 'Bodysuits':
        category = 'bodysuit'
    if category == 'Cooking Accessories':
        category = 'Cooking accessories'
    cats = getCats(category)
    #print(cats)
    db = sql.connect('Phase2.db')
    productList = []
    for cat in cats:
        cursor = db.execute('SELECT p.Title, p.Product_Name, p.Product_Description, p.Price, p.Category, '
                            'p.Seller_Email FROM Product_Listings p WHERE p.Category = ? COLLATE nocase;', [cat])
        for thing in cursor.fetchall():
            productList.append(thing)
    db.close()
    return productList

#recursive function to get category and its sub categories for getProducts function
def getCats(category):
    cats = []
    cats.append(category)
    helperList = []
    helperList.append(category)
    db = sql.connect('Phase2.db')
    while(len(helperList) > 0 ):
        helperList = getSubCats(db, helperList)
        cats = cats + helperList
    db.close()
    return cats

#recursive helper function
def getSubCats(db, cats):
    helperList = []
    for cat in cats:
        cursor = db.execute('SELECT c.category_name FROM Categories c WHERE c.parent_category = ?;', [cat])
        for thing in cursor.fetchall():
            helperList.append(thing[0])
    return helperList

#verifies that it is a valid category for new product listing
def categoryExists(category):
    db = sql.connect('Phase2.db')
    cursor = db.execute('SELECT COUNT(*) from Categories c where c.category_name = ? OR c.parent_category = ?;',
                        (category, category))
    count = cursor.fetchone()[0]
    db.close()
    if count > 0:
        return True
    else:
        return False

#grabs the next listing id for new product listing
def getNextListingId():
    db = sql.connect('Phase2.db')
    cursor = db.execute('SELECT MAX(p.Listing_ID) FROM Product_Listings p')
    listId = cursor.fetchone()[0]
    db.close()
    listId = listId + 1
    return listId


# returns a tuple with [email, first_name, last_name, gender, age, home_zipcode, home_street_num, home_street_name,
# bill_zipcode, bill_street_num, bill_street_name, last four digits of cc]
def getPersonalInfo(username):
    db = sql.connect('Phase2.db')
    cursor = db.execute('SELECT * from Buyers b where b.email = ?;', [username])
    fetchAllReturn = cursor.fetchall()[0]
    ret = []
    for i in range(5):
        ret.append(fetchAllReturn[i])
    homeAddrID = fetchAllReturn[5]
    billingAddrID = fetchAllReturn[6]

    cursor = db.execute('SELECT a.zipcode, a.street_num, a.street_name from Address a where a.address_id = ?;',
                        [homeAddrID])
    homeAddressFetch = cursor.fetchall()[0]
    for thing in homeAddressFetch:
        ret.append(thing)

    cursor = db.execute('SELECT a.zipcode, a.street_num, a.street_name from Address a where a.address_id = ?;',
                        [billingAddrID])
    billAddressFetch = cursor.fetchall()[0]
    for thing in billAddressFetch:
        ret.append(thing)
    db.close()
    ret.append(getCCNum(username)[-4:])
    ret_tuple = tuple(ret)
    return ret


def getCCNum(username):
    db = sql.connect('Phase2.db')
    cursor = db.execute('Select c.credit_card_num from Credit_Cards c where c.Owner_email = ?;', [username])
    ret = cursor.fetchall()[0][0]
    db.close()
    return ret

#function to verify that a seller does exist
def sellerExist(username):
    db = sql.connect('Phase2.db')
    rowsReturned = db.execute('SELECT COUNT(*) FROM Sellers WHERE email = ? ;', [username]).fetchall()
    db.close()
    if rowsReturned[0][0] > 0:
        return True
    else:
        return False

#function to verify that a user does exist and there password is correct
def userExist(username, password):
    db = sql.connect('Phase2.db')
    hashPassword = hashPass(password)
    rowsReturned = db.execute('SELECT COUNT(*) FROM Users WHERE (email, password) = (?,?) ;',
                              (username, hashPassword)).fetchall()
    db.close()
    if rowsReturned[0][0] > 0:
        return True
    else:
        return False

#populates data from csv
def popData():
    db = sql.connect('Phase2.db')

    # USERS TABLE
    db.execute('CREATE TABLE IF NOT EXISTS Users("email" TEXT PRIMARY KEY, "password" TEXT);')
    inData = pd.read_csv('NittanyMarketDataset-Final/Users.csv')
    inData.columns = inData.columns.str.replace(" ", "")
    hashedData = hashInData(inData)
    hashedData.to_sql("Users", db, if_exists='replace', index=False)

    # Buyers Table
    db.execute(
        'CREATE TABLE IF NOT EXISTS Buyers("email" TEXT PRIMARY KEY, "first_name" TEXT, "last_name" TEXT, "gender" TEXT,'
        ' "age" INTEGER, home_address_id TEXT, billing_address_id TEXT );')
    inData = pd.read_csv('NittanyMarketDataset-Final/Buyers.csv')
    inData.columns = inData.columns.str.replace(" ", "")
    inData.to_sql("Buyers", db, if_exists='replace', index=False)

    # CC Table
    db.execute('CREATE TABLE IF NOT EXISTS Credit_Cards("credit_card_num" TEXT PRIMARY KEY, "card_code" INTEGER,'
               ' "expire_month" INTEGER , "expire_year" INTEGER, "card_type" TEXT, "owner_email" TEXT,'
               ' FOREIGN KEY("owner_email") REFERENCES "Users" ("email"));')
    inData = pd.read_csv('NittanyMarketDataset-Final/Credit_Cards.csv')
    inData.columns = inData.columns.str.replace(" ", "")
    inData.to_sql("Credit_Cards", db, if_exists='replace', index=False)

    # Address Table
    db.execute(
        'CREATE TABLE IF NOT EXISTS Address("address_ID" TEXT PRIMARY KEY, "zipcode" INTEGER, "street_num" INTEGER,'
        ' "street_name" TEXT);')
    inData = pd.read_csv('NittanyMarketDataset-Final/Address.csv')
    inData.columns = inData.columns.str.replace(" ", "")
    inData.to_sql("Address", db, if_exists='replace', index=False)

    db.execute('CREATE TABLE IF NOT EXISTS Zipcode_Info( "zipcode" INTEGER PRIMARY KEY, "city" TEXT, "state_id" TEXT,'
               ' "population" INTEGER, "density" REAL, "county_name" TEXT, "timezone" TEXT );')
    inData = pd.read_csv('NittanyMarketDataset-Final/Zipcode_Info.csv')
    inData.columns = inData.columns.str.replace(" ", "")
    inData.to_sql("Zipcode_Info", db, if_exists='replace', index=False)

    db.execute(
        'CREATE TABLE IF NOT EXISTS Sellers("email" TEXT PRIMARY KEY, "routing_number" TEXT, "account_number" INTEGER,'
        ' "balance" REAL);')
    inData = pd.read_csv('NittanyMarketDataset-Final/Sellers.csv')
    inData.columns = inData.columns.str.replace(" ", "")
    inData.to_sql("Sellers", db, if_exists='replace', index=False)

    db.execute('CREATE TABLE IF NOT EXISTS Local_Vendors("email" TEXT PRIMARY KEY, "Business_Name" TEXT,'
               '"Business_Address_ID" TEXT,"Customer_Service_Number" TEXT, '
               'FOREIGN KEY("Business_Address_ID") REFERENCES "Address" ("address_ID"));')
    inData = pd.read_csv('NittanyMarketDataset-Final/Local_Vendors.csv')
    inData.columns = inData.columns.str.replace(" ", "")
    inData.to_sql("Local_Vendors", db, if_exists='replace', index=False)

    db.execute('CREATE TABLE IF NOT EXISTS Categories("parent_category" TEXT, "category_name" PRIMARY KEY);')
    inData = pd.read_csv('NittanyMarketDataset-Final/Categories.csv')
    inData.columns = inData.columns.str.replace(" ", "")
    inData.to_sql("Categories", db, if_exists='replace', index=False)

    db.execute('CREATE TABLE IF NOT EXISTS Product_Listings("Seller_Email" TEXT, "Listing_ID" INTEGER, "Category" TEXT,'
               ' "Title" TEXT, "Product_Name" TEXT, "Product_Description" TEXT, "Price" TEXT, "Quantity" INTEGER, '
               'PRIMARY KEY("Seller_Email", "Listing_ID"));')
    inData = pd.read_csv('NittanyMarketDataset-Final/Product_Listing.csv')
    inData.columns = inData.columns.str.replace(" ", "")
    inData.to_sql("Product_Listings", db, if_exists='replace', index=False)

    db.execute(
        'CREATE TABLE IF NOT EXISTS Orders("Transaction_ID" INTEGER PRIMARY KEY, "Seller_Email" TEXT, "Listing_ID" INTEGER,'
        ' "Buyer_Email" TEXT, "Date" TEXT, "Quantity" INTEGER, "Payment" INTEGER);')
    inData = pd.read_csv('NittanyMarketDataset-Final/Orders.csv')
    inData.columns = inData.columns.str.replace(" ", "")
    inData.to_sql("Orders", db, if_exists='replace', index=False)

    db.execute('CREATE TABLE IF NOT EXISTS Reviews("Buyer_Email" TEXT, "Seller_Email" TEXT, "Listing_ID" INTEGER,'
               ' "Review_Desc" TEXT, PRIMARY KEY ("Buyer_Email", "Seller_Email", "Listing_ID"));')
    inData = pd.read_csv('NittanyMarketDataset-Final/Reviews.csv')
    inData.columns = inData.columns.str.replace(" ", "")
    inData.to_sql("Reviews", db, if_exists='replace', index=False)

    db.execute('CREATE TABLE IF NOT EXISTS Rating("Buyer_Email" TEXT, "Seller_Email" TEXT, "Date" TEXT,'
               ' "Rating" INTEGER, "Rating_Desc" TEXT, PRIMARY KEY ("Buyer_Email", "Seller_Email", "Date"));')
    inData = pd.read_csv('NittanyMarketDataset-Final/Ratings.csv')
    inData.columns = inData.columns.str.replace(" ", "")
    inData.to_sql("Rating", db, if_exists='replace', index=False)

    db.execute('ALTER TABLE Product_Listings ADD COLUMN List_Date TEXT')
    #db.execute('UPDATE Product_Listings SET List_Date = ?;', [getCurrentDate()])
    db.commit()
    db.close()


# hashes the whole dataframe so for the population of data
def hashInData(pandaIn: pandas.DataFrame):
    pandaIn['password'] = pandaIn['password'].apply(lambda pw: hashPass(pw))
    return pandaIn


# takes password and returns its hashed equivalent
def hashPass(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

#gets the name for a user
def getFirstLastName(username):
    db = sql.connect('Phase2.db')
    cursor = db.execute('SELECT b.first_name, b.last_name from Buyers b where b.email = ?;', [username])
    ret = cursor.fetchall()
    db.close()
    return ret

#creates a time stamp
def getCurrentDate():
    return datetime.datetime.now()

if __name__ == '__main__':
    app.run()
