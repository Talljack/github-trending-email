# Tech Trending Daily 📈

> Formerly known as `github-trending-email`

A powerful GitHub Action that aggregates trending tech content from multiple platforms and delivers it to your inbox daily. Stay updated with:

- 🔥 **GitHub Trending** - Hot repositories across languages
- 🤖 **HuggingFace Models** - Trending AI/ML models
- 📰 **Hacker News** - Top tech stories and discussions
- 🚀 **Product Hunt** - Latest product launches
- 📄 **AI Papers** - Latest AI research papers from HuggingFace Daily Papers
- 💰 **Indie Hackers** - Revenue reports and MRR insights

## Features

- **Multi-platform aggregation** - Get insights from 6+ tech platforms in one place
- **Configurable** - Enable/disable specific platforms based on your interests
- **Language filtering** - Filter GitHub trending by programming language
- **Flexible scheduling** - Set up daily, weekly, or custom schedules
- **Easy integration** - Works seamlessly with email services like Gmail

## Quick Start

```yml
name: Send Tech Trending Daily via Gmail

on:
  schedule:
    # Every day at UTC 11:00 (7:00 PM in UTC+8)
    - cron: '0 11 * * *'
  workflow_dispatch: # Allow manual trigger

jobs:
  send-email:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Get Trending Data
        uses: talljack/github-trending-email@main
        id: trending
        env:
          token: ${{ secrets.GITHUB_TOKEN }}
        with:
          languages: '["", "typescript", "rust", "go", "python"]'
          enableHuggingFace: 'true'
          enableHackerNews: 'true'
          enableProductHunt: 'true'
          enableAIPapers: 'true'
          enableIndieHackers: 'true'
          itemLimit: '10'

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.x'

      - name: Install dependencies
        run: pip install yagmail

      - name: Send email
        run: |
          python ./.github/actions/send_email.py \
            "${{ secrets.GMAIL_USERNAME }}" \
            "${{ secrets.GMAIL_PASSWORD }}" \
            "your-email@example.com" \
            "Tech Trending Daily" \
            ${{ steps.trending.outputs.trendingData }}
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `token` | Your `GITHUB_TOKEN` | No | `${{ github.token }}` |
| `sendTime` | The time the email was sent | No | `19:00` |
| `languages` | GitHub trending languages (JSON array) | No | `[]` |
| `dateRange` | GitHub trending time range (`daily`, `weekly`, `monthly`) | No | `daily` |
| `enableHuggingFace` | Enable HuggingFace models | No | `true` |
| `enableHackerNews` | Enable Hacker News stories | No | `true` |
| `enableProductHunt` | Enable Product Hunt products | No | `true` |
| `enableAIPapers` | Enable AI research papers | No | `true` |
| `enableIndieHackers` | Enable Indie Hackers reports | No | `true` |
| `itemLimit` | Number of items per category | No | `10` |

## Outputs

All outputs are **base64 encoded JSON strings**. Decode them before use.

| Output | Description |
|--------|-------------|
| `githubTrendingRepos` | GitHub trending repos (backward compatible) |
| `trendingData` | **All data combined** - recommended for new integrations |
| `huggingFaceModels` | HuggingFace trending models |
| `hackerNewsStories` | Hacker News top stories |
| `productHuntProducts` | Product Hunt products |
| `aiPapers` | AI research papers |
| `indieHackerReports` | Indie Hackers revenue reports |

### Output Data Structure

The `trendingData` output contains all aggregated data:

```typescript
interface TrendingOutput {
  githubTrending: {
    [language: string]: {
      title: string
      link: string
      description: string
      language: string
      stars: string
      todayStars: string
    }[]
  }
  huggingFaceModels?: {
    id: string
    author: string
    modelId: string
    downloads: number
    likes: number
    tags: string[]
    pipeline_tag?: string
    lastModified: string
    link: string
  }[]
  hackerNewsStories?: {
    id: number
    title: string
    url?: string
    score: number
    by: string
    time: number
    descendants: number
    link: string
  }[]
  productHuntProducts?: {
    name: string
    tagline: string
    url: string
    votesCount: number
    commentsCount: number
    topics: string[]
  }[]
  aiPapers?: {
    title: string
    authors: string[]
    abstract: string
    url: string
    publishedDate: string
    likes?: number
  }[]
  indieHackerReports?: {
    productName: string
    mrr: number
    url: string
    description?: string
    category?: string
  }[]
}
```

## Example: Python Email Script

Create `.github/actions/send_email.py`:

```python
import sys
import json
import base64
import yagmail

def format_trending_email(data):
    html = "<h1>🔥 Tech Trending Daily</h1>"
    
    # GitHub Trending
    if 'githubTrending' in data:
        html += "<h2>📦 GitHub Trending</h2>"
        for lang, repos in data['githubTrending'].items():
            html += f"<h3>{lang.upper() if lang else 'All Languages'}</h3><ul>"
            for repo in repos[:5]:
                html += f'''<li>
                    <a href="https://github.com{repo['link']}">{repo['title']}</a>
                    ⭐ {repo['stars']} | {repo['todayStars']}
                    <br><small>{repo['description'][:100]}...</small>
                </li>'''
            html += "</ul>"
    
    # HuggingFace Models
    if data.get('huggingFaceModels'):
        html += "<h2>🤖 HuggingFace Trending Models</h2><ul>"
        for model in data['huggingFaceModels'][:5]:
            html += f'''<li>
                <a href="{model['link']}">{model['modelId']}</a>
                📥 {model['downloads']:,} | ❤️ {model['likes']}
            </li>'''
        html += "</ul>"
    
    # Hacker News
    if data.get('hackerNewsStories'):
        html += "<h2>📰 Hacker News Top Stories</h2><ul>"
        for story in data['hackerNewsStories'][:5]:
            html += f'''<li>
                <a href="{story['link']}">{story['title']}</a>
                🔺 {story['score']} points | 💬 {story['descendants']} comments
            </li>'''
        html += "</ul>"
    
    # AI Papers
    if data.get('aiPapers'):
        html += "<h2>📄 Latest AI Papers</h2><ul>"
        for paper in data['aiPapers'][:5]:
            authors = ', '.join(paper['authors'][:3])
            html += f'''<li>
                <a href="{paper['url']}">{paper['title']}</a>
                <br><small>👤 {authors}</small>
            </li>'''
        html += "</ul>"
    
    # Indie Hackers
    if data.get('indieHackerReports'):
        html += "<h2>💰 Indie Hackers Revenue</h2><ul>"
        for report in data['indieHackerReports'][:5]:
            html += f'''<li>
                <a href="{report['url']}">{report['productName']}</a>
                💵 ${report['mrr']:,.0f}/mo
            </li>'''
        html += "</ul>"
    
    return html

def main():
    username = sys.argv[1]
    password = sys.argv[2]
    to_email = sys.argv[3]
    subject = sys.argv[4]
    data_base64 = sys.argv[5]
    
    # Decode base64 data
    data = json.loads(base64.b64decode(data_base64).decode('utf-8'))
    
    # Format email content
    html_content = format_trending_email(data)
    
    # Send email
    yag = yagmail.SMTP(username, password)
    yag.send(to_email, subject, html_content)
    print("Email sent successfully!")

if __name__ == "__main__":
    main()
```

## Minimal Configuration (GitHub Trending Only)

If you only want GitHub trending repos (original behavior):

```yml
- name: Get GitHub Trending
  uses: talljack/github-trending-email@main
  id: trending
  with:
    languages: '["typescript", "rust"]'
    enableHuggingFace: 'false'
    enableHackerNews: 'false'
    enableProductHunt: 'false'
    enableAIPapers: 'false'
    enableIndieHackers: 'false'
```

## AI-Focused Configuration

For AI/ML developers:

```yml
- name: Get AI Trending
  uses: talljack/github-trending-email@main
  id: trending
  with:
    languages: '["python"]'
    enableHuggingFace: 'true'
    enableHackerNews: 'true'
    enableProductHunt: 'false'
    enableAIPapers: 'true'
    enableIndieHackers: 'false'
    itemLimit: '15'
```

## Indie Hacker Configuration

For indie developers and entrepreneurs:

```yml
- name: Get Indie Trending
  uses: talljack/github-trending-email@main
  id: trending
  with:
    languages: '["typescript", "python"]'
    enableHuggingFace: 'false'
    enableHackerNews: 'true'
    enableProductHunt: 'true'
    enableAIPapers: 'false'
    enableIndieHackers: 'true'
    itemLimit: '20'
```

## Data Sources

| Platform | API | Update Frequency |
|----------|-----|------------------|
| GitHub Trending | Web scraping | Real-time |
| HuggingFace | Official API | Real-time |
| Hacker News | Firebase API | Real-time |
| Product Hunt | Web scraping | Daily |
| AI Papers | HuggingFace Daily Papers | Daily |
| Indie Hackers | Web scraping | Varies |

## Migration from v0.0.x

If you're upgrading from the original `github-trending-email`:

1. The `githubTrendingRepos` output is still available for backward compatibility
2. New features are disabled by default if you don't specify the `enable*` inputs
3. Consider using `trendingData` output for access to all data

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

Licensed under the [MIT License](LICENSE).

---

Made with ❤️ by [Talljack](https://github.com/Talljack)
