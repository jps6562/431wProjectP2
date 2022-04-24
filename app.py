import hashlib

import pandas
from flask import Flask, render_template, request
import sqlite3 as sql
import pandas as pd
app = Flask(__name__)
host = 'http://127.0.0.1:5000/'

currentUserNameGlobal = '0'

@app.route('/')
def mainPage():  # put application's code here
    popData()
    return render_template('mainPage.html')



@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        #popData()
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

@app.route('/UserInfo', methods=['POST', 'GET'])
def userInfo():
    error = None
    global currentUserNameGlobal
    result = getPersonalInfo(currentUserNameGlobal)
    #if request.method == 'POST':
    return render_template('UserInfo.html', error=error, result=result)

@app.route('/buyerPage',methods=['POST', 'GET'])
def buyerPage():
    error = None
    return render_template('buyerPage.html', error=error, result=getFirstLastName(currentUserNameGlobal))

@app.route('/sellerPage',methods=['POST', 'GET'])
def sellerPage():
    error = None
    global currentUserNameGlobal
    if sellerExist(currentUserNameGlobal):
        return render_template('sellerPage.html', error=error, result=getFirstLastName(currentUserNameGlobal))
    else:
        return render_template('noSeller.html', error=error)

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
    cursor = db.execute('SELECT a.zipcode, a.street_num, a.street_name from Address a where a.address_id = ?;',
                        [billingAddrID])
    billAddressFetch = cursor.fetchall()[0]

    db.close()

def sellerExist(username):
    db = sql.connect('Phase2.db')
    rowsReturned = db.execute('SELECT COUNT(*) FROM Sellers WHERE email = ? ;', [username]).fetchall()
    #print(rowsReturned[0][0])
    #print(type(rowsReturned[0][0]))
    db.close()
    if rowsReturned[0][0] > 0:
        return True
    else:
        return False

def userExist(username, password):
    db = sql.connect('Phase2.db')
    hashPassword = hashPass(password)
    rowsReturned = db.execute('SELECT COUNT(*) FROM Users WHERE (email, password) = (?,?) ;', (username, hashPassword)).fetchall()
    #print(rowsReturned[0][0])
    #print(type(rowsReturned[0][0]))
    db.close()
    if rowsReturned[0][0] > 0:
        return True
    else:
        return False

def popData():
    db = sql.connect('Phase2.db')

    #USERS TABLE
    db.execute('CREATE TABLE IF NOT EXISTS Users("email" TEXT PRIMARY KEY, "password" TEXT);')
    inData = pd.read_csv('NittanyMarketDataset-Final/Users.csv')
    inData.columns = inData.columns.str.replace(" ","")
    hashedData = hashInData(inData)
    hashedData.to_sql("Users", db, if_exists='replace',index=False)

    #Buyers Table
    db.execute('CREATE TABLE IF NOT EXISTS Buyers("email" TEXT PRIMARY KEY, "first_name" TEXT, "last_name" TEXT, "gender" TEXT,'
               ' "age" INTEGER, home_address_id TEXT, billing_address_id TEXT );')
    inData = pd.read_csv('NittanyMarketDataset-Final/Buyers.csv')
    inData.columns = inData.columns.str.replace(" ", "")
    inData.to_sql("Buyers", db, if_exists='replace', index=False)

    #CC Table
    db.execute('CREATE TABLE IF NOT EXISTS Credit_Cards("credit_card_num" TEXT PRIMARY KEY, "card_code" INTEGER,'
               ' "expire_month" INTEGER , "expire_year" INTEGER, "card_type" TEXT, "owner_email" TEXT,'
               ' FOREIGN KEY("owner_email") REFERENCES "Users" ("email"));')
    inData = pd.read_csv('NittanyMarketDataset-Final/Credit_Cards.csv')
    inData.columns = inData.columns.str.replace(" ", "")
    inData.to_sql("Credit_Cards", db, if_exists='replace', index=False)

    #Address Table
    db.execute('CREATE TABLE IF NOT EXISTS Address("address_ID" TEXT PRIMARY KEY, "zipcode" INTEGER, "street_num" INTEGER,'
               ' "street_name" TEXT);')
    inData = pd.read_csv('NittanyMarketDataset-Final/Address.csv')
    inData.columns = inData.columns.str.replace(" ", "")
    inData.to_sql("Address", db, if_exists='replace', index=False)

    db.execute('CREATE TABLE IF NOT EXISTS Zipcode_Info( "zipcode" INTEGER PRIMARY KEY, "city" TEXT, "state_id" TEXT,'
               ' "population" INTEGER, "density" REAL, "county_name" TEXT, "timezone" TEXT );')
    inData = pd.read_csv('NittanyMarketDataset-Final/Zipcode_Info.csv')
    inData.columns = inData.columns.str.replace(" ", "")
    inData.to_sql("Zipcode_Info", db, if_exists='replace', index=False)

    db.execute('CREATE TABLE IF NOT EXISTS Sellers("email" TEXT PRIMARY KEY, "routing_number" TEXT, "account_number" INTEGER,'
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

    db.execute('CREATE TABLE IF NOT EXISTS Orders("Transaction_ID" INTEGER PRIMARY KEY, "Seller_Email" TEXT, "Listing_ID" INTEGER,'
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

    db.commit()
    db.close()
    #cursor = db.execute('SELECT * FROM Users e;')
    #for i in cursor.fetchall():
        #print(i)

#hashes the whole dataframe so for the population of data
def hashInData(pandaIn: pandas.DataFrame):
    pandaIn['password'] = pandaIn['password'].apply(lambda pw: hashPass(pw))
    return pandaIn

#takes password and returns its hashed equivalent
def hashPass(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def getFirstLastName(username):
    db = sql.connect('Phase2.db')
    print(username)
    cursor = db.execute('SELECT b.first_name, b.last_name from Buyers b where b.email = ?;', [username])
    ret = cursor.fetchall()
    db.close()
    print(type(ret))
    return ret

if __name__ == '__main__':
    app.run()
