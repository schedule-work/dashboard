import feedparser
import ssl
import json
import os
import urllib.request

# 공공기관 사이트 보안 인증서 에러 방지 설정
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

ARCHIVE_FILE = "policy_archive.json"

# 기존 데이터 불러오기
if os.path.exists(ARCHIVE_FILE):
    with open(ARCHIVE_FILE, "r", encoding="utf-8") as f:
        archive_data = json.load(f)
else:
    archive_data = []

existing_links = {item['link'] for item in archive_data}

# 고용노동부 정책자료 RSS 주소
url = "https://www.moel.go.kr/rss/policy.do"

# 💡 대한민국 PC에서 접속한 것처럼 헤더 정보(언어 설정 포함) 대폭 강화
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
}

entries = []
try:
    # 💡 브라우저 우회 접속 시도 및 15초 타임아웃 설정
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as response:
        xml_data = response.read()
        feed = feedparser.parse(xml_data)
        entries = getattr(feed, 'entries', [])
        print(f"📡 고용노동부 연결 성공! 가져온 데이터: {len(entries)}개")
except Exception as e:
    # 💡 실패 시 깃허브 Actions 로그에 정확한 에러 원인을 출력합니다.
    print(f"❌ 고용노동부 서버 접속 실패 원인: {e}")

# 데이터 누적
new_count = 0
for entry in entries:
    title = getattr(entry, 'title', '제목 없음')
    link = getattr(entry, 'link', '#')
    
    if link not in existing_links and link != '#':
        archive_data.append({
            "title": title,
            "link": link
        })
        existing_links.add(link)
        new_count += 1

# 데이터베이스 저장
with open(ARCHIVE_FILE, "w", encoding="utf-8") as f:
    json.dump(archive_data, f, ensure_ascii=False, indent=4)

# 웹페이지 생성
html_content = """
<html>
<head>
    <meta charset="utf-8">
    <title>고용노동부 정책자료 누적 아카이브</title>
    <style>
        body { font-family: 'Malgun Gothic', sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; line-height: 1.6; }
        h1 { color: #333; border-bottom: 2px solid #0076a3; padding-bottom: 10px; }
        .counter { color: #666; font-size: 14px; margin-top: -5px; }
        #searchBar { width: 100%; padding: 12px; margin: 20px 0; font-size: 16px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        ul { list-style: none; padding: 0; }
        li { padding: 12px; border-bottom: 1px solid #eee; }
        .tag { background: #e6f4fa; color: #0076a3; font-size: 11px; padding: 2px 6px; border-radius: 3px; margin-right: 10px; font-weight: bold; }
        .error-msg { color: #ff4d4d; font-size: 14px; padding: 10px; background: #fff5f5; border-radius: 4px; }
        a { color: #333; text-decoration: none; }
        a:hover { text-decoration: underline; color: #0076a3; }
    </style>
</head>
<body>
    <h1>📋 고용노동부 정책자료 아카이브</h1>
"""

html_content += f"<p class='counter'>현재까지 누적된 정책자료: <strong>{len(archive_data)}</strong>개</p>"

if len(archive_data) == 0:
    html_content += "<p class='error-msg'>⚠️ 고용노동부 보안 방화벽이 해외(GitHub) 서버를 차단 중입니다. Actions 탭에서 상세 로그 확인이 필요합니다.</p>"

html_content += """
    <input type="text" id="searchBar" onkeyup="filterList()" placeholder="과거 정책자료 검색 (예: 장려금, 유연근무, 육아)...">
    <ul id="postList">
"""

for item in reversed(archive_data):
    html_content += f"""
    <li class="post-item">
        <span class="tag">정책자료</span>
        <a href="{item['link']}" target="_blank">{item['title']}</a>
    </li>
    """

html_content += """
    </ul>
    <script>
    function filterList() {
        var input, filter, ul, li, i, txtValue;
        input = document.getElementById('searchBar');
        filter = input.value.toUpperCase();
        ul = document.getElementById("postList");
        li = ul.getElementsByTagName('li');
        for (i = 0; i < li.length; i++) {
            txtValue = li[i].textContent || li[i].innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                li[i].style.display = "";
            } else {
                li[i].style.display = "none";
            }
        }
    }
    </script>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
