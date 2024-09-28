# send_email.py
import yagmail
import base64

def send_email(username, password, recipient, subject, body):
    print("username", username)
    print("password", password)
    print("recipient", recipient)
    print("subject", subject)
    print("body", body)
    yag = yagmail.SMTP(username, password)
    yag.send(to=recipient, subject=subject, contents=body, prettify_html=False)
    print('Email sent successfully')

def format_language_table(language: str, repos):
    # 构建 HTML 邮件内容
    html_content = """
    <table>
    <tr>
        <th style="border: 1px solid #ccc;border-collapse: collapse;padding: 8px;text-align: left;">Title</th>
        <th style="border: 1px solid #ccc;border-collapse: collapse;padding: 8px;text-align: left;">Description</th>
        <th style="border: 1px solid #ccc;border-collapse: collapse;padding: 8px;text-align: left;">Language</th>
        <th style="border: 1px solid #ccc;border-collapse: collapse;padding: 8px;text-align: left;">Stars</th>
        <th style="border: 1px solid #ccc;border-collapse: collapse;padding: 8px;text-align: left;">Today's Stars</th>
    </tr>
    """

    # 添加每个仓库的信息到表格
    for repo in repos:
        html_content += f"""
        <tr>
            <td style="border: 1px solid #ccc;border-collapse: collapse;padding: 8px;text-align: left;font-size:18px;font-weight: bold;"><a class="link" href="{'https://github.com' + repo['link'] if repo['link'] else ""}">{repo['title']}</a></td>
            <td style="border: 1px solid #ccc;border-collapse: collapse;padding: 8px;text-align: left;font-size:16px; color: #333;">{repo['description']}</td>
            <td style="border: 1px solid #ccc;border-collapse: collapse;padding: 8px;text-align: left;color: green;">{repo['language']}</td>
            <td style="border: 1px solid #ccc;border-collapse: collapse;padding: 8px;text-align: left;color: #4fb233; font-size: 16px;">{repo['stars']}</td>
            <td style="border: 1px solid #ccc;border-collapse: collapse;padding: 8px;text-align: left;color: #4fb233; font-size: 16px;">{repo['todayStars']}</td>
        </tr>
        """

    # 结束 HTML 文档
    html_content += """
    </table>
    """
    return language.capitalize() + ' Repos:' + html_content

if __name__ == '__main__':
    import sys
    import json
    content = ''
    repo_data_str = sys.argv[5]
    repo_data_decoded_bytes = base64.urlsafe_b64decode(repo_data_str)
    repo_data = json.loads(repo_data_decoded_bytes.decode('utf-8'))
    repo_tables_map = {}
    repo_items = repo_data.items()
    for key, repos in repo_items:
        content += format_language_table(key if key else 'All', repos)
    send_email(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], content)



