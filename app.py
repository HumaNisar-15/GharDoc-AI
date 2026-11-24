"""GharDoc AI - Scan, Diagnose, and Fix!

Run locally:  streamlit run app.py
The Gemini key is read from st.secrets / environment (GEMINI_API_KEY) and never reaches the browser.
"""
import hashlib
import io
import os
from datetime import date, datetime

import streamlit as st
from PIL import Image

import ai_engine
import config
import content
import pricing
import risk_rules
import ui
from i18n import is_rtl, pick, t

ROOT = os.path.dirname(os.path.abspath(__file__))
st.set_page_config(page_title="GharDoc AI - Scan, Diagnose, and Fix!",
                   page_icon=Image.open(os.path.join(ROOT, "assets", "logo.png")),
                   layout="centered", initial_sidebar_state="collapsed")

ss = st.session_state
ss.setdefault("lang", config.DEFAULT_LANG)
ss.setdefault("page", "home")
ss.setdefault("prev", "home")
ss.setdefault("history", [])
LANG = ss["lang"]
RTL = is_rtl(LANG)
IMG_TYPES = ["jpg", "jpeg", "png", "webp"]

# Bottom navigation tabs and the material icon used for each.
NAV = [("home", "home"), ("history", "history"), ("rates", "payments"), ("safety", "health_and_safety"), ("more", "apps")]
NAV_KEYS = [k for k, _ in NAV]
# Secondary screens: (icon, title key, description key, icon tone). Their bottom-nav parent is in PARENT.
TOOLS = {
    "quote": ("request_quote", "tool_quote", "tool_quote_d", ""),
    "tracker": ("straighten", "tool_track", "tool_track_d", "cyan"),
    "materials": ("inventory_2", "tool_mat", "tool_mat_d", "pink"),
    "seasonal": ("partly_cloudy_day", "tool_season", "tool_season_d", "amber"),
    "settings": ("settings", "tool_settings", "tool_settings_d", ""),
}
PARENT = {"quote": "more", "tracker": "more", "seasonal": "more", "settings": "more", "materials": "rates"}
MENU = [("home", "home", "nav_home"), ("history", "history", "nav_history"), ("rates", "payments", "tool_rates"),
        ("materials", "inventory_2", "tool_mat"), ("safety", "health_and_safety", "tool_safety"),
        ("quote", "request_quote", "tool_quote"), ("tracker", "straighten", "tool_track"),
        ("seasonal", "partly_cloudy_day", "tool_season"), ("settings", "settings", "tool_settings")]


# ------------------------------------------------------------------ navigation helpers
def go(page):
    """Button callback: switch screen and remember where we came from (for the back button)."""
    if page == "materials":
        ss["rates_tab"] = "materials"
        page = "rates"
    elif page == "rates":
        ss["rates_tab"] = "rates"
    if page != ss["page"]:
        ss["prev"] = ss["page"]
    ss["page"] = page


def back_button():
    target = PARENT.get(ss["page"], "home")
    st.button(t("back"), key="back_" + ss["page"], type="tertiary", on_click=go, args=(target,),
              icon=":material/arrow_forward:" if RTL else ":material/arrow_back:")


def nav_index():
    page = PARENT.get(ss["page"], ss["page"])
    return NAV_KEYS.index(page) if page in NAV_KEYS else 0


@st.cache_data
def rates():
    return pricing.load_rates()


# ------------------------------------------------------------------ shared widgets
def photo_input(key, many=True):
    """Gallery / camera picker. Photos are kept in session state so they survive screen changes."""
    store, ver = key + "_store", key + "_v"
    ss.setdefault(store, [])
    ss.setdefault(ver, 0)
    cap = config.MAX_SCAN_PHOTOS if many else 1
    labels = {"gallery": ":material/photo_library: " + t("gallery"), "camera": ":material/photo_camera: " + t("camera")}
    with st.container(key="seg_" + key):
        src = st.radio(t("how_add"), ["gallery", "camera"], horizontal=True, key=key + "_src", label_visibility="collapsed",
                       format_func=labels.get)
    new = []
    if src == "gallery":
        fs = st.file_uploader(t("pick_photos"), type=IMG_TYPES, accept_multiple_files=many,
                              key="%s_up%d" % (key, ss[ver]), label_visibility="collapsed")
        new = list(fs or []) if many else ([fs] if fs else [])
    else:
        f = st.camera_input(t("take_photo"), key="%s_cam%d" % (key, ss[ver]), label_visibility="collapsed")
        new = [f] if f else []
    for f in new:
        b = f.getvalue()
        h = hashlib.md5(b).hexdigest()
        if any(h == x[0] for x in ss[store]):
            continue
        if many and len(ss[store]) >= cap:
            continue
        try:
            thumb = ai_engine.make_thumb(b, 200)
        except Exception:  # noqa: BLE001 - unreadable image file
            st.warning(t("err_parse"))
            continue
        ss[store] = (ss[store] + [(h, b, thumb)]) if many else [(h, b, thumb)]
    photos = ss[store]
    if photos:
        ui.render(ui.thumbs([x[2] for x in photos]))
        c1, c2 = st.columns([3, 2], vertical_alignment="center")
        if many:
            c1.caption(t("photos_count") % (len(photos), cap))
        if c2.button(t("clear_photos"), key=key + "_clr", type="tertiary", icon=":material/delete:"):
            ss[store] = []
            ss[ver] += 1
            st.rerun()
    elif many:
        st.caption(t("photo_hint"))
    return [x[1] for x in photos]


def show_ai_error(e):
    ui.render(ui.note(t("err_" + e.code), "danger", "cloud_off", t("err_title")))


def disclaimer():
    ui.render(ui.note(t("disc_text"), "warn", "gavel", t("disc_title")))


def tool_tile(page, col=None):
    ic, title, sub, tone = TOOLS[page]
    target = col or st
    with target.container(key="tile_" + page):
        ui.render(ui.tile(ic, t(title), t(sub), tone))
        st.button(t(title), key="open_" + page, on_click=go, args=(page,))


def tool_row(page):
    ic, title, sub, tone = TOOLS[page]
    with st.container(key="row_" + page):
        ui.render(ui.row(ic, t(title), t(sub), RTL, tone))
        st.button(t(title), key="openrow_" + page, on_click=go, args=(page,))


# ------------------------------------------------------------------ diagnosis result
def cost_block(d, qty):
    df = rates()
    priced = pricing.estimate(d["work_ids"], df, qty)
    waiting = pricing.pending(d["work_ids"], df)
    rows = []
    for e in priced:
        total = ""
        if e["total_min"] is not None:
            total = "<small>%s: Rs %s – %s</small>" % (ui.esc(t("total")), "{:,}".format(int(e["total_min"])),
                                                       "{:,}".format(int(e["total_max"])))
        rows.append('<div class="gd-cost-row"><div><b>%s</b><small>%s</small></div><div class="gd-amt">Rs %s – %s%s</div></div>'
                    % (ui.esc(e["kaam"]), ui.esc(e["unit"]), "{:,}".format(int(e["min"])), "{:,}".format(int(e["max"])), total))
    for w in waiting:
        rows.append('<div class="gd-cost-row"><div><b>%s</b><small>%s</small></div><div>%s</div></div>'
                    % (ui.esc(w["kaam"]), ui.esc(w["unit"]), ui.badge("muted", t("price_pending"), "schedule")))
    body = "".join(rows) if rows else '<p class="gd-text" style="margin-top:10px">%s</p>' % ui.esc(t("no_price"))
    extra = ui.note(t("pending_note"), "info", "info") if waiting and not priced else ""
    ui.render(ui.card(ui.head("payments", t("est_cost"), "", "") + '<div style="margin-top:6px">%s</div>' % body))
    if extra:
        ui.render(extra)


def report_text(s, ts):
    d, level = s["d"], s["level"]
    lines = ["GharDoc AI - %s" % ts, "%s: %s" % (t("issue_label"), t("iss_" + d["issue_type"])),
             "%s: %s" % (t("severity"), t("lv_" + level)), "", d["reason"], ""]
    for title, items in ((t("likely_causes"), d["probable_causes"]), (t("rec_fixes"), d["recommended_fixes"]),
                         (t("ask_worker"), d["questions"])):
        if items:
            lines.append(title + ":")
            lines += ["- " + i for i in items]
            lines.append("")
    lines.append("%s: %s" % (t("who_to_call"), t("w_" + d["worker_type"])))
    df = rates()
    costs = pricing.estimate(d["work_ids"], df, s["qty"])
    waiting = pricing.pending(d["work_ids"], df)
    if costs or waiting:
        lines.append(t("est_cost") + ":")
        lines += ["- %s: Rs %d - %d (%s)" % (e["kaam"], e["min"], e["max"], e["unit"]) for e in costs]
        lines += ["- %s: %s" % (w["kaam"], t("price_pending")) for w in waiting]
    lines += ["", "%s %s" % (t("disc_title"), t("disc_text"))]
    return "\n".join(lines)


def show_result(s, ts, key):
    d, level = s["d"], s["level"]
    if not d["is_wall_photo"]:
        ui.render(ui.note(t("not_wall"), "warn", "image_not_supported"))
        return
    lvl_icon = {"green": "verified", "yellow": "error", "red": "dangerous"}[level]
    top = ('<div class="gd-res-top"><span class="gd-eyebrow">%s%s</span>%s</div>'
           % (ui.icon("auto_awesome"), ui.esc(t("res_title")), ui.badge(level, t("lv_" + level), lvl_icon)))
    body = '<h3 class="gd-res-title">%s</h3>' % ui.esc(t("iss_" + d["issue_type"]))
    body += '<div class="gd-label">%s</div>' % ui.esc(t("severity"))
    body += ui.meter(level, risk_rules.LEVELS, [t("lvs_" + x) for x in risk_rules.LEVELS])
    if d["reason"]:
        body += '<div class="gd-label">%s</div><p class="gd-text">%s</p>' % (ui.esc(t("description")), ui.esc(d["reason"]))
    ui.render(ui.card(top + body, "gd-result " + level))
    if s["reasons"]:
        tone = {"green": "ok", "yellow": "warn", "red": "danger"}[level]
        ui.render(ui.note_list([t(r) for r in s["reasons"]], tone, "shield", t("why_level")))
    if s["need_more"]:
        ui.render(ui.note(t("more_photos"), "info", "add_a_photo"))
    if d["probable_causes"]:
        ui.render(ui.card(ui.head("troubleshoot", t("likely_causes"), "", "cyan") + ui.bullet_list(d["probable_causes"], ic="arrow_right")))
    diy = d["diy_ok"] and level == "green"
    fix = ui.head("construction", t("rec_fixes"))
    fix += '<div style="margin-top:10px">%s</div>' % ui.badge("green" if diy else "yellow", t("diy_yes") if diy else t("diy_no"),
                                                              "handyman" if diy else "engineering")
    if d["recommended_fixes"]:
        fix += ui.bullet_list(d["recommended_fixes"], "steps")
    fix += ('<div class="gd-who">%s<div><small>%s</small><b>%s</b></div></div>'
            % (ui.icon("person_search"), ui.esc(t("who_to_call")), ui.esc(t("w_" + d["worker_type"]))))
    ui.render(ui.card(fix))
    cost_block(d, s["qty"])
    if d["questions"]:
        ui.render(ui.card(ui.head("forum", t("ask_worker"), "", "pink") + ui.bullet_list(d["questions"], "q", "help")))
    disclaimer()
    st.download_button(t("download"), report_text(s, ts), file_name="ghardoc_report.txt", key="dl_" + key,
                       icon=":material/download:")
    st.caption("%s: %s" % (t("model_used"), s["model"]))


# ------------------------------------------------------------------ pages
def page_home():
    ui.render(ui.hero(t("tagline"), t("robot_alt")))
    with st.container(key="scancard"):
        ui.render(ui.head("document_scanner", t("scan_title"), t("scan_sub"), "solid"))
        imgs = photo_input("scan", many=True)
        if "note" not in ss:
            ss["note"] = ss.get("note_val", "")
        if "qty_in" not in ss:
            ss["qty_in"] = int(ss.get("qty_val", 0))
        note = st.text_area(t("tell_more"), key="note", placeholder=t("tell_more_ph"), height=90)
        ss["note_val"] = note
        with st.expander(t("area_exp"), icon=":material/square_foot:"):
            qty = st.number_input(t("sq_ft"), min_value=0, step=10, key="qty_in")
            ss["qty_val"] = qty
        clicked = st.button(t("diagnose_btn"), type="primary", key="go_scan", icon=":material/auto_awesome:")
        slot = st.empty()
    if clicked:
        if not imgs:
            ui.render(ui.note(t("add_one_photo"), "warn", "add_photo_alternate"))
        elif not ai_engine.is_configured():
            show_ai_error(ai_engine.AIUnavailable("no_key"))
        else:
            try:
                with slot.container():
                    ui.render(ui.scanbox(t("scanning"), t("scanning_sub")))
                data, model = ai_engine.diagnose([ai_engine.prepare_image(io.BytesIO(b)) for b in imgs], note, rates(), LANG)
                level, reasons, need_more = risk_rules.apply_rules(data)
                s = {"d": data, "level": level, "reasons": reasons, "need_more": need_more, "qty": qty, "model": model}
                ts = datetime.now().strftime("%d %b %Y, %I:%M %p")
                ss["scan"] = (s, ts)
                if data["is_wall_photo"]:
                    ss["history"].insert(0, {"ts": ts, "thumb": ai_engine.make_thumb(imgs[0]), "scan": s})
            except ai_engine.AIUnavailable as e:
                show_ai_error(e)
            except Exception as e:  # noqa: BLE001
                ui.render(ui.note("%s: %s" % (t("err_generic"), str(e)[:200]), "danger", "error"))
            finally:
                slot.empty()
    if ss.get("scan"):
        s, ts = ss["scan"]
        show_result(s, ts, "home")
    ui.render(ui.section(t("quick_tools")))
    with st.container(key="tilegrid"):
        for pair in (("quote", "tracker"), ("materials", "seasonal")):
            cols = st.columns(2)
            for col, page in zip(cols, pair):
                with col:
                    tool_tile(page)


def page_history():
    ui.render(ui.page_header(t("hist_title"), t("hist_note")))
    hs = ss["history"]
    if not hs:
        ui.render(ui.empty("history", t("hist_empty"), t("hist_note")))
        st.button(t("start_scan"), type="primary", key="hist_start", on_click=go, args=("home",), icon=":material/document_scanner:")
        return
    for i, h in enumerate(hs):
        s = h["scan"]
        d, level = s["d"], s["level"]
        summary = ('<div class="gd-hist"><img src="%s" alt=""><div><b>%s</b><div style="margin:6px 0 4px">%s</div>'
                   '<small style="color:var(--muted)">%s</small></div></div>'
                   % (ui.bytes_uri(h["thumb"]), ui.esc(t("iss_" + d["issue_type"])), ui.badge(level, t("lv_" + level)), ui.esc(h["ts"])))
        with st.container(key="card_h%d" % i):
            ui.render(summary)
            with st.expander(t("view_details"), icon=":material/description:"):
                show_result(s, h["ts"], "h%d" % i)
    if st.button(t("hist_clear"), key="hclr", icon=":material/delete_sweep:"):
        ss["history"] = []
        ss.pop("scan", None)
        st.rerun()


def page_rates():
    ui.render(ui.page_header(t("rates_title"), t("rates_sub")))
    ss.setdefault("rates_tab", "rates")
    with st.container(key="seg_rates"):
        labels = {"rates": ":material/payments: " + t("tab_rates"), "materials": ":material/inventory_2: " + t("tab_materials")}
        tab = st.radio(t("rates_title"), ["rates", "materials"], horizontal=True, key="rates_tab", label_visibility="collapsed",
                       format_func=labels.get)
    if tab == "rates":
        df = rates()
        if df.empty:
            ui.render(ui.empty("table_rows", t("rates_empty"), t("rates_note")))
            return
        p_ids = set(pricing.priced(df)["id"])
        rows = []
        for r in df.itertuples():
            if r.id in p_ids:
                price = '<span class="gd-amt">Rs %s – %s</span>' % ("{:,}".format(int(r.min_rs)), "{:,}".format(int(r.max_rs)))
            else:
                price = ui.badge("muted", t("price_pending"))
            meta = ui.esc(r.unit) + (" · %s" % ui.esc(r.shehar) if isinstance(r.shehar, str) and r.shehar else "")
            rows.append('<div class="gd-rate"><span class="id">%s</span><div class="nm"><b>%s</b><small>%s</small></div>%s</div>'
                        % (ui.esc(r.id), ui.esc(r.kaam), meta, price))
        head = ui.head("payments", t("rates_list"), t("rates_count") % (len(df), len(p_ids)))
        ui.render(ui.card(head + '<div style="margin-top:8px">%s</div>' % "".join(rows)))
        st.caption(t("rates_note"))
    else:
        ui.render(ui.note(t("mat_note"), "info", "info"))
        for name, use in content.MATERIALS:
            ui.render(ui.card(ui.head("inventory_2", pick(name), pick(use), "pink")))


def page_safety():
    ui.render(ui.page_header(t("safety_title"), t("safety_sub")))
    ui.render(ui.section(t("emg_numbers")))
    nums = "".join('<a class="gd-num%s" href="tel:%s">%s<div><b>%s</b><small>%s</small></div></a>'
                   % (" first" if i == 0 else "", n, ui.icon("call"), n, ui.esc(pick(label)))
                   for i, (label, n) in enumerate(content.NUMBERS))
    ui.render('<div class="gd-nums rise">%s</div>' % nums)
    st.caption(t("emg_note"))
    ui.render(ui.section(t("what_to_do")))
    for ic, title, steps in content.SAFETY:
        with st.expander(pick(title), icon=":material/%s:" % ic):
            ui.render(ui.bullet_list(pick(steps), "steps"))


def page_more():
    ui.render(ui.page_header(t("more_title"), t("more_sub")))
    for page in ("quote", "tracker", "materials", "seasonal", "settings"):
        tool_row(page)


def page_quote():
    back_button()
    ui.render(ui.page_header(t("quote_title"), t("quote_sub")))
    p = pricing.priced(rates())
    if p.empty:
        ui.render(ui.empty("request_quote", t("quote_title"), t("rate_empty")))
        disclaimer()
        return
    with st.container(key="card_quote"):
        opts = {"%s - %s (%s)" % (r.id, r.kaam, r.unit): r.id for r in p.itertuples()}
        label = st.selectbox(t("work"), list(opts.keys()))
        c1, c2 = st.columns(2)
        q_qty = c1.number_input(t("quantity"), min_value=0.0, value=1.0, step=1.0)
        quote = c2.number_input(t("quote_amount"), min_value=0, value=0, step=500)
        go_q = st.button(t("check_quote"), type="primary", key="go_quote", icon=":material/fact_check:")
    if go_q:
        res = pricing.quote_check(opts[label], q_qty, quote, rates())
        if not res or quote <= 0:
            ui.render(ui.note(t("quote_missing"), "warn", "edit"))
        else:
            tone = {"green": "ok", "yellow": "warn", "red": "danger"}[res["color"]]
            ui.render(ui.note("%s: Rs %s – %s" % (t("fair_range"), "{:,}".format(int(res["low"])), "{:,}".format(int(res["high"]))),
                              tone, "price_check", t("qv_" + res["verdict"])))
    disclaimer()


def page_tracker():
    back_button()
    ui.render(ui.page_header(t("track_title"), t("track_sub")))
    ui.render(ui.note(t("track_tip"), "info", "tips_and_updates"))
    with st.container(key="card_old"):
        ui.render(ui.head("history", t("older"), "", "cyan"))
        old = photo_input("old", many=False)
        old_d = st.date_input(t("date_older"), value=date.today(), key="old_d")
    with st.container(key="card_new"):
        ui.render(ui.head("update", t("newer")))
        new = photo_input("new", many=False)
        new_d = st.date_input(t("date_newer"), value=date.today(), key="new_d")
    clicked = st.button(t("compare"), type="primary", key="go_track", icon=":material/compare:")
    slot = st.empty()
    if clicked:
        if not old or not new:
            ui.render(ui.note(t("add_both"), "warn", "add_photo_alternate"))
        elif not ai_engine.is_configured():
            show_ai_error(ai_engine.AIUnavailable("no_key"))
        else:
            try:
                with slot.container():
                    ui.render(ui.scanbox(t("comparing"), t("track_sub")))
                r, _ = ai_engine.track(ai_engine.prepare_image(io.BytesIO(old[0])), ai_engine.prepare_image(io.BytesIO(new[0])),
                                       str(old_d), str(new_d), LANG)
                ss["track"] = r
            except ai_engine.AIUnavailable as e:
                show_ai_error(e)
            except Exception as e:  # noqa: BLE001
                ui.render(ui.note("%s: %s" % (t("err_generic"), str(e)[:200]), "danger", "error"))
            finally:
                slot.empty()
    r = ss.get("track")
    if r:
        tone = {"bigger": "danger", "same": "ok", "smaller": "ok", "unclear": "warn"}[r["change"]]
        ic = {"bigger": "trending_up", "same": "trending_flat", "smaller": "trending_down", "unclear": "help"}[r["change"]]
        ui.render(ui.note(r["explanation"], tone, ic, t("ch_" + r["change"])))
        advice = r["advice"] + (" " + t("ch_bigger_advice") if r["change"] == "bigger" else "")
        if advice.strip():
            ui.render(ui.note(advice.strip(), "info", "lightbulb"))
    disclaimer()


def page_seasonal():
    back_button()
    ui.render(ui.page_header(t("season_title"), t("season_sub")))
    keys = [("monsoon", "rainy"), ("summer", "sunny"), ("winter", "ac_unit")]
    tabs = st.tabs([":material/%s: %s" % (ic, t(k)) for k, ic in keys])
    for tab, (key, _) in zip(tabs, keys):
        with tab:
            items = content.SEASONS[key]
            done = sum(1 for i in range(len(items)) if ss.get("chk_%s_%d" % (key, i)))
            st.progress(done / len(items), text="%d / %d %s" % (done, len(items), t("progress")))
            for i, it in enumerate(items):
                st.checkbox(pick(it), key="chk_%s_%d" % (key, i))


def set_lang():
    ss["lang"] = ss["lang_widget"]


def page_settings():
    back_button()
    ui.render(ui.page_header(t("settings_title")))
    with st.container(key="card_lang"):
        ui.render(ui.head("translate", t("language"), t("language_sub"), "solid"))
        ss["lang_widget"] = ss["lang"]
        with st.container(key="langpick"):
            st.radio(t("language"), list(config.LANGUAGES), key="lang_widget", label_visibility="collapsed",
                     format_func=config.LANGUAGES.get, on_change=set_lang)
    with st.container(key="card_profile"):
        ui.render(ui.head("person", t("profile"), "", "cyan"))
        ss["name"] = st.text_input(t("name"), value=ss.get("name", ""))
        ss["city"] = st.text_input(t("city"), value=ss.get("city", ""))
    with st.container(key="card_privacy"):
        ui.render(ui.head("lock", t("privacy_title"), t("privacy"), "pink"))
        ok = ai_engine.is_configured()
        ui.render('<div style="display:flex;align-items:center;justify-content:space-between;gap:8px"><b style="font-size:.9rem">%s</b>%s</div>'
                  % (ui.esc(t("ai_status")), ui.badge("green" if ok else "red", t("ai_ready") if ok else t("ai_missing"),
                                                       "check_circle" if ok else "error")))
        if st.button(t("hist_clear"), key="sclr", icon=":material/delete_sweep:"):
            ss["history"] = []
            ss.pop("scan", None)
            st.toast(t("hist_cleared"), icon=":material/check_circle:")


PAGES = {"home": page_home, "history": page_history, "rates": page_rates, "safety": page_safety, "more": page_more,
         "quote": page_quote, "tracker": page_tracker, "seasonal": page_seasonal, "settings": page_settings}


# ------------------------------------------------------------------ layout
def top_bar():
    with st.container(key="topbar"):
        c1, c2 = st.columns([6, 1], vertical_alignment="center")
        c1.html(ui.top_brand())
        with c2.popover(t("menu"), icon=":material/menu:", help=t("menu")):
            ui.render('<div class="gd-menu-h">%s</div>' % ui.esc(t("menu_title")))
            for page, ic, key in MENU:
                st.button(t(key), key="menu_" + page, type="tertiary", icon=":material/%s:" % ic, on_click=go, args=(page,))


def bottom_nav():
    with st.container(key="bottomnav"):
        cols = st.columns(len(NAV))
        for col, (key, ic) in zip(cols, NAV):
            with col, st.container(key="nav_" + key):
                st.button(t("nav_" + key), key="navbtn_" + key, icon=":material/%s:" % ic, on_click=go, args=(key,))


if ss["page"] not in PAGES:
    ss["page"] = "home"
ui.inject_css(RTL, nav_index(), t("drop_here"), t("drop_limit"), t("browse"))
top_bar()
PAGES[ss["page"]]()
bottom_nav()
