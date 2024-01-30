import yagmail
import sys
username = sys.argv[1]
password = sys.argv[2]
repo_data = sys.argv[3]

def send_email():
    try:
        content = ''
        for key, repos in repo_data:
            for index, repo in repos:
                content += "{title}--{description}-{language}-{stars}-{todayStars}".format(repo.title, repo.description, repo.language, repo.stars, repo.todayStars)
        yag = yagmail.SMTP('${{ secrets.GMAIL_USERNAME }}', '${{ secrets.GMAIL_PASSWORD }}')
        yag.send(to='${{ secrets.GMAIL_USERNAME }}', subject='Github trending repos', contents=content)
        print('Email sent successfully')
    except Exception as e:
        print(f'Failed to send email: {e}')

send_email()