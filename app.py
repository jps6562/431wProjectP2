from flask import Flask
import sqlite3 as sql
import pandas as pd
app = Flask(__name__)
host = 'http://127.0.0.1:5000/'

@app.route('/')
def mainPage():  # put application's code here

    return popData()


def popData():
    db = sql.connect('Phase2.db')
    db.execute('CREATE TABLE IF NOT EXISTS Users("email" TEXT PRIMARY KEY, "password" TEXT);')
    inData = pd.read_csv('NittanyMarketDataset-Final/Users.csv')
    inData.to_sql("Users", db, if_exists='append',index=False)
    cursor = db.execute('SELECT * FROM Users e;')
    for i in cursor.fetchall():
        print(i)
    db.execute('CREATE TABLE IF NOT EXISTS Buyers("email" TEXT PRIMARY KEY, "first_name" TEXT, "last_name" TEXT, "gender" TEXT,'
               ' "age" INTEGER, home_address_id TEXT, billing_address_id TEXT );')

    db.execute('CREATE TABLE IF NOT EXISTS Credit_Cards("credit_card_num" TEXT PRIMARY KEY, "card_code" INTEGER,'
               ' "expire_month" INTEGER , "expire_year" INTEGER, "card_type" TEXT,'
               ' FOREIGN KEY("owner_email") REFRENCES(USERS(email)));')

    db.execute('CREATE TABLE IF NOT EXISTS Address("address_ID" TEXT PRIMARY KEY, "zipcode" INTEGER, "street_num" INTEGER,'
               ' "street_name" TEXT);')

    db.execute('CREATE TABLE IF NOT EXISTS Zipcode_Info( "zipcode" INTEGER PRIMARY KEY, "city" TEXT, "state_id" TEXT,'
               ' "population" INTEGER, "density" REAL, "county_name" TEXT, "timezone" TEXT );')

    db.execute('CREATE TABLE IF NOT EXISTS Sellers("email" TEXT, "routing_number" TEXT, "account_number" INTEGER,'
               ' "balance" REAL);')

    db.execute('CREATE TABLE IF NOT EXISTS Local_Vendors("email" PRIMARY KEY TEXT, "Business_Name" TEXT,'
               ' FOREIGN KEY(Business_Address_ID) REFRENCES(Address(address_ID)), "Customer_Service_Number" TEXT);')

    db.execute('CREATE TABLE IF NOT EXISTS Categories("parent_category" TEXT, "category_name" PRIMARY KEY);')

    db.execute('CREATE TABLE IF NOT EXISTS Product_Listings("Seller_Email" TEXT PRIMARY KEY, "Listing_ID" INTEGER PRIMARY KEY,'
               ' "Category" TEXT, "Title" TEXT, "Product_Name" TEXT, "Product_Description" TEXT, "Price" TEXT, "Quantity" INTEGER);')

    db.execute('CREATE TABLE IF NOT EXISTS Orders("Transaction_ID" INTEGER PRIMARY KEY, "Seller_Email" TEXT, "Listing_ID" INTEGER,'
               ' "Buyer_Email" TEXT, "Date" TEXT, "Quantity" INTEGER, "Payment" INTEGER);')

    db.execute('CREATE TABLE IF NOT EXISTS Reviews("Buyer_Email" TEXT PRIMARY KEY, "Seller_Email" TEXT PRIMARY KEY,'
               ' "Listing_ID" INTEGER, "Review_Desc" TEXT);')

    db.execute('CREATE TABLE IF NOT EXISTS Rating("Buyer_Email" TEXT PRIMARY KEY, "Seller_Email" TEXT PRIMARY KEY,'
               '"Date" TEXT, "Rating" INTEGER, "Rating_Desc" TEXT);')


if __name__ == '__main__':
    app.run()
