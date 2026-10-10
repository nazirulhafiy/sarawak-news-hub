import re, json
P='/workspace/bantuan-icons/tool/node_modules/@phosphor-icons/core/assets/duotone/'
def inner(name):
    s=open(f'{P}{name}-duotone.svg').read()
    s=re.search(r'<svg[^>]*>(.*)</svg>',s,re.S).group(1)
    return s
def tile_icon(name, size=24):
    s=inner(name).replace('opacity="0.2"','class="group-icon-fill" opacity="0.2"')
    return f'<span class="group-icon-tile"><svg class="group-icon" viewBox="0 0 256 256" width="{size}" height="{size}" aria-hidden="true" focusable="false" fill="currentColor">{s}</svg></span>'
def net_icon(name):
    s=inner(name).replace('opacity="0.2"','class="brief-net-fill" opacity="0.2"')
    return f'<svg class="brief-net-icon" x="-11" y="-11" width="22" height="22" viewBox="0 0 256 256" fill="currentColor">{s}</svg>'

SITES=[
 dict(key='ai',name='AI.Sarawak.News',domain='ai.sarawak.news',icon='brain',kind='News',
      headline='Sarawak AI news, in one place.',
      desc='Source-linked coverage across policy, public services, education, workforce, research, infrastructure and business.',
      stats='81 stories · 7 categories',updated='8 Oct 2026'),
 dict(key='bantuan',name='Bantuan.Sarawak.News',domain='bantuan.sarawak.news',icon='hand-heart',kind='Directory',
      headline='Sarawak government assistance, in one directory.',
      desc='An independent directory of Sarawak government assistance. Every scheme links to an official page.',
      stats='24 schemes · 7 categories',updated='6 Oct 2026'),
]
PCDS=dict(key='pcds',name='PCDS 2030 Project Tracker',domain='pcds2030.com',icon='chart-line-up',kind='Tracker',
      headline='Major projects under Sarawak’s Post COVID-19 Development Strategy 2030, in one place.',
      desc='An independent tracker with project status, milestones and links to public sources.')

# hero network: 3 site tiles + dots, same classes as bantuan .brief-net
nodes={'ai':(160,74),'bantuan':(222,32),'pcds':(236,150)}
dots=[(60,44),(96,160),(186,196),(330,70),(380,170),(200,104),(300,24)]
edges=[((60,44),nodes['ai']),(nodes['ai'],nodes['bantuan']),(nodes['ai'],(200,104)),(nodes['bantuan'],(200,104)),((200,104),nodes['pcds']),(nodes['bantuan'],(300,24)),(nodes['bantuan'],(330,70)),((330,70),nodes['pcds']),(nodes['pcds'],(380,170)),(nodes['pcds'],(186,196)),((96,160),nodes['ai'])]
lines=''.join(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}"/>' for a,b in edges)
dotsv=''.join(f'<circle cx="{x}" cy="{y}" r="3.2"/>' for x,y in dots)
tiles=''.join(f'<g transform="translate({x} {y})"><rect class="brief-net-tile" x="-16" y="-16" width="32" height="32" rx="8"/>{net_icon(ic)}</g>'
              for (x,y),ic in [(nodes['ai'],'brain'),(nodes['bantuan'],'hand-heart'),(nodes['pcds'],'chart-line-up')])
NET=f'<svg class="brief-net" role="presentation" viewBox="0 0 420 230" aria-hidden="true"><g class="brief-net-lines" fill="none" stroke="currentColor" stroke-width="1.15" stroke-linecap="round">{lines}</g><g fill="currentColor">{dotsv}</g>{tiles}</svg>'

HEADER=open('../src/bantuan.html').read()
HEADER=re.search(r'<header class="bar">.*?</header>',HEADER,re.S).group(0)
HEADER=HEADER.replace('Bantuan.Sarawak.News','Sarawak.News').replace('>Home<','>Sites<')

HERO=f'''<header class="brief">{NET}
<h1>Independent Sarawak sites, in one place.</h1>
<p class="brief-deck">Each site links to its sources.</p>
</header>'''
FOOTER='''<footer class="site-footer hub-footer"><div class="site-footer-bottom"><p>Built by <a class="site-footer-link site-footer-credit-link" href="https://hafiy.my">hafiy.my</a>, an independent publication. Not affiliated with the Sarawak Government.</p></div></footer>'''
ARROW='<span class="hub-arrow" aria-hidden="true">→</span>'
OPT='<span class="hub-optional">Optional</span>'

def card_A(s,optional=False):
    meta = s.get('stats') or ''
    return f'''<article class="hubA-card{' is-optional' if optional else ''}">
<div class="hubA-top">{tile_icon(s['icon'])}<span class="hubA-tags">{OPT if optional else ''}<span class="hub-pill">{s['kind']}</span></span></div>
<h2 class="hubA-name">{s['name']}</h2>
{f'<p class="hub-meta">{meta}</p>' if meta else ''}
<p class="hubA-desc">{s['desc']}</p>
<p class="hubA-foot"><span class="hub-domain">{s['domain']}</span><a class="hub-visit" href="#">Visit {ARROW}</a></p>
</article>'''

def card_B(s,optional=False):
    th=f"thumbs/{s['key']}-light.png"; thd=f"thumbs/{s['key']}-{'light' if s['key']=='pcds' else 'dark'}.png"
    stats = f'<p class="hub-meta">{s["stats"]} · Updated {s["updated"]}</p>' if s.get('stats') else ''
    return f'''<article class="hubB-card{' is-optional' if optional else ''}">
<div class="hubB-head">{tile_icon(s['icon'])}<h2>{s['name']}</h2>{OPT if optional else ''}</div>
<div class="hubB-body">
<a class="hubB-thumb" href="#"><img class="only-light" src="{th}" alt=""><img class="only-dark" src="{thd}" alt=""></a>
<div class="hubB-text"><p class="hubB-quote">{s['headline']}</p><p class="hubB-desc">{s['desc']}</p>{stats}
<p class="hubB-foot"><a class="hub-visit-btn" href="#">Visit {s['domain']} {ARROW}</a></p></div>
</div></article>'''

def row_C(i,s,optional=False):
    meta = (' · '+s['stats']) if s.get('stats') else ''
    return f'''<a class="hubC-row{' is-optional' if optional else ''}" href="#">
<span class="hubC-rank">{i}</span>{tile_icon(s['icon'],22)}
<span class="hubC-main"><span class="hubC-name">{s['name']}{OPT if optional else ''}</span><span class="hubC-line">{s['headline']}</span><span class="hub-meta">{s['domain']}{meta}</span></span>
{ARROW}</a>'''

BODY={
'A': f'''<section class="hubA-grid" aria-label="Sites">{card_A(SITES[0])}{card_A(SITES[1])}{card_A(PCDS,True)}</section>''',
'B': f'''<section class="hubB-list" aria-label="Sites">{card_B(SITES[0])}{card_B(SITES[1])}
<div class="hubB-more"><span class="group-icon-tile hub-plus">{'<svg class="group-icon" viewBox="0 0 256 256" width="24" height="24" fill="currentColor">'+inner('plus').replace('opacity="0.2"','class="group-icon-fill" opacity="0.2"')+'</svg>'}</span><span><b>More sites coming.</b> Optional next: PCDS 2030 Project Tracker.</span></div></section>''',
'C': f'''<section class="hubC-list" aria-label="Sites"><p class="category-filter-title">Sites</p>{row_C(1,SITES[0])}{row_C(2,SITES[1])}{row_C(3,PCDS,True)}</section>''',
}
WIDTH={'A':'840px','B':'840px','C':'840px'}
for k,body in BODY.items():
    doc=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<script>document.documentElement.classList.add("js");if(window.matchMedia("(prefers-color-scheme: dark)").matches)document.documentElement.dataset.theme="dark";</script>
<link rel="stylesheet" href="style.css"><link rel="stylesheet" href="hub.css"><style>body{{max-width:{WIDTH[k]}}}</style></head>
<body class="hub hub-{k}">{HEADER}<main id="content">{HERO}{body}</main>{FOOTER}</body></html>'''
    open(f'hub-{k}.html','w').write(doc)
print('ok')
