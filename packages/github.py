import requests
import time
import sys

from pathlib import Path
cwd = Path.cwd()
sys.path.append(str(cwd)+"\packages") 
from file import read_base_data
from user import User

GITHUB_TOKEN = read_base_data(str(cwd)+"\\assets\\base\\_githubtoken.json")["GITHUB_TOKEN"]
print(GITHUB_TOKEN)
HEADERS = {
	"Authorization": f"token {GITHUB_TOKEN}"
}

def get_github_email( nth_number,location,language,created) -> User:
	#https://api.github.com/search/users?q=location:India+language:Python+created:>2022-01-01
	url = f"https://api.github.com/search/users?q=location:{location}+language:{language}+created:{created}&per_page=1&page={nth_number}"
	while True:
		try:
			response = requests.get(url,headers=HEADERS)
			users = response.json().get("items", [])
			message = response.json().get("message","")
			if len(users) == 0:
				if("limit" not in message):
					print(f"No more users found {url}. Ending search.")
				return User("","","")
			user = users[0]
			must_find = True
			while must_find:
				try:                        
					username = user['login']
					user_details = requests.get(f"https://api.github.com/users/{username}", headers=HEADERS).json()
					if user_details.get("message") == "Not Found":
						time.sleep(10)
						continue
					name = user_details.get("name", "Not Public")
					if not name:
						name = "There"
					repos = requests.get(f"https://api.github.com/users/{username}/repos?per_page=2&sort=updated", headers=HEADERS).json()
					if not repos or len(repos) == 0:
						time.sleep(10)
						continue
					repo_name = repos[0]['name']
					commits = requests.get(f"https://api.github.com/repos/{username}/{repo_name}/commits", headers=HEADERS).json()
					if not commits or len(commits) == 0:
						time.sleep(10)
						continue
					email = commits[0]['commit']['author']['email']
					return User(email,username,name)

				except Exception as e:
					err_str = str(e)
					if "empty" in err_str or "not found" in err_str or err_str == '0':
						return User("","","")
					time.sleep(10)
		except Exception as e:
			time.sleep(5)
