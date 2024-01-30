# send_email.py
import yagmail
import base64

def send_email(username, password, recipient, subject, body):
    print('username', username, 'subject', subject)
    yag = yagmail.SMTP(username, password)
    yag.send(to=recipient, subject=subject, contents=body)
    print('Email sent successfully')

if __name__ == '__main__':
    import sys
    import json
    content = ''
    repo_data_str = sys.argv[5]
    repo_data_decoded_bytes = base64.urlsafe_b64decode(repo_data_str)
    repo_data = json.loads(repo_data_decoded_bytes.decode('utf-8'))

    repo_items = repo_data.items()
    for key, repos in repo_items:
        for i, repo in enumerate(repos):
            repo_item_str = "{}--{}-{}-{}-{}\n".format(repo['title'], repo['description'], repo['language'], repo['stars'], repo['todayStars'])
            content += repo_item_str
    send_email(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], content)



