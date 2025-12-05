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
    
    html_content = f"""
    <h3 style="color: #24292e; border-bottom: 1px solid #e1e4e8; padding-bottom: 8px;">
        📦 {language.capitalize() if language else 'All Languages'} Repos
    </h3>
    <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
    <tr style="background-color: #f6f8fa;">
        <th style="border: 1px solid #e1e4e8; padding: 12px; text-align: left;">Repository</th>
        <th style="border: 1px solid #e1e4e8; padding: 12px; text-align: left;">Description</th>
        <th style="border: 1px solid #e1e4e8; padding: 12px; text-align: center;">Stars</th>
        <th style="border: 1px solid #e1e4e8; padding: 12px; text-align: center;">Today</th>
    </tr>
    """

    for repo in repos[:10]:
        html_content += f"""
        <tr>
            <td style="border: 1px solid #e1e4e8; padding: 12px;">
                <a href="https://github.com{repo['link']}" style="color: #0366d6; text-decoration: none; font-weight: 600;">
                    {repo['title']}
                </a>
                <br><span style="color: #6a737d; font-size: 12px;">{repo.get('language', '')}</span>
            </td>
            <td style="border: 1px solid #e1e4e8; padding: 12px; color: #586069; font-size: 14px;">
                {repo['description'][:150] + '...' if len(repo.get('description', '')) > 150 else repo.get('description', '')}
            </td>
            <td style="border: 1px solid #e1e4e8; padding: 12px; text-align: center; color: #28a745; font-weight: 600;">
                ⭐ {repo['stars']}
            </td>
            <td style="border: 1px solid #e1e4e8; padding: 12px; text-align: center; color: #f9826c; font-size: 13px;">
                {repo['todayStars']}
            </td>
        </tr>
        """

    html_content += "</table>"
    return html_content

def format_huggingface_models(models):
    """Format HuggingFace models as HTML"""
    if not models:
        return ""
    
    html = """
    <h2 style="color: #ff9d00; margin-top: 30px;">🤖 HuggingFace Trending Models</h2>
    <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
    <tr style="background-color: #fff8e6;">
        <th style="border: 1px solid #ffd700; padding: 12px; text-align: left;">Model</th>
        <th style="border: 1px solid #ffd700; padding: 12px; text-align: center;">Downloads</th>
        <th style="border: 1px solid #ffd700; padding: 12px; text-align: center;">Likes</th>
        <th style="border: 1px solid #ffd700; padding: 12px; text-align: left;">Type</th>
    </tr>
    """
    
    for model in models[:10]:
        downloads = model.get('downloads', 0)
        downloads_str = f"{downloads:,}" if downloads < 1000000 else f"{downloads/1000000:.1f}M"
        
        html += f"""
        <tr>
            <td style="border: 1px solid #ffd700; padding: 12px;">
                <a href="{model['link']}" style="color: #ff9d00; text-decoration: none; font-weight: 600;">
                    {model['modelId']}
                </a>
                <br><span style="color: #6a737d; font-size: 12px;">by {model.get('author', 'unknown')}</span>
            </td>
            <td style="border: 1px solid #ffd700; padding: 12px; text-align: center; color: #28a745;">
                📥 {downloads_str}
            </td>
            <td style="border: 1px solid #ffd700; padding: 12px; text-align: center; color: #e91e63;">
                ❤️ {model.get('likes', 0):,}
            </td>
            <td style="border: 1px solid #ffd700; padding: 12px; color: #6a737d; font-size: 13px;">
                {model.get('pipeline_tag', 'N/A')}
            </td>
        </tr>
        """
    
    html += "</table>"
    return html

def format_hackernews_stories(stories):
    """Format Hacker News stories as HTML"""
    if not stories:
        return ""
    
    html = """
    <h2 style="color: #ff6600; margin-top: 30px;">📰 Hacker News Top Stories</h2>
    <div style="margin-bottom: 20px;">
    """
    
    for i, story in enumerate(stories[:10], 1):
        html += f"""
        <div style="padding: 12px; border-bottom: 1px solid #e1e4e8; background-color: {'#fafafa' if i % 2 == 0 else '#fff'};">
            <div style="font-size: 16px; margin-bottom: 4px;">
                <span style="color: #999; margin-right: 8px;">{i}.</span>
                <a href="{story['link']}" style="color: #000; text-decoration: none; font-weight: 500;">
                    {story['title']}
                </a>
            </div>
            <div style="font-size: 12px; color: #828282;">
                🔺 {story['score']} points | 👤 {story['by']} | 💬 {story.get('descendants', 0)} comments
                <a href="https://news.ycombinator.com/item?id={story['id']}" style="color: #ff6600; margin-left: 8px;">discuss</a>
            </div>
        </div>
        """
    
    html += "</div>"
    return html

def format_ai_papers(papers):
    """Format AI papers as HTML"""
    if not papers:
        return ""
    
    html = """
    <h2 style="color: #673ab7; margin-top: 30px;">📄 Latest AI Research Papers</h2>
    <div style="margin-bottom: 20px;">
    """
    
    for paper in papers[:10]:
        authors = ', '.join(paper.get('authors', [])[:3])
        if len(paper.get('authors', [])) > 3:
            authors += ' et al.'
        
        abstract = paper.get('abstract', '')[:200]
        if len(paper.get('abstract', '')) > 200:
            abstract += '...'
        
        html += f"""
        <div style="padding: 15px; border: 1px solid #e1e4e8; border-radius: 8px; margin-bottom: 12px; background-color: #fafafa;">
            <div style="font-size: 15px; font-weight: 600; margin-bottom: 8px;">
                <a href="{paper['url']}" style="color: #673ab7; text-decoration: none;">
                    {paper['title']}
                </a>
            </div>
            <div style="font-size: 12px; color: #666; margin-bottom: 6px;">
                👤 {authors}
            </div>
            <div style="font-size: 13px; color: #444; line-height: 1.5;">
                {abstract}
            </div>
            <div style="font-size: 11px; color: #999; margin-top: 8px;">
                ❤️ {paper.get('likes', 0)} likes | 📅 {paper.get('publishedDate', '')[:10]}
            </div>
        </div>
        """
    
    html += "</div>"
    return html

def format_producthunt_products(products):
    """Format Product Hunt products as HTML"""
    if not products:
        return ""
    
    html = """
    <h2 style="color: #da552f; margin-top: 30px;">🚀 Product Hunt Today</h2>
    <div style="margin-bottom: 20px;">
    """
    
    for product in products[:10]:
        html += f"""
        <div style="padding: 12px; border: 1px solid #e1e4e8; border-radius: 8px; margin-bottom: 10px; display: flex; align-items: center;">
            <div style="flex: 1;">
                <div style="font-size: 15px; font-weight: 600;">
                    <a href="{product['url']}" style="color: #da552f; text-decoration: none;">
                        {product['name']}
                    </a>
                </div>
                <div style="font-size: 13px; color: #666; margin-top: 4px;">
                    {product.get('tagline', '')}
                </div>
            </div>
            <div style="text-align: center; padding: 8px 16px; background-color: #da552f; color: white; border-radius: 4px; font-weight: 600;">
                ▲ {product.get('votesCount', 0)}
            </div>
        </div>
        """
    
    html += "</div>"
    return html

def format_indie_hackers(reports):
    """Format Indie Hackers revenue reports as HTML"""
    if not reports:
        return ""
    
    html = """
    <h2 style="color: #1a73e8; margin-top: 30px;">💰 Indie Hackers Revenue Reports</h2>
    <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
    <tr style="background-color: #e8f0fe;">
        <th style="border: 1px solid #c2d7f5; padding: 12px; text-align: left;">Product</th>
        <th style="border: 1px solid #c2d7f5; padding: 12px; text-align: right;">MRR</th>
        <th style="border: 1px solid #c2d7f5; padding: 12px; text-align: left;">Description</th>
    </tr>
    """
    
    for report in reports[:10]:
        mrr = report.get('mrr', 0)
        mrr_str = f"${mrr:,.0f}/mo" if mrr > 0 else "N/A"
        
        html += f"""
        <tr>
            <td style="border: 1px solid #c2d7f5; padding: 12px;">
                <a href="{report['url']}" style="color: #1a73e8; text-decoration: none; font-weight: 600;">
                    {report['productName']}
                </a>
            </td>
            <td style="border: 1px solid #c2d7f5; padding: 12px; text-align: right; color: #28a745; font-weight: 600; font-size: 15px;">
                {mrr_str}
            </td>
            <td style="border: 1px solid #c2d7f5; padding: 12px; color: #666; font-size: 13px;">
                {report.get('description', '')[:100]}
            </td>
        </tr>
        """
    
    html += "</table>"
    return html

def format_full_trending_email(data):
    """Format the complete trending email with all sections"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f6f8fa;">
        <div style="background-color: white; border-radius: 12px; padding: 30px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <h1 style="text-align: center; color: #24292e; margin-bottom: 30px; font-size: 28px;">
                🔥 Tech Trending Daily
            </h1>
    """
    
    # GitHub Trending
    if 'githubTrending' in data:
        html += "<h2 style='color: #24292e; margin-top: 20px;'>📦 GitHub Trending Repositories</h2>"
        for lang, repos in data['githubTrending'].items():
            html += format_github_repos_table(lang if lang else 'All', repos)
    
    # HuggingFace Models
    if data.get('huggingFaceModels'):
        html += format_huggingface_models(data['huggingFaceModels'])
    
    # Hacker News
    if data.get('hackerNewsStories'):
        html += format_hackernews_stories(data['hackerNewsStories'])
    
    # AI Papers
    if data.get('aiPapers'):
        html += format_ai_papers(data['aiPapers'])
    
    # Product Hunt
    if data.get('productHuntProducts'):
        html += format_producthunt_products(data['productHuntProducts'])
    
    # Indie Hackers
    if data.get('indieHackerReports'):
        html += format_indie_hackers(data['indieHackerReports'])
    
    html += """
            <div style="text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #e1e4e8; color: #6a737d; font-size: 12px;">
                <p>Generated by <a href="https://github.com/Talljack/github-trending-email" style="color: #0366d6;">Tech Trending Daily</a></p>
                <p>Stay curious, keep building! 🚀</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

def format_legacy_email(repo_data):
    """Format email in legacy mode (GitHub repos only) for backward compatibility"""
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
    
    # Decode base64 data
    decoded_bytes = base64.urlsafe_b64decode(data_base64)
    data = json.loads(decoded_bytes.decode('utf-8'))
    
    # Check if this is the new format (with trendingData) or legacy format
    if 'githubTrending' in data:
        # New format with all trending data
        content = format_full_trending_email(data)
    else:
        # Legacy format (GitHub repos only)
        content = format_legacy_email(data)
    
    send_email(username, password, recipient, subject, content)
