import feedparser
import ssl
import json
import os

# 공공기관 사이트 보안 인증서 에러 방지
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

# 1. 데이터베이스 파일 경로 설정
ARCHIVE_FILE = "policy_archive.json"

# 기존에 쌓아둔 데이터가 있다면 불러오고, 없다면 새로 시작합니다.
if os.path.exists(ARCHIVE_FILE):
    with open(ARCHIVE_FILE, "r", encoding="utf-8") as f:
        archive_data = json.load(f)
else:
    archive_data = []

# 중복 수집을 막기 위해 기존에 저장된 링크 목록을 추출합니다.
existing_links = {item['link'] for item in archive_data}

# 2. 고용노동부 정책자료 RSS 수집 (행정예고 제외)
url = "https://www.moel.go.kr/rss/policy.do"
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
feed = feedparser.parse(url, agent=user_agent)

entries = getattr(feed, 'entries', [])
new_count = 0

# 가져온 최신 글들을 돌면서 새로운 글만 아카이브에 추가합니다.
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

# 3. 업데이트된 누적 데이터베이스를 다시 파일로 저장합니다.
with open(ARCHIVE_FILE, "w", encoding="utf-8") as f:
    json.dump(archive_data, f, ensure_ascii=False, indent=4)

print(f"🔄 업데이트 완료: 새로운 정책자료 {new_count}개 추가 (총 {len(archive_data)}개 축적됨)")

# 4. 누적된 전체 데이터를 바탕으로 HTML 검색 대시보드 생성
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
        a { color: #333; text-decoration: none; }
        a:hover { text-decoration: underline; color: #0076a3; }
    </style>
</head>
<body>
    <h1>📋 고용노동부 정책자료 아카이브</h1>
"""

html_content += f"<p class='counter'>현재까지 누적된 정책자료: <strong>{len(archive_data)}</strong>개</p>"
html_content += """
    <input type="text" id="searchBar" onkeyup="filterList()" placeholder="과거 정책자료 검색 (예: 장려금, 유연근무, 육아)...">
    <ul id="postList">
"""

# 저장된 데이터를 역순(최신순)으로 대시보드에 배치합니다.
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
