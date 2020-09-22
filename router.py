#requirements python 3.6+?
# pip install requests, selenium + chromedriver(version=equal to chrome version) download and put in path dir
import requests, time, json, random, re, configparser, ast
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#config load
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

#Adreshu saraksts // pirmais ieraksts buus saakumpunkts (un beigu punkts round-tripam)
AdressArray = ast.literal_eval(config.get('Settings', 'AdressArray'))
#Settingi
triptype = config.getint('Settings', 'triptype') #1 for roundtrip / 2 for A-Z trip
StopCount = config.getint('Settings', 'StopCount') #cik adreses randomaa izveeleesies no pilnaa adreshu saraksta, lai veiktu apreekinus
iteracijas = config.getint('Settings', 'iteracijas') #cik pilnus ciklus skripts veiks (cik reizes veers valjaa chrome un pildiis darbiibas)
visibility = config.getint('Settings', 'visibility') # 0 = process notiek backgroundaa, jebkura cita vertiba = redzams logs un darbiiba
path = config.get('Settings', 'path')

pieturuSkaits = browser = None
def WriteOutput():
	global pieturuSkaits, browser
	KM2=browser.find_element_by_class_name("pathdata").text.strip().replace('Trip duration:', '').replace('Trip length:', '')
	l1= re.sub(r'\([^)]*\)', '', KM2)
	l2= re.sub(r'\r?\n|\r', '', l1)
	attalums= (re.split('sec | min | hrs | km ', l2))[2]
	fullroute=[]
	for adrese in browser.find_elements_by_class_name("centered-directions"):
		fullroute.append(adrese.text)
	while('' in fullroute): 
		fullroute.remove('')
	pieturuSkaits = len(fullroute) - 2 # -2 jo nonjem saakuma un beigu adresi
	StrRoute = ' - '.join([str(adress) for adress in fullroute]) 
	print(StrRoute + " |" + attalums)
	with open("routi.txt", "a", encoding='utf8') as outfile: 
		outfile.write('\n')
		outfile.write(StrRoute + " |" + attalums)

def RouteBot():
	global browser, iteracijas
	chrome_options = Options()
	chrome_options.add_argument("--incognito")
	if visibility == 0:
		chrome_options.add_argument("--headless")
	browser = webdriver.Chrome(executable_path=path,options=chrome_options)
	browser.get('http://www.optimap.net/')
	RandomAdreses = random.sample(AdressArray, StopCount)
	print(RandomAdreses)
	#iznjemt sakumpunktu ja randomaa iekriit
	try:
		RandomAdreses.remove(f"{AdressArray[0]}")
	except:
		pass
	AdressList = f"{AdressArray[0]}\n" + '\n'.join([str(adressR) for adressR in RandomAdreses])
	try:
		time.sleep(1)
		browser.find_element(By.XPATH, '/html/body/div[2]/div[3]/div[2]/table/tbody/tr/td[1]/input').click()#clicks uz BULK ADD buttona
	except:
		print("BULK ADD ADRESSES nav atrasts!")
	time.sleep(2)
	browser.find_element(By.XPATH, '//*[@id="dialogBulk"]/form/textarea').clear()
	browser.find_element(By.XPATH, '//*[@id="dialogBulk"]/form/textarea').send_keys(AdressList)#paste adreshu listi logaa
	time.sleep(1)
	browser.find_element(By.XPATH, '//*[@id="dialogBulk"]/form/input').click()#confirmo inputu
	time.sleep(1)
	browser.find_element(By.XPATH, '//*[@id="calculateButton"]').click()#spiezh calculate - atver next boxu
	time.sleep(2)
	browser.find_element(By.XPATH, '//*[@id="metricUnits"]').click()#iekeksee lai reekina km
	time.sleep(1)
	browser.find_element(By.XPATH, f'//*[@id="dialogOptions"]/p[3]/input[{triptype}]').click()#Spiezh calcualte fastest Roundtrip # for A-Z trip change 1 to 2 (//*[@id="dialogOptions"]/p[3]/input[2])
	#Explicit wait - 15 sec max vai liidz paraadaas elements
	WebDriverWait(browser, 15).until(EC.presence_of_element_located((By.XPATH, '//*[@id="my_textual_div"]/table/tbody/tr[1]/td[2]/div[1]')))
	#print/output modulis
	WriteOutput()
	browser.find_element(By.XPATH, '//*[@id="editButton"]').click()
	time.sleep(1)
	#Pa vienai dzeesh aaraa starp-pieturas un piefiksee datus katru reizi
	while(pieturuSkaits > 1):
		randPiet = random.randint(1,int(pieturuSkaits))
		time.sleep(1)
		browser.find_element_by_id(f'dragClose{randPiet}').click()#click on edit button
		time.sleep(2)
		WriteOutput()
	browser.quit()
	iteracijas -= 1
#####Skripta izpilde#####
while(iteracijas > 0):
	RouteBot()
	time.sleep(3)