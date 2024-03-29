# send_email.py
import yagmail
import base64

def send_email(username, password, recipient, subject, body):
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
    # repo_data_str = 'eyJhbGwiOlt7InRpdGxlIjoibGVwdG9uYWkvc2VhcmNoX3dpdGhfbGVwdG9uIiwiZGVzY3JpcHRpb24iOiJCdWlsZGluZyBhIHF1aWNrIGNvbnZlcnNhdGlvbi1iYXNlZCBzZWFyY2ggZGVtbyB3aXRoIExlcHRvbiBBSS4iLCJsYW5ndWFnZSI6IlR5cGVTY3JpcHQiLCJzdGFycyI6IjMsNTM1IiwidG9kYXlTdGFycyI6IjEsMzA4IHN0YXJzIHRvZGF5IiwibGluayI6Ii9sZXB0b25haS9zZWFyY2hfd2l0aF9sZXB0b24ifSx7InRpdGxlIjoicmFzYnQvTExNcy1mcm9tLXNjcmF0Y2giLCJkZXNjcmlwdGlvbiI6IkltcGxlbWVudGluZyBhIENoYXRHUFQtbGlrZSBMTE0gZnJvbSBzY3JhdGNoLCBzdGVwIGJ5IHN0ZXAiLCJsYW5ndWFnZSI6Ikp1cHl0ZXIgTm90ZWJvb2siLCJzdGFycyI6IjUsNTU5IiwidG9kYXlTdGFycyI6IjEsNzk4IHN0YXJzIHRvZGF5IiwibGluayI6Ii9yYXNidC9MTE1zLWZyb20tc2NyYXRjaCJ9LHsidGl0bGUiOiJ2aWtoeWF0L21vb25kcmVhbSIsImRlc2NyaXB0aW9uIjoidGlueSB2aXNpb24gbGFuZ3VhZ2UgbW9kZWwiLCJsYW5ndWFnZSI6IlB5dGhvbiIsInN0YXJzIjoiOTE3IiwidG9kYXlTdGFycyI6IjEzOCBzdGFycyB0b2RheSIsImxpbmsiOiIvdmlraHlhdC9tb29uZHJlYW0ifSx7InRpdGxlIjoiZmVkZXJpY28tYnVzYXRvL01vZGVybi1DUFAtUHJvZ3JhbW1pbmciLCJkZXNjcmlwdGlvbiI6Ik1vZGVybiBDKysgUHJvZ3JhbW1pbmcgQ291cnNlIChDKysxMS8xNC8xNy8yMC8yMykiLCJsYW5ndWFnZSI6IiIsInN0YXJzIjoiOSw1MDEiLCJ0b2RheVN0YXJzIjoiNDcgc3RhcnMgdG9kYXkiLCJsaW5rIjoiL2ZlZGVyaWNvLWJ1c2F0by9Nb2Rlcm4tQ1BQLVByb2dyYW1taW5nIn0seyJ0aXRsZSI6IkthaXNlbkFtaW4vY19zdGQiLCJkZXNjcmlwdGlvbiI6IkltcGxlbWVudGF0aW9uIG9mIEMrKyBzdGFuZGFyZCBsaWJyYXJpZXMgaW4gQyIsImxhbmd1YWdlIjoiQyIsInN0YXJzIjoiNzY2IiwidG9kYXlTdGFycyI6IjIzMSBzdGFycyB0b2RheSIsImxpbmsiOiIvS2Fpc2VuQW1pbi9jX3N0ZCJ9LHsidGl0bGUiOiJoNHgwci1kei9DVkUtMjAyNC0yMzg5NyIsImRlc2NyaXB0aW9uIjoiQ1ZFLTIwMjQtMjM4OTciLCJsYW5ndWFnZSI6IlB5dGhvbiIsInN0YXJzIjoiOTUiLCJ0b2RheVN0YXJzIjoiMTUgc3RhcnMgdG9kYXkiLCJsaW5rIjoiL2g0eDByLWR6L0NWRS0yMDI0LTIzODk3In0seyJ0aXRsZSI6Iklua2JveFNvZnR3YXJlL2V4Y2VsQ1BVIiwiZGVzY3JpcHRpb24iOiIxNi1iaXQgQ1BVIGZvciBFeGNlbCwgYW5kIHJlbGF0ZWQgZmlsZXMiLCJsYW5ndWFnZSI6IlB5dGhvbiIsInN0YXJzIjoiOTc3IiwidG9kYXlTdGFycyI6IjQ4MiBzdGFycyB0b2RheSIsImxpbmsiOiIvSW5rYm94U29mdHdhcmUvZXhjZWxDUFUifSx7InRpdGxlIjoiMDEtYWkvWWkiLCJkZXNjcmlwdGlvbiI6IkEgc2VyaWVzIG9mIGxhcmdlIGxhbmd1YWdlIG1vZGVscyB0cmFpbmVkIGZyb20gc2NyYXRjaCBieSBkZXZlbG9wZXJzIEAwMS1haSIsImxhbmd1YWdlIjoiUHl0aG9uIiwic3RhcnMiOiI1LDc5NCIsInRvZGF5U3RhcnMiOiI0MyBzdGFycyB0b2RheSIsImxpbmsiOiIvMDEtYWkvWWkifSx7InRpdGxlIjoicHJhY3RpY2FsLXR1dG9yaWFscy9wcm9qZWN0LWJhc2VkLWxlYXJuaW5nIiwiZGVzY3JpcHRpb24iOiJDdXJhdGVkIGxpc3Qgb2YgcHJvamVjdC1iYXNlZCB0dXRvcmlhbHMiLCJsYW5ndWFnZSI6IiIsInN0YXJzIjoiMTUzLDcyMyIsInRvZGF5U3RhcnMiOiI3NjMgc3RhcnMgdG9kYXkiLCJsaW5rIjoiL3ByYWN0aWNhbC10dXRvcmlhbHMvcHJvamVjdC1iYXNlZC1sZWFybmluZyJ9LHsidGl0bGUiOiJmYXJoYW5hc2hyYWZkZXYvOTBEYXlzT2ZDeWJlclNlY3VyaXR5IiwiZGVzY3JpcHRpb24iOiJUaGlzIHJlcG9zaXRvcnkgY29udGFpbnMgYSA5MC1kYXkgY3liZXJzZWN1cml0eSBzdHVkeSBwbGFuLCBhbG9uZyB3aXRoIHJlc291cmNlcyBhbmQgbWF0ZXJpYWxzIGZvciBsZWFybmluZyB2YXJpb3VzIGN5YmVyc2VjdXJpdHkgY29uY2VwdHMgYW5kIHRlY2hub2xvZ2llcy4gVGhlIHBsYW4gaXMgb3JnYW5pemVkIGludG8gZGFpbHkgdGFza3MsIGNvdmVyaW5nIHRvcGljcyBzdWNoIGFzIE5ldHdvcmsrLCBTZWN1cml0eSssIExpbnV4LCBQeXRob24sIFRyYWZmaWMgQW5hbHlzaXMsIEdpdCwgRUxLLCBBV1MsIEF6dXJlLCBhbmQgSGFja2luZy4gVGhlIHJlcG9zaXRvcnkgYWxzbyBpbmNsdWRlcyBhIGBMRUFSTi5tZCIsImxhbmd1YWdlIjoiIiwic3RhcnMiOiI0LDA0OSIsInRvZGF5U3RhcnMiOiIxNzEgc3RhcnMgdG9kYXkiLCJsaW5rIjoiL2ZhcmhhbmFzaHJhZmRldi85MERheXNPZkN5YmVyU2VjdXJpdHkifSx7InRpdGxlIjoidHJpbXN0cmF5L3RoZS1ib29rLW9mLXNlY3JldC1rbm93bGVkZ2UiLCJkZXNjcmlwdGlvbiI6IkEgY29sbGVjdGlvbiBvZiBpbnNwaXJpbmcgbGlzdHMsIG1hbnVhbHMsIGNoZWF0c2hlZXRzLCBibG9ncywgaGFja3MsIG9uZS1saW5lcnMsIGNsaS93ZWIgdG9vbHMgYW5kIG1vcmUuIiwibGFuZ3VhZ2UiOiIiLCJzdGFycyI6IjEyMCw4NDkiLCJ0b2RheVN0YXJzIjoiMjc5IHN0YXJzIHRvZGF5IiwibGluayI6Ii90cmltc3RyYXkvdGhlLWJvb2stb2Ytc2VjcmV0LWtub3dsZWRnZSJ9LHsidGl0bGUiOiJsaXpvbmd5aW5nL215LXR2IiwiZGVzY3JpcHRpb24iOiLmiJHnmoTnlLXop4Yg55S16KeG55u05pKt6L2v5Lu277yM5a6J6KOF5Y2z5Y+v5L2/55SoIiwibGFuZ3VhZ2UiOiJDIiwic3RhcnMiOiIzLDQyNCIsInRvZGF5U3RhcnMiOiIzNzkgc3RhcnMgdG9kYXkiLCJsaW5rIjoiL2xpem9uZ3lpbmcvbXktdHYifSx7InRpdGxlIjoiZGFuaWVsbWllc3NsZXIvZmFicmljIiwiZGVzY3JpcHRpb24iOiJmYWJyaWMgaXMgYW4gb3Blbi1zb3VyY2UgZnJhbWV3b3JrIGZvciBhdWdtZW50aW5nIGh1bWFucyB1c2luZyBBSS4iLCJsYW5ndWFnZSI6IlB5dGhvbiIsInN0YXJzIjoiMzc4IiwidG9kYXlTdGFycyI6IjkzIHN0YXJzIHRvZGF5IiwibGluayI6Ii9kYW5pZWxtaWVzc2xlci9mYWJyaWMifSx7InRpdGxlIjoiVGFza2luZ0FJL1Rhc2tpbmdBSSIsImRlc2NyaXB0aW9uIjoiVGhlIG9wZW4gc291cmNlIHBsYXRmb3JtIGZvciBBSS1uYXRpdmUgYXBwbGljYXRpb24gZGV2ZWxvcG1lbnQuIiwibGFuZ3VhZ2UiOiJQeXRob24iLCJzdGFycyI6IjgwOCIsInRvZGF5U3RhcnMiOiIzMTYgc3RhcnMgdG9kYXkiLCJsaW5rIjoiL1Rhc2tpbmdBSS9UYXNraW5nQUkifSx7InRpdGxlIjoicGxhc21hLXVtYXNzL3NjYWxlbmUiLCJkZXNjcmlwdGlvbiI6IlNjYWxlbmU6IGEgaGlnaC1wZXJmb3JtYW5jZSwgaGlnaC1wcmVjaXNpb24gQ1BVLCBHUFUsIGFuZCBtZW1vcnkgcHJvZmlsZXIgZm9yIFB5dGhvbiB3aXRoIEFJLXBvd2VyZWQgb3B0aW1pemF0aW9uIHByb3Bvc2FscyIsImxhbmd1YWdlIjoiSmF2YVNjcmlwdCIsInN0YXJzIjoiMTAsNzA2IiwidG9kYXlTdGFycyI6IjI2IHN0YXJzIHRvZGF5IiwibGluayI6Ii9wbGFzbWEtdW1hc3Mvc2NhbGVuZSJ9LHsidGl0bGUiOiJzYWFnYXJqaGEvRW5zZW1ibGUiLCJkZXNjcmlwdGlvbiI6IkNhc3QgTWFjIHdpbmRvd3MgdG8gdmlzaW9uT1MiLCJsYW5ndWFnZSI6IlN3aWZ0Iiwic3RhcnMiOiIzMjUiLCJ0b2RheVN0YXJzIjoiNzQgc3RhcnMgdG9kYXkiLCJsaW5rIjoiL3NhYWdhcmpoYS9FbnNlbWJsZSJ9LHsidGl0bGUiOiJwdXBwZXRlZXIvcHVwcGV0ZWVyIiwiZGVzY3JpcHRpb24iOiJOb2RlLmpzIEFQSSBmb3IgQ2hyb21lIiwibGFuZ3VhZ2UiOiJUeXBlU2NyaXB0Iiwic3RhcnMiOiI4NSw5MDMiLCJ0b2RheVN0YXJzIjoiMjAgc3RhcnMgdG9kYXkiLCJsaW5rIjoiL3B1cHBldGVlci9wdXBwZXRlZXIifSx7InRpdGxlIjoiRGF0YVRhbGtzQ2x1Yi9kYXRhLWVuZ2luZWVyaW5nLXpvb21jYW1wIiwiZGVzY3JpcHRpb24iOiJGcmVlIERhdGEgRW5naW5lZXJpbmcgY291cnNlISIsImxhbmd1YWdlIjoiSnVweXRlciBOb3RlYm9vayIsInN0YXJzIjoiMjAsMjc4IiwidG9kYXlTdGFycyI6IjI1NSBzdGFycyB0b2RheSIsImxpbmsiOiIvRGF0YVRhbGtzQ2x1Yi9kYXRhLWVuZ2luZWVyaW5nLXpvb21jYW1wIn0seyJ0aXRsZSI6Im5pY2tub2NobmFjay9NTFRyYWRpbmdCb3QiLCJkZXNjcmlwdGlvbiI6IiIsImxhbmd1YWdlIjoiSFRNTCIsInN0YXJzIjoiMzA3IiwidG9kYXlTdGFycyI6IjE0NCBzdGFycyB0b2RheSIsImxpbmsiOiIvbmlja25vY2huYWNrL01MVHJhZGluZ0JvdCJ9LHsidGl0bGUiOiJBc2FiZW5laC8zMC1EYXlzLU9mLVB5dGhvbiIsImRlc2NyaXB0aW9uIjoiMzAgZGF5cyBvZiBQeXRob24gcHJvZ3JhbW1pbmcgY2hhbGxlbmdlIGlzIGEgc3RlcC1ieS1zdGVwIGd1aWRlIHRvIGxlYXJuIHRoZSBQeXRob24gcHJvZ3JhbW1pbmcgbGFuZ3VhZ2UgaW4gMzAgZGF5cy4gVGhpcyBjaGFsbGVuZ2UgbWF5IHRha2UgbW9yZSB0aGFuMTAwIGRheXMsIGZvbGxvdyB5b3VyIG93biBwYWNlLiBUaGVzZSB2aWRlb3MgbWF5IGhlbHAgdG9vOiBodHRwczovL3d3dy55b3V0dWJlLmNvbS9jaGFubmVsL1VDN1BOUnVubzFyellQYjF4TGE0eWt0dyIsImxhbmd1YWdlIjoiUHl0aG9uIiwic3RhcnMiOiIyOCw2MjciLCJ0b2RheVN0YXJzIjoiNTMgc3RhcnMgdG9kYXkiLCJsaW5rIjoiL0FzYWJlbmVoLzMwLURheXMtT2YtUHl0aG9uIn0seyJ0aXRsZSI6ImZhY2Vib29rcmVzZWFyY2gvY29kZWxsYW1hIiwiZGVzY3JpcHRpb24iOiJJbmZlcmVuY2UgY29kZSBmb3IgQ29kZUxsYW1hIG1vZGVscyIsImxhbmd1YWdlIjoiUHl0aG9uIiwic3RhcnMiOiIxMiwzNzAiLCJ0b2RheVN0YXJzIjoiMTg0IHN0YXJzIHRvZGF5IiwibGluayI6Ii9mYWNlYm9va3Jlc2VhcmNoL2NvZGVsbGFtYSJ9LHsidGl0bGUiOiJGdWVsTGFicy9zd2F5IiwiZGVzY3JpcHRpb24iOiLwn4y0IEVtcG93ZXJpbmcgZXZlcnlvbmUgdG8gYnVpbGQgcmVsaWFibGUgYW5kIGVmZmljaWVudCBzbWFydCBjb250cmFjdHMuIiwibGFuZ3VhZ2UiOiJSdXN0Iiwic3RhcnMiOiI0Myw4MDciLCJ0b2RheVN0YXJzIjoiNjI3IHN0YXJzIHRvZGF5IiwibGluayI6Ii9GdWVsTGFicy9zd2F5In0seyJ0aXRsZSI6InZlcmNlbC9uZXh0LmpzIiwiZGVzY3JpcHRpb24iOiJUaGUgUmVhY3QgRnJhbWV3b3JrIiwibGFuZ3VhZ2UiOiJKYXZhU2NyaXB0Iiwic3RhcnMiOiIxMTcsMzgyIiwidG9kYXlTdGFycyI6IjU0IHN0YXJzIHRvZGF5IiwibGluayI6Ii92ZXJjZWwvbmV4dC5qcyJ9LHsidGl0bGUiOiJNYXRzdXJpRGF5by9OZWtvQm94Rm9yQW5kcm9pZCIsImRlc2NyaXB0aW9uIjoiTmVrb0JveCBmb3IgQW5kcm9pZCAvIHNpbmctYm94IC8gdW5pdmVyc2FsIHByb3h5IHRvb2xjaGFpbiBmb3IgQW5kcm9pZCIsImxhbmd1YWdlIjoiS290bGluIiwic3RhcnMiOiI2LDUwOCIsInRvZGF5U3RhcnMiOiIyNSBzdGFycyB0b2RheSIsImxpbmsiOiIvTWF0c3VyaURheW8vTmVrb0JveEZvckFuZHJvaWQifSx7InRpdGxlIjoiemVkZXVzL25pdHRlciIsImRlc2NyaXB0aW9uIjoiQWx0ZXJuYXRpdmUgVHdpdHRlciBmcm9udC1lbmQiLCJsYW5ndWFnZSI6Ik5pbSIsInN0YXJzIjoiOSwyODciLCJ0b2RheVN0YXJzIjoiNjUgc3RhcnMgdG9kYXkiLCJsaW5rIjoiL3plZGV1cy9uaXR0ZXIifV19'
    repo_data_decoded_bytes = base64.urlsafe_b64decode(repo_data_str)
    repo_data = json.loads(repo_data_decoded_bytes.decode('utf-8'))
    repo_tables_map = {}
    repo_items = repo_data.items()
    for key, repos in repo_items:
        content += format_language_table(key if key else 'All', repos)
    send_email(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], content)



