import feedparser

# 수집할 RSS 주소 목록
rss_urls = [
    "https://www.moel.go.kr/rss/notice.do",
    "https://www.moel.go.kr/rss/policy.do",
    "https://www.moel.go.kr/rss/lawinfo.do"
]

# 만들어질 웹페이지의 뼈대 (스타일 및 검색 기능 추가)
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
        a { color: #333; text-decoration: none; }
        a:hover { text-decoration: underline; color: #2cc295; }
    </style>
</head>
<body>
    <h1>📌 실시간 업데이트 대시보드</h1>
    
    <input type="text" id="searchBar" onkeyup="filterList()" placeholder="검색어를 입력하세요 (예: 고용, 지원금, 행정예고)...">
    
    <ul id="postList">
"""

# 각 주소를 돌면서 최신 글 20개씩 가져와서 하나의 리스트로 합치기
for url in rss_urls:
    feed = feedparser.parse(url)
    category_name = feed.feed.title.replace("고용노동부 ", "") # 카테고리 이름 깔끔하게 정리
    
    for entry in feed.entries[:20]: # 검색 풀을 넓히기 위해 최신 글 20개 추출
        html_content += f"""
        <li class="post-item">
            <span class="category">{category_name}</span>
            <a href="{entry.link}" target="_blank">{entry.title}</a>
        </li>
        """

# 💡 실시간 검색을 가능하게 하는 자바스크립트 소스코드
html_content += """
    </ul>

    <script>
    function filterList() {
        var input, filter, ul, li, a, i, txtValue;
        input = document.getElementById('searchBar');
        filter = input.value.toUpperCase(); // 대소문자 구분 없이 검색
        ul = document.getElementById("postList");
        li = ul.getElementsByTagName('li');

        // 리스트를 하나씩 돌면서 검색어가 포함되어 있는지 확인
        for (i = 0; i < li.length; i++) {
            txtValue = li[i].textContent || li[i].innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                li[i].style.display = ""; // 검색어가 있으면 보임
            } else {
                li[i].style.display = "none"; // 검색어가 없으면 숨김
            }
        }
    }
    </script>
</body>
</html>
"""

# 추출한 데이터를 index.html 파일로 저장
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
print("대시보드 파일 생성 완료!")
