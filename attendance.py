from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re
import os.path
from os import path
import sqlite3
import schedule
from datetime import datetime
from selenium.webdriver.common.action_chains import ActionChains

opt = Options()
opt.add_argument("--disable-infobars")
opt.add_argument("start-maximized")
opt.add_argument("--disable-extensions")
opt.add_argument("--start-maximized")
opt.add_experimental_option("prefs", { \
		"profile.default_content_setting_values.media_stream_mic": 1, 
		"profile.default_content_setting_values.media_stream_camera": 1,
		"profile.default_content_setting_values.geolocation": 1, 
		"profile.default_content_setting_values.notifications": 1 
	})

URL = "YOUR MOODLE URL ( ENDED WITH /MY )"

CREDS = {'username' : 'YOUR_MOODLE_USERNAME','passwd':'YOUR_MOODLE_PASSWORD'}

def start_browser():
	global driver
	driver = webdriver.Chrome(executable_path="chromedriver.exe",options=opt,service_log_path='NUL')

def login():
	global driver
	usernameField = driver.find_element_by_xpath('//*[@id="username"]')
	passwordField = driver.find_element_by_xpath('//*[@id="password"]')
	loginBtn = driver.find_element_by_xpath('//*[@id="loginbtn"]')
	usernameField.click()
	usernameField.send_keys(CREDS['username'])
	print('[+] Masuk ke halaman login')
	passwordField.click()
	passwordField.send_keys(CREDS['passwd'])
	loginBtn.click()
	print('[+] Berhasil login')

def masukKelas(link_kelas):
	global driver
	if("course" in link_kelas):
		driver.get(link_kelas)
		driver.find_element_by_xpath('//li[@class="section main clearfix current"]/div[3]/ul/li[@class="activity attendance modtype_attendance "]/div/div/div[2]/div/a').click()
	else:
		driver.get(link_kelas)
	attendance = driver.find_element_by_xpath('//a[contains(text(),"Submit attendance")]')
	attendance.click()
	print('[+] Mengklik tombol submit attendence')
	present = driver.find_element_by_xpath('//span[contains(text(),"Present") and @class="statusdesc"]')
	present.click()
	print('[+] Mengklik tombol present')
	submit = driver.find_element_by_xpath('//*[@id="id_submitbutton"]')
	submit.click()
	print('[+] Mengklik tombol submit')

def validate_input(regex,inp):
	if not re.match(regex,inp):
		return False
	return True

def validate_day(inp):
	days = ["senin","selasa","rabu","kamis","jumat","sabtu","minggu"]

	if inp.lower() in days:
		return True
	else:
		return False

def createDB():
	conn = sqlite3.connect('timetable.db')
	c=conn.cursor()
	# Create table
	c.execute('''CREATE TABLE timetable (id INTEGER PRIMARY KEY AUTOINCREMENT, nama TEXT, link TEXT, hari TEXT, jam TEXT)''')
	conn.commit()
	conn.close()
	print("database timetable berhasil dibuat")

def add_database():
	if(not(path.exists("timetable.db"))):
			createDB()
	op = int(input("1. Tambah Jadwal\n2. Selesai Tambah\nMasukan Opsi : "))
	while(op==1):
		name = input("Masukan nama kelas : ")

		day = input("Masukan hari (senin, selasa, rabu, kamis, jumat, sabtu, minggu): ")
		while not(validate_day(day.strip())):
			print("format salah, silahkan ulangi lagi")
			end_time = input("Masukan hari (senin, selasa, rabu, kamis, jumat, sabtu, minggu) : ")

		start_time = input("Masukan jam mulai kelas (format HH:MM contoh 07:00) : ")
		while not(validate_input("\d\d:\d\d",start_time)):
			print("format salah, silahkan ulangi lagi")
			start_time = input("Masukan jam mulai kelas (format HH:MM contoh 07:00) : ")

		links = input("Masukan link attendance kelas-nya ( https://elearning.itenas.ac.id/mod/attendance/view.php?id=38907 ), masukan link kelas jika link attendance berbeda beda tiap pertemuan : ")

		conn = sqlite3.connect('timetable.db')
		c=conn.cursor()

		# Insert a row of data
		c.execute("INSERT INTO timetable(nama, link, hari, jam) VALUES ('%s','%s','%s','%s')"%(name,links,day,start_time))

		conn.commit()
		conn.close()

		print("Kelas berhasil ditambah ke database\n")

		op = int(input("1. Tambah Jadwal\n2. Selesai Tambah\nMasukan Opsi : "))

def view_timetable():
	conn = sqlite3.connect('timetable.db')
	c=conn.cursor()
	for row in c.execute('SELECT * FROM timetable'):
		print(row)
	conn.close()

def startBot():
	start_browser()
	driver.get(URL)
	if("elearning.itenas.ac.id/login/index.php" in driver.current_url):
		login()
	time.sleep(1)

def sched():
	conn = sqlite3.connect('timetable.db')
	c=conn.cursor()
	for row in c.execute('SELECT * FROM timetable'):
		#schedule all classes
		name = row[1]
		links = row[2]
		day = row[3]
		start_time = row[4]

		if day.lower()=="senin":
			schedule.every().monday.at(start_time).do(masukKelas,links)
			print("[-] Database berhasil di import untuk kelas '%s' hari %s jam %s"%(name,day,start_time))
		if day.lower()=="selasa":
			schedule.every().tuesday.at(start_time).do(masukKelas,links)
			print("[-] Database berhasil di import untuk kelas '%s' on %s at %s"%(name,day,start_time))
		if day.lower()=="rabu":
			schedule.every().wednesday.at(start_time).do(masukKelas,links)
			print("[-] Database berhasil di import untuk kelas '%s' on %s at %s"%(name,day,start_time))
		if day.lower()=="kamis":
			schedule.every().thursday.at(start_time).do(masukKelas,links)
			print("[-] Database berhasil di import untuk kelas '%s' on %s at %s"%(name,day,start_time))
		if day.lower()=="jumat":
			schedule.every().friday.at(start_time).do(masukKelas,links)
			print("[-] Database berhasil di import untuk kelas '%s' on %s at %s"%(name,day,start_time))
		if day.lower()=="sabtu":
			schedule.every().saturday.at(start_time).do(masukKelas,links)
			print("[-] Database berhasil di import untuk kelas '%s' on %s at %s"%(name,day,start_time))
		if day.lower()=="minggu":
			schedule.every().sunday.at(start_time).do(masukKelas,links)
			print("[-] Database berhasil di import untuk kelas '%s' on %s at %s"%(name,day,start_time))

	#Start browser
	startBot()
	while True:
		# Checks whether a scheduled task
		# is pending to run or not
		schedule.run_pending()
		time.sleep(1)


if __name__=="__main__":
	op = int(input(("1. Modifikasi Database\n2. Lihat Database\n3. Mulai Bot\nMasukan Opsi: ")))
	if(op == 1):
		add_database()
	if(op == 2):
		view_timetable()
	if(op == 3):
		sched()
