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
    
    # Display name for language
    lang_display = language.capitalize() if language and language != 'All' else 'All Languages'
    
    html_content = f"""
    <h3 style="color: #24292e; border-bottom: 1px solid #e1e4e8; padding-bottom: 8px;">
        {'🌟' if lang_display == 'All Languages' else '📦'} {lang_display} Repos
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
    <p style="color: #666; font-size: 13px; margin-bottom: 15px;">热门 AI/ML 模型，可直接用于推理或微调</p>
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

def generate_chinese_summary(title, description=""):
    """Generate a simple Chinese summary based on keywords"""
    # Common tech keywords to Chinese mapping
    keywords = {
        'ai': 'AI人工智能',
        'machine learning': '机器学习',
        'deep learning': '深度学习',
        'llm': '大语言模型',
        'gpt': 'GPT模型',
        'neural': '神经网络',
        'transformer': 'Transformer架构',
        'python': 'Python开发',
        'javascript': 'JavaScript开发',
        'typescript': 'TypeScript开发',
        'rust': 'Rust开发',
        'go': 'Go开发',
        'web': 'Web开发',
        'api': 'API接口',
        'database': '数据库',
        'cloud': '云计算',
        'docker': 'Docker容器',
        'kubernetes': 'K8s容器编排',
        'security': '安全',
        'performance': '性能优化',
        'open source': '开源项目',
        'framework': '开发框架',
        'library': '开发库',
        'tool': '开发工具',
        'startup': '创业',
        'saas': 'SaaS服务',
        'devops': 'DevOps运维',
        'frontend': '前端开发',
        'backend': '后端开发',
        'mobile': '移动开发',
        'react': 'React前端',
        'vue': 'Vue前端',
        'node': 'Node.js',
        'agent': 'AI Agent智能体',
        'rag': 'RAG检索增强',
        'vector': '向量数据库',
        'embedding': '向量嵌入',
        'fine-tuning': '模型微调',
        'inference': '模型推理',
        'training': '模型训练',
        'dataset': '数据集',
        'benchmark': '性能基准',
        'optimization': '优化',
        'automation': '自动化',
        'testing': '测试',
        'debugging': '调试',
        'monitoring': '监控',
        'logging': '日志',
        'caching': '缓存',
        'scaling': '扩展',
        'microservices': '微服务',
        'serverless': '无服务器',
        'edge': '边缘计算',
        'iot': '物联网',
        'blockchain': '区块链',
        'crypto': '加密货币',
        'fintech': '金融科技',
        'healthtech': '医疗科技',
        'edtech': '教育科技',
        'gaming': '游戏开发',
        'graphics': '图形处理',
        'audio': '音频处理',
        'video': '视频处理',
        'image': '图像处理',
        'nlp': '自然语言处理',
        'cv': '计算机视觉',
        'speech': '语音识别',
        'recommendation': '推荐系统',
        'search': '搜索引擎',
        'analytics': '数据分析',
        'visualization': '数据可视化',
    }
    
    text = (title + " " + description).lower()
    found_topics = []
    
    for key, chinese in keywords.items():
        if key in text and chinese not in found_topics:
            found_topics.append(chinese)
            if len(found_topics) >= 3:
                break
    
    if found_topics:
        return "相关: " + "、".join(found_topics)
    return ""

def format_hackernews_stories(stories):
    """Format Hacker News stories as HTML with Chinese summary"""
    if not stories:
        return ""
    
    html = """
    <h2 style="color: #ff6600; margin-top: 30px;">📰 Hacker News Top Stories</h2>
    <p style="color: #666; font-size: 13px; margin-bottom: 15px;">硅谷技术社区热门讨论，了解最新技术趋势</p>
    <div style="margin-bottom: 20px;">
    """
    
    for i, story in enumerate(stories[:10], 1):
        chinese_summary = generate_chinese_summary(story['title'])
        summary_html = f'<div style="font-size: 12px; color: #ff6600; margin-top: 4px;">{chinese_summary}</div>' if chinese_summary else ''
        
        html += f"""
        <div style="padding: 12px; border-bottom: 1px solid #e1e4e8; background-color: {'#fafafa' if i % 2 == 0 else '#fff'};">
            <div style="font-size: 16px; margin-bottom: 4px;">
                <span style="color: #999; margin-right: 8px;">{i}.</span>
                <a href="{story['link']}" style="color: #000; text-decoration: none; font-weight: 500;">
                    {story['title']}
                </a>
            </div>
            {summary_html}
            <div style="font-size: 12px; color: #828282; margin-top: 4px;">
                🔺 {story['score']} points | 👤 {story['by']} | 💬 {story.get('descendants', 0)} comments
                <a href="https://news.ycombinator.com/item?id={story['id']}" style="color: #ff6600; margin-left: 8px;">discuss</a>
            </div>
        </div>
        """
    
    html += "</div>"
    return html

def format_devto_articles(articles):
    """Format Dev.to articles as HTML with Chinese summary"""
    if not articles:
        return ""
    
    html = """
    <h2 style="color: #3b49df; margin-top: 30px;">📝 Dev.to Trending Articles</h2>
    <p style="color: #666; font-size: 13px; margin-bottom: 15px;">开发者社区热门技术文章和教程</p>
    <div style="margin-bottom: 20px;">
    """
    
    for article in articles[:10]:
        tags_html = ' '.join([f'<span style="background-color: #e8e8e8; padding: 2px 6px; border-radius: 3px; font-size: 11px; margin-right: 4px;">#{tag}</span>' for tag in article.get('tags', [])[:3]])
        chinese_summary = generate_chinese_summary(article['title'], article.get('description', ''))
        summary_html = f'<div style="font-size: 12px; color: #3b49df; margin-top: 6px;">{chinese_summary}</div>' if chinese_summary else ''
        
        html += f"""
        <div style="padding: 15px; border: 1px solid #e1e4e8; border-radius: 8px; margin-bottom: 12px;">
            <div style="font-size: 16px; font-weight: 600; margin-bottom: 8px;">
                <a href="{article['url']}" style="color: #3b49df; text-decoration: none;">
                    {article['title']}
                </a>
            </div>
            <div style="font-size: 13px; color: #666; margin-bottom: 8px;">
                {article.get('description', '')[:150]}...
            </div>
            {summary_html}
            <div style="font-size: 12px; color: #999; margin-top: 8px;">
                👤 {article['user']['name']} | ❤️ {article.get('publicReactionsCount', 0)} | 💬 {article.get('commentsCount', 0)}
            </div>
            <div style="margin-top: 6px;">{tags_html}</div>
        </div>
        """
    
    html += "</div>"
    return html

def format_ai_papers(papers):
    """Format AI papers as HTML with Chinese summary"""
    if not papers:
        return ""
    
    html = """
    <h2 style="color: #673ab7; margin-top: 30px;">📄 Latest AI Research Papers</h2>
    <p style="color: #666; font-size: 13px; margin-bottom: 15px;">最新 AI 研究论文，来自 HuggingFace Daily Papers</p>
    <div style="margin-bottom: 20px;">
    """
    
    for paper in papers[:10]:
        authors = ', '.join(paper.get('authors', [])[:3])
        if len(paper.get('authors', [])) > 3:
            authors += ' et al.'
        
        abstract = paper.get('abstract', '')[:200]
        if len(paper.get('abstract', '')) > 200:
            abstract += '...'
        
        chinese_summary = generate_chinese_summary(paper['title'], paper.get('abstract', ''))
        summary_html = f'<div style="font-size: 12px; color: #673ab7; margin-top: 8px; font-weight: 500;">{chinese_summary}</div>' if chinese_summary else ''
        
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
            {summary_html}
            <div style="font-size: 11px; color: #999; margin-top: 8px;">
                ❤️ {paper.get('likes', 0)} likes | 📅 {paper.get('publishedDate', '')[:10]}
            </div>
        </div>
        """
    
    html += "</div>"
    return html

def format_indie_revenue(revenues):
    """Format Indie Revenue data as HTML"""
    if not revenues:
        return ""
    
    html = """
    <h2 style="color: #10b981; margin-top: 30px;">💰 Indie Developer Revenue (TrustMRR)</h2>
    <p style="color: #666; font-size: 13px; margin-bottom: 15px;">独立开发者收入排行，数据来自 TrustMRR 验证</p>
    <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
    <tr style="background-color: #ecfdf5;">
        <th style="border: 1px solid #a7f3d0; padding: 12px; text-align: center;">#</th>
        <th style="border: 1px solid #a7f3d0; padding: 12px; text-align: left;">Product</th>
        <th style="border: 1px solid #a7f3d0; padding: 12px; text-align: right;">ARR</th>
        <th style="border: 1px solid #a7f3d0; padding: 12px; text-align: right;">MRR</th>
    </tr>
    """
    
    for revenue in revenues[:10]:
        arr = revenue.get('arr', 0)
        mrr = revenue.get('mrr', 0)
        
        # Format currency
        arr_str = f"${arr:,.0f}" if arr > 0 else "N/A"
        mrr_str = f"${mrr:,.0f}/mo" if mrr > 0 else "N/A"
        
        verified_badge = "✅" if revenue.get('isVerified') else ""
        
        html += f"""
        <tr>
            <td style="border: 1px solid #a7f3d0; padding: 12px; text-align: center; color: #6b7280; font-weight: 600;">
                {revenue.get('rank', '-')}
            </td>
            <td style="border: 1px solid #a7f3d0; padding: 12px;">
                <div style="font-weight: 600; color: #10b981;">
                    {revenue['name']} {verified_badge}
                </div>
                <div style="font-size: 12px; color: #6b7280; margin-top: 4px;">
                    {revenue.get('description', '')[:80]}{'...' if len(revenue.get('description', '')) > 80 else ''}
                </div>
            </td>
            <td style="border: 1px solid #a7f3d0; padding: 12px; text-align: right; color: #059669; font-weight: 600; font-size: 15px;">
                {arr_str}
            </td>
            <td style="border: 1px solid #a7f3d0; padding: 12px; text-align: right; color: #10b981; font-size: 14px;">
                {mrr_str}
            </td>
        </tr>
        """

    html += """
    </table>
    <div style="font-size: 11px; color: #9ca3af; text-align: right;">
        Data from <a href="https://trustmrr.com" style="color: #10b981;">TrustMRR</a> - Verified Revenue Rankings
    </div>
    """
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
    
    # GitHub Trending - Always first, with All Languages at the top
    if 'githubTrending' in data:
        html += "<h2 style='color: #24292e; margin-top: 20px;'>📦 GitHub Trending Repositories</h2>"
        
        github_data = data['githubTrending']
        
        # First: All Languages (empty string key or 'all' key)
        all_repos = github_data.get('', github_data.get('all', github_data.get('All', [])))
        if all_repos:
            html += format_github_repos_table('All', all_repos)
        
        # Then: Other languages (sorted alphabetically)
        other_langs = sorted([k for k in github_data.keys() if k and k.lower() not in ['all', '']])
        for lang in other_langs:
            html += format_github_repos_table(lang, github_data[lang])
    
    # HuggingFace Models
    if data.get('huggingFaceModels'):
        html += format_huggingface_models(data['huggingFaceModels'])
    
    # Hacker News
    if data.get('hackerNewsStories'):
        html += format_hackernews_stories(data['hackerNewsStories'])
    
    # Dev.to Articles
    if data.get('devToArticles'):
        html += format_devto_articles(data['devToArticles'])
    
    # AI Papers
    if data.get('aiPapers'):
        html += format_ai_papers(data['aiPapers'])
    
    # Indie Revenue
    if data.get('indieRevenue'):
        html += format_indie_revenue(data['indieRevenue'])
    
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
