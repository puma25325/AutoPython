
import threading
import random
import time
from datetime import datetime,timezone,timedelta
from packages.user import User

from packages import file,github,mail


def check_mails(service,mail_address):
	msg_ids = mail.get_inbox_message_ids(service)
	now = datetime.now(timezone.utc)
	for msg_id in msg_ids:
		received_date = mail.get_received_date_by_id(service,msg_id)
		if(received_date):
			content = mail.get_message_content_by_id(service,msg_id)
			if "delivered" in content or "Security" in content:
				mail.delete_message(service, msg_id,mail_address,content)
			if "blocked" in content or "limit" in content:
				if now> received_date+timedelta(days=1):
					mail.delete_message(service,msg_id,mail_address,content)
					return True
				else :
					return False
	return True
content_array = file.read_base_data("./assets/base/_contents.json")
location_array = file.read_base_data("./assets/base/_locations.json")
mail_array = file.read_base_data("./assets/base/_mails.json")
subject_array =  file.read_base_data("./assets/base/_subjects.json")

def send_thread(mail_address,location,mail_number):
	service = mail.gmail_authenticate(mail_address)
	if(service):
		nth_count = file.get_page_num(f"./save/page/{mail_address}.txt")
		while True:
			if(check_mails(service,mail_address)):
				email = User("","","")
				email = github.get_github_email(nth_count,location,"farmer&type=users&s=repositories&o=desc")
				if(email.mail_address != "" and "github" not in email.mail_address and "@" in email.mail_address):
					succeed = mail.send_email(service,mail_address,email.mail_address,random.choice(subject_array)+" "+email.realname,random.choice(content_array))
					if(succeed):
						nth_count +=1
						file.update_page_file(f"./save/page/{mail_address}.txt",nth_count)
						file.update_sent_file(f"./save/sent/{mail_address}.txt",email.logname,email.realname,email.mail_address,nth_count-1)
						print(f"{mail_number} --> {mail_address} --> sent to mail {email.mail_address}")
						random_number = random.randint(1800, 2700)
						time.sleep(random_number)  # Random delay to avoid rate limiting	
						continue
					else:	
						time.sleep(10)  # Random delay to avoid rate limiting	
				else:
					nth_count+=1
					time.sleep(10)  # Random delay to avoid rate limiting	
					continue
			else:
				print(f"{mail_number} --> {mail_address} --> blocked")
				time.sleep(3600)		
					

threads =[]
#th = threading.Thread(target=send_thread,args=(mail_array[0],location_array[0],1),daemon=True)
#th.start()
#threads.append(th)
#th.join()
for index, mail_address in enumerate(mail_array):
	time.sleep(index*10)
	th = threading.Thread(target=send_thread,args=(mail_address,location_array[index],index+1),daemon=True)
	th.start()
	threads.append(th)

for t in threads:
	t.join()