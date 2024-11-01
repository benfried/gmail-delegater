from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
import sys

# Service account credentials
# This file was generated on the google cloud console (or maybe by the gcloud cli)
# The service account was created with:
# $ gcloud iam service-accounts create gmail-delegater --display-name="gmail-delegater"
SERVICE_ACCOUNT_FILE = './gmail-delegater.json'
SCOPES = ['https://www.googleapis.com/auth/gmail.settings.sharing',
          'https://www.googleapis.com/auth/gmail.settings.basic']

# User's email address
USER_EMAIL = 'unset@unset.com'

# Delegate's email address
DELEGATE_EMAIL = 'unset-delegate@unset.com'

def create_delegate(service, user_id, delegate_email):
  """Creates a delegate for the user."""
  try:
    delegate = (
        service.users()
        .settings()
        .delegates()
        .create(userId=user_id, body={'delegateEmail': delegate_email})
        .execute()
    )
    print(f'Delegate created: {delegate}')
  except HttpError as error:
    print(f'An error occurred: {error}')

def delete_delegate(service, user_id, delegate_email):
  """Deletes a delegate for the user."""
  try:
    (
        service.users()
        .settings()
        .delegates()
        .delete(userId=user_id, delegateEmail=delegate_email)
        .execute()
    )
    print(f'Delegate deleted: {delegate_email}')
  except HttpError as error:
    print(f'An error occurred: {error}')


def read_delegates(service, user_id):
    """Retrieves and prints the email addresses of delegates for a user.

    Args:
      service: The Gmail API service instance.
      user_id: The ID of the user.
    """
    try:
        results = service.users().settings().delegates().list(userId=user_id).execute()
        delegates = results.get('delegates', [])

        if not delegates:
            print(f'No delegates found for user {user_id}.')
        else:
            print(f'Delegates for user {user_id}:')
            for delegate in delegates:
                print(f' - {delegate["delegateEmail"]}')

    except Exception as error:
        print(f'An error occurred: {error}')


def main():
    """Creates a Gmail API service and changes / lists the user's delegate(s)."""

    if len(sys.argv) < 3 or len(sys.argv) > 4 :
        print(f"Usage: python {sys.argv[0]} l | a | d <user_email> [ <delegate_email> ]")
        sys.exit(1)

    command = sys.argv[1]
    USER_EMAIL = sys.argv[2]

    if command not in ('l', 'a', 'd'):
       print("illegal command")
       sys.exit(1)

    if command != 'l':
        DELEGATE_EMAIL = sys.argv[3]


    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )

    delegated_credentials = credentials.with_subject(USER_EMAIL)

    service = build('gmail', 'v1', credentials=delegated_credentials)

    if command == 'a':
        # Add a new delegate
        print(f'create_delegate(service, {USER_EMAIL}, {DELEGATE_EMAIL})')
        create_delegate(service, USER_EMAIL, DELEGATE_EMAIL)
    elif command == 'd':
        # Remove an existing delegate
        print(f'delete_delegate(service, {USER_EMAIL}, {DELEGATE_EMAIL})')
        delete_delegate(service, USER_EMAIL, DELEGATE_EMAIL)
    elif command == 'l':
        # List delegates
        print(f'read_delegate(service, {USER_EMAIL}')
        read_delegates(service, USER_EMAIL)
    
if __name__ == '__main__':
  main()