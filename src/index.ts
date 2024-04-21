import https from 'https';
import { getInput, setFailed, setOutput } from '@actions/core';
import axios from 'axios';
import { load } from 'cheerio';

const axiosInstance = axios.create({
  httpsAgent: new https.Agent({ keepAlive: true }),
});

const dateRangeEnum = ['daily', 'weekly', 'monthly'];

interface GithubRepoType {
  title: string;
  link: string;
  description: string;
  language: string;
  stars: string;
  todayStars: string;
}

interface RepoOutput {
  [key: string]: GithubRepoType[];
}

interface UserOptions {
  sendTime: string;
  languages: string[];
  dateRange: string;
}

const getUserInputs = (): UserOptions => {
  const sendTime = getInput('sendTime') || '19:00';
  const languagesJson = getInput('languages') || '[]';
  console.log('languagesJson', languagesJson);
  const languages = JSON.parse(languagesJson);
  console.log('languages', languages);
  const dateRange = getInput('dateRange') || 'daily';
  if (!dateRangeEnum.includes(dateRange)) {
    setFailed(
      `Invalid input dateRange: ${dateRange}. Valid options are: ${dateRangeEnum.join(', ')}.`,
    );
  }
  return {
    sendTime,
    languages,
    dateRange,
  };
};

const getTrendingReposByLanguage = async (
  language: string = '',
  dateRange: string = 'daily',
) => {
  try {
    // 获取 GitHub Trending 页面的 HTML
    let url;
    if (language)
      url = `https://github.com/trending/${language}?since=${dateRange}`;
    else url = `https://github.com/trending?since=${dateRange}`;

    const { data } = await axiosInstance.get(url);
    const $ = load(data);
    const repos: GithubRepoType[] = [];

    // 解析 HTML，获取每个 Trending 仓库的信息
    $('.Box-row').each((index, element) => {
      const title = $(element)
        .find('h2 a')
        .text()
        .replace(/[\n\s]+/g, '');
      const link = $(element).find('h2 a').attr('href') ?? '';
      const description = $(element).find('p').text().trim();
      const language = $(element)
        .find('[itemprop=programmingLanguage]')
        .text()
        .trim();
      const stars = $(element)
        .find('.Link--muted')
        .first()
        .text()
        .replace(/[\n\s]+/g, '');
      const todayStars = $(element).find('.float-sm-right').text().trim();

      repos.push({ title, description, language, stars, todayStars, link });
    });

    return repos;
  } catch (error) {
    console.error('Error fetching trending repos:', error);
    return [];
  }
};
/**
 *
 * @param { UserOptions } userOptions user options
 * @returns { RepoOutput } all repos result
 */
async function getAllRepos(userOptions: UserOptions) {
  const result = {} as RepoOutput;
  const { languages = [], dateRange } = userOptions;
  if (languages.length === 0) {
    const languageReposData = await getTrendingReposByLanguage('', dateRange);
    result.all = languageReposData;
  } else {
    for (let i = 0; i < languages.length; i++) {
      const language = languages[i];
      const languageReposData = await getTrendingReposByLanguage(
        language,
        dateRange,
      );
      result[language] = languageReposData;
    }
  }
  return result;
}

/**
 * @returns { RepoOutput } githubTrendingRepos data
 */
async function main() {
  const userOptions = getUserInputs();
  console.log('userOptions', userOptions);
  const data = await getAllRepos(userOptions);
  setOutput(
    'githubTrendingRepos',
    Buffer.from(JSON.stringify(data), 'utf-8').toString('base64'),
  );
  return data;
}

try {
  main();
} catch (error) {
  setFailed(`${(error as unknown as { message: string }).message} -> ${error}`);
}
