
import os
import pickle
import base64
import email
import time
from email.message import EmailMessage
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import date, timedelta,datetime,timezone
from email.utils import parsedate_to_datetime
from email.mime.text import MIMEText
SCOPES = ['https://mail.google.com/']
def gmail_authenticate(mail_address):
	try:
		creds = None
		if os.path.exists(f'./save/tokens/{mail_address}.pickle'):
			with open(f'./save/tokens/{mail_address}.pickle', 'rb') as token:
				creds = pickle.load(token)
		if not creds or not creds.valid:
			if creds and creds.expired and creds.refresh_token:
				creds.refresh(Request())
			else:
				flow = InstalledAppFlow.from_client_secrets_file(f'./assets/credentials/{mail_address}.json', SCOPES)
				creds = flow.run_local_server(port=633)
			with open(f'./save/tokens/{mail_address}.pickle', 'wb') as token:
				pickle.dump(creds, token)
		return build('gmail', 'v1', credentials=creds)
	except Exception as err:
		print(f"Error in gmail_authenticate --> {err}")
		return False

def get_sent_date_by_msg_id(service, msg_id):
	try:
		# Get message details (metadata includes headers)
		msg = service.users().messages().get(
			userId='me',
			id=msg_id,
			format='metadata'
		).execute()

		headers = msg['payload']['headers']

		# Find the 'Date' header
		date_str = next((h['value'] for h in headers if h['name'] == 'Date'), None)

		if date_str:
			# Parse it to datetime object
			parsed_date = email.utils.parsedate_to_datetime(date_str)
			return parsed_date
		else:
			return datetime.now()

	except Exception as e:
		print(f"Error in get_sent_date_by_msg_id  -->{e}")
		return False

def get_inbox_message_ids(service, max_results=50):
	try:
		result = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=max_results).execute()
		messages = result.get('messages', [])
		return [msg['id'] for msg in messages]
	except Exception as e:
		print(f"Error in get_inbox_message_ids --> {e}")
		return []

def get_received_date_by_id(service, msg_id):
	try:
		msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
		headers = msg['payload']['headers']
		for header in headers:
			if header['name'] == 'Date':
				return parsedate_to_datetime(header['value'])
		return datetime.now()
	except Exception as e:
		print(f"Error in get_received_date_by_id --> {e}")
		return None

def get_message_content_by_id(service, msg_id):
		try:
			msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
			return msg.get('snippet')
		except Exception as e:
			print(f"Error in get_message_content_by_id --> {e}")
			return ""

def delete_message(service, message_id,mail_address,content):
	try:
		service.users().messages().delete(userId='me', id=message_id).execute()
		print(f"Deleted  {content} in {mail_address}")
	except Exception as e:
		print(f"Error in  delete_message --> {e}")

def get_sent_emails_without_reply(service, max_results=500):
	try:
		no_reply_emails = []

		# List sent messages
		result = service.users().messages().list(
			userId='me',
			labelIds=['SENT'],
			maxResults=max_results
		).execute()

		sent_messages = result.get('messages', [])

		for msg in sent_messages:
			# Get detailed message info
			msg_detail = service.users().messages().get(
				userId='me',
				id=msg['id'],
				format='metadata'
			).execute()

			thread_id = msg_detail['threadId']

			# Get the full thread
			thread = service.users().threads().get(userId='me', id=thread_id).execute()
			thread_messages = thread.get('messages', [])

			# If thread only has one message (your sent one), no reply
			if len(thread_messages) == 1:
				no_reply_emails.append(msg_detail)

		return no_reply_emails
	except Exception as e:
		print(f"error in get_sent_emails_without_reply --> {e}")
		return []

def get_sent_message_ids_without_reply(service, max_results=150):
		try:
			no_reply_ids = []

			# List sent messages
			response = service.users().messages().list(
				userId='me',
				labelIds=['SENT'],
				maxResults=max_results
			).execute()

			messages = response.get('messages', [])

			for msg in messages:
				msg_id = msg['id']

				# Get message details to retrieve thread ID
				msg_detail = service.users().messages().get(
					userId='me',
					id=msg_id,
					format='metadata'
				).execute()

				thread_id = msg_detail['threadId']

				# Get the thread details
				thread = service.users().threads().get(
					userId='me',
					id=thread_id
				).execute()

				thread_messages = thread.get('messages', [])

				# If only one message in the thread, it's likely never replied to
				if len(thread_messages) == 1:
					no_reply_ids.append(msg_id)

			return no_reply_ids
		except Exception as e:
			print(f"Error in get_sent_message_ids_without_reply --> {e}")
			return []


def send_email(service,mail_address, to_email, subject, html_body):
	must_send = True
	while must_send:
		try:
			message = EmailMessage()
			message.set_content(html_body, subtype='html')
			message['To'] = to_email
			message['Subject'] = subject
			message['From'] = mail_address
			encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
			service.users().messages().send(userId="me", body={"raw": encoded_message}).execute()
			return True
		except Exception as e:
			estr = str(e)
			print(f"error in sending --> {estr}")
			if("undefined" in estr):
				print(f"  Error in send_mail: {e}")
				return False			
			time.sleep(10)  # Wait before retrying
