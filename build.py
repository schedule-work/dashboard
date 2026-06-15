import feedparser
import ssl

# 공공기관 사이트 보안 인증서 에러 방지 설정
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

# 수집할 RSS 주소 목록
rss_urls = [
    "https://www.moel.go.kr/rss/notice.do",
    "https://www.moel.go.kr/rss/policy.do",
    "https://www.moel.go.kr/rss/lawinfo.do"
]

# 만들어질 웹페이지의 뼈대
html_content = """
<html>
<head>
    <meta charset="utf-8">
    <title>업무용 RSS 검색 대시보드</title>
    <style>
        body { font-family: 'Malgun Gothic', sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; line-height: 1.6; }
        h1 { color: #333; border-bottom: 2px solid #2cc295; padding-bottom: 10px; }
        #searchBar { width: 100%; padding: 12px; margin: 20px 0; font-size: 16px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        ul { list-style: none; padding: 0; }
        li { padding: 10px; border-bottom: 1px solid #eee; display: flex; align-items: center; }
        .category { background: #f0f0f0; color: #666; font-size: 12px; padding: 2px 6px; border-radius: 3px; margin-right: 10px; white-space: nowrap; }
        .error-msg { color: #ff4d4d; font-size: 14px; padding: 10px; }
        a { color: #333; text-decoration: none; }
        a:hover { text-decoration: underline; color: #2cc295; }
    </style>
</head>
<body>
    <h1>📌 실시간 업데이트 대시보드</h1>
    <input type="text" id="searchBar" onkeyup="filterList()" placeholder="검색어를 입력하세요 (예: 고용, 지원금, 행정예고)...">
    <ul id="postList">
"""

has_data = False

for url in rss_urls:
    # 💡 1. 일반 크롬 브라우저인 것처럼 위장하여 방화벽 차단 회피
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    feed = feedparser.parse(url, agent=user_agent)
    
    # URL별 기본 카테고리 이름 설정 (백업용)
    if "notice" in url: category_name = "공지사항"
    elif "policy" in url: category_name = "정책자료"
    else: category_name = "입법·행정예고"
    
    # 💡 2. 안전장치: 정상적으로 사이트 제목을 가져왔을 때만 이름 업데이트
    if hasattr(feed, 'feed') and hasattr(feed.feed, 'title'):
        category_name = feed.feed.title.replace("고용노동부 ", "")
    
    # 💡 3. 안전장치: 글 목록이 정상적으로 존재할 때만 데이터 추출
    entries = getattr(feed, 'entries', [])
    if entries:
        has_data = True
        for entry in entries[:20]:
            title = getattr(entry, 'title', '제목 없음')
            link = getattr(entry, 'link', '#')
            html_content += f"""
            <li class="post-item">
                <span class="category">{category_name}</span>
                <a href="{link}" target="_blank">{title}</a>
            </li>
            """
    else:
        print(f"⚠️ {category_name} 피드를 일시적으로 불러올 수 없습니다. (차단 또는 서버 점검)")

# 만약 모든 사이트가 차단되어 가져온 글이 하나도 없다면 안내 문구 출력
if not has_data:
    html_content += "<p class='error-msg'>현재 고용노동부 서버 접속이 원활하지 않아 데이터를 불러올 수 없습니다. 잠시 후 자동 업데이트를 기다려주세요.</p>"

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
print("대시보드 파일 생성 완료!")
