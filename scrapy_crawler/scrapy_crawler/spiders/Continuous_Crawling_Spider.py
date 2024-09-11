import scrapy
from urllib.parse import urljoin, urlparse
from konlpy.tag import Okt
from collections import Counter
import time
import os


class ContinuousCrawlingSpider(scrapy.Spider):
    name = "Continuous_Crawling_Spider"

    def __init__(self, search_term='', *args, **kwargs):
        super(ContinuousCrawlingSpider, self).__init__(*args, **kwargs)
        self.search_term = search_term
        self.start_urls = [
            f'https://www.chosun.com/search?query={search_term}',
            f'https://search.hani.co.kr/search?searchword={search_term}',
            f'https://search.daum.net/search?w=news&lpp=10&DA=STC&rtmaxcoll=1&q={search_term}'
        ]

        self.xpath_expressions = [
            '//p//text()[normalize-space()]',
            '//div//text()[normalize-space()]',
            '//section//text()[normalize-space()]',
            '//header//text()[normalize-space()]',
            '//h1//text()[normalize-space()]',
            '//h2//text()[normalize-space()]',
            '//h3//text()[normalize-space()]',
            '//h4//text()[normalize-space()]',
            '//h5//text()[normalize-space()]',
            '//h6//text()[normalize-space()]',
            '//blockquote//text()[normalize-space()]',
            '//pre//text()[normalize-space()]',
            '//code//text()[normalize-space()]',
            '//li//text()[normalize-space()]',
            '//a//text()[normalize-space()]',
            '//strong//text()[normalize-space()]',
            '//td//text()[normalize-space()]'
        ]

        self.word_count = Counter()
        self.excluded_words = ["이", "가", "은", "는", "께", "서"]
        self.okt = Okt()
        self.visited_sites = self.load_visited_sites()  # 방문한 URL 로드

    def load_visited_sites(self):
        if os.path.exists('visited_sites.txt'):
            with open('visited_sites.txt', 'r', encoding='utf-8') as f:
                return set(line.strip() for line in f)
        return set()

    def save_visited_sites(self):
        with open('visited_sites.txt', 'w', encoding='utf-8') as f:
            for url in self.visited_sites:
                f.write(f'{url}\n')

    def is_valid_url(self, url):
        invalid_patterns = [
            '.jpg', '.png', '.gif', '.pdf', '.mp4',
            'vimeo.com', 'instagram.com', 'imgur.com',
            'download', 'attachment', 'down.do', 'FileDown.do',
            'google.com', 'youtube.com', 'melon', 'w=', 'p=',
            'kakao', 'facebook', 'japan', 'china', 'subscribe',
            'signin', 'signup', 'register', 'apply', 'recruit',
            'applyin', 'customer_report', 'customer_submit',
            'customer_view', 'privacy', 'mypage_help', 'help',
            'rules', 'sitemap', 'about', 'contact', 'careers',
            'pdf', 'search', 'twitter', 'shopping', 'company',
            'subscription', 'member'
        ]
        return not any(pattern in url for pattern in invalid_patterns) and url.startswith('http')

    def parse(self, response):
        links = response.xpath('//a/@href').getall()
        for link in links:
            full_url = urljoin(response.url, link)
            domain = urlparse(full_url).netloc

            if full_url not in self.visited_sites and self.is_valid_url(full_url):
                self.visited_sites.add(full_url)  # 이미 방문한 URL로 기록
                yield scrapy.Request(full_url, callback=self.parse_page)

    def parse_page(self, response):
        for xpath in self.xpath_expressions:
            paragraphs = response.xpath(xpath).getall()
            if paragraphs:
                for paragraph in paragraphs:
                    words = self.okt.nouns(paragraph)
                    filtered_words = [word for word in words if word not in self.excluded_words]
                    self.word_count.update(filtered_words)

        # 주기적으로 단어 개수를 파일에 기록
        current_time = time.time()
        if current_time - self.last_save_time > 300:  # 5분마다 저장
            self.save_word_counts()
            self.last_save_time = current_time

    def save_word_counts(self):
        total_words = sum(self.word_count.values())
        min_word_count = 30  # 원하는 갯수 이상의 단어만 보이게

        with open('word_counts2s.txt', 'w', encoding='utf-8') as f:
            f.write(f'Total word count: {total_words}\n\n')
            for word, count in self.word_count.items():
                if count >= min_word_count:
                    f.write(f'{word}: {count}\n')

    def closed(self, reason):
        self.save_word_counts()
        self.save_visited_sites()
