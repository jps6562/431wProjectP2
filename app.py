import hashlib

import pandas
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


if __name__ == '__main__':
    app.run()
