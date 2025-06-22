
import json
from datetime import datetime,timezone
def update_page_file(path, next_page):
	try:
		with open(path,"w") as file:
			file.write(str(next_page))
			return True
		return False
	except Exception as err:
		print(f"Error in update_page_file {path}  --> {err}")
		return False
	

def update_sent_file(path, logname, realname,mail_address,page):
	try:
		with open(path,"a") as file:
			file.write(f"{datetime.now(timezone.utc)} --> logname:{logname} --> realname:{realname} --> mailAddress:{mail_address} --> currentPage:{page}\n")
			return True
		return False
	except Exception as err:
		print(f"Error in update_sent_file {path}  --> {err}")
		return False
	
def read_base_data(path):
	try:
		with open(path,"r") as file:
			data_array = json.load(file)
			return data_array
		return []
	except Exception as err:
		print(f"Error in read_base_data {path}  --> {err}")
		return False
	

def get_page_num(path):
	page_num = 0
	try:
		with open(path,"r") as file:
			content = file.read()
			page_num = int(content.strip())
	except FileNotFoundError:
		page_num = 1
	except ValueError:
		page_num = 1
	return page_num