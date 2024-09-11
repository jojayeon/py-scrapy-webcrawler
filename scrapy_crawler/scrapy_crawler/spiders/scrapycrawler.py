import scrapy
from urllib.parse import urljoin
from konlpy.tag import Okt
from collections import Counter


class BasicSpider(scrapy.Spider):
    name = "scrapycrawler"
    
    def __init__(self, search_term='', *args, **kwargs):
        super(BasicSpider, self).__init__(*args, **kwargs)
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
        self.total_word_count = Counter()
        self.excluded_words = ["이", "가", "은", "는", "께", "서"]
        self.okt = Okt()
        
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
        # 모든 <a> 태그의 href 속성을 추출하여 리스트로 가져옵니다.
        links = response.xpath('//a/@href').getall()

        for link in links:
            full_url = urljoin(response.url, link)  # 상대 URL을 절대 URL로 
            if self.is_valid_url(full_url):
                yield scrapy.Request(full_url, callback=self.parse_page)
        
    def parse_page(self, response):
        for xpath in self.xpath_expressions:
            paragraphs = response.xpath(xpath).getall()
            if paragraphs:
                for paragraph in paragraphs:
                    words = self.okt.nouns(paragraph)
                    filtered_words = [word for word in words if word not in self.excluded_words]
                    self.word_count.update(filtered_words)

    def closed(self, reason):
        # 스파이더가 종료될 때 단어 개수를 출력
        total_words = sum(self.word_count.values())
        total_words_all_sites = sum(self.total_word_count.values())
        min_word_count = 30 # 원하는 갯수 이상의 단어만 보이게

        with open('word_counts.txt', 'w', encoding='utf-8') as f:
            f.write(f'Total word count: {total_words}\n\n')
            f.write(f'Total word count (all sites): {total_words_all_sites}\n\n')
            for word, count in self.word_count.items():
                if count >= min_word_count:
                    f.write(f'{word}: {count}\n')
                    
                    
                    