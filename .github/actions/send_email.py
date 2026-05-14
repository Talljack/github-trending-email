# send_email.py
import base64
import html
import json
import os
from pathlib import Path
import random
import re
import string
import sys

import yagmail

def send_email(username, password, recipient, subject, body):
    print("Sending email...")
    yag = yagmail.SMTP(username, password)
    yag.send(to=recipient, subject=subject, contents=body, prettify_html=False)
    print('Email sent successfully')

def uid():
    """Generate unique id to prevent Gmail pattern detection"""
    return ''.join(random.choices(string.ascii_lowercase, k=4))

def parse_bool(value):
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {'1', 'true', 'yes', 'on'}

def load_remote_jobs_report(report_path):
    if not report_path:
        return {
            'status': 'missing',
            'message': '未提供远程岗位报告路径。',
            'path': '',
        }

    path = Path(report_path)
    if not path.exists():
        return {
            'status': 'missing',
            'message': f'未找到远程岗位报告：{path}',
            'path': str(path),
        }

    content = path.read_text(encoding='utf-8').strip()
    title = path.stem.replace('_', ' ')
    for line in content.splitlines():
        if line.startswith('主题：'):
            title = line.replace('主题：', '', 1).strip()
            break

    return {
        'status': 'ready',
        'title': title,
        'path': str(path),
        'content': content,
    }

def render_remote_jobs_report(report):
    lines = report.get('content', '').splitlines()
    parts = [
        f'<div style="background:#2f2f2f;padding:24px;border-radius:10px;margin:24px 0;color:#f3f4f6;" id="remote-{uid()}">',
        f'<h2 style="color:#f9fafb;margin:0 0 8px 0;font-size:28px;line-height:1.3;">{html.escape(report.get("title", "每日远程岗位推荐"))}</h2>',
        '<p style="color:#d1d5db;margin:0 0 20px 0;font-size:14px;line-height:1.7;">以下内容来自每日远程开发岗位搜索 automation 同步的当日报告。</p>',
    ]

    in_list = False

    def close_list():
        nonlocal in_list
        if in_list:
            parts.append('</ul>')
            in_list = False

    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith('主题：'):
            close_list()
            continue

        if line.startswith('## '):
            close_list()
            parts.append(
                f'<h3 style="color:#f9fafb;margin:28px 0 18px 0;font-size:24px;line-height:1.35;">'
                f'{html.escape(line[3:])}'
                '</h3>',
            )
            continue

        if re.match(r'^\d+\.\s+', line):
            close_list()
            parts.append(
                f'<p style="margin:0 0 12px 0;color:#f3f4f6;font-size:22px;font-weight:800;line-height:1.55;">'
                f'{html.escape(line)}'
                '</p>',
            )
            continue

        if line.startswith('- '):
            if not in_list:
                parts.append(
                    '<ul style="margin:0 0 18px 28px;padding:0;color:#d1d5db;line-height:1.8;font-size:18px;">',
                )
                in_list = True
            bullet_text = html.escape(line[2:].strip())
            bullet_text = re.sub(
                r'(https?://[^\s<]+)',
                r'<a href="\1" style="color:#60a5fa;text-decoration:underline;">\1</a>',
                bullet_text,
            )
            parts.append(f'<li style="margin:0 0 10px 0;">{bullet_text}</li>')
            continue

        close_list()
        parts.append(
            f'<p style="margin:10px 0 16px 0;color:#d1d5db;font-size:18px;line-height:1.8;">'
            f'{html.escape(line)}'
            '</p>',
        )

    close_list()
    parts.append('</div>')
    return ''.join(parts)

def render_remote_jobs_warning(report):
    message = html.escape(report.get('message', '远程岗位报告暂不可用。'))
    path = report.get('path', '')
    path_hint = ''
    if path:
        path_hint = f'<p style="margin:8px 0 0 0;color:#7f1d1d;font-size:12px;">预期路径：{html.escape(path)}</p>'

    return (
        f'<div style="background:#fef2f2;padding:18px;border-radius:8px;margin:20px 0;border-left:5px solid #dc2626;" id="remote-missing-{uid()}">'
        '<h2 style="color:#991b1b;margin:0 0 8px 0;">💼 远程岗位报告未同步</h2>'
        f'<p style="color:#7f1d1d;margin:0;line-height:1.7;">{message}</p>'
        f'{path_hint}'
        '</div>'
    )

def get_github_all_repos(gh):
    candidates = [
        gh.get('all'),
        gh.get('All'),
        gh.get(''),
    ]
    for repos in candidates:
        if isinstance(repos, list):
            return repos

    for key, repos in gh.items():
        if isinstance(repos, list):
            return repos

    return []

def format_email(data, remote_jobs_report=None):
    html = f'''<html><body style="font-family:Arial,sans-serif;max-width:900px;margin:0 auto;padding:20px;background:#fafafa;">
<div style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);padding:30px;border-radius:12px;margin-bottom:20px;">
<h1 style="color:#fff;text-align:center;margin:0;">🔥 Tech Trending Daily</h1>
<p style="color:#e0e0e0;text-align:center;margin:10px 0 0 0;">{uid()}</p>
</div>'''

    # GitHub Trending - All languages with detailed cards
    if 'githubTrending' in data:
        gh = data['githubTrending']
        all_repos = get_github_all_repos(gh)
        
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

    if remote_jobs_report:
        if remote_jobs_report.get('status') == 'ready':
            html += render_remote_jobs_report(remote_jobs_report)
        else:
            html += render_remote_jobs_warning(remote_jobs_report)

    html += f'<p style="text-align:center;color:#999;font-size:12px;margin-top:30px;">Generated by Tech Trending Daily 🚀 [{uid()}]</p>'
    html += '</body></html>'
    return html

if __name__ == '__main__':
    username = sys.argv[1]
    password = sys.argv[2]
    recipient = sys.argv[3]
    subject = sys.argv[4]
    data_base64 = sys.argv[5]
    enable_remote_jobs = parse_bool(sys.argv[6]) if len(sys.argv) > 6 else parse_bool(os.getenv('ENABLE_REMOTE_JOBS'))
    remote_jobs_path = sys.argv[7] if len(sys.argv) > 7 else os.getenv('REMOTE_JOBS_REPORT_PATH', '')
    
    decoded_bytes = base64.urlsafe_b64decode(data_base64)
    data = json.loads(decoded_bytes.decode('utf-8'))
    remote_jobs_report = None
    if enable_remote_jobs:
        remote_jobs_report = load_remote_jobs_report(remote_jobs_path)
        print(f"Remote jobs report status: {remote_jobs_report['status']}")

    content = format_email(data, remote_jobs_report)
    
    # Print size for debugging
    print(f"Email HTML size: {len(content)} bytes ({len(content)/1024:.1f} KB)")
    
    send_email(username, password, recipient, subject, content)
