import feedparser
import json
import os
import urllib.request

ARCHIVE_FILE = "policy_archive.json"

if os.path.exists(ARCHIVE_FILE):
    with open(ARCHIVE_FILE, "r", encoding="utf-8") as f:
        archive_data = json.load(f)
else:
    archive_data = []

existing_links = {item['link'] for item in archive_data}

url = "https://script.google.com/macros/s/AKfycbxun4FU75pH4bcr6Cl8zDQaiO_pF9NW_NYdo7E1-fmtgEWJUu19CtWS9WqL44SqSEg94w/exec"

entries = []
try:
    # 구글 서버를 거쳐오기 때문에 보안 차단 없이 부드럽게 데이터를 가져옵니다.
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=15) as response:
        xml_data = response.read()
        feed = feedparser.parse(xml_data)
        entries = getattr(feed, 'entries', [])
        print(f"📡 구글 우회 통로 연결 성공! 가져온 데이터: {len(entries)}개")
except Exception as e:
    print(f"❌ 접속 실패 원인: {e}")

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

with open(ARCHIVE_FILE, "w", encoding="utf-8") as f:
    json.dump(archive_data, f, ensure_ascii=False, indent=4)

# 웹페이지 생성 뼈대
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
