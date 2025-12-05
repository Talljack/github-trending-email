/**
 * Local test script for Tech Trending Daily
 * Run with: npx ts-node scripts/test-local.ts
 */

import https from 'https'
import axios from 'axios'
import { load } from 'cheerio'
import * as fs from 'fs'
import * as path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const axiosInstance = axios.create({
  httpsAgent: new https.Agent({ keepAlive: true }),
  timeout: 30000,
})

// ============ Type Definitions ============

interface GithubRepoType {
  title: string
  link: string
  description: string
  language: string
  stars: string
  todayStars: string
}

interface HuggingFaceModel {
  id: string
  author: string
  modelId: string
  downloads: number
  likes: number
  tags: string[]
  pipeline_tag?: string
  lastModified: string
  link: string
}

interface HackerNewsStory {
  id: number
  title: string
  url?: string
  score: number
  by: string
  time: number
  descendants: number
  link: string
}

interface DevToArticle {
  id: number
  title: string
  description: string
  url: string
  commentsCount: number
  publicReactionsCount: number
  publishedAt: string
  user: {
    name: string
    username: string
  }
  tags: string[]
}

interface AIPaper {
  title: string
  authors: string[]
  abstract: string
  url: string
  publishedDate: string
  likes?: number
}

interface RedditPost {
  title: string
  url: string
  score: number
  numComments: number
  author: string
  subreddit: string
  permalink: string
}

interface TrendingOutput {
  githubTrending: { [key: string]: GithubRepoType[] }
  huggingFaceModels?: HuggingFaceModel[]
  hackerNewsStories?: HackerNewsStory[]
  devToArticles?: DevToArticle[]
  aiPapers?: AIPaper[]
  redditPosts?: RedditPost[]
}

// ============ Fetch Functions ============

async function getTrendingReposByLanguage(
  language: string = '',
  dateRange: string = 'daily',
): Promise<GithubRepoType[]> {
  try {
    console.log(`  Fetching GitHub trending for: ${language || 'all languages'}`)
    let url = language
      ? `https://github.com/trending/${language}?since=${dateRange}`
      : `https://github.com/trending?since=${dateRange}`

    const { data } = await axiosInstance.get(url)
    const $ = load(data)
    const repos: GithubRepoType[] = []

    $('.Box-row').each((_index, element) => {
      const title = $(element).find('h2 a').text().replace(/[\n\s]+/g, '')
      const link = $(element).find('h2 a').attr('href') ?? ''
      const description = $(element).find('p').text().trim()
      const language = $(element).find('[itemprop=programmingLanguage]').text().trim()
      const stars = $(element).find('.Link--muted').first().text().replace(/[\n\s]+/g, '')
      const todayStars = $(element).find('.float-sm-right').text().trim()

      repos.push({ title, description, language, stars, todayStars, link })
    })

    console.log(`    Found ${repos.length} repos`)
    return repos
  }
  catch (error) {
    console.error('Error fetching trending repos:', error)
    return []
  }
}

async function getHuggingFaceModels(limit: number = 10): Promise<HuggingFaceModel[]> {
  try {
    console.log('  Fetching HuggingFace models...')
    const { data } = await axiosInstance.get(
      `https://huggingface.co/api/models?sort=downloads&direction=-1&limit=${limit}`,
    )

    const models = data.map((model: any) => ({
      id: model._id,
      author: model.author || model.id.split('/')[0],
      modelId: model.modelId || model.id,
      downloads: model.downloads || 0,
      likes: model.likes || 0,
      tags: model.tags || [],
      pipeline_tag: model.pipeline_tag,
      lastModified: model.lastModified,
      link: `https://huggingface.co/${model.id}`,
    }))

    console.log(`    Found ${models.length} models`)
    return models
  }
  catch (error) {
    console.error('Error fetching HuggingFace models:', error)
    return []
  }
}

async function getHackerNewsStories(limit: number = 10): Promise<HackerNewsStory[]> {
  try {
    console.log('  Fetching Hacker News stories...')
    const { data: storyIds } = await axiosInstance.get(
      'https://hacker-news.firebaseio.com/v0/topstories.json',
    )

    const topIds = storyIds.slice(0, limit)

    const stories = await Promise.all(
      topIds.map(async (id: number) => {
        const { data: story } = await axiosInstance.get(
          `https://hacker-news.firebaseio.com/v0/item/${id}.json`,
        )
        return {
          id: story.id,
          title: story.title,
          url: story.url,
          score: story.score,
          by: story.by,
          time: story.time,
          descendants: story.descendants || 0,
          link: story.url || `https://news.ycombinator.com/item?id=${story.id}`,
        }
      }),
    )

    console.log(`    Found ${stories.length} stories`)
    return stories
  }
  catch (error) {
    console.error('Error fetching Hacker News stories:', error)
    return []
  }
}

async function getDevToArticles(limit: number = 10): Promise<DevToArticle[]> {
  try {
    console.log('  Fetching Dev.to articles...')
    const { data } = await axiosInstance.get(
      `https://dev.to/api/articles?per_page=${limit}&top=1`,
    )

    const articles = data.map((article: any) => ({
      id: article.id,
      title: article.title,
      description: article.description || '',
      url: article.url,
      commentsCount: article.comments_count || 0,
      publicReactionsCount: article.public_reactions_count || 0,
      publishedAt: article.published_at,
      user: {
        name: article.user?.name || '',
        username: article.user?.username || '',
      },
      tags: article.tag_list || [],
    }))

    console.log(`    Found ${articles.length} articles`)
    return articles
  }
  catch (error) {
    console.error('Error fetching Dev.to articles:', error)
    return []
  }
}

async function getAIPapers(limit: number = 10): Promise<AIPaper[]> {
  try {
    console.log('  Fetching AI papers...')
    const { data } = await axiosInstance.get(
      `https://huggingface.co/api/daily_papers?limit=${limit}`,
    )

    const papers = data.map((paper: any) => ({
      title: paper.paper?.title || paper.title || 'Unknown Title',
      authors: paper.paper?.authors?.map((a: any) => a.name || a) || [],
      abstract: paper.paper?.summary || paper.paper?.abstract || '',
      url: paper.paper?.id
        ? `https://huggingface.co/papers/${paper.paper.id}`
        : `https://arxiv.org/abs/${paper.paper?.arxivId || ''}`,
      publishedDate: paper.publishedAt || paper.paper?.publishedAt || '',
      likes: paper.paper?.upvotes || 0,
    }))

    console.log(`    Found ${papers.length} papers`)
    return papers
  }
  catch (error) {
    console.error('Error fetching AI papers:', error)
    return []
  }
}

async function getRedditPosts(limit: number = 10): Promise<RedditPost[]> {
  try {
    console.log('  Fetching Reddit posts...')
    const subreddits = ['programming', 'webdev', 'MachineLearning']
    const allPosts: RedditPost[] = []

    for (const subreddit of subreddits) {
      try {
        const { data } = await axiosInstance.get(
          `https://www.reddit.com/r/${subreddit}/hot.json?limit=${Math.ceil(limit / subreddits.length)}`,
          {
            headers: {
              'User-Agent': 'TechTrendingDaily/1.0',
            },
          },
        )

        const posts = data.data.children.map((child: any) => ({
          title: child.data.title,
          url: child.data.url,
          score: child.data.score,
          numComments: child.data.num_comments,
          author: child.data.author,
          subreddit: child.data.subreddit,
          permalink: `https://reddit.com${child.data.permalink}`,
        }))

        allPosts.push(...posts)
        console.log(`    Found ${posts.length} posts from r/${subreddit}`)
      }
      catch (e) {
        console.error(`    Error fetching r/${subreddit}:`, e)
      }
    }

    // Sort by score and return top items
    const sortedPosts = allPosts
      .sort((a, b) => b.score - a.score)
      .slice(0, limit)

    console.log(`    Total: ${sortedPosts.length} posts`)
    return sortedPosts
  }
  catch (error) {
    console.error('Error fetching Reddit posts:', error)
    return []
  }
}

// ============ Main Test Function ============

async function runTest() {
  console.log('\n🚀 Starting Tech Trending Daily Local Test\n')
  console.log('='.repeat(50))

  const result: TrendingOutput = {
    githubTrending: {},
  }

  // Test GitHub Trending
  console.log('\n📦 Testing GitHub Trending...')
  const languages = ['', 'typescript', 'python']
  for (const lang of languages) {
    const repos = await getTrendingReposByLanguage(lang, 'daily')
    result.githubTrending[lang || 'all'] = repos.slice(0, 5) // Limit for testing
  }

  // Test HuggingFace
  console.log('\n🤖 Testing HuggingFace Models...')
  result.huggingFaceModels = await getHuggingFaceModels(5)

  // Test Hacker News
  console.log('\n📰 Testing Hacker News...')
  result.hackerNewsStories = await getHackerNewsStories(5)

  // Test Dev.to
  console.log('\n📝 Testing Dev.to...')
  result.devToArticles = await getDevToArticles(5)

  // Test AI Papers
  console.log('\n📄 Testing AI Papers...')
  result.aiPapers = await getAIPapers(5)

  // Test Reddit
  console.log('\n🔥 Testing Reddit...')
  result.redditPosts = await getRedditPosts(5)

  console.log('\n' + '='.repeat(50))
  console.log('✅ All data fetched!\n')

  // Save to file
  const outputDir = path.join(__dirname, '../test-output')
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true })
  }

  const outputPath = path.join(outputDir, 'trending-data.json')
  fs.writeFileSync(outputPath, JSON.stringify(result, null, 2))
  console.log(`📁 Data saved to: ${outputPath}`)

  // Generate base64 for email test
  const base64Data = Buffer.from(JSON.stringify(result)).toString('base64')
  const base64Path = path.join(outputDir, 'trending-data-base64.txt')
  fs.writeFileSync(base64Path, base64Data)
  console.log(`📁 Base64 data saved to: ${base64Path}`)

  // Print summary
  console.log('\n📊 Summary:')
  console.log(`  ✅ GitHub repos: ${Object.values(result.githubTrending).flat().length}`)
  console.log(`  ✅ HuggingFace models: ${result.huggingFaceModels?.length || 0}`)
  console.log(`  ✅ Hacker News stories: ${result.hackerNewsStories?.length || 0}`)
  console.log(`  ✅ Dev.to articles: ${result.devToArticles?.length || 0}`)
  console.log(`  ✅ AI papers: ${result.aiPapers?.length || 0}`)
  console.log(`  ✅ Reddit posts: ${result.redditPosts?.length || 0}`)

  console.log('\n📧 To send test email, run:')
  console.log(`  python .github/actions/send_email.py <gmail_username> <gmail_app_password> <recipient_email> "Test Email" $(cat ${base64Path})`)

  return result
}

// Run the test
runTest().catch(console.error)
