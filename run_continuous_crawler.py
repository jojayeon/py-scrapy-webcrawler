import os
import subprocess
import time

def run_spider():
    project_dir = 'scrapy_crawler'  # 스크래피 프로젝트 디렉토리 경로
    
    while True:
        try:
            # 현재 디렉토리를 스크래피 프로젝트 디렉토리로 변경
            os.chdir(project_dir)
            # 스크래피 명령어 실행
            subprocess.run(["scrapy", "crawl", "Continuous_Crawling_Spider"], check=True, cwd=project_dir)
        except subprocess.CalledProcessError as e:
            print(f"Error occurred: {e}")
        time.sleep(300)  # 5분 대기

if __name__ == "__main__":
    run_spider()
