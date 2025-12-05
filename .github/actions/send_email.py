# send_email.py
import yagmail
import base64
import sys
import json
import random
import string

def send_email(username, password, recipient, subject, body):
    print("Sending email...")
    yag = yagmail.SMTP(username, password)
    yag.send(to=recipient, subject=subject, contents=body, prettify_html=False)
    print('Email sent successfully')

def uid():
    """Generate unique id to prevent Gmail pattern detection"""
    return ''.join(random.choices(string.ascii_lowercase, k=4))

def format_email(data):
    html = f'''<html><body style="font-family:Arial,sans-serif;max-width:900px;margin:0 auto;padding:20px;background:#fafafa;">
<div style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);padding:30px;border-radius:12px;margin-bottom:20px;">
<h1 style="color:#fff;text-align:center;margin:0;">🔥 Tech Trending Daily</h1>
<p style="color:#e0e0e0;text-align:center;margin:10px 0 0 0;">{uid()}</p>
</div>'''

    # GitHub Trending - All languages with detailed cards
    if 'githubTrending' in data:
        gh = data['githubTrending']
        all_repos = gh.get('', gh.get('all', gh.get('All', [])))
        
        if all_repos:
            html += f'<div style="background:#24292e;padding:20px;border-radius:8px;margin-bottom:15px;" id="gh-{uid()}">'
            html += '<h2 style="color:#fff;margin:0 0 15px 0;">📦 GitHub Trending - All</h2>'
            for i, r in enumerate(all_repos[:10]):
                desc = (r.get("description","") or "")[:70]
                html += f'<div style="background:#{"2d333b" if i%2==0 else "22272e"};padding:12px;margin:5px 0;border-radius:4px;border-left:3px solid #58a6ff;">'
                html += f'<a href="https://github.com{r["link"]}" style="color:#58a6ff;font-weight:bold;text-decoration:none;">{r["title"]}</a>'
                html += f'<span style="color:#8b949e;float:right;">⭐{r["stars"]} | +{r["todayStars"]}</span>'
                html += f'<p style="color:#8b949e;margin:5px 0 0 0;font-size:13px;">{desc}</p></div>'
            html += '</div>'
        
        # Other languages - also detailed
        lang_colors = {'typescript':'#3178c6','python':'#3572A5','go':'#00ADD8','rust':'#dea584','javascript':'#f1e05a'}
        for lang in sorted([k for k in gh.keys() if k and k.lower() not in ['all', '']])[:3]:
            repos = gh[lang][:10]
            color = lang_colors.get(lang.lower(),'#6e7681')
            html += f'<div style="background:#1a1a2e;padding:15px;border-radius:8px;margin-bottom:10px;border-top:3px solid {color};" id="lang-{uid()}">'
            html += f'<h3 style="color:{color};margin:0 0 10px 0;">📦 {lang.capitalize()}</h3>'
            for i, r in enumerate(repos):
                desc = (r.get("description","") or "")[:60]
                html += f'<div style="padding:10px;margin:5px 0;background:#{"252540" if i%2==0 else "1e1e35"};border-radius:4px;">'
                html += f'<a href="https://github.com{r["link"]}" style="color:#e0e0e0;text-decoration:none;font-weight:bold;">{r["title"]}</a>'
                html += f'<span style="color:{color};float:right;">⭐{r["stars"]} | +{r["todayStars"]}</span>'
                if desc:
                    html += f'<p style="color:#888;margin:5px 0 0 0;font-size:12px;">{desc}</p>'
                html += '</div>'
            html += '</div>'

    # HuggingFace - orange theme
    models = data.get('huggingFaceModels', [])
    if models:
        html += f'<div style="background:#fff3e0;padding:20px;border-radius:8px;margin:20px 0;border-left:5px solid #ff9800;" id="hf-{uid()}">'
        html += '<h2 style="color:#e65100;margin:0 0 15px 0;">🤖 HuggingFace Hot Models</h2>'
        html += '<table style="width:100%;border-collapse:collapse;">'
        html += '<tr style="background:#ffe0b2;"><th style="padding:10px;text-align:left;">Model</th><th style="padding:10px;">Downloads</th><th style="padding:10px;">Likes</th></tr>'
        for i, m in enumerate(models[:10]):
            bg = '#fff8e1' if i%2==0 else '#fff3e0'
            html += f'<tr style="background:{bg};"><td style="padding:8px;"><a href="{m["link"]}" style="color:#e65100;">{m["modelId"]}</a></td><td style="padding:8px;text-align:center;">{m.get("downloads",0):,}</td><td style="padding:8px;text-align:center;">❤️{m.get("likes",0)}</td></tr>'
        html += '</table></div>'

    # Hacker News - distinct orange cards
    stories = data.get('hackerNewsStories', [])
    if stories:
        html += f'<div style="background:#fff5f0;padding:20px;border-radius:8px;margin:20px 0;" id="hn-{uid()}">'
        html += '<h2 style="color:#ff6600;margin:0 0 15px 0;border-bottom:2px solid #ff6600;padding-bottom:10px;">📰 Hacker News Top Stories</h2>'
        for i, s in enumerate(stories[:10]):
            html += f'<article style="padding:10px;margin:8px 0;background:#{"fffaf5" if i%2==0 else "fff0e5"};border-radius:4px;">'
            html += f'<a href="{s["link"]}" style="color:#ff6600;font-size:15px;text-decoration:none;font-weight:500;">{s["title"]}</a>'
            html += f'<footer style="color:#828282;font-size:12px;margin-top:5px;">▲{s["score"]} pts by {s["by"]} | {s.get("descendants",0)} comments</footer></article>'
        html += '</div>'

    # Dev.to - purple theme
    articles = data.get('devToArticles', [])
    if articles:
        html += f'<div style="background:#f3e5f5;padding:20px;border-radius:8px;margin:20px 0;" id="dev-{uid()}">'
        html += '<h2 style="color:#7b1fa2;margin:0 0 15px 0;">📝 Dev.to Popular Articles</h2>'
        html += '<ul style="list-style:none;padding:0;margin:0;">'
        for a in articles[:10]:
            html += f'<li style="padding:10px;border-bottom:1px dashed #ce93d8;"><a href="{a["url"]}" style="color:#7b1fa2;text-decoration:none;">{a["title"]}</a> <small style="color:#9c27b0;">by {a["user"]["name"]} • ❤️{a.get("publicReactionsCount",0)}</small></li>'
        html += '</ul></div>'

    # AI Papers - deep purple
    papers = data.get('aiPapers', [])
    if papers:
        html += f'<div style="background:#ede7f6;padding:20px;border-radius:8px;margin:20px 0;" id="paper-{uid()}">'
        html += '<h2 style="color:#512da8;margin:0 0 15px 0;">📄 Latest AI Research Papers</h2>'
        html += '<ol style="padding-left:20px;margin:0;">'
        for p in papers[:10]:
            authors = ", ".join(p.get("authors",[])[:2])
            html += f'<li style="padding:8px 0;color:#5e35b1;"><a href="{p["url"]}" style="color:#512da8;text-decoration:none;">{p["title"]}</a><br/><small style="color:#7e57c2;">{authors} • ❤️{p.get("likes",0)}</small></li>'
        html += '</ol></div>'

    # Indie Revenue - green theme with detailed cards including links and descriptions
    revenues = data.get('indieRevenue', [])
    if revenues:
        html += f'<div style="background:#e8f5e9;padding:20px;border-radius:8px;margin:20px 0;" id="indie-{uid()}">'
        html += '<h2 style="color:#2e7d32;margin:0 0 15px 0;">💰 Indie Hackers Revenue Report</h2>'
        for i, r in enumerate(revenues[:10]):
            url = r.get("url", "")
            desc = r.get("description", "")[:80]
            founders = ", ".join(r.get("founders", [])[:2]) if r.get("founders") else ""
            bg = '#f1f8e9' if i%2==0 else '#e8f5e9'
            html += f'<div style="background:{bg};padding:15px;margin:8px 0;border-radius:6px;border-left:4px solid #4caf50;">'
            html += f'<div style="display:flex;justify-content:space-between;align-items:center;">'
            html += f'<span style="background:#4caf50;color:#fff;padding:2px 8px;border-radius:10px;font-size:12px;">#{r.get("rank","-")}</span>'
            html += f'<span style="color:#2e7d32;font-weight:bold;font-size:16px;">${r.get("mrr",0):,.0f}/mo</span>'
            html += '</div>'
            if url:
                html += f'<h3 style="margin:10px 0 5px 0;"><a href="{url}" style="color:#1b5e20;text-decoration:none;">{r["name"]} ↗</a></h3>'
            else:
                html += f'<h3 style="margin:10px 0 5px 0;color:#1b5e20;">{r["name"]}</h3>'
            if desc:
                html += f'<p style="color:#558b2f;margin:5px 0;font-size:13px;">{desc}</p>'
            html += f'<div style="display:flex;justify-content:space-between;margin-top:8px;font-size:12px;color:#689f38;">'
            html += f'<span>ARR: ${r.get("arr",0):,.0f}</span>'
            if founders:
                html += f'<span>👤 {founders}</span>'
            html += '</div></div>'
        html += '</div>'

    html += f'<p style="text-align:center;color:#999;font-size:12px;margin-top:30px;">Generated by Tech Trending Daily 🚀 [{uid()}]</p>'
    html += '</body></html>'
    return html

if __name__ == '__main__':
    username = sys.argv[1]
    password = sys.argv[2]
    recipient = sys.argv[3]
    subject = sys.argv[4]
    data_base64 = sys.argv[5]
    
    decoded_bytes = base64.urlsafe_b64decode(data_base64)
    data = json.loads(decoded_bytes.decode('utf-8'))
    content = format_email(data)
    
    # Print size for debugging
    print(f"Email HTML size: {len(content)} bytes ({len(content)/1024:.1f} KB)")
    
    send_email(username, password, recipient, subject, content)
