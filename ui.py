"""Design system and reusable HTML components for GharDoc AI.

All colours, shadows and radii live in the CSS variables below (60-30-10 rule):
60% soft lavender-white background, 30% royal purple / violet, 10% cyan and pink accents.
"""
import base64
import html
import os

import streamlit as st

ROOT = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(ROOT, "assets")

FONTS = ("https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800"
         "&family=Noto+Naskh+Arabic:wght@400;500;600;700&family=Noto+Nastaliq+Urdu:wght@500;700&display=swap")
ICONS = "https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,400..600,0..1,0&display=block"

BASE_CSS = """
<style>
@import url('__FONTS__');
@import url('__ICONS__');
:root {
  --bg:#F8F7FF; --surface:#FFFFFF; --soft:#F1EDFF; --soft-2:#E7E0FF;
  --primary:#6338D8; --primary-2:#8B5CF6; --primary-deep:#3E1CA8;
  --accent:#20C4D8; --pink:#F472B6;
  --ink:#202039; --muted:#6C6A8A; --line:#E9E4FA;
  --ok:#12A150; --ok-bg:#E7F7EE; --warn:#D98A04; --warn-bg:#FFF5E1; --bad:#E5484D; --bad-bg:#FDECEC;
  --info-bg:#E5F8FB; --info:#0E8FA0;
  --grad:linear-gradient(135deg,#6338D8 0%,#8B5CF6 100%);
  --grad-accent:linear-gradient(90deg,#6338D8,#8B5CF6 55%,#20C4D8);
  --grad-hero:radial-gradient(120% 80% at 85% 0%,rgba(32,196,216,.42) 0%,transparent 45%),
              radial-gradient(90% 70% at 0% 100%,rgba(244,114,182,.38) 0%,transparent 50%),
              linear-gradient(165deg,#4A22C2 0%,#6338D8 48%,#8B5CF6 100%);
  --shadow-sm:0 1px 2px rgba(40,24,110,.04),0 4px 14px -6px rgba(40,24,110,.10);
  --shadow:0 2px 6px rgba(40,24,110,.05),0 18px 40px -22px rgba(40,24,110,.35);
  --shadow-pri:0 14px 30px -12px rgba(99,56,216,.60);
  --r-sm:12px; --r:18px; --r-lg:24px; --r-xl:30px;
  --font:'Plus Jakarta Sans',system-ui,-apple-system,'Segoe UI',sans-serif;
}
/* ---------- base ---------- */
.stApp { background:
   radial-gradient(700px 360px at 0% -10%, rgba(139,92,246,.10), transparent 60%),
   radial-gradient(600px 300px at 100% 0%, rgba(32,196,216,.08), transparent 60%), var(--bg); }
.stApp, .stApp p, .stApp li, .stApp label, .stApp button, .stApp input, .stApp textarea, .stApp h1, .stApp h2,
.stApp h3, .stApp h4, .stApp small, .stApp div[data-baseweb] { font-family:var(--font); color:var(--ink); }
span[data-testid="stIconMaterial"], .msr, [class*="material-symbols"] {
   font-family:'Material Symbols Rounded' !important; font-weight:normal; font-style:normal; line-height:1;
   letter-spacing:normal; text-transform:none; white-space:nowrap; direction:ltr; -webkit-font-smoothing:antialiased; }
.msr { font-size:1.25rem; display:inline-flex; vertical-align:middle; font-variation-settings:'FILL' 0,'wght' 500; }
.msr.fill { font-variation-settings:'FILL' 1,'wght' 500; }
header[data-testid="stHeader"] { background:transparent; height:0; }
[data-testid="stToolbar"], [data-testid="stDecoration"], footer, #MainMenu, [data-testid="stStatusWidget"] { display:none !important; }
.block-container, [data-testid="stMainBlockContainer"] { max-width:720px; padding:.9rem 1rem 7.5rem 1rem !important; }
[data-testid="stVerticalBlock"] { gap:.85rem; }
@media (min-width: 768px) { .block-container, [data-testid="stMainBlockContainer"] { padding-top:1.4rem !important; } }
.rise { animation:rise .5s cubic-bezier(.2,.8,.2,1) both; }
@keyframes rise { from { opacity:0; transform:translateY(12px); } to { opacity:1; transform:none; } }
@keyframes floaty { 0%,100% { transform:translateY(0); } 50% { transform:translateY(-7px); } }

/* ---------- top bar ---------- */
.st-key-topbar [data-testid="stHorizontalBlock"] { flex-wrap:nowrap !important; align-items:center; gap:.5rem; }
.st-key-topbar [data-testid="stColumn"] { min-width:0 !important; }
.st-key-topbar [data-testid="stColumn"]:last-child { flex:0 0 46px !important; width:46px !important; }
.gd-top { display:flex; align-items:center; gap:10px; }
.gd-mark { width:42px; height:42px; border-radius:11px; background:transparent; overflow:hidden;
   box-shadow:0 6px 16px -6px rgba(99,56,216,.55); flex:0 0 42px; }
.gd-mark img { width:100%; height:100%; object-fit:cover; }
.gd-top b { font-size:1.08rem; font-weight:800; letter-spacing:-.02em; color:var(--ink); }
.gd-top b span { background:var(--grad); -webkit-background-clip:text; background-clip:text; color:transparent; }
div[data-testid="stPopover"] > div > button, div[data-testid="stPopover"] button[kind] {
   width:44px; height:44px; min-height:44px; padding:0; border-radius:14px; border:1px solid var(--line);
   background:var(--surface); box-shadow:var(--shadow-sm); color:var(--primary); transition:all .15s ease; }
div[data-testid="stPopover"] button:hover { border-color:var(--primary-2); background:var(--soft); color:var(--primary); }
div[data-testid="stPopover"] button:active { transform:scale(.95); }
div[data-testid="stPopover"] button [data-testid="stMarkdownContainer"], div[data-testid="stPopover"] button div[aria-hidden="true"],
div[data-testid="stPopover"] button svg { display:none !important; }
div[data-testid="stPopover"] button > div { justify-content:center; }
div[data-testid="stPopover"] button span[data-testid="stIconMaterial"] { font-size:1.45rem; color:var(--primary); margin:0; }
div[data-testid="stPopoverBody"] { border-radius:20px; border:1px solid var(--line); box-shadow:var(--shadow); padding:.6rem; min-width:250px; }
div[data-testid="stPopoverBody"] [data-testid="stVerticalBlock"] { gap:.15rem; }
div[data-testid="stPopoverBody"] .stButton button { justify-content:flex-start; border-radius:12px; padding:.55rem .7rem;
   width:100%; color:var(--ink); font-weight:600; }
div[data-testid="stPopoverBody"] .stButton button:hover { background:var(--soft); color:var(--primary); }
div[data-testid="stPopoverBody"] .stButton button span[data-testid="stIconMaterial"] { color:var(--primary); }
.gd-menu-h { font-size:.72rem; font-weight:800; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); padding:.2rem .7rem .4rem; }

/* ---------- hero ---------- */
.gd-hero { position:relative; overflow:hidden; border-radius:var(--r-xl); background:var(--grad-hero);
   padding:26px 20px 0; text-align:center; box-shadow:var(--shadow-pri); isolation:isolate; }
.gd-hero::after { content:""; position:absolute; inset:0; border-radius:inherit; pointer-events:none;
   box-shadow:inset 0 1px 0 rgba(255,255,255,.25); }
.gd-brand { margin:0; font-size:2.35rem; line-height:1.1; font-weight:800; letter-spacing:-.035em; color:#FFFFFF !important; direction:ltr; }
.gd-brand span { background:linear-gradient(90deg,#8BF0FA,#FFD0EA); -webkit-background-clip:text; background-clip:text; color:transparent; }
.gd-tag { margin:.45rem 0 0; font-size:1.02rem; font-weight:600; color:rgba(255,255,255,.9) !important; letter-spacing:.005em; }
.gd-robot { display:block; width:min(74%,290px); margin:14px auto -10px; animation:floaty 4.2s ease-in-out infinite;
   filter:drop-shadow(0 22px 30px rgba(18,6,72,.45)); }
@media (min-width: 768px) {
  .gd-hero { display:flex; align-items:flex-end; text-align:left; padding:0 28px; min-height:300px; gap:10px; }
  .gd-hero-txt { flex:1; padding:0 0 92px; }
  .gd-brand { font-size:3rem; }
  .gd-robot { width:270px; margin:20px 0 -10px; }
}

/* ---------- cards ---------- */
.gd-card { background:var(--surface); border:1px solid var(--line); border-radius:var(--r-lg); padding:18px; box-shadow:var(--shadow-sm); }
.gd-head { display:flex; align-items:center; gap:12px; }
.gd-head h3 { margin:0; font-size:1.06rem; font-weight:800; letter-spacing:-.01em; line-height:1.3; }
.gd-head p { margin:2px 0 0; font-size:.84rem; color:var(--muted) !important; line-height:1.4; }
.gd-ic { width:42px; height:42px; flex:0 0 42px; border-radius:14px; display:flex; align-items:center; justify-content:center;
   background:var(--soft); color:var(--primary); }
.gd-ic .msr { font-size:1.4rem; color:var(--primary); }
.gd-ic.solid { background:var(--grad); box-shadow:var(--shadow-pri); }
.gd-ic.solid .msr { color:#FFFFFF; }
.gd-ic.red { background:var(--bad-bg); } .gd-ic.red .msr { color:var(--bad); }
.gd-ic.cyan { background:var(--info-bg); } .gd-ic.cyan .msr { color:var(--info); }
.gd-ic.pink { background:#FDEAF4; } .gd-ic.pink .msr { color:#D63C8A; }
.gd-ic.amber { background:var(--warn-bg); } .gd-ic.amber .msr { color:var(--warn); }
.gd-sec { display:flex; align-items:center; justify-content:space-between; margin:.6rem 2px -.2rem; }
.gd-sec h4 { margin:0; font-size:1rem; font-weight:800; letter-spacing:-.01em; }
.gd-page { padding:.2rem 2px .1rem; }
.gd-page h2 { margin:0; font-size:1.55rem; font-weight:800; letter-spacing:-.03em; line-height:1.2; }
.gd-page p { margin:.3rem 0 0; color:var(--muted) !important; font-size:.92rem; line-height:1.5; }

/* chips and badges */
.gd-chips { display:flex; flex-wrap:wrap; gap:6px; margin-top:12px; }
.gd-chip { display:inline-flex; align-items:center; gap:5px; padding:5px 10px; border-radius:999px; background:var(--soft);
   color:var(--primary-deep) !important; font-size:.76rem; font-weight:700; }
.gd-chip .msr { font-size:1rem; color:var(--primary); }
.gd-badge { white-space:nowrap; display:inline-flex; align-items:center; gap:5px; padding:4px 11px; border-radius:999px; font-size:.76rem; font-weight:800; }
.gd-badge .msr { font-size:.95rem; }
.gd-badge.green { background:var(--ok-bg); color:var(--ok) !important; } .gd-badge.green .msr { color:var(--ok); }
.gd-badge.yellow { background:var(--warn-bg); color:var(--warn) !important; } .gd-badge.yellow .msr { color:var(--warn); }
.gd-badge.red { background:var(--bad-bg); color:var(--bad) !important; } .gd-badge.red .msr { color:var(--bad); }
.gd-badge.blue { background:var(--soft); color:var(--primary) !important; } .gd-badge.blue .msr { color:var(--primary); }
.gd-badge.muted { background:#F2F1F7; color:var(--muted) !important; }

/* result */
.gd-result { position:relative; overflow:hidden; padding-top:22px; }
.gd-result::before { content:""; position:absolute; left:0; right:0; top:0; height:5px; background:var(--grad-accent); }
.gd-result.green::before { background:linear-gradient(90deg,#12A150,#20C4D8); }
.gd-result.yellow::before { background:linear-gradient(90deg,#F5B83D,#F472B6); }
.gd-result.red::before { background:linear-gradient(90deg,#E5484D,#F472B6); }
.gd-eyebrow { display:inline-flex; align-items:center; gap:6px; font-size:.74rem; font-weight:800; text-transform:uppercase;
   letter-spacing:.08em; color:var(--primary) !important; }
.gd-eyebrow .msr { font-size:1rem; color:var(--primary); }
.gd-res-top { display:flex; align-items:center; justify-content:space-between; gap:8px; flex-wrap:wrap; }
.gd-res-title { margin:.55rem 0 .2rem; font-size:1.45rem; font-weight:800; letter-spacing:-.03em; line-height:1.25; }
.gd-label { font-size:.78rem; font-weight:700; color:var(--muted) !important; margin:14px 0 6px; text-transform:uppercase; letter-spacing:.06em; }
.gd-text { margin:0; line-height:1.65; font-size:.95rem; }
.gd-meter { display:grid; grid-template-columns:repeat(3,1fr); gap:6px; }
.gd-seg { height:8px; border-radius:99px; background:#EEEBF7; }
.gd-seg.on.green { background:var(--ok); } .gd-seg.on.yellow { background:#F5B83D; } .gd-seg.on.red { background:var(--bad); }
.gd-seg.on { animation:grow .7s cubic-bezier(.2,1.3,.4,1) both; transform-origin:left; }
@keyframes grow { from { transform:scaleX(.1); } to { transform:scaleX(1); } }
.gd-meter-l { display:grid; grid-template-columns:repeat(3,1fr); gap:6px; margin-top:6px; font-size:.72rem; font-weight:700; color:var(--muted); }
.gd-meter-l span { text-align:center; } .gd-meter-l span.on { color:var(--ink); }

/* lists */
.gd-list { list-style:none; margin:12px 0 0 !important; padding:0 !important; display:flex; flex-direction:column; gap:10px; }
.gd-list li { margin:0 !important; padding:0 !important; display:flex; gap:10px; align-items:flex-start; line-height:1.55; font-size:.93rem; }
.gd-list li > .msr { font-size:1.15rem; color:var(--primary); margin-top:1px; }
.gd-list.q li > .msr { color:var(--info); }
.gd-list.red li > .msr { color:var(--bad); }
.gd-steps { counter-reset:s; }
.gd-steps li::before { counter-increment:s; content:counter(s); flex:0 0 26px; height:26px; border-radius:9px; background:var(--grad);
   color:#FFFFFF; font-size:.78rem; font-weight:800; display:flex; align-items:center; justify-content:center; margin-top:-1px; }
.gd-who { display:flex; align-items:center; gap:10px; margin-top:14px; padding:12px; border-radius:14px; background:var(--soft); }
.gd-who .msr { color:var(--primary); }
.gd-who small { display:block; color:var(--muted) !important; font-size:.74rem; font-weight:700; }
.gd-who b { font-size:.95rem; }

/* notes */
.gd-note { display:flex; gap:10px; align-items:flex-start; padding:12px 14px; border-radius:16px; font-size:.88rem; line-height:1.55; }
.gd-note .msr { font-size:1.2rem; margin-top:1px; }
.gd-note.info { background:var(--info-bg); } .gd-note.info, .gd-note.info .msr { color:#0B6E7B !important; }
.gd-note.warn { background:var(--warn-bg); } .gd-note.warn, .gd-note.warn .msr { color:#8A5A00 !important; }
.gd-note.danger { background:var(--bad-bg); } .gd-note.danger, .gd-note.danger .msr { color:#A8282D !important; }
.gd-note.ok { background:var(--ok-bg); } .gd-note.ok, .gd-note.ok .msr { color:#0D7A3D !important; }
.gd-note b { color:inherit !important; }
.gd-note ul { margin:4px 0 0; padding-inline-start:18px; } .gd-note li { color:inherit !important; }

/* cost */
.gd-cost-row { display:flex; justify-content:space-between; align-items:center; gap:12px; padding:12px 0; border-bottom:1px dashed var(--line); }
.gd-cost-row:last-child { border-bottom:0; padding-bottom:0; }
.gd-cost-row b { font-size:.92rem; font-weight:700; line-height:1.4; }
.gd-cost-row small { display:block; color:var(--muted) !important; font-size:.76rem; margin-top:2px; }
.gd-amt { text-align:end; white-space:nowrap; font-weight:800; color:var(--primary-deep) !important; font-size:.95rem; }
.gd-amt small { font-weight:600; }

/* rate list */
.gd-rate { display:flex; align-items:center; gap:12px; padding:11px 0; border-bottom:1px solid var(--line); }
.gd-rate:last-child { border-bottom:0; }
.gd-rate .id { flex:0 0 40px; height:28px; border-radius:9px; background:var(--soft); color:var(--primary) !important; font-size:.72rem;
   font-weight:800; display:flex; align-items:center; justify-content:center; }
.gd-rate .nm { flex:1; min-width:0; } .gd-rate .nm b { font-size:.9rem; font-weight:600; line-height:1.4; display:block; }
.gd-rate .nm small { color:var(--muted) !important; font-size:.75rem; }

/* tiles and rows (clickable via an invisible button overlay) */
[class*="st-key-tile_"], [class*="st-key-row_"] { position:relative; }
[class*="st-key-tile_"] [data-testid="stElementContainer"]:has(.stButton),
[class*="st-key-row_"] [data-testid="stElementContainer"]:has(.stButton) { position:absolute !important; inset:0; z-index:3; margin:0;
   width:100% !important; height:100% !important; }
[class*="st-key-tile_"] .stButton, [class*="st-key-row_"] .stButton,
[class*="st-key-tile_"] .stButton button, [class*="st-key-row_"] .stButton button { width:100% !important; height:100% !important; }
[class*="st-key-tile_"] .stButton button, [class*="st-key-row_"] .stButton button { opacity:0; cursor:pointer; border-radius:var(--r-lg); }
[class*="st-key-tile_"] .stButton button:focus-visible, [class*="st-key-row_"] .stButton button:focus-visible { opacity:1; background:transparent;
   outline:3px solid var(--accent); }
.gd-tile, .gd-row { transition:transform .18s ease, box-shadow .18s ease, border-color .18s ease; }
[class*="st-key-tile_"]:hover .gd-tile, [class*="st-key-row_"]:hover .gd-row { transform:translateY(-3px); box-shadow:var(--shadow); border-color:var(--soft-2); }
[class*="st-key-tile_"]:active .gd-tile, [class*="st-key-row_"]:active .gd-row { transform:scale(.97); }
.gd-tile { background:var(--surface); border:1px solid var(--line); border-radius:var(--r-lg); padding:16px 14px; box-shadow:var(--shadow-sm); min-height:132px; }
.gd-tile b { display:block; margin-top:12px; font-size:.95rem; font-weight:800; letter-spacing:-.01em; line-height:1.3; }
.gd-tile small { display:block; margin-top:3px; font-size:.78rem; color:var(--muted) !important; line-height:1.4; }
.gd-row { display:flex; align-items:center; gap:14px; background:var(--surface); border:1px solid var(--line); border-radius:var(--r);
   padding:14px; box-shadow:var(--shadow-sm); }
.gd-row > div { flex:1; min-width:0; } .gd-row b { display:block; font-weight:800; font-size:.96rem; }
.gd-row small { display:block; color:var(--muted) !important; font-size:.8rem; margin-top:2px; }
.gd-row .chev { color:#B7B2D3; }
.st-key-tilegrid [data-testid="stHorizontalBlock"] { flex-wrap:nowrap !important; gap:12px; }
.st-key-tilegrid [data-testid="stColumn"] { min-width:0 !important; flex:1 1 0 !important; width:auto !important; }

/* emergency numbers */
.gd-nums { display:grid; grid-template-columns:repeat(2,1fr); gap:10px; }
.gd-num { display:flex; align-items:center; gap:10px; padding:12px; border-radius:18px; text-decoration:none !important;
   background:linear-gradient(135deg,#E5484D,#D63C8A); box-shadow:0 12px 24px -12px rgba(229,72,77,.7); transition:transform .15s ease, filter .15s; }
.gd-num:hover { transform:translateY(-2px); filter:brightness(1.06); } .gd-num:active { transform:scale(.97); }
.gd-num .msr { color:#FFFFFF; font-size:1.3rem; background:rgba(255,255,255,.18); border-radius:10px; padding:6px; }
.gd-num b { display:block; color:#FFFFFF !important; font-size:1.15rem; font-weight:800; letter-spacing:.02em; }
.gd-num small { display:block; color:rgba(255,255,255,.88) !important; font-size:.72rem; font-weight:600; line-height:1.3; }
.gd-num.first { grid-column:1 / -1; }

/* scanning animation */
.gd-scan { position:relative; overflow:hidden; border-radius:var(--r-lg); padding:30px 18px; text-align:center;
   background:linear-gradient(135deg,#F1EDFF,#E9FBFD); border:1px solid var(--soft-2); }
.gd-scan .ln { position:absolute; left:0; right:0; height:3px; top:0; background:linear-gradient(90deg,transparent,#20C4D8,#8B5CF6,transparent);
   box-shadow:0 0 18px #20C4D8; animation:sweep 1.6s ease-in-out infinite; }
@keyframes sweep { 0% { top:0; } 50% { top:calc(100% - 3px); } 100% { top:0; } }
.gd-scan b { font-size:1.02rem; font-weight:800; } .gd-scan small { display:block; color:var(--muted) !important; margin-top:4px; }
.gd-dots { margin-top:12px; } .gd-dots span { display:inline-block; width:8px; height:8px; margin:0 3px; border-radius:50%;
   background:var(--primary); animation:blink 1s infinite both; }
.gd-dots span:nth-child(2) { animation-delay:.2s; background:var(--primary-2); } .gd-dots span:nth-child(3) { animation-delay:.4s; background:var(--accent); }
@keyframes blink { 0%,80%,100% { opacity:.25; transform:scale(.8); } 40% { opacity:1; transform:scale(1.2); } }

/* thumbnails */
.gd-thumbs { display:flex; gap:10px; flex-wrap:wrap; }
.gd-thumbs img { width:84px; height:84px; object-fit:cover; border-radius:16px; border:2px solid var(--surface); box-shadow:var(--shadow-sm); }
.gd-hist { display:flex; gap:12px; align-items:center; }
.gd-hist img { width:72px; height:72px; object-fit:cover; border-radius:16px; }

/* empty state */
.gd-empty { text-align:center; padding:34px 20px; }
.gd-empty .gd-ic { margin:0 auto 12px; width:58px; height:58px; border-radius:20px; }
.gd-empty .gd-ic .msr { font-size:1.8rem; }
.gd-empty b { display:block; font-size:1.02rem; font-weight:800; }
.gd-empty small { display:block; margin-top:4px; color:var(--muted) !important; line-height:1.5; }

/* ---------- streamlit widgets ---------- */
[data-testid="stElementContainer"]:has(> .stMarkdown style), [data-testid="stElementContainer"]:has(style:only-child) { display:none; }
[data-testid="stElementContainer"]:has(> .stButton button[kind="primary"]), .stButton:has(button[kind="primary"]),
[data-testid="stElementContainer"]:has(> .stDownloadButton) { width:100% !important; }
/* keyed cards */
.st-key-scancard, [class*="st-key-card_"] { background:var(--surface); border:1px solid var(--line); border-radius:var(--r-lg);
   padding:18px; box-shadow:var(--shadow-sm); }
[class*="st-key-card_"] [data-testid="stExpander"] details { box-shadow:none; background:var(--soft); border:0 !important; }
[class*="st-key-card_"] [data-testid="stExpander"] summary:hover { background:var(--soft-2); }
/* buttons */
.stDownloadButton, .stDownloadButton button { width:100%; }
.stButton button, .stDownloadButton button { border-radius:999px; font-weight:700; min-height:46px; transition:transform .15s ease, box-shadow .15s ease, background .15s ease, filter .15s; }
.stButton button[kind="primary"], .stFormSubmitButton button { width:100%; border:0; background:var(--grad); color:#FFFFFF;
   box-shadow:var(--shadow-pri); min-height:52px; font-size:1rem; }
.stButton button[kind="primary"] p, .stButton button[kind="primary"] span { color:#FFFFFF !important; }
.stButton button[kind="primary"]:hover { transform:translateY(-2px); filter:brightness(1.07); box-shadow:0 18px 34px -12px rgba(99,56,216,.7); }
.stButton button[kind="primary"]:active { transform:scale(.98); filter:brightness(.97); }
.stButton button[kind="primary"]:focus-visible { outline:3px solid var(--accent); outline-offset:2px; }
.stButton button[kind="secondary"], .stDownloadButton button { background:var(--surface); border:1px solid var(--soft-2); color:var(--primary); }
.stButton button[kind="secondary"] p, .stDownloadButton button p, .stButton button[kind="secondary"] span[data-testid="stIconMaterial"],
.stDownloadButton button span[data-testid="stIconMaterial"] { color:var(--primary) !important; }
.stButton button[kind="secondary"]:hover, .stDownloadButton button:hover { background:var(--soft); border-color:var(--primary-2); transform:translateY(-1px); }
.stButton button[kind="secondary"]:active, .stDownloadButton button:active { transform:scale(.98); }
.stButton button[kind="tertiary"] { min-height:38px; padding:.3rem .2rem; color:var(--primary); font-weight:700; }
.stButton button[kind="tertiary"] p, .stButton button[kind="tertiary"] span { color:var(--primary) !important; }
.stButton button[kind="tertiary"]:hover p { text-decoration:underline; text-underline-offset:3px; }
/* inputs */
.stTextInput input, .stNumberInput input, .stDateInput input, .stTextArea textarea { font-size:.95rem; }
div[data-baseweb="textarea"] textarea, div[data-baseweb="input"] input, div[data-baseweb="base-input"] { background:#FBFAFF !important; }
div[data-baseweb="input"], div[data-baseweb="textarea"], div[data-baseweb="select"] > div {
   border-radius:14px !important; border-color:var(--line) !important; background:#FBFAFF !important; }
div[data-baseweb="input"]:focus-within, div[data-baseweb="textarea"]:focus-within, div[data-baseweb="select"] > div:focus-within {
   border-color:var(--primary) !important; box-shadow:0 0 0 3px rgba(99,56,216,.14); }
.stApp label p { font-weight:600; font-size:.86rem; color:var(--ink); }
/* file uploader */
[data-testid="stFileUploaderDropzone"] { border:2px dashed #CFC3FA; border-radius:20px; background:linear-gradient(135deg,#FAF8FF,#F2FCFD);
   padding:22px 16px; transition:border-color .15s, background .15s; display:flex; flex-direction:column-reverse; align-items:center;
   justify-content:center; gap:12px; text-align:center; cursor:pointer; }
[data-testid="stFileUploaderDropzoneInstructions"] { margin:0 !important; }
[data-testid="stFileUploaderDropzone"] button [data-testid="stMarkdownContainer"] { display:none; }
[data-testid="stFileUploaderDropzone"]:hover { border-color:var(--primary); background:#F4F0FF; }
[data-testid="stFileUploaderDropzone"] button { border-radius:999px; background:var(--grad) !important; color:#FFFFFF !important; border:0; font-weight:700; }
[data-testid="stFileUploaderDropzone"] svg { color:var(--primary); }
[data-testid="stFileUploaderFile"], [data-testid="stFileUploader"] section + div, [data-testid="stFileChip"] { display:none !important; }
[data-testid="stFileChips"] { justify-content:center; display:flex; }
[data-testid="stFileUploaderDropzone"] > div:not([data-testid]) { width:100%; display:flex; justify-content:center; }
[data-testid="stFileUploader"], [data-testid="stElementContainer"]:has(> .stFileUploader),
[data-testid="stElementContainer"]:has(> [data-testid="stCameraInput"]) { width:100% !important; }
[data-testid="stFileUploaderDropzone"] button[kind="borderlessIcon"] { padding:.5rem 1.2rem; }
[data-testid="stCameraInput"] video, [data-testid="stCameraInput"] img { border-radius:18px; }
[data-testid="stCameraInput"] button { border-radius:999px; }
/* segmented radio (keyed containers starting with seg_) */
[class*="st-key-seg_"] div[role="radiogroup"] { display:grid !important; grid-auto-flow:column; grid-auto-columns:1fr; gap:4px;
   background:var(--soft); border-radius:14px; padding:4px; }
[class*="st-key-seg_"] label:is([data-baseweb="radio"],[data-testid="stRadioOption"]) { margin:0; justify-content:center; padding:8px 6px; border-radius:11px; cursor:pointer;
   transition:background .2s, box-shadow .2s; }
[class*="st-key-seg_"] label:is([data-baseweb="radio"],[data-testid="stRadioOption"]) > div:first-child:not([data-testid]),
[class*="st-key-seg_"] label[data-testid="stRadioOption"] > div > div:first-child:not([data-testid]) { display:none; }
[class*="st-key-seg_"] label:is([data-baseweb="radio"],[data-testid="stRadioOption"]) p { font-weight:700; font-size:.86rem; color:var(--muted); display:flex; align-items:center; gap:6px; }
[class*="st-key-seg_"] label:is([data-baseweb="radio"],[data-testid="stRadioOption"]):has(input:checked) { background:var(--surface); box-shadow:var(--shadow-sm); }
[class*="st-key-seg_"] label[data-testid="stRadioOption"] > div { justify-content:center; width:100%; }
[class*="st-key-seg_"] label:is([data-baseweb="radio"],[data-testid="stRadioOption"]):has(input:checked) p { color:var(--primary); }
[class*="st-key-seg_"] label:is([data-baseweb="radio"],[data-testid="stRadioOption"]) span[data-testid="stIconMaterial"] { font-size:1.15rem; }
/* language options */
.st-key-langpick div[role="radiogroup"] { display:flex; flex-direction:column; gap:8px; }
.st-key-langpick label:is([data-baseweb="radio"],[data-testid="stRadioOption"]) { margin:0; padding:14px 16px; border-radius:16px; border:1.5px solid var(--line);
   background:var(--surface); transition:all .15s; cursor:pointer; }
.st-key-langpick label:is([data-baseweb="radio"],[data-testid="stRadioOption"]):hover { border-color:var(--soft-2); background:#FCFBFF; }
.st-key-langpick label:is([data-baseweb="radio"],[data-testid="stRadioOption"]):has(input:checked) { border-color:var(--primary); background:var(--soft); box-shadow:0 0 0 3px rgba(99,56,216,.10); }
.st-key-langpick [role="radiogroup"], .st-key-langpick label[data-testid="stRadioOption"] { width:100%; }
.st-key-langpick label:is([data-baseweb="radio"],[data-testid="stRadioOption"]) p { font-weight:700; font-size:.98rem; }
/* expanders */
[data-testid="stExpander"] details { border:1px solid var(--line) !important; border-radius:var(--r) !important; background:var(--surface);
   box-shadow:var(--shadow-sm); overflow:hidden; }
[data-testid="stExpander"] summary { padding:14px 16px; }
[data-testid="stExpander"] summary:hover { background:#FCFBFF; }
[data-testid="stExpander"] summary p { font-weight:700; font-size:.94rem; }
[data-testid="stExpander"] summary span[data-testid="stIconMaterial"] { color:var(--primary); }
/* text inputs (current Streamlit DOM) */
[data-testid="stTextInputRootElement"], [data-testid="stTextAreaRootElement"], [data-testid="stNumberInputContainer"],
[data-testid="stDateInputField"], [data-testid="stSelectbox"] [role="combobox"] {
   border-radius:14px !important; border:1px solid var(--line) !important; background:#FBFAFF !important; overflow:hidden; }
[data-testid="stTextInputRootElement"]:focus-within, [data-testid="stTextAreaRootElement"]:focus-within,
[data-testid="stNumberInputContainer"]:focus-within { border-color:var(--primary) !important; box-shadow:0 0 0 3px rgba(99,56,216,.14); }
[data-testid="stTextInputRootElement"] input, [data-testid="stTextAreaRootElement"] textarea, [data-testid="stNumberInputContainer"] input {
   background:transparent !important; border:0 !important; }
.st-key-langpick [data-testid="stElementContainer"], .st-key-langpick .stRadio { width:100% !important; }
/* tabs (current Streamlit DOM) */
.stTabs [role="tablist"] { gap:4px; background:var(--soft); padding:4px; border-radius:14px; border:0 !important; }
.stTabs [data-testid="stTab"] { flex:1; display:flex; justify-content:center; align-items:center; height:40px; border-radius:11px;
   padding:0 6px; cursor:pointer; transition:background .2s, box-shadow .2s; }
.stTabs [data-testid="stTab"] p { font-weight:700; font-size:.86rem; color:var(--muted); margin:0; }
.stTabs [data-testid="stTab"][aria-selected="true"] { background:var(--surface); box-shadow:var(--shadow-sm); }
.stTabs [data-testid="stTab"][aria-selected="true"] p { color:var(--primary); }
.stTabs .react-aria-SelectionIndicator { display:none !important; }
/* tabs */
.stTabs [data-baseweb="tab-list"] { gap:6px; background:var(--soft); padding:4px; border-radius:14px; }
.stTabs [data-baseweb="tab"] { flex:1; justify-content:center; height:40px; border-radius:11px; padding:0 8px; }
.stTabs [data-baseweb="tab"] p { font-weight:700; font-size:.86rem; color:var(--muted); }
.stTabs [aria-selected="true"] { background:var(--surface) !important; box-shadow:var(--shadow-sm); }
.stTabs [aria-selected="true"] p { color:var(--primary); }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display:none; }
/* checkboxes and progress */
[data-testid="stElementContainer"]:has(> .stCheckbox), .stCheckbox { width:100% !important; }
.stCheckbox { background:var(--surface); border:1px solid var(--line); border-radius:14px; padding:10px 12px; }
.stCheckbox label p { font-weight:500 !important; font-size:.9rem !important; line-height:1.5; }
.stCheckbox:has(input:checked) { background:var(--soft); border-color:var(--soft-2); }
.stCheckbox:has(input:checked) label p { color:var(--muted) !important; text-decoration:line-through; }
.stProgress > div > div > div { background:#E9E4FA; border-radius:99px; height:10px; }
.stProgress > div > div > div > div { background:var(--grad-accent) !important; border-radius:99px; }
/* alerts */
[data-testid="stAlert"] { border-radius:16px; }
[data-testid="stCaptionContainer"] p { color:var(--muted) !important; }

/* ---------- bottom navigation ---------- */
.st-key-bottomnav { position:fixed !important; left:0; right:0; bottom:0; z-index:999; background:rgba(255,255,255,.94);
   backdrop-filter:saturate(1.6) blur(18px); -webkit-backdrop-filter:saturate(1.6) blur(18px); border-top:1px solid var(--line);
   box-shadow:0 -10px 30px -18px rgba(40,24,110,.35); padding:4px 6px calc(2px + env(safe-area-inset-bottom)) !important; }
.st-key-bottomnav [data-testid="stHorizontalBlock"] { position:relative; flex-wrap:nowrap !important; gap:0 !important; max-width:640px;
   margin:0 auto; }
.st-key-bottomnav [data-testid="stColumn"] { min-width:0 !important; flex:1 1 0 !important; width:20% !important; }
.st-key-bottomnav [data-testid="stHorizontalBlock"]::after { content:""; position:absolute; bottom:0; width:20%; height:3px;
   background:linear-gradient(90deg,var(--primary),var(--primary-2)) center / 46% 100% no-repeat; border-radius:3px;
   transition:transform .38s cubic-bezier(.3,1.25,.4,1); pointer-events:none; }
.st-key-bottomnav .stButton button { width:100%; min-height:58px; border:0 !important; background:transparent !important;
   box-shadow:none !important; border-radius:14px; padding:6px 2px 8px; color:var(--muted); }
.st-key-bottomnav [data-testid="stElementContainer"], .st-key-bottomnav .stButton { width:100% !important; }
.st-key-bottomnav [data-testid="stVerticalBlock"] { gap:0; }
.st-key-bottomnav .stButton button > div, .st-key-bottomnav .stButton button span[data-has-shortcut] { display:flex !important;
   flex-direction:column; align-items:center; justify-content:center; gap:3px; }
.st-key-bottomnav .stButton button span[data-testid="stIconMaterial"] { font-size:1.45rem; color:#8E8AAE; margin:0 !important;
   padding:3px 14px; border-radius:99px; transition:background .25s, color .25s; }
.st-key-bottomnav .stButton button p { font-size:.7rem !important; font-weight:700; color:#8E8AAE !important; margin:0; white-space:nowrap;
   transition:color .25s; }
.st-key-bottomnav .stButton button[kind] span[data-testid="stIconMaterial"] { color:#8E8AAE !important; }
.st-key-bottomnav .stButton button[kind] p { color:#8E8AAE !important; }
.st-key-bottomnav .stButton button:hover span[data-testid="stIconMaterial"] { background:#F4F1FF; }
.st-key-bottomnav .stButton button:active { transform:scale(.94); }
.st-key-bottomnav .stButton button:focus-visible { outline:2px solid var(--accent); }
</style>
"""

RTL_CSS = """
<style>
.block-container, [data-testid="stMainBlockContainer"], div[data-testid="stPopoverBody"], .st-key-bottomnav { direction:rtl; }
.stApp, .stApp p, .stApp li, .stApp label, .stApp button, .stApp input, .stApp textarea, .stApp small, .stApp b,
.stApp div[data-baseweb] { font-family:'Plus Jakarta Sans','Noto Naskh Arabic',sans-serif; }
.gd-page h2, .gd-head h3, .gd-res-title, .gd-tag, .gd-sec h4, .gd-tile b, .gd-row b, .gd-empty b {
   font-family:'Plus Jakarta Sans','Noto Nastaliq Urdu','Noto Naskh Arabic',serif !important; line-height:1.9; letter-spacing:0; }
.gd-tag { font-size:1.08rem; }
.gd-eyebrow, .gd-label, .gd-menu-h { letter-spacing:0; text-transform:none; }
.gd-list li, .gd-text, .gd-note { line-height:1.85; }
.gd-seg.on { transform-origin:right; }
.st-key-bottomnav [data-testid="stHorizontalBlock"]::after { right:0; }
div[data-testid="stPopoverBody"] .stButton button { justify-content:flex-start; }
.gd-brand, .gd-top b { font-family:'Plus Jakarta Sans',sans-serif !important; }
.gd-amt, .gd-num b { direction:ltr; unicode-bidi:embed; }
@media (min-width: 768px) { .gd-hero { text-align:right; } }
</style>
"""


def esc(x):
    return html.escape(str(x))


def icon(name, cls=""):
    return '<span class="msr %s">%s</span>' % (cls, esc(name))


@st.cache_data(show_spinner=False)
def asset_uri(name):
    """Return an asset as a base64 data URI so it can be used inside custom HTML."""
    ext = name.rsplit(".", 1)[-1]
    with open(os.path.join(ASSETS, name), "rb") as f:
        return "data:image/%s;base64,%s" % (ext, base64.b64encode(f.read()).decode())


def bytes_uri(b, mime="image/jpeg"):
    return "data:%s;base64,%s" % (mime, base64.b64encode(b).decode())


def render(markup):
    """Render trusted component markup (all user/AI text is escaped before it gets here)."""
    st.html(markup)


def inject_css(rtl, nav_index, uploader_title, uploader_hint, browse):
    """Inject the design system plus the few rules that depend on language and the active tab."""
    st.markdown(BASE_CSS.replace("__FONTS__", FONTS).replace("__ICONS__", ICONS), unsafe_allow_html=True)
    if rtl:
        st.markdown(RTL_CSS, unsafe_allow_html=True)
    shift = (-1 if rtl else 1) * nav_index * 100
    dynamic = """
<style>
.st-key-bottomnav [data-testid="stHorizontalBlock"]::after { transform:translateX(%d%%); opacity:%d; }
.st-key-bottomnav .st-key-nav_%s .stButton button[kind] span[data-testid="stIconMaterial"] { background:var(--soft) !important; color:var(--primary) !important;
   font-variation-settings:'FILL' 1; }
.st-key-bottomnav .st-key-nav_%s .stButton button[kind] p { color:var(--primary) !important; font-weight:800 !important; }
[data-testid="stFileUploaderDropzoneInstructions"] > div > * { display:none; }
[data-testid="stFileUploaderDropzoneInstructions"] > div::before { content:"%s"; display:block; font-weight:800; font-size:.98rem; color:var(--ink); }
[data-testid="stFileUploaderDropzoneInstructions"] > div::after { content:"%s"; display:block; margin-top:2px; font-size:.78rem; color:var(--muted); }
[data-testid="stFileUploaderDropzone"] button span[data-has-shortcut]::after { content:"%s"; font-size:.9rem; font-weight:700; }
</style>""" % (shift, 1 if nav_index >= 0 else 0, NAV_KEYS_SAFE.get(nav_index, "none"), NAV_KEYS_SAFE.get(nav_index, "none"),
               _css_str(uploader_title), _css_str(uploader_hint), _css_str(browse))
    st.markdown(dynamic, unsafe_allow_html=True)


NAV_KEYS_SAFE = {0: "home", 1: "history", 2: "rates", 3: "safety", 4: "more"}


def _css_str(s):
    return str(s).replace("\\", "\\\\").replace('"', '\\"')


# ------------------------------------------------------------------ components
def top_brand():
    return ('<div class="gd-top"><div class="gd-mark"><img src="%s" alt=""></div><b>GharDoc <span>AI</span></b></div>'
            % asset_uri("logo.png"))


def hero(tagline, alt):
    return ('<section class="gd-hero rise"><div class="gd-hero-txt"><h1 class="gd-brand">GharDoc <span>AI</span></h1>'
            '<p class="gd-tag">%s</p></div><img class="gd-robot" src="%s" alt="%s"></section>'
            % (esc(tagline), asset_uri("robot.webp"), esc(alt)))


def page_header(title, sub=""):
    p = "<p>%s</p>" % esc(sub) if sub else ""
    return '<div class="gd-page rise"><h2>%s</h2>%s</div>' % (esc(title), p)


def head(ic, title, sub="", tone=""):
    p = "<p>%s</p>" % esc(sub) if sub else ""
    return ('<div class="gd-head"><div class="gd-ic %s">%s</div><div><h3>%s</h3>%s</div></div>'
            % (tone, icon(ic), esc(title), p))


def section(title):
    return '<div class="gd-sec"><h4>%s</h4></div>' % esc(title)


def chips(items):
    return '<div class="gd-chips">%s</div>' % "".join('<span class="gd-chip">%s%s</span>' % (icon(i), esc(lbl)) for i, lbl in items)


def badge(level, text, ic=""):
    return '<span class="gd-badge %s">%s%s</span>' % (level, icon(ic) if ic else "", esc(text))


def meter(level, levels, labels):
    segs = "".join('<div class="gd-seg %s%s"></div>' % (lv, " on" if lv == level else "") for lv in levels)
    labs = "".join('<span class="%s">%s</span>' % ("on" if lv == level else "", esc(lb)) for lv, lb in zip(levels, labels))
    return '<div class="gd-meter">%s</div><div class="gd-meter-l">%s</div>' % (segs, labs)


def bullet_list(items, kind="bullet", ic="check_circle"):
    cls = {"bullet": "", "steps": "gd-steps", "q": "q", "red": "red"}.get(kind, "")
    if kind == "steps":
        lis = "".join("<li><span>%s</span></li>" % esc(i) for i in items)
    else:
        lis = "".join("<li>%s<span>%s</span></li>" % (icon(ic), esc(i)) for i in items)
    return '<ul class="gd-list %s">%s</ul>' % (cls, lis)


def card(inner, cls=""):
    return '<div class="gd-card rise %s">%s</div>' % (cls, inner)


def note(text, tone="info", ic="info", title=""):
    t = "<b>%s</b> " % esc(title) if title else ""
    return '<div class="gd-note %s rise">%s<div>%s%s</div></div>' % (tone, icon(ic), t, esc(text))


def note_list(items, tone="warn", ic="warning", title=""):
    t = "<b>%s</b>" % esc(title) if title else ""
    lis = "".join("<li>%s</li>" % esc(i) for i in items)
    return '<div class="gd-note %s rise">%s<div>%s<ul>%s</ul></div></div>' % (tone, icon(ic), t, lis)


def scanbox(title, sub):
    return ('<div class="gd-scan"><div class="ln"></div><b>%s</b><small>%s</small>'
            '<div class="gd-dots"><span></span><span></span><span></span></div></div>' % (esc(title), esc(sub)))


def thumbs(images):
    return '<div class="gd-thumbs">%s</div>' % "".join('<img src="%s" alt="">' % bytes_uri(b) for b in images)


def tile(ic, title, sub, tone=""):
    return ('<div class="gd-tile"><div class="gd-ic %s">%s</div><b>%s</b><small>%s</small></div>'
            % (tone, icon(ic), esc(title), esc(sub)))


def row(ic, title, sub, rtl=False, tone=""):
    chev = "chevron_left" if rtl else "chevron_right"
    return ('<div class="gd-row"><div class="gd-ic %s" style="flex:0 0 42px">%s</div><div><b>%s</b><small>%s</small></div>%s</div>'
            % (tone, icon(ic), esc(title), esc(sub), icon(chev, "chev")))


def empty(ic, title, sub):
    return card('<div class="gd-empty"><div class="gd-ic">%s</div><b>%s</b><small>%s</small></div>' % (icon(ic), esc(title), esc(sub)))
