#Joseph Malafronte
#Web Scraper for BoA to find balance information for bank accounts
#Place balance in Google Sheets Spreadsheet using Google API
#For personal non-profit use only


#import libraries
from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException
import time
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import keyring, os, sys
import gspread
import requests
from oauth2client.service_account import ServiceAccountCredentials


def run() :
	#Access Google Sheet For Editing
	scope = ['https://spreadsheets.google.com/feeds',
	         'https://www.googleapis.com/auth/drive']
	creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json',scope)
	print("Test")
	client = gspread.authorize(creds)
	print("Test")


	sheet = client.open('Finances').sheet1


	#Get secure password from keyring
	#Only authorized users so this program can not be used malicously 
	key = keyring.get_password('bankofamerica.com', 'jgmalafronte')


	print("Fetching Data...")
	sheet.update_cell(33,5, "Fetching Data...")

	#Load Selenium up 
	option = webdriver.ChromeOptions()
	option.add_argument(" — incognito")
	#option.add_argument("--headless") 
	browser = webdriver.Chrome(executable_path='/Users/josephmalafronte/ChromeDriver/chromedriver', chrome_options=option)


	#Load BoA Sign In Page
	browser.get("https://secure.bankofamerica.com/login/sign-in/signOnV2Screen.go") 

	#file = open("test")


	#Element Ids for username and password input boxes
	usernameElementId = "enterID-input"
	passwordElementId = "tlpvt-passcode-input"

	#Wait until element loads or 20 seconds pass
	WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.ID, usernameElementId)))

	username = browser.find_element_by_id(usernameElementId)
	password = browser.find_element_by_id(passwordElementId)
	username.send_keys("jgmalafronte")
	password.send_keys(key)
	login_attempt = browser.find_element_by_name("enter-online-id-submit")
	login_attempt.submit()


	#Check if there is a answer requirement if so provide answer
	needAnswer = len(browser.find_elements_by_class_name("answer-section"))>0
	key = ""
	if needAnswer == True:
		answerDiv = browser.find_element_by_class_name("answer-section")
		answerLabel = answerDiv.find_element_by_tag_name("label").text
		if answerLabel == "What was the name of your first pet?":
			key = keyring.get_password('boaPetName', 'jgmalafronte')
		elif answerLabel == "What is the first name of your high school prom date?":
			key = keyring.get_password('boaProm', 'jgmalafronte')
		elif answerLabel == "What was the name of your first boyfriend or girlfriend?":
			key = keyring.get_password('boaGirlfriend', 'jgmalafronte')

		#If the key is succesfully updated	
		if key != "":
			inputBox = browser.find_element_by_id("tlpvt-challenge-answer")
			inputBox.send_keys(key)
			browser.find_element_by_id("yes-recognize").click()
			browser.find_element_by_id("verify-cq-submit").click()




	#Wait until element loads or 20 seconds pass
	WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.ID, 'Traditional')))


	#Pass the html to Soup for scraping
	page_html = browser.page_source
	page_soup = soup(page_html, "html.parser") 

	#grabs each product places into array
	containers = page_soup.findAll("div", {"class","AccountItem AccountItemDeposit"})

	for container in containers:
		
		balanceContainer = container.findAll("div", {"class","AccountBalance"})
		balance = balanceContainer[0].span.text.strip()
		accountNameContainer = container.findAll("span", {"class","AccountName"})
		accountName = accountNameContainer[0].a.text.strip()	
		
		
		#Cell locations must match google sheets spreadsheet
		if(accountName == "Checking - 7532"): sheet.update_cell(80,5, balance)
		elif(accountName == "Savings - 1082"): sheet.update_cell(81,5, balance)
		elif(accountName == "Emergency Fund - 3246"): sheet.update_cell(82,5, balance)




	print("Data Fetched")
	sheet.update_cell(33,5, "Data Fetched")


	browser.quit()

#run()