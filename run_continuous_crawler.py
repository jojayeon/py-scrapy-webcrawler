import os
import subprocess
import time

def run_spider(search_term):
    project_dir = 'C:/Users/Administrator/py-scrapy-webcrawler/scrapy_crawler'  # 스크래피 프로젝트 디렉토리 경로
    
    while True:
        try:
            # 현재 디렉토리를 스크래피 프로젝트 디렉토리로 변경
            os.chdir(project_dir)
            
            # 스크래피 명령어 실행
            result = subprocess.run(
                ["scrapy", "crawl", "Continuous_Crawling_Spider", "-a", f"search_term={search_term}"],
                check=True,
                capture_output=True,  # 명령어 출력 캡처
                text=True  # 텍스트 형식으로 출력
            )
            
            # 명령어 실행 결과 출력
            print(result.stdout)
            print(result.stderr)
        
        except subprocess.CalledProcessError as e:
            print(f"Error occurred: {e}")
            print(f"Error output: {e.output}")
        
        time.sleep(3600)  # 1시간 대기 (단위: 초)

if __name__ == "__main__":
    search_term = "저출산"  # 원하는 검색어로 변경
    run_spider(search_term)