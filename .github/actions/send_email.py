# send_email.py
import yagmail
import base64
import sys
import json

def send_email(username, password, recipient, subject, body):
    print("Sending email...")
    yag = yagmail.SMTP(username, password)
    yag.send(to=recipient, subject=subject, contents=body, prettify_html=False)
    print('Email sent successfully')

def format_github_repos_table(language: str, repos):
    """Format GitHub trending repos as HTML table"""
    if not repos:
        return ""
    
    lang_display = language.capitalize() if language and language != 'All' else 'All Languages'
    icon = '🌟' if lang_display == 'All Languages' else '📦'
    
    rows = []
    for repo in repos[:10]:
        desc = repo.get('description', '') or ''
        desc_display = (desc[:100] + '...') if len(desc) > 100 else desc
        lang = repo.get('language', '') or ''
        rows.append(f'<tr><td style="border:1px solid #e1e4e8;padding:10px;"><a href="https://github.com{repo["link"]}" style="color:#0366d6;text-decoration:none;font-weight:600;">{repo["title"]}</a><br/><span style="color:#6a737d;font-size:12px;">{lang}</span></td><td style="border:1px solid #e1e4e8;padding:10px;color:#586069;font-size:13px;">{desc_display}</td><td style="border:1px solid #e1e4e8;padding:10px;text-align:center;color:#28a745;font-weight:600;">⭐{repo["stars"]}</td><td style="border:1px solid #e1e4e8;padding:10px;text-align:center;color:#f9826c;font-size:13px;">{repo["todayStars"]}</td></tr>')
    
    html = f'<h3 style="color:#24292e;border-bottom:1px solid #e1e4e8;padding-bottom:8px;">{icon} {lang_display} Repos</h3>'
    html += '<table style="width:100%;border-collapse:collapse;margin-bottom:20px;">'
    html += '<tr style="background-color:#f6f8fa;"><th style="border:1px solid #e1e4e8;padding:10px;text-align:left;">Repository</th><th style="border:1px solid #e1e4e8;padding:10px;text-align:left;">Description</th><th style="border:1px solid #e1e4e8;padding:10px;text-align:center;">Stars</th><th style="border:1px solid #e1e4e8;padding:10px;text-align:center;">Today</th></tr>'
    html += ''.join(rows)
    html += '</table>'
    return html

def format_huggingface_models(models):
    """Format HuggingFace models as HTML"""
    if not models:
        return ""
    
    rows = []
    for model in models[:10]:
        downloads = model.get('downloads', 0)
        downloads_str = f"{downloads:,}" if downloads < 1000000 else f"{downloads/1000000:.1f}M"
        author = model.get('author', 'unknown')
        likes = model.get('likes', 0)
        pipeline = model.get('pipeline_tag', 'N/A')
        rows.append(f'<tr><td style="border:1px solid #ffd700;padding:10px;"><a href="{model["link"]}" style="color:#ff9d00;text-decoration:none;font-weight:600;">{model["modelId"]}</a><br/><span style="color:#6a737d;font-size:12px;">by {author}</span></td><td style="border:1px solid #ffd700;padding:10px;text-align:center;color:#28a745;">📥 {downloads_str}</td><td style="border:1px solid #ffd700;padding:10px;text-align:center;color:#e91e63;">❤️ {likes:,}</td><td style="border:1px solid #ffd700;padding:10px;color:#6a737d;font-size:13px;">{pipeline}</td></tr>')
    
    html = '<h2 style="color:#ff9d00;margin-top:30px;">🤖 HuggingFace Trending Models</h2>'
    html += '<p style="color:#666;font-size:13px;margin-bottom:15px;">热门 AI/ML 模型，可直接用于推理或微调</p>'
    html += '<table style="width:100%;border-collapse:collapse;margin-bottom:20px;">'
    html += '<tr style="background-color:#fff8e6;"><th style="border:1px solid #ffd700;padding:10px;text-align:left;">Model</th><th style="border:1px solid #ffd700;padding:10px;text-align:center;">Downloads</th><th style="border:1px solid #ffd700;padding:10px;text-align:center;">Likes</th><th style="border:1px solid #ffd700;padding:10px;text-align:left;">Type</th></tr>'
    html += ''.join(rows)
    html += '</table>'
    return html

def generate_chinese_summary(title, description=""):
    """Generate a simple Chinese summary based on keywords"""
    keywords = {
        'ai': 'AI人工智能', 'machine learning': '机器学习', 'deep learning': '深度学习',
        'llm': '大语言模型', 'gpt': 'GPT模型', 'neural': '神经网络',
        'transformer': 'Transformer', 'python': 'Python', 'javascript': 'JavaScript',
        'typescript': 'TypeScript', 'rust': 'Rust', 'go': 'Go',
        'web': 'Web开发', 'api': 'API', 'database': '数据库',
        'cloud': '云计算', 'docker': 'Docker', 'kubernetes': 'K8s',
        'security': '安全', 'performance': '性能', 'open source': '开源',
        'framework': '框架', 'agent': 'AI Agent', 'rag': 'RAG',
        'vector': '向量', 'embedding': '嵌入', 'inference': '推理',
        'training': '训练', 'nlp': 'NLP', 'cv': '计算机视觉',
    }
    
    text = (title + " " + description).lower()
    found = []
    for key, chinese in keywords.items():
        if key in text and chinese not in found:
            found.append(chinese)
            if len(found) >= 3:
                break
    return "相关: " + "、".join(found) if found else ""

def format_hackernews_stories(stories):
    """Format Hacker News stories as HTML"""
    if not stories:
        return ""
    
    items = []
    for i, story in enumerate(stories[:10], 1):
        summary = generate_chinese_summary(story['title'])
        summary_html = f'<span style="font-size:12px;color:#ff6600;margin-left:8px;">{summary}</span>' if summary else ''
        bg = '#fafafa' if i % 2 == 0 else '#fff'
        items.append(f'<div style="padding:10px;border-bottom:1px solid #e1e4e8;background-color:{bg};"><span style="color:#999;margin-right:8px;">{i}.</span><a href="{story["link"]}" style="color:#000;text-decoration:none;font-weight:500;">{story["title"]}</a>{summary_html}<br/><span style="font-size:12px;color:#828282;">🔺 {story["score"]} points | 👤 {story["by"]} | 💬 {story.get("descendants", 0)} comments</span></div>')
    
    html = '<h2 style="color:#ff6600;margin-top:30px;">📰 Hacker News Top Stories</h2>'
    html += '<p style="color:#666;font-size:13px;margin-bottom:15px;">硅谷技术社区热门讨论</p>'
    html += '<div style="margin-bottom:20px;">' + ''.join(items) + '</div>'
    return html

def format_devto_articles(articles):
    """Format Dev.to articles as HTML"""
    if not articles:
        return ""
    
    items = []
    for article in articles[:10]:
        desc = (article.get('description', '') or '')[:150]
        tags = ' '.join([f'<span style="background:#e8e8e8;padding:2px 6px;border-radius:3px;font-size:11px;margin-right:4px;">#{tag}</span>' for tag in article.get('tags', [])[:3]])
        summary = generate_chinese_summary(article['title'], article.get('description', ''))
        summary_html = f'<div style="font-size:12px;color:#3b49df;margin-top:4px;">{summary}</div>' if summary else ''
        desc_suffix = '...' if len(article.get('description', '') or '') > 150 else ''
        items.append(f'<div style="padding:12px;border:1px solid #e1e4e8;border-radius:8px;margin-bottom:10px;"><a href="{article["url"]}" style="color:#3b49df;text-decoration:none;font-weight:600;font-size:15px;">{article["title"]}</a><div style="font-size:13px;color:#666;margin:6px 0;">{desc}{desc_suffix}</div>{summary_html}<div style="font-size:12px;color:#999;margin-top:6px;">👤 {article["user"]["name"]} | ❤️ {article.get("publicReactionsCount", 0)} | 💬 {article.get("commentsCount", 0)}</div><div style="margin-top:6px;">{tags}</div></div>')
    
    html = '<h2 style="color:#3b49df;margin-top:30px;">📝 Dev.to Trending Articles</h2>'
    html += '<p style="color:#666;font-size:13px;margin-bottom:15px;">开发者社区热门技术文章</p>'
    html += '<div style="margin-bottom:20px;">' + ''.join(items) + '</div>'
    return html

def format_ai_papers(papers):
    """Format AI papers as HTML"""
    if not papers:
        return ""
    
    items = []
    for paper in papers[:10]:
        authors_list = paper.get('authors', [])[:3]
        authors = ', '.join(authors_list) + (' et al.' if len(paper.get('authors', [])) > 3 else '')
        abstract = (paper.get('abstract', '') or '')[:200]
        if len(paper.get('abstract', '') or '') > 200:
            abstract += '...'
        summary = generate_chinese_summary(paper['title'], paper.get('abstract', ''))
        summary_html = f'<div style="font-size:12px;color:#673ab7;margin-top:6px;font-weight:500;">{summary}</div>' if summary else ''
        items.append(f'<div style="padding:12px;border:1px solid #e1e4e8;border-radius:8px;margin-bottom:10px;background:#fafafa;"><a href="{paper["url"]}" style="color:#673ab7;text-decoration:none;font-weight:600;font-size:14px;">{paper["title"]}</a><div style="font-size:12px;color:#666;margin:4px 0;">👤 {authors}</div><div style="font-size:13px;color:#444;line-height:1.4;">{abstract}</div>{summary_html}<div style="font-size:11px;color:#999;margin-top:6px;">❤️ {paper.get("likes", 0)} likes | 📅 {paper.get("publishedDate", "")[:10]}</div></div>')
    
    html = '<h2 style="color:#673ab7;margin-top:30px;">📄 Latest AI Research Papers</h2>'
    html += '<p style="color:#666;font-size:13px;margin-bottom:15px;">最新 AI 研究论文</p>'
    html += '<div style="margin-bottom:20px;">' + ''.join(items) + '</div>'
    return html

def format_indie_revenue(revenues):
    """Format Indie Revenue data as HTML"""
    if not revenues:
        return ""
    
    rows = []
    for revenue in revenues[:10]:
        arr = revenue.get('arr', 0)
        mrr = revenue.get('mrr', 0)
        arr_str = f"${arr:,.0f}" if arr > 0 else "N/A"
        mrr_str = f"${mrr:,.0f}/mo" if mrr > 0 else "N/A"
        verified = "✅" if revenue.get('isVerified') else ""
        desc = (revenue.get('description', '') or '')[:60]
        rows.append(f'<tr><td style="border:1px solid #a7f3d0;padding:10px;text-align:center;color:#6b7280;font-weight:600;">{revenue.get("rank", "-")}</td><td style="border:1px solid #a7f3d0;padding:10px;"><span style="font-weight:600;color:#10b981;">{revenue["name"]} {verified}</span><br/><span style="font-size:12px;color:#6b7280;">{desc}</span></td><td style="border:1px solid #a7f3d0;padding:10px;text-align:right;color:#059669;font-weight:600;">{arr_str}</td><td style="border:1px solid #a7f3d0;padding:10px;text-align:right;color:#10b981;">{mrr_str}</td></tr>')
    
    html = '<h2 style="color:#10b981;margin-top:30px;">💰 Indie Developer Revenue</h2>'
    html += '<p style="color:#666;font-size:13px;margin-bottom:15px;">独立开发者收入排行</p>'
    html += '<table style="width:100%;border-collapse:collapse;margin-bottom:20px;">'
    html += '<tr style="background-color:#ecfdf5;"><th style="border:1px solid #a7f3d0;padding:10px;text-align:center;">#</th><th style="border:1px solid #a7f3d0;padding:10px;text-align:left;">Product</th><th style="border:1px solid #a7f3d0;padding:10px;text-align:right;">ARR</th><th style="border:1px solid #a7f3d0;padding:10px;text-align:right;">MRR</th></tr>'
    html += ''.join(rows)
    html += '</table>'
    return html

def format_full_trending_email(data):
    """Format the complete trending email with all sections"""
    html = '<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>'
    html += '<body style="font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica,Arial,sans-serif;max-width:800px;margin:0 auto;padding:20px;background-color:#f6f8fa;">'
    html += '<div style="background-color:white;border-radius:12px;padding:30px;box-shadow:0 1px 3px rgba(0,0,0,0.1);">'
    html += '<h1 style="text-align:center;color:#24292e;margin-bottom:30px;font-size:28px;">🔥 Tech Trending Daily</h1>'
    
    # GitHub Trending
    if 'githubTrending' in data:
        html += '<h2 style="color:#24292e;margin-top:20px;">📦 GitHub Trending Repositories</h2>'
        github_data = data['githubTrending']
        all_repos = github_data.get('', github_data.get('all', github_data.get('All', [])))
        if all_repos:
            html += format_github_repos_table('All', all_repos)
        other_langs = sorted([k for k in github_data.keys() if k and k.lower() not in ['all', '']])
        for lang in other_langs:
            html += format_github_repos_table(lang, github_data[lang])
    
    if data.get('huggingFaceModels'):
        html += format_huggingface_models(data['huggingFaceModels'])
    
    if data.get('hackerNewsStories'):
        html += format_hackernews_stories(data['hackerNewsStories'])
    
    if data.get('devToArticles'):
        html += format_devto_articles(data['devToArticles'])
    
    if data.get('aiPapers'):
        html += format_ai_papers(data['aiPapers'])
    
    if data.get('indieRevenue'):
        html += format_indie_revenue(data['indieRevenue'])
    
    html += '<div style="text-align:center;margin-top:40px;padding-top:20px;border-top:1px solid #e1e4e8;color:#6a737d;font-size:12px;">'
    html += '<p>Generated by <a href="https://github.com/Talljack/github-trending-email" style="color:#0366d6;">Tech Trending Daily</a></p>'
    html += '<p>Stay curious, keep building! 🚀</p></div></div></body></html>'
    return html

def format_legacy_email(repo_data):
    """Format email in legacy mode (GitHub repos only)"""
    content = ''
    for key, repos in repo_data.items():
        content += format_github_repos_table(key if key else 'All', repos)
    return content

if __name__ == '__main__':
    username = sys.argv[1]
    password = sys.argv[2]
    recipient = sys.argv[3]
    subject = sys.argv[4]
    data_base64 = sys.argv[5]
    
    decoded_bytes = base64.urlsafe_b64decode(data_base64)
    data = json.loads(decoded_bytes.decode('utf-8'))
    
    if 'githubTrending' in data:
        content = format_full_trending_email(data)
    else:
        content = format_legacy_email(data)
    
    send_email(username, password, recipient, subject, content)
