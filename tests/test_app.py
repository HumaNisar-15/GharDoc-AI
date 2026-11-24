"""UI smoke tests with Streamlit's AppTest: every screen renders, navigation and language switching work.

Run:  python -m pytest tests   (no API key needed)
"""
import os
import sys

from streamlit.testing.v1 import AppTest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
APP = os.path.join(ROOT, "app.py")
SCREENS = ["home", "history", "rates", "safety", "more", "quote", "tracker", "seasonal", "settings"]


def fresh():
    at = AppTest.from_file(APP, default_timeout=30)
    at.run()
    assert not at.exception, at.exception
    return at


def html_text(at):
    return " ".join(str(getattr(h, "proto", "")) for h in at.get("html"))


def click(at, key):
    at.button(key=key).click().run()
    assert not at.exception, at.exception


def test_every_nav_tab_and_menu_item_opens_its_screen():
    at = fresh()
    for page in ["history", "rates", "safety", "more", "home"]:
        click(at, "navbtn_" + page)
        assert at.session_state["page"] == page
    for page in [p for p in SCREENS if p != "more"] + ["materials"]:
        click(at, "menu_" + page)
        expected = "rates" if page == "materials" else page
        assert at.session_state["page"] == expected


def test_tool_tiles_and_back_button():
    at = fresh()
    click(at, "open_quote")  # home tile
    assert at.session_state["page"] == "quote"
    click(at, "back_quote")
    assert at.session_state["page"] == "more"
    for page in ["tracker", "seasonal", "settings"]:
        click(at, "openrow_" + page)  # rows on the More screen
        assert at.session_state["page"] == page
        click(at, "back_" + page)
        assert at.session_state["page"] == "more"
    click(at, "navbtn_home")
    click(at, "open_materials")
    assert at.session_state["page"] == "rates" and at.session_state["rates_tab"] == "materials"


def test_language_switching_to_urdu_and_roman():
    at = fresh()
    click(at, "menu_settings")
    at.radio(key="lang_widget").set_value("ur").run()
    assert at.session_state["lang"] == "ur"
    assert at.button(key="navbtn_more").label == "مزید"
    click(at, "navbtn_home")
    assert "اسکین کریں" in html_text(at)
    click(at, "menu_settings")
    at.radio(key="lang_widget").set_value("roman").run()
    assert at.button(key="navbtn_safety").label == "Hifazat"


def test_diagnose_without_photo_or_key_shows_clear_message():
    at = fresh()
    click(at, "go_scan")
    assert "at least one photo" in html_text(at)


def test_rates_and_materials_are_listed():
    at = fresh()
    click(at, "navbtn_rates")
    txt = html_text(at)
    assert "R01" in txt and "R20" in txt
    at.radio(key="rates_tab").set_value("materials").run()
    assert "Bitumen membrane" in html_text(at)


def test_removed_sections_are_gone():
    at = fresh()
    for page in SCREENS:
        at.session_state["page"] = page
        at.run()
        assert not at.exception
        txt = html_text(at)
        assert "Claude" not in txt and "credits" not in txt.lower()


def test_camera_option_and_tracker_validation():
    at = fresh()
    at.radio(key="scan_src").set_value("camera").run()
    assert not at.exception and len(at.get("camera_input")) == 1
    click(at, "menu_tracker")
    click(at, "go_track")
    assert "both photos" in html_text(at)


def test_quote_checker_explains_missing_prices():
    at = fresh()
    click(at, "menu_quote")
    assert "Prices have not been added" in html_text(at)
