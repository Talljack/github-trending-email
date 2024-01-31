# github-trending-email

A Nodejs script to get Github trending repos by language or dateRange.

You can use this action to get Github trending Repos and send it to your email every day. [Example](/.github/workflows/email.yml)

# Usage

```yml
name: Send Github Trending Repos via Gmail

on:
  schedule:
    # 每天 UTC 时间 11:00，如果你在东八区，这相当于晚上 7:00
    - cron: '0 1,12 * * *'

jobs:
  send-email:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v2

      - name: Get Trending repos
        uses: talljack/github-trending-email@main
        id: trending-repos
        env:
          token: ${{secrets.GITHUB_TOKEN}} # 使用存储在仓库 Secrets 中的 GitHub 令牌
        with:
          languages: '["", "typescript", "rust", "go", "swift", "python", "vue"]'

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.x' # Specify the Python version
      - name: Install dependencies
        run: pip install yagmail
        # Maybe you want to send Email
      - name: Send email
        run: |
          python ./.github/actions/send_email.py "${{ secrets.GMAIL_USERNAME }}" "${{ secrets.GMAIL_PASSWORD }}" "yugang.cao12@gmail.com" "Github Trending Repos" ${{ steps.trending-repos.outputs.githubTrendingRepos }}
```

## Inputs

- `token` - Your `GITHUB_TOKEN`. This is required. Why do we need a `token`? Read more here: [About the GITHUB_TOKEN secret](https://help.github.com/en/actions/automating-your-workflow-with-github-actions/authenticating-with-the-github_token#about-the-github_token-secret). Default: `${{ github.token }}`
- `languages` - What languages do you want to query, It's an array, and you can use it to get any language Github trending Repos. Example: `["python", "go", "typescript"]`.
- `dateRange` - What time do you want to query, It has three values `"daily"`、`"weekly"` and `"monthly"`, The default value is `"daily"`, you can choose what time you want to get it.

## Outputs

- `githubTrendingRepos` - The GitHub Trending Repos J**SON String** with \*\*base64 encode, you just need to base64 decode and use it.

## License

Licensed under the [MIT License](LICENSE).
