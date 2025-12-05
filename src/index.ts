import https from 'https'
import { getInput, setFailed, setOutput } from '@actions/core'
import axios from 'axios'
import { load } from 'cheerio'

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

interface ProductHuntProduct {
  name: string
  tagline: string
  url: string
  votesCount: number
  commentsCount: number
  thumbnail?: string
  topics: string[]
}

interface AIPaper {
  title: string
  authors: string[]
  abstract: string
  url: string
  publishedDate: string
  likes?: number
}

interface IndieHackerReport {
  productName: string
  mrr: number
  url: string
  description?: string
  category?: string
}

interface RepoOutput {
  [key: string]: GithubRepoType[]
}

interface TrendingOutput {
  githubTrending: RepoOutput
  huggingFaceModels?: HuggingFaceModel[]
  hackerNewsStories?: HackerNewsStory[]
  productHuntProducts?: ProductHuntProduct[]
  aiPapers?: AIPaper[]
  indieHackerReports?: IndieHackerReport[]
}

interface UserOptions {
  sendTime: string
  languages: string[]
  dateRange: string
  enableHuggingFace: boolean
  enableHackerNews: boolean
  enableProductHunt: boolean
  enableAIPapers: boolean
  enableIndieHackers: boolean
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
  const enableProductHunt = getInput('enableProductHunt') !== 'false'
  const enableAIPapers = getInput('enableAIPapers') !== 'false'
  const enableIndieHackers = getInput('enableIndieHackers') !== 'false'
  const itemLimit = Number.parseInt(getInput('itemLimit') || '10', 10)

  return {
    sendTime,
    languages,
    dateRange,
    enableHuggingFace,
    enableHackerNews,
    enableProductHunt,
    enableAIPapers,
    enableIndieHackers,
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

// ============ Product Hunt Products ============

async function getProductHuntProducts(limit: number = 10): Promise<ProductHuntProduct[]> {
  try {
    // Product Hunt doesn't have a public API, scrape the homepage
    const { data } = await axiosInstance.get('https://www.producthunt.com/', {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      },
    })

    const $ = load(data)
    const products: ProductHuntProduct[] = []

    // Try to extract products from the page
    $('[data-test="post-item"]').each((_index, element) => {
      if (products.length >= limit)
        return false

      const name = $(element).find('[data-test="post-name"]').text().trim()
      const tagline = $(element).find('[data-test="post-tagline"]').text().trim()
      const href = $(element).find('a').first().attr('href')

      if (name) {
        products.push({
          name,
          tagline,
          url: href ? `https://www.producthunt.com${href}` : '',
          votesCount: 0,
          commentsCount: 0,
          topics: [],
        })
      }
    })

    // Fallback: try alternative selectors
    if (products.length === 0) {
      $('article').each((_index, element) => {
        if (products.length >= limit)
          return false

        const name = $(element).find('h3').first().text().trim()
        const tagline = $(element).find('p').first().text().trim()
        const href = $(element).find('a').first().attr('href')

        if (name && name.length > 0) {
          products.push({
            name,
            tagline,
            url: href?.startsWith('http') ? href : `https://www.producthunt.com${href || ''}`,
            votesCount: 0,
            commentsCount: 0,
            topics: [],
          })
        }
      })
    }

    return products
  }
  catch (error) {
    console.error('Error fetching Product Hunt products:', error)
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

// ============ Indie Hackers Revenue Reports ============

async function getIndieHackerReports(limit: number = 10): Promise<IndieHackerReport[]> {
  try {
    // Indie Hackers doesn't have a public API, try to scrape
    const { data } = await axiosInstance.get('https://www.indiehackers.com/products?sorting=highest-revenue', {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      },
    })

    const $ = load(data)
    const reports: IndieHackerReport[] = []

    // Try to extract product cards
    $('.product-card, [class*="product"]').each((_index, element) => {
      if (reports.length >= limit)
        return false

      const productName = $(element).find('h2, h3, [class*="name"]').first().text().trim()
      const mrrText = $(element).find('[class*="revenue"], [class*="mrr"]').text().trim()
      const href = $(element).find('a').first().attr('href')

      // Parse MRR from text like "$10,000/mo" or "$10k MRR"
      const mrrMatch = mrrText.match(/\$?([\d,]+(?:\.\d+)?)\s*k?/i)
      const mrr = mrrMatch ? Number.parseFloat(mrrMatch[1].replace(/,/g, '')) * (mrrText.toLowerCase().includes('k') ? 1000 : 1) : 0

      if (productName) {
        reports.push({
          productName,
          mrr,
          url: href ? `https://www.indiehackers.com${href}` : '',
          description: $(element).find('p, [class*="description"]').first().text().trim(),
        })
      }
    })

    return reports
  }
  catch (error) {
    console.error('Error fetching Indie Hackers reports:', error)
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

  if (userOptions.enableProductHunt) {
    console.log('Fetching Product Hunt products...')
    fetchPromises.push(
      getProductHuntProducts(userOptions.itemLimit).then((products) => {
        result.productHuntProducts = products
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

  if (userOptions.enableIndieHackers) {
    console.log('Fetching Indie Hackers reports...')
    fetchPromises.push(
      getIndieHackerReports(userOptions.itemLimit).then((reports) => {
        result.indieHackerReports = reports
      }),
    )
  }

  // Wait for all fetches to complete
  await Promise.all(fetchPromises)

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

  if (result.productHuntProducts) {
    setOutput(
      'productHuntProducts',
      Buffer.from(JSON.stringify(result.productHuntProducts), 'utf-8').toString('base64'),
    )
  }

  if (result.aiPapers) {
    setOutput(
      'aiPapers',
      Buffer.from(JSON.stringify(result.aiPapers), 'utf-8').toString('base64'),
    )
  }

  if (result.indieHackerReports) {
    setOutput(
      'indieHackerReports',
      Buffer.from(JSON.stringify(result.indieHackerReports), 'utf-8').toString('base64'),
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
