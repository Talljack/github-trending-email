import https from 'https'
import { getInput, setFailed, setOutput } from '@actions/core'
import axios from 'axios'
import { load } from 'cheerio'
import { chromium } from 'playwright-core'

const axiosInstance = axios.create({
  httpsAgent: new https.Agent({ keepAlive: true }),
  timeout: 30000,
})

const dateRangeEnum = ['daily', 'weekly', 'monthly']

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

interface IndieRevenue {
  rank: number
  name: string
  description: string
  arr: number
  mrr: number
  founders: string[]
  isVerified: boolean
}

interface RepoOutput {
  [key: string]: GithubRepoType[]
}

interface TrendingOutput {
  githubTrending: RepoOutput
  huggingFaceModels?: HuggingFaceModel[]
  hackerNewsStories?: HackerNewsStory[]
  devToArticles?: DevToArticle[]
  aiPapers?: AIPaper[]
  indieRevenue?: IndieRevenue[]
}

interface UserOptions {
  sendTime: string
  languages: string[]
  dateRange: string
  enableHuggingFace: boolean
  enableHackerNews: boolean
  enableDevTo: boolean
  enableAIPapers: boolean
  enableIndieRevenue: boolean
  itemLimit: number
}

// ============ User Input Parsing ============

const getUserInputs = (): UserOptions => {
  const sendTime = getInput('sendTime') || '19:00'
  const languagesJson = getInput('languages') || '[]'
  console.log('languagesJson', languagesJson)
  const languages = JSON.parse(languagesJson)
  console.log('languages', languages)
  const dateRange = getInput('dateRange') || 'daily'
  if (!dateRangeEnum.includes(dateRange)) {
    setFailed(
      `Invalid input dateRange: ${dateRange}. Valid options are: ${dateRangeEnum.join(', ')}.`,
    )
  }

  // New options for extended features
  const enableHuggingFace = getInput('enableHuggingFace') !== 'false'
  const enableHackerNews = getInput('enableHackerNews') !== 'false'
  const enableDevTo = getInput('enableDevTo') !== 'false'
  const enableAIPapers = getInput('enableAIPapers') !== 'false'
  const enableIndieRevenue = getInput('enableIndieRevenue') !== 'false'
  const itemLimit = Number.parseInt(getInput('itemLimit') || '10', 10)

  return {
    sendTime,
    languages,
    dateRange,
    enableHuggingFace,
    enableHackerNews,
    enableDevTo,
    enableAIPapers,
    enableIndieRevenue,
    itemLimit,
  }
}

// ============ GitHub Trending ============

const getTrendingReposByLanguage = async (
  language: string = '',
  dateRange: string = 'daily',
): Promise<GithubRepoType[]> => {
  try {
    let url
    if (language)
      url = `https://github.com/trending/${language}?since=${dateRange}`
    else url = `https://github.com/trending?since=${dateRange}`

    const { data } = await axiosInstance.get(url)
    const $ = load(data)
    const repos: GithubRepoType[] = []

    $('.Box-row').each((_index, element) => {
      const title = $(element)
        .find('h2 a')
        .text()
        .replace(/[\n\s]+/g, '')
      const link = $(element).find('h2 a').attr('href') ?? ''
      const description = $(element).find('p').text().trim()
      const language = $(element)
        .find('[itemprop=programmingLanguage]')
        .text()
        .trim()
      const stars = $(element)
        .find('.Link--muted')
        .first()
        .text()
        .replace(/[\n\s]+/g, '')
      const todayStars = $(element).find('.float-sm-right').text().trim()

      repos.push({ title, description, language, stars, todayStars, link })
    })

    return repos
  }
  catch (error) {
    console.error('Error fetching trending repos:', error)
    return []
  }
}

async function getAllRepos(userOptions: UserOptions): Promise<RepoOutput> {
  const result = {} as RepoOutput
  const { languages = [], dateRange } = userOptions
  if (languages.length === 0) {
    const languageReposData = await getTrendingReposByLanguage('', dateRange)
    result.all = languageReposData
  }
  else {
    for (let i = 0; i < languages.length; i++) {
      const language = languages[i]
      const languageReposData = await getTrendingReposByLanguage(
        language,
        dateRange,
      )
      result[language] = languageReposData
    }
  }
  return result
}

// ============ HuggingFace Models ============

async function getHuggingFaceModels(limit: number = 10): Promise<HuggingFaceModel[]> {
  try {
    const { data } = await axiosInstance.get(
      `https://huggingface.co/api/models?sort=downloads&direction=-1&limit=${limit}`,
    )

    return data.map((model: any) => ({
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
  }
  catch (error) {
    console.error('Error fetching HuggingFace models:', error)
    return []
  }
}

// ============ Hacker News Stories ============

async function getHackerNewsStories(limit: number = 10): Promise<HackerNewsStory[]> {
  try {
    // Get top story IDs
    const { data: storyIds } = await axiosInstance.get(
      'https://hacker-news.firebaseio.com/v0/topstories.json',
    )

    const topIds = storyIds.slice(0, limit)

    // Fetch story details in parallel
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

    return stories
  }
  catch (error) {
    console.error('Error fetching Hacker News stories:', error)
    return []
  }
}

// ============ Dev.to Articles ============

async function getDevToArticles(limit: number = 10): Promise<DevToArticle[]> {
  try {
    // Dev.to has a public API
    const { data } = await axiosInstance.get(
      `https://dev.to/api/articles?per_page=${limit}&top=1`,
    )

    return data.map((article: any) => ({
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
  }
  catch (error) {
    console.error('Error fetching Dev.to articles:', error)
    return []
  }
}

// ============ AI Papers (HuggingFace Daily Papers) ============

async function getAIPapers(limit: number = 10): Promise<AIPaper[]> {
  try {
    // Use HuggingFace Daily Papers API
    const { data } = await axiosInstance.get(
      `https://huggingface.co/api/daily_papers?limit=${limit}`,
    )

    return data.map((paper: any) => ({
      title: paper.paper?.title || paper.title || 'Unknown Title',
      authors: paper.paper?.authors?.map((a: any) => a.name || a) || [],
      abstract: paper.paper?.summary || paper.paper?.abstract || '',
      url: paper.paper?.id
        ? `https://huggingface.co/papers/${paper.paper.id}`
        : `https://arxiv.org/abs/${paper.paper?.arxivId || ''}`,
      publishedDate: paper.publishedAt || paper.paper?.publishedAt || '',
      likes: paper.paper?.upvotes || 0,
    }))
  }
  catch (error) {
    console.error('Error fetching AI papers:', error)
    return []
  }
}

// ============ Indie Revenue (TrustMRR) - Using Playwright ============

async function getIndieRevenue(limit: number = 10): Promise<IndieRevenue[]> {
  let browser = null
  try {
    console.log('Launching browser for TrustMRR...')

    // Try to connect to browserless or launch local browser
    const browserWSEndpoint = process.env.BROWSERLESS_WS_ENDPOINT
    if (browserWSEndpoint) {
      browser = await chromium.connect(browserWSEndpoint)
    }
    else {
      // For GitHub Actions, use the installed chromium
      browser = await chromium.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox'],
      })
    }

    const page = await browser.newPage()

    // Set a realistic user agent
    await page.setExtraHTTPHeaders({
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    })

    console.log('Navigating to TrustMRR...')
    await page.goto('https://trustmrr.com', {
      waitUntil: 'networkidle',
      timeout: 60000,
    })

    // Wait for the content to load
    await page.waitForTimeout(3000)

    // Extract data from the page
    const revenues = await page.evaluate((limit: number) => {
      const results: any[] = []

      // Try to find revenue cards/rows
      const cards = document.querySelectorAll('[class*="card"], [class*="row"], [class*="item"], tr, article')

      cards.forEach((card, index) => {
        if (results.length >= limit)
          return

        const text = card.textContent || ''

        // Look for ARR/MRR patterns
        const arrMatch = text.match(/\$?([\d,]+(?:\.\d+)?)\s*(?:k|K|M)?\s*(?:ARR|\/yr|\/year)/i)
        const mrrMatch = text.match(/\$?([\d,]+(?:\.\d+)?)\s*(?:k|K|M)?\s*(?:MRR|\/mo|\/month)/i)

        if (arrMatch || mrrMatch) {
          // Try to extract name
          const nameEl = card.querySelector('h1, h2, h3, h4, [class*="name"], [class*="title"]')
          const name = nameEl?.textContent?.trim() || `Company ${index + 1}`

          // Try to extract description
          const descEl = card.querySelector('p, [class*="desc"]')
          const description = descEl?.textContent?.trim() || ''

          let arr = 0
          let mrr = 0

          if (arrMatch) {
            let value = Number.parseFloat(arrMatch[1].replace(/,/g, ''))
            if (text.toLowerCase().includes('k'))
              value *= 1000
            if (text.toLowerCase().includes('m'))
              value *= 1000000
            arr = value
          }

          if (mrrMatch) {
            let value = Number.parseFloat(mrrMatch[1].replace(/,/g, ''))
            if (text.toLowerCase().includes('k'))
              value *= 1000
            if (text.toLowerCase().includes('m'))
              value *= 1000000
            mrr = value
          }

          if (arr > 0 || mrr > 0) {
            results.push({
              rank: results.length + 1,
              name,
              description: description.slice(0, 200),
              arr,
              mrr: mrr || arr / 12,
              founders: [],
              isVerified: text.toLowerCase().includes('verified'),
            })
          }
        }
      })

      return results
    }, limit)

    await browser.close()
    console.log(`Found ${revenues.length} indie revenue entries`)
    return revenues
  }
  catch (error) {
    console.error('Error fetching TrustMRR data:', error)
    if (browser)
      await browser.close()
    return []
  }
}

// ============ Main Function ============

async function main(): Promise<TrendingOutput> {
  const userOptions = getUserInputs()
  console.log('userOptions', userOptions)

  const result: TrendingOutput = {
    githubTrending: {},
  }

  // Fetch GitHub Trending (always enabled)
  console.log('Fetching GitHub Trending repos...')
  result.githubTrending = await getAllRepos(userOptions)

  // Fetch additional data based on user options
  const fetchPromises: Promise<void>[] = []

  if (userOptions.enableHuggingFace) {
    console.log('Fetching HuggingFace models...')
    fetchPromises.push(
      getHuggingFaceModels(userOptions.itemLimit).then((models) => {
        result.huggingFaceModels = models
      }),
    )
  }

  if (userOptions.enableHackerNews) {
    console.log('Fetching Hacker News stories...')
    fetchPromises.push(
      getHackerNewsStories(userOptions.itemLimit).then((stories) => {
        result.hackerNewsStories = stories
      }),
    )
  }

  if (userOptions.enableDevTo) {
    console.log('Fetching Dev.to articles...')
    fetchPromises.push(
      getDevToArticles(userOptions.itemLimit).then((articles) => {
        result.devToArticles = articles
      }),
    )
  }

  if (userOptions.enableAIPapers) {
    console.log('Fetching AI papers...')
    fetchPromises.push(
      getAIPapers(userOptions.itemLimit).then((papers) => {
        result.aiPapers = papers
      }),
    )
  }

  // Wait for all API-based fetches to complete first
  await Promise.all(fetchPromises)

  // Fetch Playwright-based data separately (slower)
  if (userOptions.enableIndieRevenue) {
    console.log('Fetching Indie Revenue data (using Playwright)...')
    result.indieRevenue = await getIndieRevenue(userOptions.itemLimit)
  }

  // Output results
  setOutput(
    'githubTrendingRepos',
    Buffer.from(JSON.stringify(result.githubTrending), 'utf-8').toString('base64'),
  )

  setOutput(
    'trendingData',
    Buffer.from(JSON.stringify(result), 'utf-8').toString('base64'),
  )

  // Individual outputs for convenience
  if (result.huggingFaceModels) {
    setOutput(
      'huggingFaceModels',
      Buffer.from(JSON.stringify(result.huggingFaceModels), 'utf-8').toString('base64'),
    )
  }

  if (result.hackerNewsStories) {
    setOutput(
      'hackerNewsStories',
      Buffer.from(JSON.stringify(result.hackerNewsStories), 'utf-8').toString('base64'),
    )
  }

  if (result.devToArticles) {
    setOutput(
      'devToArticles',
      Buffer.from(JSON.stringify(result.devToArticles), 'utf-8').toString('base64'),
    )
  }

  if (result.aiPapers) {
    setOutput(
      'aiPapers',
      Buffer.from(JSON.stringify(result.aiPapers), 'utf-8').toString('base64'),
    )
  }

  if (result.indieRevenue) {
    setOutput(
      'indieRevenue',
      Buffer.from(JSON.stringify(result.indieRevenue), 'utf-8').toString('base64'),
    )
  }

  console.log('All trending data fetched successfully!')
  return result
}

try {
  main()
}
catch (error) {
  setFailed(`${(error as unknown as { message: string }).message} -> ${error}`)
}
