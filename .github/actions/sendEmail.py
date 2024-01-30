# send_email.py
import yagmail

def send_email(username, password, recipient, subject, body):
    print('username', username, 'subject', subject)
    yag = yagmail.SMTP(username, password)
    yag.send(to=recipient, subject=subject, contents=body)
    print('Email sent successfully')

if __name__ == '__main__':
    import sys
    content = ''
    repo_data = sys.argv[5]
    for key, repos in repo_data:
        for index, repo in repos:
            content += "{title}--{description}-{language}-{stars}-{todayStars}".format(repo.title, repo.description, repo.language, repo.stars, repo.todayStars)

    print('content', content)
    send_email(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], content)
