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
    print('repo_data_str', repo_data_str)
    repo_data_decoded_bytes = base64.urlsafe_b64decode(repo_data_str)
    # print('repo_data_str',repo_data_str, type(repo_data_str))
    repo_data = json.loads(repo_data_decoded_bytes.decode('utf-8'))

    print("repo_data", repo_data, type(repo_data))

    for key, repos in repo_data:
        for index, repo in repos:
            content += "{title}--{description}-{language}-{stars}-{todayStars}".format(repo.title, repo.description, repo.language, repo.stars, repo.todayStars)

    print('content', content)
    send_email(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], content)
