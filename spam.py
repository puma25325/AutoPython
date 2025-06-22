
import threading
import random
import time
from datetime import datetime,timezone,timedelta
from packages.user import User

from packages import file,github,mail

content_array = file.read_base_data("./assets/base/_contents.json")
location_array = file.read_base_data("./assets/base/_locations.json")
mail_array = file.read_base_data("./assets/base/_mails.json")
subject_array =  file.read_base_data("./assets/base/_subjects.json")

spam_check = ""
for index, mail_address in enumerate(mail_array):
	service = mail.gmail_authenticate(mail_address)
	succeed = mail.send_email(service,mail_address,spam_check,random.choice(subject_array)+" There",random.choice(content_array))
	print(f"{index+1} --> {mail_address} --> sent to mail")