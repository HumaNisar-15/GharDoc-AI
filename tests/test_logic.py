"""Offline tests for the business logic (no internet or API key needed).

Run:  python tests/test_logic.py   (or: python -m pytest tests)
"""
import os
import re
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import ai_engine  # noqa: E402
import config  # noqa: E402
import content  # noqa: E402
import i18n  # noqa: E402
import pricing  # noqa: E402
import risk_rules  # noqa: E402


def mk_csv():
    p = os.path.join(tempfile.mkdtemp(), "r.csv")
    with open(p, "w") as f:
        f.write("id,kaam,unit,min_rs,max_rs,shehar,tareekh,source\n"
                "T1,test kaam,per sq ft,10,20,x,y,z\nT2,khali kaam,per kaam,,,,,\n")
    return p


def test_pricing():
    df = pricing.load_rates(mk_csv())
    assert len(pricing.priced(df)) == 1
    assert pricing.estimate(["T1", "T2"], df, 100)[0]["total_max"] == 2000
    assert [w["id"] for w in pricing.pending(["T1", "T2", "ZZ"], df)] == ["T2"]
    assert pricing.quote_check("T1", 100, 1500, df)["verdict"] == "fair"
    assert pricing.quote_check("T1", 100, 2400, df)["verdict"] == "slightly_high"
    assert pricing.quote_check("T1", 100, 9000, df)["verdict"] == "very_high"
    assert pricing.quote_check("T1", 100, 100, df)["verdict"] == "very_low"


def test_rates_file_preserved():
    df = pricing.load_rates()
    assert len(df) == 20 and df["id"].tolist()[0] == "R01" and df["id"].tolist()[-1] == "R20"


def test_risk_rules():
    base = {"issue_type": "dampness", "risk_level": "green", "confidence": 0.9, "flags": {}}
    assert risk_rules.apply_rules(base)[0] == "green"
    assert risk_rules.apply_rules({**base, "issue_type": "structural_crack"})[0] == "red"
    assert risk_rules.apply_rules({**base, "flags": {"stair_step_or_diagonal": True}})[0] == "red"
    assert risk_rules.apply_rules({**base, "confidence": 0.3})[0] == "yellow"
    assert risk_rules.apply_rules({**base, "issue_type": "pipe_leak"})[0] == "yellow"
    assert "r_lowconf" in risk_rules.apply_rules({**base, "confidence": 0.3})[1]


def test_ai_parsing():
    n = ai_engine.normalize_diagnosis({"issue_type": "???", "work_ids": ["T1", "ZZ"], "confidence": 5, "flags": "x"}, {"T1"})
    assert n["issue_type"] == "unclear" and n["work_ids"] == ["T1"] and n["confidence"] == 1.0 and n["diy_ok"] is False
    assert ai_engine.parse_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert ai_engine.parse_json('text {"a": 2} more') == {"a": 2}
    assert ai_engine.parse_json('[{"a": 3}]') == {"a": 3}
    assert set(ai_engine.LANG_RULE) == set(config.LANGUAGES)


def test_missing_key_raises_clear_error():
    old, real = os.environ.pop("GEMINI_API_KEY", None), ai_engine.get_api_key
    try:
        ai_engine.get_api_key = lambda: None
        try:
            ai_engine._call(["x"])
            raise AssertionError("expected AIUnavailable")
        except ai_engine.AIUnavailable as e:
            assert e.code == "no_key"
    finally:
        ai_engine.get_api_key = real
        if old:
            os.environ["GEMINI_API_KEY"] = old


def test_diagnose_pipeline_with_fake_gemini_client():
    """Runs the real request-building code (google-genai types) against a fake client: no network, no key leak."""
    import io
    from PIL import Image
    calls = []

    class Resp:
        text = '{"is_wall_photo": true, "issue_type": "dampness", "risk_level": "green", "confidence": 0.9, "work_ids": ["R01", "XX"]}'

    class Models:
        def generate_content(self, model, contents, config):
            calls.append((model, contents, config))
            return Resp()

    class Client:
        models = Models()

    real_key, real_client = ai_engine.get_api_key, ai_engine._client
    try:
        ai_engine.get_api_key = lambda: "test-key"
        ai_engine._client = lambda key: Client()
        buf = io.BytesIO()
        Image.new("RGB", (40, 30), (200, 190, 180)).save(buf, format="PNG")
        img = ai_engine.prepare_image(io.BytesIO(buf.getvalue()))
        d, model = ai_engine.diagnose([img], "kitchen wall", pricing.load_rates(), "ur")
    finally:
        ai_engine.get_api_key, ai_engine._client = real_key, real_client
    assert model == config.MODELS[0] and d["issue_type"] == "dampness" and d["work_ids"] == ["R01"]
    prompt = calls[0][1][-1]
    assert "Urdu script" in prompt and "R20" in prompt and "test-key" not in prompt


def test_i18n_complete():
    for k, v in i18n.STR.items():
        assert len(v) == 3 and all(v), k
    src = open(os.path.join(ROOT, "app.py"), encoding="utf-8").read()
    used = set(re.findall(r'(?<![A-Za-z0-9_.])t\("([a-z_0-9]+)"\)', src))
    used |= {"iss_" + x for x in ai_engine.ISSUE_TYPES} | {"w_" + x for x in ai_engine.WORKERS}
    used |= {"ch_" + x for x in ai_engine.CHANGES} | {"lv_" + x for x in risk_rules.LEVELS} | {"lvs_" + x for x in risk_rules.LEVELS}
    used |= {"qv_" + x for x in ("very_low", "fair", "slightly_high", "very_high")}
    used |= {"err_" + x for x in ai_engine.ERROR_CODES}
    used |= {"nav_" + x for x in ("home", "history", "rates", "safety", "more")}
    used |= {"r_struct", "r_diag", "r_wide", "r_near", "r_spread", "r_pipe", "r_lowconf", "gallery", "camera",
             "monsoon", "summer", "winter"}
    used |= {k for k in ("tool_quote", "tool_quote_d", "tool_track", "tool_track_d", "tool_season", "tool_season_d",
                         "tool_settings", "tool_settings_d", "tool_mat", "tool_mat_d", "tool_rates", "tool_safety")}
    missing = sorted(k for k in used if k not in i18n.STR)
    assert not missing, "i18n keys missing: %s" % missing
    assert i18n.t("nav_more", "ur") == "مزید" and i18n.t("nav_more", "roman") == "Mazeed"
    assert i18n.pick(("a", "b"), "ur") == "b"  # 2-item tuples fall back to Roman Urdu


def test_content_preserved():
    assert len(content.MATERIALS) == 9 and len(content.SAFETY) == 6 and len(content.NUMBERS) == 5
    assert all(len(x) == 3 for s in content.SEASONS.values() for x in s)
    assert all(len(name) == 3 and len(use) == 3 for name, use in content.MATERIALS)
    assert all(len(steps) == 3 for _, _, steps in content.SAFETY)
    assert not hasattr(content, "ABOUT_AI")


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
    print("All logic tests passed")
