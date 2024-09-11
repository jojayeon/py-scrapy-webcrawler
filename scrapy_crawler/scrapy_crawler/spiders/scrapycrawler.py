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
            '//p/text()',
            '//div/text()',
            '//section/text()',
            '//header/text()',
            '//h1/text()',
            '//h2/text()',
            '//h3/text()',
            '//h4/text()',
            '//h5/text()',
            '//h6/text()',
            '//blockquote/text()',
            '//pre/text()',
            '//code/text()',
            '//li/text()',
            '//a/text()',
            '//strong/text()',
            '//td/text()'
        ]

        self.word_count = Counter()

        self.total_word_count = Counter()
        self.excluded_words = ["이", "가", "은", "는", "께", "서"]


    def parse(self, response):
        # 모든 <a> 태그의 href 속성을 추출하여 리스트로 가져옵니다.
        links = response.xpath('//a/@href').getall()

        for link in links:
            full_url = urljoin(response.url, link)  # 상대 URL을 절대 URL로 변환
            if not ( '.jpg' in full_url or '.png' in full_url or '.gif' in full_url or '.pdf' in full_url or '.mp4' in full_url or 'vimeo.com' in full_url or 'instagram.com' in full_url or 'imgur.com' in full_url or 'download' in full_url or 'attachment' in full_url or 'down.do' in full_url or 'FileDown.do' in full_url or 'google.com' in full_url or 'youtube.com' in full_url or 'melon' in full_url or 'w=' in full_url or 'p=' in full_url or 'kakao' in full_url or 'facebook' in full_url or 'japan' in full_url or 'china' in full_url or 'subscribe' in full_url or 'signin' in full_url or 'signup' in full_url or 'register' in full_url or 'apply' in full_url or 'recruit' in full_url or 'applyin' in full_url or 'customer_report' in full_url or 'customer_submit' in full_url or 'customer_view' in full_url or 'privacy' in full_url or 'mypage_help' in full_url or 'help' in full_url or 'rules' in full_url or 'sitemap' in full_url or 'about' in full_url or 'contact' in full_url or 'careers' in full_url or 'pdf' in full_url or 'search' in full_url or 'twitter' in full_url or 'shopping' in full_url or 'company' in full_url or 'subscription' in full_url or 'member' in full_url ) and ( full_url.startswith('http') ):
                yield scrapy.Request(full_url, callback=self.parse_page)
        
    def parse(self, response):
        self.log(f'Visited {response.url}')
        
        # 모든 <a> 태그의 href 속성을 추출하여 리스트로 가져옵니다.
        links = response.xpath('//a/@href').getall()

        for link in links:
            full_url = urljoin(response.url, link)  # 상대 URL을 절대 URL로 변환
            if not ('.jpg' in full_url or '.png' in full_url or '.gif' in full_url or '.pdf' in full_url or '.mp4' in full_url or 'vimeo.com' in full_url or 'instagram.com' in full_url or 'imgur.com' in full_url or 'download' in full_url or 'attachment' in full_url or 'down.do' in full_url or 'FileDown.do' in full_url or 'google.com' in full_url or 'youtube.com' in full_url or 'melon' in full_url or 'w=' in full_url or 'p=' in full_url or 'kakao' in full_url or 'facebook' in full_url or 'japan' in full_url or 'china' in full_url or 'subscribe' in full_url or 'signin' in full_url or 'signup' in full_url or 'register' in full_url or 'apply' in full_url or 'recruit' in full_url or 'applyin' in full_url or 'customer_report' in full_url or 'customer_submit' in full_url or 'customer_view' in full_url or 'privacy' in full_url or 'mypage_help' in full_url or 'help' in full_url or 'rules' in full_url or 'sitemap' in full_url or 'about' in full_url or 'contact' in full_url or 'careers' in full_url or 'pdf' in full_url or 'search' in full_url or 'twitter' in full_url or 'shopping' in full_url or 'company' in full_url or 'subscription' in full_url or 'member' in full_url) and (full_url.startswith('http')):
                yield scrapy.Request(full_url, callback=self.parse_page)
        
    def parse_page(self, response):
        okt = Okt()
        for xpath in self.xpath_expressions:
            paragraphs = response.xpath(xpath).getall()
            if paragraphs:
                # self.log(f'Extracted paragraphs with XPath {xpath}: {paragraphs}')
                for paragraph in paragraphs:
                    words = okt.nouns(paragraph)
                    filtered_words = [word for word in words if word not in self.excluded_words]
                    self.word_count.update(filtered_words)
                    self.total_word_count.update(filtered_words)


    def closed(self, reason):
        # 스파이더가 종료될 때 단어 개수를 출력
        total_words = sum(self.word_count.values())
        site_word_counts = {site: count for site, count in self.word_count.items()}
        min_word_count = 30 # 예시: 단어가 최소 5개 이상인 경우만 표기

        with open('word_counts.txt', 'w', encoding='utf-8') as f:
            f.write(f'Total word count: {total_words}\n\n')
            for site, count in site_word_counts.items():
                if count >= min_word_count:
                    f.write(f'{site}: {count}\n')