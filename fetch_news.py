import feedparser
import json
from datetime import date

feeds = {
    "Top News": "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en",
    "Current Affairs": "https://www.thehindu.com/opinion/feeder/default.rss",
    "BBC India": "https://feeds.bbci.co.uk/news/world/asia/india/rss.xml",
    "World Affairs": "https://feeds.bbci.co.uk/news/world/rss.xml",
}

news_list = []
for source, url in feeds.items():
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            news_list.append({
                "title": entry.title,
                "link": entry.link,
                "published": entry.get("published", ""),
                "source": source
            })
        print("OK " + source + ": " + str(len(feed.entries)))
    except:
        print("FAIL " + source)

today = date.today().strftime("%Y-%m-%d")
with open("news_" + today + ".json", "w", encoding="utf-8") as f:
    json.dump(news_list, f, indent=4, ensure_ascii=False)
print("Total: " + str(len(news_list)))

badge_classes = {
    "Top News": "badge-top-news",
    "Current Affairs": "badge-current-affairs",
    "BBC India": "badge-bbc-india",
    "World Affairs": "badge-world-affairs",
}

news_cards = ""
for i, item in enumerate(news_list):
    badge = badge_classes.get(item['source'], 'badge-top-news')
    safe_title = item['title'].replace('"','').replace("'",'').replace('`','')
    news_cards += (
        '<div class="news-item" data-source="' + item['source'].lower() +
        '" data-title="' + safe_title + '">' +
        '<div><span class="source-badge ' + badge + '">' + item['source'] + '</span>' +
        '<a class="news-title" href="' + item['link'] + '" target="_blank">' + item['title'] + '</a></div>' +
        '<div><div class="date">' + item['published'] + '</div>' +
        '<div class="action-btns">' +
        '<button class="copy-btn" onclick="copyNews(this)">Copy</button>' +
        '<button class="bookmark-btn" onclick="toggleBookmark(this)">Save</button>' +
        '<button class="share-btn" onclick="shareNews(this)">Share</button>' +
        '</div></div></div>'
    )

highlights = ""
for i in range(min(5, len(news_list))):
    highlights += '<div class="hl-item">' + news_list[i]["title"] + '</div>\n'

source_counts = {}
for item in news_list:
    source_counts[item['source']] = source_counts.get(item['source'], 0) + 1

sc_json = json.dumps(source_counts)
cc_json = json.dumps(["#2a5298","#8B0000","#BB1919","#006400"])
total = str(len(news_list))

page = open("index.html", "w", encoding="utf-8")
page.write("""<!DOCTYPE html>
<html>
<head>
<title>News Intelligence</title>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Segoe UI',Arial,sans-serif;background:linear-gradient(135deg,#1e3c72,#2a5298);min-height:100vh;display:flex;flex-direction:column;}
body.light{background:linear-gradient(135deg,#dce9f9,#b8d0f0);}
#progressBar{position:fixed;top:0;left:0;height:3px;background:#FFD700;width:0%;z-index:9999;}
.header{background:rgba(0,0,0,0.25);padding:13px 20px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:100;}
.header h1{color:white;font-size:21px;}
.header-right{display:flex;align-items:center;gap:12px;}
#liveClock{color:white;font-size:13px;font-weight:700;}
#statsText{color:rgba(255,255,255,0.55);font-size:11px;}
.toggle-btn{background:white;border:none;padding:5px 12px;border-radius:16px;cursor:pointer;font-size:12px;font-weight:700;color:#1e3c72;}
.layout{display:flex;flex:1;overflow:hidden;height:calc(100vh - 50px);}
.sidebar{width:210px;background:rgba(0,0,0,0.22);padding:14px 0;display:flex;flex-direction:column;gap:2px;flex-shrink:0;overflow-y:auto;}
.nav-item{display:flex;align-items:center;gap:10px;padding:11px 18px;color:rgba(255,255,255,0.65);cursor:pointer;font-size:13px;font-weight:600;border:none;border-left:3px solid transparent;background:none;width:100%;text-align:left;transition:all 0.2s;}
.nav-item:hover{background:rgba(255,255,255,0.1);color:white;}
.nav-item.active{background:rgba(255,255,255,0.15);color:#FFD700;border-left:3px solid #FFD700;}
.sidebar-footer{color:rgba(255,255,255,0.35);font-size:10px;padding:10px 18px;margin-top:auto;}
.main{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:12px;}
.panel{display:none;}
.panel.active{display:block;}
.panel-title{color:white;font-size:17px;font-weight:800;margin-bottom:14px;padding-bottom:8px;border-bottom:2px solid rgba(255,255,255,0.15);}
.search-bar input{width:100%;padding:11px 16px;border-radius:10px;border:none;font-size:14px;outline:none;margin-bottom:10px;}
.cats{display:flex;gap:7px;flex-wrap:wrap;margin-bottom:12px;}
.cat-btn{padding:6px 12px;border-radius:16px;border:2px solid white;background:transparent;color:white;cursor:pointer;font-size:12px;font-weight:700;transition:all 0.2s;}
.cat-btn:hover,.cat-btn.active{background:white;color:#1e3c72;}
.cat-count{background:#FFD700;color:#1e3c72;border-radius:10px;padding:1px 5px;font-size:10px;margin-left:3px;}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:13px;}
.news-item{background:white;padding:13px 14px;border-radius:14px;box-shadow:0 4px 12px rgba(0,0,0,0.15);transition:transform 0.25s;overflow:hidden;display:flex;flex-direction:column;justify-content:space-between;max-height:180px;}
.news-item.kw-highlight{border:2px solid #FF6600;box-shadow:0 0 12px rgba(255,102,0,0.4);}
.news-item:hover{transform:translateY(-3px);}
.source-badge{display:inline-block;padding:2px 7px;border-radius:7px;font-size:10px;font-weight:800;margin-bottom:5px;color:white;}
.badge-top-news{background:#2a5298;}
.badge-current-affairs{background:#8B0000;}
.badge-bbc-india{background:#BB1919;}
.badge-world-affairs{background:#006400;}
.news-title{text-decoration:none;color:#1a1a2e;font-size:13px;font-weight:700;line-height:1.4;display:block;flex:1;}
.news-title:hover{color:#2a5298;}
.date{color:#aaa;font-size:10px;margin-top:5px;}
.action-btns{display:flex;gap:5px;margin-top:8px;}
.copy-btn,.bookmark-btn,.share-btn{background:#f0f4ff;border:none;border-radius:7px;padding:4px 6px;cursor:pointer;font-size:11px;font-weight:600;flex:1;transition:background 0.2s;}
.copy-btn:hover{background:#d0e0ff;}
.bookmark-btn.saved{background:#FFD700;}
.share-btn:hover{background:#d0ffd0;}
#no-results{color:white;text-align:center;font-size:16px;padding:30px 0;display:none;grid-column:1/-1;}
.dash-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:14px;}
.stat-card{background:rgba(255,255,255,0.15);border-radius:12px;padding:14px 10px;text-align:center;color:white;}
.stat-card .num{font-size:24px;font-weight:800;}
.stat-card .lbl{font-size:10px;opacity:0.75;margin-top:3px;}
.bar-row{display:flex;align-items:center;gap:8px;margin-bottom:7px;}
.bar-lbl{color:white;font-size:11px;width:110px;text-align:right;flex-shrink:0;}
.bar-track{flex:1;background:rgba(255,255,255,0.12);border-radius:6px;height:20px;overflow:hidden;}
.bar-fill{height:100%;border-radius:6px;display:flex;align-items:center;padding-left:8px;color:white;font-size:11px;font-weight:700;}
.kw-box{background:rgba(255,255,255,0.12);padding:14px;border-radius:12px;display:flex;gap:8px;flex-wrap:wrap;align-items:center;}
.kw-box input{flex:1;padding:8px 12px;border-radius:8px;border:none;font-size:13px;outline:none;min-width:140px;}
.kw-box button{padding:8px 16px;border-radius:8px;border:none;background:#FFD700;color:#1e3c72;font-weight:800;cursor:pointer;font-size:13px;}
.kw-tags{display:flex;gap:6px;flex-wrap:wrap;margin-top:10px;}
.kw-tag{background:#FFD700;color:#1e3c72;padding:4px 11px;border-radius:12px;font-size:12px;font-weight:700;cursor:pointer;}
.hl-item{background:rgba(255,255,255,0.13);color:white;padding:11px 14px;border-radius:10px;margin-bottom:8px;font-size:13px;border-left:4px solid #FFD700;}
.hl-item.kw-match{border-left-color:#FF6600;background:rgba(255,120,0,0.2);}
.past-item{background:rgba(255,255,255,0.1);color:white;padding:10px 14px;border-radius:10px;margin-bottom:8px;font-size:13px;border:1px solid rgba(255,255,255,0.15);}
.bk-item{background:rgba(255,255,255,0.13);color:white;padding:10px 14px;border-radius:10px;margin-bottom:8px;font-size:13px;}
@media(max-width:900px){.grid{grid-template-columns:repeat(2,1fr);}.dash-grid{grid-template-columns:repeat(2,1fr);}.sidebar{width:170px;}}
@media(max-width:560px){.sidebar{display:none;}.grid{grid-template-columns:repeat(2,1fr);}}
</style>
</head>
<body>
<div id="progressBar"></div>
<div class="header">
  <h1>📰 News Intelligence</h1>
  <div class="header-right">
    <div id="liveClock"></div>
    <span id="statsText"></span>
    <button class="toggle-btn" id="modeBtn" onclick="toggleMode()">🌙 Dark</button>
  </div>
</div>
<div class="layout">
  <div class="sidebar">
    <button class="nav-item active" id="nav-news" onclick="showPanel('news')">🏠 Home</button>
    <button class="nav-item" id="nav-dashboard" onclick="showPanel('dashboard')">📊 Dashboard</button>
    <button class="nav-item" id="nav-highlights" onclick="showPanel('highlights')">⭐ Highlights</button>
    <button class="nav-item" id="nav-alerts" onclick="showPanel('alerts')">🔔 Alerts</button>
    <button class="nav-item" id="nav-past" onclick="showPanel('past')">📅 Past News</button>
    <button class="nav-item" id="nav-bookmarks" onclick="showPanel('bookmarks')">🔖 Saved</button>
    <div class="sidebar-footer" id="sideDate"></div>
  </div>
  <div class="main">

    <div class="panel active" id="panel-news">
      <div class="search-bar"><input type="text" id="searchInput" placeholder="🔍 Search news..." oninput="filterNews()"></div>
      <div class="cats">
        <button class="cat-btn active" onclick="setCategory('all',this)">🌐 All <span class="cat-count" id="cnt-all"></span></button>
        <button class="cat-btn" onclick="setCategory('top news',this)">📰 Top News <span class="cat-count" id="cnt-top news"></span></button>
        <button class="cat-btn" onclick="setCategory('current affairs',this)">📚 Current Affairs <span class="cat-count" id="cnt-current affairs"></span></button>
        <button class="cat-btn" onclick="setCategory('bbc india',this)">🇮🇳 BBC India <span class="cat-count" id="cnt-bbc india"></span></button>
        <button class="cat-btn" onclick="setCategory('world affairs',this)">🌍 World <span class="cat-count" id="cnt-world affairs"></span></button>
      </div>
      <div class="grid" id="newsGrid">
        """ + news_cards + """
        <div id="no-results">😔 No news found!</div>
      </div>
    </div>

    <div class="panel" id="panel-dashboard">
      <div class="panel-title">📊 Dashboard</div>
      <div class="dash-grid" id="statCards"></div>
      <div id="chartBars"></div>
    </div>

    <div class="panel" id="panel-highlights">
      <div class="panel-title">⭐ Top 5 Highlights</div>
      """ + highlights + """
    </div>

    <div class="panel" id="panel-alerts">
      <div class="panel-title">🔔 Keyword Alerts</div>
      <div class="kw-box">
        <input type="text" id="kwInput" placeholder="e.g. Tamil Nadu, Modi...">
        <button onclick="addKeyword()">+ Add</button>
      </div>
      <div class="kw-tags" id="kwTags"></div>
      <p style="color:rgba(255,255,255,0.5);font-size:12px;margin-top:12px;">💡 Matching news will glow orange in Home!</p>
    </div>

    <div class="panel" id="panel-past">
      <div class="panel-title">📅 Past News</div>
      <div class="past-item">📁 Files saved as <b>news_YYYY-MM-DD.json</b> in your project folder</div>
      <div class="past-item">📂 Open VS Code → Explorer → click any <b>news_*.json</b> file</div>
      <div class="past-item">🗓️ Today: <b>news_""" + today + """.json</b></div>
    </div>

    <div class="panel" id="panel-bookmarks">
      <div class="panel-title">🔖 Saved Articles</div>
      <div id="bookmarksList"></div>
    </div>

  </div>
</div>
<script>
var SC = """ + sc_json + """;
var CC = """ + cc_json + """;
var TOTAL = """ + total + """;
var TODAY = '""" + today + """';

// INIT
document.getElementById('statsText').textContent = TODAY + ' | ' + TOTAL + ' articles';
document.getElementById('sideDate').textContent = TODAY;

// THEME
var isLight = localStorage.getItem('theme') === 'light';
function applyTheme(){
  document.body.classList.toggle('light', isLight);
  document.getElementById('modeBtn').textContent = isLight ? '☀️ Light' : '🌙 Dark';
}
applyTheme();
function toggleMode(){
  isLight = !isLight;
  localStorage.setItem('theme', isLight ? 'light' : 'dark');
  applyTheme();
}

// CLOCK
function tick(){
  document.getElementById('liveClock').textContent = new Date().toLocaleTimeString('en-IN');
}
setInterval(tick, 1000); tick();

// AUTO REFRESH
setTimeout(function(){ location.reload(); }, 30*60*1000);

// PROGRESS
document.querySelector('.main').addEventListener('scroll', function(){
  var el = this;
  var pct = (el.scrollTop / (el.scrollHeight - el.clientHeight)) * 100;
  document.getElementById('progressBar').style.width = pct + '%';
});

// SIDEBAR
function showPanel(name){
  document.querySelectorAll('.panel').forEach(function(p){ p.classList.remove('active'); });
  document.querySelectorAll('.nav-item').forEach(function(b){ b.classList.remove('active'); });
  document.getElementById('panel-' + name).classList.add('active');
  document.getElementById('nav-' + name).classList.add('active');
  if(name === 'bookmarks') renderBookmarks();
  if(name === 'dashboard') buildDashboard();
}

// DASHBOARD
function buildDashboard(){
  var keys = Object.keys(SC);
  var html = '<div class="stat-card"><div class="num">' + TOTAL + '</div><div class="lbl">Total</div></div>';
  for(var i=0;i<keys.length;i++){
    html += '<div class="stat-card"><div class="num">' + SC[keys[i]] + '</div><div class="lbl">' + keys[i] + '</div></div>';
  }
  document.getElementById('statCards').innerHTML = html;
  var vals = Object.values(SC);
  var mx = Math.max.apply(null, vals);
  var ch = '';
  for(var j=0;j<keys.length;j++){
    var pct = Math.round((SC[keys[j]]/mx)*100);
    ch += '<div class="bar-row"><div class="bar-lbl">' + keys[j] + '</div><div class="bar-track"><div class="bar-fill" style="width:'+pct+'%;background:'+CC[j%CC.length]+'">' + SC[keys[j]] + '</div></div></div>';
  }
  document.getElementById('chartBars').innerHTML = ch;
}

// KEYWORDS
var keywords = JSON.parse(localStorage.getItem('alertKeywords') || '[]');
function addKeyword(){
  var v = document.getElementById('kwInput').value.trim().toLowerCase();
  if(v && keywords.indexOf(v)===-1){
    keywords.push(v);
    localStorage.setItem('alertKeywords', JSON.stringify(keywords));
    document.getElementById('kwInput').value = '';
    renderKeywords(); applyHighlights();
  }
}
function removeKeyword(kw){
  keywords = keywords.filter(function(k){ return k!==kw; });
  localStorage.setItem('alertKeywords', JSON.stringify(keywords));
  renderKeywords(); applyHighlights();
}
function renderKeywords(){
  var h = '';
  for(var i=0;i<keywords.length;i++){
    h += '<span class="kw-tag" onclick="removeKeyword(\\'' + keywords[i] + '\\')">🔔 ' + keywords[i] + ' ✕</span>';
  }
  document.getElementById('kwTags').innerHTML = h;
}
function applyHighlights(){
  document.querySelectorAll('.news-item').forEach(function(item){
    var t = item.querySelector('a').innerText.toLowerCase();
    var m = keywords.some(function(kw){ return t.indexOf(kw)!==-1; });
    item.classList.toggle('kw-highlight', m);
  });
  document.querySelectorAll('.hl-item').forEach(function(item){
    var t = item.innerText.toLowerCase();
    var m = keywords.some(function(kw){ return t.indexOf(kw)!==-1; });
    item.classList.toggle('kw-match', m);
  });
}

// FILTER + CATEGORY
var currentCat = 'all';
function filterNews(){
  var s = document.getElementById('searchInput').value.toLowerCase();
  var items = document.querySelectorAll('.news-item');
  var v = 0;
  items.forEach(function(item){
    if(item.id==='no-results') return;
    var t = item.querySelector('a').innerText.toLowerCase();
    var src = item.getAttribute('data-source');
    var ok = t.indexOf(s)!==-1 && (currentCat==='all' || src===currentCat);
    item.style.display = ok ? 'flex' : 'none';
    if(ok) v++;
  });
  document.getElementById('no-results').style.display = v===0 ? 'block' : 'none';
}
function setCategory(cat, btn){
  currentCat = cat;
  document.querySelectorAll('.cat-btn').forEach(function(b){ b.classList.remove('active'); });
  btn.classList.add('active');
  filterNews();
}
function updateCounts(){
  var items = document.querySelectorAll('.news-item');
  document.getElementById('cnt-all').textContent = items.length;
  ['top news','current affairs','bbc india','world affairs'].forEach(function(cat){
    var c=0;
    items.forEach(function(item){ if(item.getAttribute('data-source')===cat) c++; });
    var el=document.getElementById('cnt-'+cat);
    if(el) el.textContent=c;
  });
}

// COPY
function copyNews(btn){
  var t = btn.closest('.news-item').querySelector('a').innerText;
  navigator.clipboard.writeText(t);
  btn.textContent='✅'; setTimeout(function(){ btn.textContent='Copy'; },1500);
}

// SHARE
function shareNews(btn){
  var item=btn.closest('.news-item');
  var t=item.querySelector('a').innerText;
  var l=item.querySelector('a').href;
  window.open('https://wa.me/?text='+encodeURIComponent(t+' '+l),'_blank');
}

// BOOKMARK
var bookmarks = JSON.parse(localStorage.getItem('bookmarks') || '[]');
function toggleBookmark(btn){
  var item=btn.closest('.news-item');
  var title=item.getAttribute('data-title');
  var link=item.querySelector('a').href;
  var idx=-1;
  for(var i=0;i<bookmarks.length;i++){ if(bookmarks[i].title===title){idx=i;break;} }
  if(idx===-1){ bookmarks.push({title:title,link:link}); btn.classList.add('saved'); btn.textContent='Saved'; }
  else{ bookmarks.splice(idx,1); btn.classList.remove('saved'); btn.textContent='Save'; }
  localStorage.setItem('bookmarks', JSON.stringify(bookmarks));
}
function renderBookmarks(){
  var list=document.getElementById('bookmarksList');
  if(bookmarks.length===0){
    list.innerHTML='<p style="color:rgba(255,255,255,0.5);font-size:13px;">No saved articles yet — click Save on any news card!</p>';
    return;
  }
  var h='';
  for(var i=0;i<bookmarks.length;i++){
    h+='<div class="bk-item"><a href="'+bookmarks[i].link+'" target="_blank" style="color:white">'+bookmarks[i].title+'</a></div>';
  }
  list.innerHTML=h;
  document.querySelectorAll('.bookmark-btn').forEach(function(btn){
    var t=btn.closest('.news-item').getAttribute('data-title');
    for(var i=0;i<bookmarks.length;i++){
      if(bookmarks[i].title===t){ btn.classList.add('saved'); btn.textContent='Saved'; break; }
    }
  });
}

// INIT
updateCounts(); renderKeywords(); applyHighlights(); renderBookmarks();
</script>
</body>
</html>""")
page.close()
print("Done!")

keyword = input("\nSearch (Enter to skip): ")
if keyword.strip():
    found = 0
    for item in news_list:
        if keyword.lower() in item["title"].lower():
            print("[" + item['source'] + "] " + item['title'])
            found += 1
    if found == 0:
        print("No results.")