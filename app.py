"""
GymStart — dein täglicher KI-Coach fürs Gym (Streamlit).

Day-by-Day Journey für absolute Anfänger, wie im Konzept:
- Onboarding -> exakte Kalorien/Makros (Mifflin-St Jeor, in Python, keine API)
- Gym-Finder mit Empfehlung + Karte
- Commit-Moment
- Tägliche Timeline: Tag 1 mentale Vorbereitung, Tag 2 Ernährung, Tag 3 erster
  Gymbesuch, Tag 4 erste Übungen, ab Tag 5 progressives Training / Ruhetage
- Adaptive Logik (Feedback -> Schwierigkeit, 3x zu leicht -> Progressive Overload,
  verpasster Tag -> Nachfrage, Gewichtsänderung -> neue Kalorien)
- Wissens-Bereich (Etikette, Geräte-Guide, Supplements, Regeneration)
- Fortschritt (Streaks, Meilensteine, Maße, Fotos, Makro-Log)
- Paywall-Moment an Tag 14
- Statischer Content ohne API; GPT-4o-mini NUR für Coaching-Text & Mahlzeiten.
"""
import json
import math
import base64
import datetime
import urllib.request
import urllib.error
import urllib.parse
import streamlit as st

try:
    from streamlit_oauth import OAuth2Component
    OAUTH_AVAILABLE = True
except Exception:
    OAUTH_AVAILABLE = False

st.set_page_config(page_title="GymStart", page_icon="💪", layout="centered",
                   initial_sidebar_state="collapsed")

# =============================================================================
# STYLING – Apple-Look: klar, hell, feine Typografie, dezente Karten.
# Alle Klassennamen bleiben identisch, damit jede Funktion weiterläuft.
# =============================================================================
st.markdown("""
<style>
  :root {
    color-scheme: light;
    --bg:#f5f5f7; --surface:#ffffff; --ink:#1d1d1f; --sub:#6e6e73;
    --line:rgba(0,0,0,.09); --accent:#FF7A1A; --accent-ink:#C2410C; --accent-soft:#FFF3EA;
    --green:#34C759; --green-ink:#248A3D; --green-soft:#EAF9EE;
    --red-ink:#C0392B; --red-soft:#FDF0EE;
    --font:-apple-system,BlinkMacSystemFont,"SF Pro Display","SF Pro Text","Helvetica Neue",Helvetica,Arial,sans-serif;
  }
  html, body, .stApp { background-color:var(--bg) !important; }
  .stApp, .stApp * { font-family:var(--font); -webkit-font-smoothing:antialiased; -moz-osx-font-smoothing:grayscale; }
  .block-container { max-width:500px; padding-top:1.2rem; padding-bottom:5rem; }
  #MainMenu, footer, header { visibility:hidden; }

  .stApp, .stApp p, .stApp li, .stApp label, .stApp span,
  [data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] p,
  [data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] *,
  .stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp h5 { color:var(--ink); }
  .stApp h1 { font-weight:700; letter-spacing:-.028em; font-size:2.15rem; }
  .stApp h2 { font-weight:700; letter-spacing:-.024em; font-size:1.6rem; }
  .stApp h3 { font-weight:600; letter-spacing:-.018em; }
  [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] * { color:var(--sub) !important; }

  .stApp input, .stApp textarea { color:var(--ink) !important; background-color:var(--surface) !important;
      border-radius:12px !important; }
  [data-baseweb="input"], [data-baseweb="base-input"] { border-radius:12px !important; }
  /* Zahlenfelder: reine Eingabe, KEINE Hoch/Runter-Pfeile */
  [data-testid="stNumberInputStepUp"], [data-testid="stNumberInputStepDown"] { display:none !important; }
  [data-baseweb="select"] > div { background-color:var(--surface) !important; border-radius:12px !important; }
  [data-baseweb="select"] div, [data-baseweb="popover"] li, [role="option"] { color:var(--ink) !important; }
  [data-baseweb="popover"] li, [role="option"] { background-color:var(--surface) !important; }

  /* Buttons – Apple-Pill */
  div.stButton > button { border-radius:980px; font-weight:600; padding:.6rem .9rem; font-size:15px;
      white-space:nowrap; background:var(--surface); color:var(--ink) !important; border:1px solid var(--line); width:100%;
      transition:transform .12s ease, box-shadow .2s ease, background .2s ease; box-shadow:0 1px 2px rgba(0,0,0,.04); }
  div.stButton > button:hover { border-color:rgba(0,0,0,.18); }
  div.stButton > button:active { transform:scale(.985); }
  div.stButton > button[kind="primary"], div.stButton > button[kind="primary"] * {
      background:var(--accent) !important; color:#fff !important; border:none; }
  div.stButton > button[kind="primary"]:hover { box-shadow:0 6px 18px rgba(255,122,26,.34); }

  /* Segmented control (horizontale Radios: Top-Nav + Sub-Navs) */
  div[role="radiogroup"] { gap:2px !important; background:#e9e9ee; border-radius:12px; padding:3px;
      flex-wrap:wrap; }
  div[role="radiogroup"] > label { flex:1 1 auto; margin:0 !important; justify-content:center;
      border-radius:9px; padding:6px 8px; transition:background .18s ease, box-shadow .18s ease; }
  div[role="radiogroup"] > label:hover { background:rgba(255,255,255,.5); }
  div[role="radiogroup"] > label > div:first-child { display:none !important; }
  div[role="radiogroup"] > label p { font-size:13px; font-weight:600; color:var(--sub) !important; }
  div[role="radiogroup"] > label:has(input:checked) { background:var(--surface);
      box-shadow:0 1px 3px rgba(0,0,0,.12); }
  div[role="radiogroup"] > label:has(input:checked) p { color:var(--ink) !important; }

  .card { background:var(--surface); border:1px solid var(--line); border-radius:20px;
          padding:18px 20px; margin:12px 0; box-shadow:0 1px 3px rgba(0,0,0,.05); }
  .card p { color:#3a3a3c !important; line-height:1.55; margin:0 0 6px; }
  .card h3 { margin:0 0 10px; }
  .badge { display:inline-block; background:var(--accent-soft); color:var(--accent-ink) !important; font-weight:600;
           font-size:12px; letter-spacing:.02em; padding:6px 13px; border-radius:980px; }
  .badge.green { background:var(--green-soft); color:var(--green-ink) !important; }
  .kcal { font-size:52px; font-weight:700; color:var(--ink) !important; line-height:1; letter-spacing:-.03em; }
  .muted { color:var(--sub) !important; }
  .pill { display:inline-block; background:#f2f2f4; color:#3a3a3c !important; font-size:12px;
          font-weight:600; padding:6px 12px; border-radius:980px; margin:0 5px 6px 0; border:1px solid var(--line); }
  .setpill { display:inline-block; background:var(--accent-soft); color:var(--accent-ink) !important; font-weight:600;
             font-size:14px; padding:8px 14px; border-radius:980px; margin:4px 0 8px; }
  .tip { background:var(--green-soft); border:1px solid rgba(52,199,89,.22); border-radius:14px; padding:12px 15px;
         color:var(--green-ink) !important; font-size:14px; line-height:1.5; margin:10px 0; }
  .tip b { color:var(--green-ink) !important; }
  .warn { background:var(--red-soft); border:1px solid rgba(192,57,43,.18); border-radius:14px; padding:12px 15px;
          color:var(--red-ink) !important; font-size:14px; line-height:1.5; margin:8px 0; }
  .warn b { color:var(--red-ink) !important; }
  .streak { background:linear-gradient(120deg,#FF7A1A,#FF9F45); border-radius:18px;
            padding:14px 20px; font-weight:700; font-size:19px; margin:6px 0 4px;
            box-shadow:0 8px 22px rgba(255,122,26,.24); }
  .streak, .streak * { color:#fff !important; }
  .meal { display:flex; gap:12px; align-items:center; padding:12px 14px; background:#fafafc;
          border:1px solid var(--line); border-radius:14px; margin:8px 0; }
  .meal .mi { font-size:24px; } .meal .mt { font-weight:600; font-size:14px; color:var(--ink) !important; }
  .meal .md { font-size:12px; color:var(--sub) !important; }
  .meal .mk { margin-left:auto; text-align:right; font-size:12px; font-weight:600; color:var(--accent-ink) !important; }
  .step { display:flex; gap:12px; margin-bottom:11px; align-items:flex-start; }
  .step .num { min-width:26px; height:26px; border-radius:50%; background:var(--accent-soft); color:var(--accent-ink) !important;
               font-weight:700; font-size:13px; display:flex; align-items:center; justify-content:center; }
  .wkrow { display:flex; gap:14px; align-items:center; padding:12px; border-radius:16px;
           margin-bottom:8px; background:#fafafc; border:1px solid var(--line); }
  .wkrow.train { background:var(--accent-soft); border-color:rgba(255,122,26,.2); }
  .wkday { width:46px; height:46px; border-radius:13px; background:var(--surface); display:flex; align-items:center;
           justify-content:center; font-weight:700; border:1px solid var(--line); color:var(--ink) !important; }
  .wkrow.train .wkday { background:var(--accent); color:#fff !important; border-color:var(--accent); }
  .wktitle { font-weight:600; font-size:14.5px; color:var(--ink) !important; }
  .wkfocus { font-size:12.5px; color:var(--sub) !important; }
  .dots { display:flex; gap:6px; flex-wrap:wrap; margin:4px 0 2px; }
  .dot { width:30px; height:30px; border-radius:50%; display:flex; align-items:center; justify-content:center;
         font-size:12px; font-weight:700; background:var(--surface); border:1.5px solid var(--line); color:var(--sub) !important; }
  .dot.done { background:var(--green); border-color:var(--green); color:#fff !important; }
  .dot.today { background:var(--accent); border-color:var(--accent); color:#fff !important; box-shadow:0 0 0 4px var(--accent-soft); }
  .stat { background:var(--surface); border:1px solid var(--line); border-radius:16px; padding:16px 6px; text-align:center;
          box-shadow:0 1px 3px rgba(0,0,0,.05); }
  .stat .v { font-size:28px; font-weight:700; color:var(--ink); line-height:1; letter-spacing:-.02em; }
  .stat .l { font-size:11px; color:var(--sub); margin-top:5px; }
  .mile { display:flex; align-items:center; gap:10px; padding:12px 14px; border-radius:14px; margin-bottom:8px; font-weight:500; }
  .mile.on { background:var(--green-soft); color:var(--green-ink); border:1px solid rgba(52,199,89,.22); }
  .mile.off { background:#f2f2f4; color:#a1a1a6; border:1px solid var(--line); }
  .knav { display:flex; gap:8px; margin-bottom:6px; }
  .gcard { background:var(--surface); border:1px solid var(--line); border-radius:20px; overflow:hidden;
           margin:12px 0; box-shadow:0 1px 3px rgba(0,0,0,.05); }
  .gcard img { width:100%; display:block; aspect-ratio:16/9; object-fit:cover; }
  .gcard .gbody { padding:14px 18px 16px; }
  .gcard .gname { font-weight:600; font-size:17px; color:var(--ink); letter-spacing:-.01em; }
  .gcard .gmus { display:inline-block; background:var(--accent-soft); color:var(--accent-ink) !important; font-weight:600;
                 font-size:11px; padding:3px 10px; border-radius:980px; margin-left:6px; }
  .supp { display:flex; gap:12px; align-items:flex-start; padding:13px 15px; border-radius:14px; margin-bottom:8px; border:1px solid var(--line); }
  .supp .se { font-size:22px; } .supp .st { font-weight:600; color:var(--ink); }
  .supp .sd { font-size:13px; color:var(--sub); }
  .supp.good { background:var(--green-soft); border-color:rgba(52,199,89,.22); }
  .supp.mid { background:#FFF8E9; border-color:#F3E6C4; }
  .supp.bad { background:var(--red-soft); border-color:rgba(192,57,43,.16); }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# STATE
# =============================================================================
def init_state():
    d = st.session_state
    d.setdefault("phase", "onboarding")
    d.setdefault("profile", dict(weight=75, height=175, age=26, sex="Männlich",
                                 bodytype="Normal", goal="Muskeln aufbauen",
                                 exp="Noch nie im Gym", days=3, train_days=[0, 2, 4],
                                 budget="20–40 €"))
    d.setdefault("gym", None)
    d.setdefault("start_date", None)
    d.setdefault("completed", set())
    d.setdefault("checklist", {})
    d.setdefault("feedback", {})       # day -> "zu leicht"/"passt"/"zu schwer"
    d.setdefault("ai_cache", {})       # day -> {"coaching":..,"meals":[..]}
    d.setdefault("ai_workout", {})     # day -> {"name","exercises","focus","reason"}
    d.setdefault("day_offset", 0)
    d.setdefault("premium", False)
    d.setdefault("view", "Heute")
    d.setdefault("api_key", "")
    d.setdefault("weight_log", [])     # [(date, weight)]
    d.setdefault("measure_log", [])    # [{date, waist, arm, chest}]
    d.setdefault("photos", [])         # [(date, bytes)]
    d.setdefault("food_log", {})       # "YYYY-MM-DD" -> [{"name","protein","kcal"}]
    d.setdefault("missed_handled", set())
    d.setdefault("swaps", {})          # f"{day}|{übung}" -> Alternativ-Übungsname
    d.setdefault("workout_wish", {})   # day -> Freitext-Wunsch fürs Training


init_state()
ss = st.session_state


# =============================================================================
# BERECHNUNGEN (Mifflin-St Jeor, keine API)
# =============================================================================
ACT = {1: 1.2, 2: 1.2, 3: 1.375, 4: 1.46, 5: 1.55, 6: 1.6, 7: 1.7}


def bmr(p):
    base = 10 * p["weight"] + 6.25 * p["height"] - 5 * p["age"]
    return round(base + 5 if p["sex"] == "Männlich"
                 else base - 161 if p["sex"] == "Weiblich" else base - 78)


def tdee(p):
    return round(bmr(p) * ACT.get(p["days"], 1.375))


def goal_kcal(p):
    t = tdee(p)
    return t - 350 if p["goal"] == "Abnehmen" else t + 300 if p["goal"] == "Muskeln aufbauen" else t


def macro_split(p):
    if p["bodytype"] == "Sehr dünn" or p["goal"] == "Muskeln aufbauen":
        return (.30, .50, .20)
    if p["bodytype"] == "Übergewichtig" or p["goal"] == "Abnehmen":
        return (.35, .35, .30)
    return (.30, .40, .30)


def macros(p):
    kcal = goal_kcal(p)
    pr, ca, fa = macro_split(p)
    return dict(kcal=kcal, protein=round(kcal * pr / 4),
                carbs=round(kcal * ca / 4), fat=round(kcal * fa / 9))


def plan():
    """Aktive Tagesziele (kcal/Makros). KI-berechnet wenn Key da, sonst Formel.
    Wird einmal berechnet und in ss.plan gecacht (bis Gewicht sich ändert)."""
    if ss.get("plan"):
        return ss["plan"]
    ss["plan"] = compute_plan()
    return ss["plan"]


def compute_plan():
    p = ss.profile
    f = macros(p)  # Formel als Anker & Fallback
    if get_key():
        ai = ai_calc_calories(p, f)
        if ai:
            return ai
    f["reason"] = (f"Grundumsatz {bmr(p)} kcal × Aktivität ({p['days']} Trainingstage) "
                   f"= {tdee(p)} kcal Gesamtbedarf → Ziel {f['kcal']} kcal für „{p['goal']}“.")
    f["ai"] = False
    return f


def ai_calc_calories(p, f):
    prompt = (
        "Du bist Ernährungswissenschaftler. Berechne den täglichen Kalorien- und Makrobedarf "
        f"für diese Person und gehe dabei sorgfältig vor:\n"
        f"- {p['age']} Jahre, {p['sex']}, {p['weight']} kg, {p['height']} cm\n"
        f"- Körpertyp {p['bodytype']}, Ziel: {p['goal']}, {p['days']}× Training/Woche, Erfahrung: {p['exp']}\n"
        "Denke wie ein Profi: Grundumsatz (Mifflin-St Jeor), passender Aktivitätsfaktor, "
        "sinnvolle Ziel-Anpassung (Defizit/Überschuss) und eine für Ziel & Körpertyp passende "
        "Makroverteilung. Antworte NUR als JSON: "
        '{"kcal":Zahl,"protein":Gramm,"carbs":Gramm,"fat":Gramm,'
        '"reason":"2-3 Sätze per Du, wie du zu den Zahlen kommst"}'
    )
    data = _openai({"model": MODEL_CALORIES, "temperature": 0.4,
                    "response_format": {"type": "json_object"},
                    "messages": [
                        {"role": "system", "content": "Du rechnest sorgfältig und antwortest ausschließlich mit gültigem JSON."},
                        {"role": "user", "content": prompt}]})
    if not data:
        return None
    try:
        r = json.loads(data["choices"][0]["message"]["content"])
        kcal, pro = int(round(r["kcal"])), int(round(r["protein"]))
        car, fat = int(round(r["carbs"])), int(round(r["fat"]))
        # Plausibilitäts-Check — bei Unsinn lieber die Formel
        if not (1000 <= kcal <= 5000 and 30 <= pro <= 400 and 0 <= car <= 700 and 0 <= fat <= 250):
            return None
        return dict(kcal=kcal, protein=pro, carbs=car, fat=fat,
                    reason=r.get("reason", ""), ai=True)
    except Exception:
        return None


def plan_name(p):
    if p["days"] >= 4 and p["goal"] == "Muskeln aufbauen":
        return "Push / Pull / Legs"
    if p["days"] >= 3 and p["goal"] == "Muskeln aufbauen":
        return "Ganzkörper → Split"
    if p["goal"] == "Abnehmen":
        return "Ganzkörper + Cardio"
    return "Ganzkörper-Basis"


# =============================================================================
# ÜBUNGEN + WORKOUT-LOGIK (statisch, individualisiert)
# =============================================================================
EXERCISES = {
    "Beinpresse": dict(m="Beine & Po", vid="dIhx9s2akVo",
                       desc="Du drückst im Sitzen eine Platte mit den Füßen weg — trainiert Oberschenkel und Po, ganz ohne Belastung für den Rücken.",
                       setup="Rückenlehne aufrecht, Füße schulterbreit auf der Platte.",
                       warn="Knie in Richtung Zehen bewegen — nie nach innen kippen und nicht ganz durchdrücken."),
    "Brustpresse (Maschine)": dict(m="Brust & Trizeps", vid="vfWqWby1PZ0",
                       desc="Du drückst zwei Griffe von der Brust weg — baut Brust, Schultern und Trizeps auf.",
                       setup="Griffe auf Höhe der mittleren Brust einstellen.",
                       warn="Rücken bleibt an der Lehne, kein Hohlkreuz."),
    "Latzug (Kabelzug)": dict(m="Rücken & Bizeps", vid="x4fHENgCi6o",
                       desc="Du ziehst eine Stange von oben zur Brust — formt den breiten, kräftigen Rücken.",
                       setup="Beinpolster fixieren, Stange etwas weiter als schulterbreit greifen.",
                       warn="Zur oberen Brust ziehen, nicht in den Nacken. Kein Reißen."),
    "Rudern (Maschine)": dict(m="Oberer Rücken", vid="qPiF6y_HOBs",
                       desc="Du ziehst Griffe zum Körper — stärkt den oberen Rücken und verbessert die Haltung.",
                       setup="Brust ans Polster, Sitzhöhe so, dass Griffe auf Bauchhöhe sind.",
                       warn="Rücken gerade halten, Schulterblätter zusammenziehen."),
    "Schulterpresse (Maschine)": dict(m="Schultern", vid="3b3xodJR75U",
                       desc="Du drückst Griffe über den Kopf — formt runde, kräftige Schultern.",
                       setup="Griffe starten auf Schulterhöhe.",
                       warn="Nicht bis zum Anschlag durchdrücken."),
    "Beinbeuger": dict(m="Beinrückseite", vid="1aJCM5ewSv8",
                       desc="Du beugst die Beine gegen Widerstand — trainiert die oft vernachlässigte Beinrückseite.",
                       setup="Polster knapp über der Ferse, Drehachse auf Kniehöhe.",
                       warn="Langsam und ohne Schwung beugen und strecken."),
    "Beinstrecker": dict(m="Beinvorderseite", vid="fIyf6iLZn5U",
                       desc="Du streckst die Beine gegen Widerstand — kräftigt die Oberschenkelvorderseite.",
                       setup="Kniegelenk auf Drehachse, Polster über den Fußgelenken.",
                       warn="Oben kurz halten, kontrolliert ablassen — kein Schwung."),
    "Bauchmaschine": dict(m="Bauch", vid="k3bF5LQAjB4",
                       desc="Du rollst den Oberkörper gegen Widerstand ein — kräftigt gezielt die Bauchmuskeln.",
                       setup="Griffe fassen, Brustpolster an der Brust.",
                       warn="Aus dem Bauch einrollen, nicht am Nacken ziehen."),
    "Butterfly (Brust)": dict(m="Brust", vid="4x9DdhvieI4",
                       desc="Du führst zwei Griffe vor der Brust zusammen — isoliert und formt die Brust sichtbar.",
                       setup="Griffe auf Brusthöhe, Arme leicht angewinkelt, Rücken an die Lehne.",
                       warn="Kontrolliert zusammenführen — nicht mit Schwung zuschlagen."),
    "Bizeps-Curl (Maschine)": dict(m="Bizeps", vid="o5kPXkSv26Y",
                       desc="Du beugst die Arme gegen Widerstand — baut gezielt den Bizeps auf.",
                       setup="Oberarme liegen ganz auf dem Polster, Ellbogen auf der Drehachse.",
                       warn="Nicht mit Schwung reißen — langsam beugen und strecken."),
    "Trizepsdrücken (Kabel)": dict(m="Trizeps", vid="yk6VdVwww5k",
                       desc="Du drückst Stange oder Seil nach unten — formt die Rückseite des Oberarms.",
                       setup="Ellbogen eng am Körper fixieren, aufrecht stehen.",
                       warn="Nur die Unterarme bewegen sich — Ellbogen bleiben am Körper."),
    # --- Erweiterung: weitere gängige Maschinen (alle mit geprüftem Video) ---
    "V-Squat (Hackenschmidt)": dict(m="Beine & Po", vid="0Y9GHL5kL_Q",
                       desc="Geführte Kniebeuge-Maschine: Du drückst dich über die Beine gegen ein Schulterpolster nach oben — starke Beinübung mit sicherer Führung.",
                       setup="Schultern unter die Polster, Füße schulterbreit auf die Platte, Rücken angelehnt.",
                       warn="Knie in Richtung Zehen, nicht ganz durchdrücken, nur so tief wie sauber."),
    "Wadenheben-Maschine": dict(m="Waden", vid="6XQ38VxOyp0",
                       desc="Du drückst dich über die Fußballen nach oben — trainiert gezielt die oft vergessenen Waden.",
                       setup="Fußballen auf die Kante, Fersen frei, Polster auf Schultern oder Knien.",
                       warn="Volle Bewegung: unten dehnen, oben kurz halten. Kein Wippen."),
    "Abduktoren-Maschine": dict(m="Po & Beinaußenseite", vid="tESLPpvrRGM",
                       desc="Du drückst die Knie gegen Polster nach außen — kräftigt Po und die seitliche Hüfte.",
                       setup="Aufrecht sitzen, Polster außen an den Knien, Rücken angelehnt.",
                       warn="Kontrolliert öffnen und schließen, nicht mit Schwung nach außen."),
    "Adduktoren-Maschine": dict(m="Beininnenseite", vid="Vx8xOogv-og",
                       desc="Du führst die Knie gegen Widerstand zusammen — trainiert die Innenseite der Oberschenkel.",
                       setup="Aufrecht sitzen, Polster innen an den Knien, Rücken angelehnt.",
                       warn="Langsam zusammenführen und öffnen, nicht ruckartig."),
    "Rückenstrecker (Maschine)": dict(m="Unterer Rücken", vid="mhddol8ssTQ",
                       desc="Du richtest den Oberkörper gegen die Schwerkraft auf — stärkt den unteren Rücken und die Körpermitte.",
                       setup="Hüfte auf dem Polster, Fersen fixiert, Oberkörper frei.",
                       warn="Nur bis zur geraden Linie aufrichten, nicht ins Hohlkreuz überstrecken.",
                       wtxt="Erst nur Körpergewicht, später eine Hantelscheibe vor der Brust."),
    "Seitheben-Maschine": dict(m="Schultern (seitlich)", vid="Xk-oRzoKFaw",
                       desc="Du hebst die Arme gegen Polster seitlich an — formt die seitliche Schulter für eine breitere Optik.",
                       setup="Aufrecht sitzen, Oberarme an die Polster, Ellbogen führen die Bewegung.",
                       warn="Nur bis Schulterhöhe, Schultern nicht zum Ohr hochziehen."),
    "Reverse Butterfly (Maschine)": dict(m="Hintere Schulter & oberer Rücken", vid="uXFjLXgIcYc",
                       desc="Wie Butterfly, nur rückwärts: Du führst die Arme nach hinten — trainiert die hintere Schulter für eine gesunde Haltung.",
                       setup="Brust ans Polster, Arme fast gestreckt, Griffe auf Schulterhöhe.",
                       warn="Aus den Schulterblättern führen, nicht mit Schwung reißen."),
    "Cable Cross (Kabelzug-Brust)": dict(m="Brust", vid="tL-1I_pg5mk",
                       desc="Du führst zwei Kabelgriffe vor dem Körper zusammen — dehnt und formt die Brust über den vollen Bewegungsweg.",
                       setup="Griffe oben einhängen, leichte Schrittstellung, Arme leicht gebeugt.",
                       warn="Kontrolliert zusammenführen, Schulterblätter hinten lassen."),
    "Klimmzug-/Dip-Maschine": dict(m="Rücken & Arme", vid="jl3pqU3Dp14",
                       desc="Ein Polster nimmt dir Gewicht ab, sodass du Klimmzüge oder Dips sauber schaffst — ideal für den Einstieg.",
                       setup="Auf das Polster knien/stellen, Gegengewicht so wählen, dass ~8 Wdh. gehen.",
                       warn="Kontrolliert hoch und runter, unten voll ausstrecken.",
                       wtxt="Gegengewicht so wählen, dass ~8 saubere Wiederholungen gehen."),
    "Scott-Curl-Maschine": dict(m="Bizeps", vid="ajbryIHUcoo",
                       desc="Die Oberarme liegen fest auf einem Schrägpolster — isoliert den Bizeps besonders sauber.",
                       setup="Achseln ans obere Polsterende, Oberarme komplett auflegen.",
                       warn="Unten nicht ruckartig durchstrecken — schont die Ellbogen."),
    "Hip-Thrust-Maschine": dict(m="Po", vid="HW7Emnd61Bg",
                       desc="Du drückst die Hüfte gegen ein Polster nach oben — die stärkste Maschine gezielt für den Po.",
                       setup="Rücken ans Rückenpolster, Füße schulterbreit, Polster über der Hüfte.",
                       warn="Oben den Po fest anspannen, kein Hohlkreuz — aus der Hüfte drücken."),
    "Rotationsmaschine (Bauch)": dict(m="Seitliche Bauchmuskeln", vid="hgKbzySPctg",
                       desc="Du drehst den Oberkörper gegen Widerstand zur Seite — trainiert die schräge Bauchmuskulatur.",
                       setup="Aufrecht sitzen, Oberkörper fixieren, Bewegung nur aus dem Rumpf.",
                       warn="Langsam und kontrolliert drehen, kein Schwung — schont die Wirbelsäule."),
    "Dips-Maschine": dict(m="Brust & Trizeps", vid="jIQPDQJPXdE",
                       desc="Du drückst dich zwischen zwei Griffen nach oben — kräftige Übung für Trizeps und untere Brust.",
                       setup="Griffe fassen, Schultern tief, Oberkörper leicht vorgelehnt.",
                       warn="Nur so tief, wie die Schulter schmerzfrei bleibt.",
                       wtxt="An der assistierten Maschine mit Unterstützung starten."),
    "Smith-Maschine (Kniebeuge)": dict(m="Beine & Po", vid="XuzmpMeOSDI",
                       desc="Kniebeuge an der geführten Stange — sie läuft in einer Schiene, das gibt Sicherheit beim Lernen.",
                       setup="Stange auf dem oberen Rücken (nicht Nacken), Füße etwas vor der Stange.",
                       warn="Knie in Richtung Zehen, Rücken gerade, nur so tief wie sauber."),
    "T-Bar Rudern (Maschine)": dict(m="Oberer Rücken", vid="v0FcLxplgBA",
                       desc="Vorgebeugt ziehst du ein T-Griff-Gewicht zum Körper — baut einen breiten, dicken Rücken auf.",
                       setup="Brust ans Polster (falls vorhanden), Rücken gerade, Griff fassen.",
                       warn="Aus dem Rücken ziehen, Schulterblätter zusammen, kein Rundrücken."),
    "Cable Crunch (Bauch am Kabel)": dict(m="Bauch", vid="HhJjrqdcyVE",
                       desc="Kniend rollst du den Oberkörper gegen den Kabelzug ein — sehr effektiv für die geraden Bauchmuskeln.",
                       setup="Vor dem Kabelturm knien, Seil hinter den Kopf, Hüfte fixieren.",
                       warn="Aus dem Bauch einrollen, nicht aus der Hüfte ziehen."),
    "Beinheben-Maschine": dict(m="Unterer Bauch", vid="DWSkW9wR7GI",
                       desc="In der Armstütze hebst du die Beine an — trainiert gezielt den unteren Bauch.",
                       setup="Unterarme auf die Polster, Rücken ans Polster, Schultern tief.",
                       warn="Beine kontrolliert heben und senken, kein Schwung.",
                       wtxt="Nur Körpergewicht — angewinkelte Beine sind leichter."),
}
EX_LIST = list(EXERCISES.keys())

# Konservative Anfänger-Startgewichte als Anteil vom Körpergewicht (lo, hi).
# Wird nach Geschlecht/Erfahrung/Fortschritt personalisiert (start_weight()).
START_WF = {
    "Beinpresse": (0.50, 0.80),
    "Brustpresse (Maschine)": (0.22, 0.38),
    "Latzug (Kabelzug)": (0.32, 0.50),
    "Rudern (Maschine)": (0.30, 0.46),
    "Schulterpresse (Maschine)": (0.14, 0.24),
    "Beinbeuger": (0.20, 0.32),
    "Beinstrecker": (0.24, 0.40),
    "Bauchmaschine": (0.14, 0.24),
    "Butterfly (Brust)": (0.15, 0.28),
    "Bizeps-Curl (Maschine)": (0.10, 0.18),
    "Trizepsdrücken (Kabel)": (0.14, 0.26),
    "V-Squat (Hackenschmidt)": (0.40, 0.70),
    "Wadenheben-Maschine": (0.40, 0.75),
    "Abduktoren-Maschine": (0.25, 0.45),
    "Adduktoren-Maschine": (0.25, 0.45),
    "Seitheben-Maschine": (0.08, 0.16),
    "Reverse Butterfly (Maschine)": (0.10, 0.20),
    "Cable Cross (Kabelzug-Brust)": (0.12, 0.22),
    "Scott-Curl-Maschine": (0.10, 0.18),
    "Hip-Thrust-Maschine": (0.40, 0.80),
    "Rotationsmaschine (Bauch)": (0.12, 0.22),
    "Smith-Maschine (Kniebeuge)": (0.30, 0.60),
    "T-Bar Rudern (Maschine)": (0.25, 0.45),
    "Cable Crunch (Bauch am Kabel)": (0.15, 0.30),
}

# Alternativen pro Übung – falls das genaue Gerät im Gym fehlt.
# Gleicher Muskel, ohne diese Maschine. Kein festes Video (Suchlink statt Embed).
ALTS = {
    "Beinpresse": [
        {"name": "Goblet-Squat", "m": "Beine & Po",
         "desc": "Kniebeuge, bei der du eine Kurzhantel vor der Brust hältst — trainiert Beine und Po ganz ohne Maschine.",
         "setup": "Füße schulterbreit, Hantel dicht am Körper, Brust aufrecht.",
         "warn": "Knie in Richtung Zehen, Rücken gerade, nur so tief wie es sauber geht.",
         "wtxt": "Start mit leichter Kurzhantel (~6–10 kg) — erst die Technik."},
        {"name": "Ausfallschritte", "m": "Beine & Po",
         "desc": "Großer Schritt nach vorn, hinteres Knie absenken — starke Übung für Beine und Po.",
         "setup": "Oberkörper aufrecht, Schritt so groß, dass beide Knie ~90° sind.",
         "warn": "Vorderes Knie bleibt über dem Fuß, nicht nach innen kippen.",
         "wtxt": "Zuerst nur Körpergewicht, später leichte Kurzhanteln."},
    ],
    "Brustpresse (Maschine)": [
        {"name": "Kurzhantel-Bankdrücken", "m": "Brust & Trizeps",
         "desc": "Auf einer Flachbank drückst du zwei Kurzhanteln nach oben — baut Brust, Schultern und Trizeps.",
         "setup": "Rücken flach auf der Bank, Hanteln auf Brusthöhe starten.",
         "warn": "Handgelenke gerade, kontrolliert, nicht bis zum Anschlag zusammenführen.",
         "wtxt": "Start ~2×5–8 kg, Technik vor Gewicht."},
        {"name": "Liegestütze", "m": "Brust & Trizeps",
         "desc": "Klassische Liegestütze mit dem eigenen Körpergewicht — Brust und Arme, überall machbar.",
         "setup": "Hände etwas breiter als schulterbreit, Körper bildet eine gerade Linie.",
         "warn": "Hüfte nicht durchhängen lassen; zu schwer? Auf den Knien starten.",
         "wtxt": "Nur Körpergewicht — auf den Knien leichter."},
    ],
    "Latzug (Kabelzug)": [
        {"name": "Klimmzüge (unterstützt)", "m": "Rücken & Bizeps",
         "desc": "An der Klimmzugmaschine oder mit Band ziehst du dich hoch — top für den breiten Rücken.",
         "setup": "Griff etwas breiter als schulterbreit; Unterstützung so, dass ~8 Wdh. gehen.",
         "warn": "Kontrolliert hoch und runter, nicht schwungvoll reißen.",
         "wtxt": "Unterstützung/Band so wählen, dass es fordert, aber machbar ist."},
        {"name": "Kurzhantel-Rudern", "m": "Rücken & Bizeps",
         "desc": "Vorgebeugt ziehst du eine Kurzhantel zum Körper — kräftigt den Rücken ohne Kabelzug.",
         "setup": "Ein Knie auf der Bank, Rücken gerade, Hantel frei hängen lassen.",
         "warn": "Aus dem Rücken ziehen statt aus dem Arm reißen, Rücken bleibt gerade.",
         "wtxt": "Start ~5–8 kg pro Hand."},
    ],
    "Rudern (Maschine)": [
        {"name": "Kurzhantel-Rudern (einarmig)", "m": "Oberer Rücken",
         "desc": "Einarmig ziehst du eine Kurzhantel zum Körper — stärkt oberen Rücken und Haltung.",
         "setup": "Eine Hand und ein Knie auf der Bank, Rücken parallel zum Boden.",
         "warn": "Nicht verdrehen, Schulter nach hinten-unten ziehen.",
         "wtxt": "Start ~5–8 kg."},
        {"name": "Kabelrudern (sitzend)", "m": "Oberer Rücken",
         "desc": "Sitzend ziehst du einen Griff am Kabel zum Bauch — für den mittleren Rücken.",
         "setup": "Leicht gebeugte Knie, aufrecht sitzen, Schulterblätter zusammenziehen.",
         "warn": "Oberkörper ruhig halten, nicht mit dem Rumpf schwingen.",
         "wtxt": "Leicht beginnen, sauber ziehen."},
    ],
    "Schulterpresse (Maschine)": [
        {"name": "Kurzhantel-Schulterdrücken", "m": "Schultern",
         "desc": "Sitzend oder stehend drückst du zwei Kurzhanteln über den Kopf — formt die Schultern.",
         "setup": "Hanteln auf Schulterhöhe, Rücken gerade, Bauch fest.",
         "warn": "Kein Hohlkreuz, nicht bis zum Anschlag durchdrücken.",
         "wtxt": "Start ~2×3–6 kg."},
        {"name": "Seitheben", "m": "Schultern",
         "desc": "Mit leichten Kurzhanteln hebst du die Arme seitlich an — für runde Schultern.",
         "setup": "Ellbogen leicht gebeugt, bis Schulterhöhe heben.",
         "warn": "Ganz leicht wählen, ohne Schwung — sonst geht's in den Nacken.",
         "wtxt": "Sehr leicht: ~2×2–4 kg."},
    ],
    "Beinbeuger": [
        {"name": "Rumänisches Kreuzheben (Kurzhanteln)", "m": "Beinrückseite",
         "desc": "Mit fast gestreckten Beinen senkst du die Hanteln entlang der Beine — dehnt und kräftigt die Beinrückseite.",
         "setup": "Leichte Kniebeugung, Hüfte nach hinten schieben, Rücken gerade.",
         "warn": "Rücken immer gerade, Hanteln nah am Bein führen.",
         "wtxt": "Leicht starten: ~2×5–8 kg, Technik ist alles."},
        {"name": "Beinbeuger am Band", "m": "Beinrückseite",
         "desc": "Im Stehen beugst du ein Bein gegen ein Band — trainiert die Beinrückseite ohne Maschine.",
         "setup": "Band am Knöchel, festhalten, Oberschenkel ruhig lassen.",
         "warn": "Langsam beugen und strecken, kein Schwung.",
         "wtxt": "Widerstand leicht wählen."},
    ],
    "Beinstrecker": [
        {"name": "Goblet-Squat", "m": "Beinvorderseite",
         "desc": "Kniebeuge mit Kurzhantel vor der Brust — kräftigt die Oberschenkelvorderseite.",
         "setup": "Füße schulterbreit, aufrecht, Hantel am Körper.",
         "warn": "Knie in Richtung Zehen, sauber tief gehen.",
         "wtxt": "Leichte Kurzhantel ~6–10 kg."},
        {"name": "Ausfallschritte", "m": "Beinvorderseite",
         "desc": "Großer Schritt nach vorn, hinteres Knie senken — fordert die vordere Oberschenkelmuskulatur.",
         "setup": "Aufrecht, beide Knie ~90°.",
         "warn": "Vorderes Knie über dem Fuß halten.",
         "wtxt": "Erst Körpergewicht, dann leichte Hanteln."},
    ],
    "Bauchmaschine": [
        {"name": "Crunches", "m": "Bauch",
         "desc": "Auf der Matte rollst du den Oberkörper ein — klassisches Bauchtraining ohne Gerät.",
         "setup": "Auf dem Rücken, Beine angewinkelt, Hände an den Schläfen.",
         "warn": "Aus dem Bauch einrollen, nicht am Kopf/Nacken ziehen.",
         "wtxt": "Nur Körpergewicht."},
        {"name": "Plank (Unterarmstütz)", "m": "Bauch",
         "desc": "Du hältst den Körper im Unterarmstütz gerade — stärkt die ganze Rumpfmitte.",
         "setup": "Ellbogen unter den Schultern, Körper in einer Linie.",
         "warn": "Hüfte nicht durchhängen oder hochschieben; mit 15–20 Sek. starten.",
         "wtxt": "Nur Körpergewicht, Haltezeit langsam steigern."},
    ],
    "Butterfly (Brust)": [
        {"name": "Kurzhantel-Fliegende", "m": "Brust",
         "desc": "Liegend führst du zwei Kurzhanteln im Bogen über der Brust zusammen — isoliert die Brust.",
         "setup": "Flach auf der Bank, Arme leicht gebeugt, weiter Bogen.",
         "warn": "Nicht zu tief, kontrolliert — schont die Schultern.",
         "wtxt": "Leicht: ~2×3–6 kg."},
        {"name": "Liegestütze", "m": "Brust",
         "desc": "Liegestütze mit Körpergewicht treffen die Brust ganz ohne Gerät.",
         "setup": "Hände etwas breiter als schulterbreit, Körper gerade.",
         "warn": "Hüfte gerade halten; auf den Knien leichter.",
         "wtxt": "Nur Körpergewicht."},
    ],
    "Bizeps-Curl (Maschine)": [
        {"name": "Kurzhantel-Curls", "m": "Bizeps",
         "desc": "Im Stehen beugst du Kurzhanteln zur Schulter — baut den Bizeps auf.",
         "setup": "Ellbogen am Körper, Oberarme ruhig halten.",
         "warn": "Nicht mit dem Rücken schwingen, kontrolliert beugen.",
         "wtxt": "Start ~2×4–7 kg."},
        {"name": "Langhantel-Curls", "m": "Bizeps",
         "desc": "Mit einer Langhantel beugst du beide Arme gemeinsam — der Bizeps-Klassiker.",
         "setup": "Schulterbreiter Untergriff, Ellbogen am Körper.",
         "warn": "Rücken gerade, kein Schwung aus der Hüfte.",
         "wtxt": "Leere oder leichte Stange zum Start."},
    ],
    "Trizepsdrücken (Kabel)": [
        {"name": "Trizeps-Dips (Bank)", "m": "Trizeps",
         "desc": "Hände auf einer Bank hinter dir, du senkst und drückst den Körper — Trizeps mit Körpergewicht.",
         "setup": "Hände schulterbreit auf der Bankkante, Füße vor dir.",
         "warn": "Nur so tief, wie die Schulter schmerzfrei bleibt.",
         "wtxt": "Körpergewicht; Beine anwinkeln = leichter."},
        {"name": "Kurzhantel-Überkopf-Trizeps", "m": "Trizeps",
         "desc": "Eine Kurzhantel hinter dem Kopf strecken — formt die Rückseite des Oberarms.",
         "setup": "Ellbogen zeigen nach vorn-oben, Oberarme ruhig.",
         "warn": "Ellbogen eng lassen, langsam absenken.",
         "wtxt": "Leicht: ~1×4–8 kg."},
    ],
}


def alt_info(base, alt_name):
    """Alternativ-Übung (Dict) zu einer Basis-Übung finden – oder None."""
    for a in ALTS.get(base, []):
        if a["name"] == alt_name:
            return a
    return None


def difficulty():
    """3x 'zu leicht' -> Progressive Overload; 'zu schwer' -> leichter."""
    easy = 0
    for d in sorted(ss.feedback):
        fb = ss.feedback[d]
        easy = easy + 1 if fb == "zu leicht" else 0
    base = 1.0 + 0.06 * min(easy, 5)
    hard = sum(1 for v in ss.feedback.values() if v == "zu schwer")
    return max(0.85, base - 0.05 * min(hard, 3))


def overload_ready():
    """True, wenn 3x in Folge 'zu leicht' -> Gewicht erhöhen."""
    seq = [ss.feedback[d] for d in sorted(ss.feedback)]
    run = 0
    for f in seq:
        run = run + 1 if f == "zu leicht" else 0
    return run >= 3


# Strukturierte Trainingseinheiten (gezielte Muskelgruppen statt bloßer Rotation)
SESSIONS = {
    "Ganzkörper A": ["Beinpresse", "Brustpresse (Maschine)", "Latzug (Kabelzug)", "Bauchmaschine"],
    "Ganzkörper B": ["Beinbeuger", "Schulterpresse (Maschine)", "Rudern (Maschine)", "Beinstrecker"],
    "Push (Drücken)": ["Brustpresse (Maschine)", "Schulterpresse (Maschine)", "Butterfly (Brust)", "Trizepsdrücken (Kabel)"],
    "Pull (Ziehen)": ["Latzug (Kabelzug)", "Rudern (Maschine)", "Bizeps-Curl (Maschine)"],
    "Beine": ["Beinpresse", "Beinbeuger", "Beinstrecker", "Bauchmaschine"],
    "Oberkörper": ["Brustpresse (Maschine)", "Latzug (Kabelzug)", "Schulterpresse (Maschine)",
                   "Rudern (Maschine)", "Bizeps-Curl (Maschine)", "Trizepsdrücken (Kabel)"],
    "Unterkörper": ["Beinpresse", "Beinbeuger", "Beinstrecker", "Bauchmaschine"],
}
WD = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]


def plan_sessions():
    """Welche Einheiten rotiert werden — je nach Trainingstagen pro Woche."""
    d = ss.profile.get("days", 3)
    if d <= 3:
        return ["Ganzkörper A", "Ganzkörper B"]          # Anfänger: Ganzkörper = bester Muskelaufbau
    if d == 4:
        return ["Oberkörper", "Unterkörper"]             # Upper/Lower-Split
    return ["Push (Drücken)", "Pull (Ziehen)", "Beine"]  # Push/Pull/Legs


def training_day_number(day):
    """Wievielte Trainingseinheit ist dieser Journey-Tag (für Progression & Rotation)."""
    return sum(1 for d in range(4, day + 1) if is_training_day(d))


def session_for(day):
    sess = plan_sessions()
    idx = max(0, training_day_number(day) - 1)
    return sess[idx % len(sess)]


def exercises_for(day):
    return [n for n in SESSIONS[session_for(day)] if n in EXERCISES]


def workout_exercises(day):
    """Übungen eines (auch vergangenen) Tages — KI-Wahl wenn vorhanden, sonst regelbasiert."""
    w = ss.get("ai_workout", {}).get(day)
    if w and w.get("exercises"):
        return [e for e in w["exercises"] if e in EXERCISES]
    return exercises_for(day)


def recent_sessions(day, n=4):
    """Muskelgruppen der letzten Trainingseinheiten (neueste zuerst) — für Balance."""
    out = []
    for d in range(day - 1, 3, -1):
        if is_training_day(d):
            muscles = list(dict.fromkeys(EXERCISES[e]["m"] for e in workout_exercises(d)))
            out.append(muscles)
            if len(out) >= n:
                break
    return out


def ai_workout(day):
    """Wählt das heutige Workout adaptiv: KI prüft Stand & zuletzt trainierte Muskeln."""
    cache = ss.setdefault("ai_workout", {})
    if day in cache:
        return cache[day]
    default = {"name": session_for(day), "exercises": exercises_for(day), "focus": "", "reason": ""}
    wish = (ss.get("workout_wish", {}).get(day) or "").strip()
    if get_key():
        p = ss.profile
        tnum = training_day_number(day)
        hist = recent_sessions(day)
        hist_txt = " | ".join(", ".join(m) for m in hist) if hist else "noch keine"
        avail = "; ".join(f"{k} ({v['m']})" for k, v in EXERCISES.items())
        wish_txt = (f"\nWICHTIG – der Nutzer hat heute einen konkreten Wunsch: „{wish}“. "
                    "Erfülle diesen Wunsch so gut es geht (z.B. gewünschte Muskelgruppe betonen), "
                    "bleib dabei aber bei sinnvollem, sicherem Training. Erwähne den Wunsch kurz im 'reason'.\n"
                    if wish else "")
        prompt = (
            "Du bist ein erfahrener Kraft- und Reha-Coach. Plane das heutige Workout durchdacht.\n"
            f"Person: {p['exp']}, Ziel {p['goal']}, trainiert {p['days']}× pro Woche, heute Trainingseinheit Nr. {tnum}.\n"
            f"Letzte Einheiten (Muskelgruppen, neueste zuerst): {hist_txt}.\n"
            f"{wish_txt}"
            "Überlege wie ein Profi: In welcher Phase steht die Person? Welche Muskelgruppen wurden "
            "zuletzt vernachlässigt und sind heute dran (ausgewogene Erholung, jede Gruppe regelmäßig)? "
            "Wähle 4–5 Übungen AUSSCHLIESSLICH aus dieser Liste (exakte Namen verwenden):\n"
            f"{avail}\n"
            'Antworte NUR als JSON: {"name":"kurzer Sessionname","exercises":["exakte Namen"],'
            '"focus":"Zielmuskeln heute","reason":"1-2 Sätze per Du, warum genau diese Übungen heute dran sind"}'
        )
        data = _openai({"model": MODEL_WORKOUT, "temperature": 0.5,
                        "response_format": {"type": "json_object"},
                        "messages": [
                            {"role": "system", "content": "Du planst sorgfältig und antwortest ausschließlich mit gültigem JSON."},
                            {"role": "user", "content": prompt}]})
        if data:
            try:
                r = json.loads(data["choices"][0]["message"]["content"])
                ex = [e for e in r.get("exercises", []) if e in EXERCISES]
                if 3 <= len(ex) <= 6:
                    default = {"name": r.get("name") or session_for(day), "exercises": ex,
                               "focus": r.get("focus", ""), "reason": r.get("reason", "")}
            except Exception:
                pass
    cache[day] = default
    return default


def sets_reps(day):
    n = training_day_number(day)
    sets = 2 if n <= 3 else 3
    reps = int(round((10 + n // 3) * difficulty()))
    return sets, max(8, min(reps, 15))


# --- Gesunde Startgewichts-Empfehlung (personalisiert, konservativ) -----------
SEX_F = {"Männlich": 1.0, "Weiblich": 0.65, "Divers": 0.82}
EXP_F = {"Noch nie im Gym": 0.85, "Kurz reingeschaut": 1.0, "Leichte Erfahrung": 1.12}


def round25(x):
    """Auf 2,5-kg-Schritte runden (typische Geräte-/Hantelstufen)."""
    return max(2.5, round(x / 2.5) * 2.5)


def fmt_kg(x):
    return f"{x:g}"


def start_weight(name):
    """Empfohlener Start-Kilobereich (lo, hi) für eine Maschinen-Übung, sonst None.
    Basis: Körpergewicht × muskelabhängiger Anteil, skaliert nach Geschlecht,
    Erfahrung und aktuellem Fortschritt (difficulty). Bewusst eher niedrig."""
    wf = START_WF.get(name)
    if not wf:
        return None
    p = ss.profile
    f = SEX_F.get(p["sex"], 1.0) * EXP_F.get(p["exp"], 1.0) * difficulty()
    lo = round25(p["weight"] * wf[0] * f)
    hi = round25(p["weight"] * wf[1] * f)
    if hi <= lo:
        hi = lo + 2.5
    return lo, hi


def yt_search(name):
    """Zuverlässiger YouTube-Such-Link (statt evtl. falschem Embed) für Alternativen."""
    return "https://www.youtube.com/results?search_query=" + urllib.parse.quote(
        f"{name} richtig ausführen Anfänger")


# Trainingsrhythmus (Fallback, falls keine Wochentage gewählt)
TRAIN_SLOTS = {2: {0, 3}, 3: {0, 2, 4}, 4: {0, 1, 3, 4}, 5: {0, 1, 2, 3, 4}}


def weekday_of(day):
    if not ss.start_date:
        return (day - 1) % 7
    return (ss.start_date + datetime.timedelta(days=day - 1)).weekday()


def is_training_day(day):
    if day <= 3:
        return False
    td = ss.profile.get("train_days")
    if td:
        return weekday_of(day) in td   # strikt nach den gewählten Wochentagen
    idx = (day - 4) % 7
    return idx in TRAIN_SLOTS.get(ss.profile.get("days", 3), {0, 2, 4})


def first_training_day():
    """Erster Journey-Tag ab Tag 4, der auf einen gewählten Wochentag fällt —
    das ist der geführte 'Erste echte Übungen'-Tag."""
    for d in range(4, 4 + 21):
        if is_training_day(d):
            return d
    return 4


# =============================================================================
# STATISCHER WISSENS-CONTENT
# =============================================================================
ETIKETTE = [
    ("🧼", "Geräte abwischen", "Nach jeder Übung Schweiß mit dem Handtuch/Spray entfernen."),
    ("🏋️", "Gewichte zurückräumen", "Hanteln und Scheiben zurück an ihren Platz."),
    ("⏳", "Nicht blockieren", "Zwischen den Sätzen andere ranlassen, nicht am Handy sitzen bleiben."),
    ("🤝", "Fragen ist okay", "Jeder war mal Anfänger. Personal fragt man ohne schlechtes Gewissen."),
    ("👀", "Niemand schaut", "Alle sind mit sich selbst beschäftigt — wirklich."),
]
SUPPLEMENTS = [
    ("✅", "Protein-Pulver", "Sinnvoll, wenn du dein Protein-Ziel über Essen nicht erreichst. Kein Muss."),
    ("✅", "Kreatin (3–5 g/Tag)", "Das am besten erforschte Supplement. Günstig, wirkt, sicher."),
    ("🟡", "Koffein", "Vor dem Training okay für mehr Fokus. Nicht spät am Tag."),
    ("❌", "Fatburner", "Rausgeschmissenes Geld. Bringt fast nichts."),
    ("❌", "BCAAs", "Überflüssig, wenn du genug Protein isst."),
]
REGEN = [
    ("😴", "Schlaf", "7–9 Stunden. Muskeln wachsen in der Pause, nicht im Training."),
    ("🦵", "Muskelkater", "Leichter Kater ist okay. Scharfer/stechender Schmerz = Pause."),
    ("💧", "Trinken", "2–3 Liter Wasser über den Tag verteilt."),
    ("🧘", "Ruhetage", "Mindestens 1–2 pro Woche. Dein Körper braucht die Erholung."),
]
BAG_ITEMS = ["🧻 Handtuch", "💧 Wasserflasche", "👟 Sportschuhe",
             "👕 Sportklamotten", "🔒 Schloss für den Spind", "🎧 Kopfhörer (optional)"]


# =============================================================================
# KI — je Aufgabe wählbares Modell, mit statischem Fallback ohne Key
# =============================================================================
# Stärkeres Modell für die "denkintensiven" Aufgaben (Übungsauswahl, Kalorien),
# schnelles/günstiges für Text (Coaching & Mahlzeiten). Namen einfach hier ändern.
#   Optionen z.B.: "gpt-5", "gpt-5-mini", "gpt-4o-mini", "gpt-4.1", "gpt-4.1-mini"
MODEL_WORKOUT = "gpt-5-mini"    # Workout-Auswahl (überlegt mehr mit)
MODEL_CALORIES = "gpt-5-mini"   # Kalorien-/Makroberechnung
MODEL_TEXT = "gpt-4o-mini"      # Coaching-Text & Mahlzeiten


def get_key():
    """Key robust holen: erst Session, dann Streamlit-Secrets (Cloud)."""
    k = (ss.get("api_key") or "").strip()
    if k:
        return k
    try:
        s = st.secrets.get("OPENAI_API_KEY", "")
        if s:
            return str(s).strip()
    except Exception:
        pass
    return ""


def key_source():
    if (ss.get("api_key") or "").strip():
        return "App-Eingabe"
    try:
        if st.secrets.get("OPENAI_API_KEY", ""):
            return "Streamlit-Secrets"
    except Exception:
        pass
    return None


def _is_reasoning(model):
    """Reasoning-Modelle (gpt-5*, o1/o3/o4*) akzeptieren keine freie temperature
    und nutzen andere Token-Parameter."""
    return model.startswith("gpt-5") or model[:2] in ("o1", "o3", "o4")


def _openai(payload):
    key = get_key()
    if not key:
        ss["_last_ai_error"] = "Kein API-Key gefunden."
        return None
    # Reasoning-Modelle vertragen kein temperature != 1 -> sonst 400-Fehler.
    if _is_reasoning(payload.get("model", "")):
        payload.pop("temperature", None)
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + key},
        method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            ss["_last_ai_error"] = ""
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode()
        except Exception:
            body = ""
        ss["_last_ai_error"] = f"HTTP {e.code} bei „{payload.get('model','?')}“: {body[:400]}"
        return None
    except Exception as e:
        ss["_last_ai_error"] = f"{type(e).__name__}: {e}"
        return None


# Mahlzeiten-Pool je Slot – rotiert pro Tag, damit nicht immer dasselbe erscheint.
MEAL_DIST = [.28, .12, .35, .25]
MEAL_POOL = [
    [  # Frühstück
        ("🥣", "Haferflocken + Skyr + Beeren", "Proteinreicher Start"),
        ("🍳", "Rührei mit Vollkornbrot", "Herzhaft & sättigend"),
        ("🥛", "Magerquark mit Banane & Honig", "Cremig, viel Protein"),
        ("🥐", "Porridge mit Nüssen & Apfel", "Warm & energiereich"),
        ("🍌", "Protein-Smoothie (Banane, Hafer, Milch)", "Schnell für unterwegs"),
        ("🧇", "Vollkorn-Pancakes mit Quark", "Sattmacher am Morgen"),
    ],
    [  # Snack
        ("🥜", "Nüsse + Apfel", "Schneller Snack"),
        ("🍌", "Banane + Handvoll Mandeln", "Energie-Kick"),
        ("🧀", "Käsewürfel + Vollkorncracker", "Herzhafter Snack"),
        ("🥕", "Gemüsesticks + Hummus", "Leicht & knackig"),
        ("🍏", "Skyr + Beeren", "Proteinreicher Snack"),
        ("🥚", "2 gekochte Eier", "Purer Protein-Snack"),
    ],
    [  # Mittagessen
        ("🍗", "Hähnchen/Tofu, Reis & Gemüse", "Klassiker fürs Ziel"),
        ("🍝", "Vollkornnudeln, Hack-Tomatensauce", "Sättigend & einfach"),
        ("🌯", "Wrap mit Pute/Tofu & Salat", "Schnell & handlich"),
        ("🍚", "Bowl: Reis, Bohnen, Avocado", "Pflanzlich & satt"),
        ("🥔", "Kartoffeln mit Magerquark & Kräutern", "Einfach & proteinreich"),
        ("🍲", "Chili sin/con Carne", "Warm & eiweißreich"),
    ],
    [  # Abendessen
        ("🐟", "Lachs/Tofu + Kartoffeln", "Protein + gute Fette"),
        ("🥗", "Großer Salat mit Ei & Thunfisch", "Leicht am Abend"),
        ("🍲", "Gemüsepfanne mit Hähnchen/Tempeh", "Warm & bunt"),
        ("🍳", "Omelett mit Gemüse", "Schnell & leicht"),
        ("🫘", "Linsen-Curry mit Reis", "Pflanzlich & herzhaft"),
        ("🥩", "Steak/Halloumi mit Ofengemüse", "Deftig & proteinreich"),
    ],
]


def static_meals(m, day=1):
    out = []
    for i, pool in enumerate(MEAL_POOL):
        e, t, b = pool[(day + i) % len(pool)]   # +i: Slots rotieren versetzt
        out.append(dict(emoji=e, titel=t, beschreibung=b,
                        kcal=round(m["kcal"] * MEAL_DIST[i]),
                        protein=round(m["protein"] * MEAL_DIST[i])))
    return out


def static_coaching(day):
    p = ss.profile
    stk = streak()
    if stk >= 7:
        return f"Über eine Woche am Stück — das schaffen die wenigsten! Du bist längst dabei, {p['goal'].lower()} zur Gewohnheit zu machen."
    if day == 1:
        return "Willkommen. Heute geht's nur ums Ankommen im Kopf — kein Training, kein Druck. Ein Schritt nach dem anderen."
    if stk >= 3:
        return f"{stk} Tage Streak 🔥 Du bleibst dran — genau so entsteht Fortschritt. Weiter im Tempo."
    return "Schön, dass du da bist. Heute machst du einfach deinen nächsten kleinen Schritt. Mehr braucht es nicht."


def ai_day(day):
    """Gibt {coaching, meals} zurück – KI wenn Key da, sonst statisch."""
    if day in ss.ai_cache:
        return ss.ai_cache[day]
    p, m = ss.profile, plan()
    result = {"coaching": static_coaching(day), "meals": static_meals(m, day), "ai": False}
    if get_key():
        goal = p["goal"]
        prompt = (
            f"Person: {p['age']} J, {p['sex']}, {p['weight']}kg, {p['height']}cm, "
            f"Körpertyp {p['bodytype']}, Ziel {goal}, Erfahrung {p['exp']}, Streak {streak()} Tage, "
            f"heute Journey-Tag {day}. Tagesziel exakt: {m['kcal']} kcal, {m['protein']}g Protein, "
            f"{m['carbs']}g Carbs, {m['fat']}g Fett (VERWENDE GENAU DIESE ZAHLEN).\n"
            "Variiere die Gerichte von Tag zu Tag – wiederhole nicht ständig dieselben Mahlzeiten, "
            "biete abwechslungsreiche, alltagstaugliche Ideen.\n"
            "Gib JSON: {\"coaching\":\"2-3 warme, motivierende Sätze, per Du, persönlich\","
            "\"meals\":[{\"emoji\":\"🍳\",\"titel\":\"...\",\"beschreibung\":\"max 6 Wörter\","
            "\"kcal\":Zahl,\"protein\":Zahl}]}. Genau 4 Mahlzeiten, deutsche Texte.")
        data = _openai({"model": MODEL_TEXT, "temperature": 0.85,
                        "response_format": {"type": "json_object"},
                        "messages": [
                            {"role": "system", "content": "Du bist ein warmer Fitness-Coach für Anfänger. Antworte nur mit gültigem JSON."},
                            {"role": "user", "content": prompt}]})
        if data:
            try:
                parsed = json.loads(data["choices"][0]["message"]["content"])
                if parsed.get("coaching"):
                    result["coaching"] = parsed["coaching"]
                if parsed.get("meals"):
                    result["meals"] = parsed["meals"]
                result["ai"] = True
            except Exception:
                pass
    ss.ai_cache[day] = result
    return result


# =============================================================================
# ZEIT / STREAK / GYMS
# =============================================================================
def current_day():
    if not ss.start_date:
        return 1
    return max(1, (datetime.date.today() - ss.start_date).days + 1 + ss.day_offset)


def streak():
    best = run = 0
    for i in range(1, current_day() + 1):
        run = run + 1 if i in ss.completed else 0
        best = max(best, run)
    return best


def card(html):
    st.markdown(f"<div class='card'>{html}</div>", unsafe_allow_html=True)


# =============================================================================
# ONBOARDING / RESULT / TRAININGSTAGE / COMMIT
# =============================================================================
def view_onboarding():
    st.markdown("# Gym<span style='color:#FF7A1A'>Start</span>", unsafe_allow_html=True)
    st.markdown("#### Erzähl uns von dir")
    st.caption("Damit wir alles exakt für dich berechnen — jeder erlebt eine andere App.")
    p = ss.profile
    st.caption("Tippe deine Werte einfach ein.")
    c1, c2 = st.columns(2)
    p["weight"] = c1.number_input("Gewicht (kg)", 35, 250, int(p["weight"]))
    p["height"] = c2.number_input("Größe (cm)", 130, 220, int(p["height"]))
    c3, c4 = st.columns(2)
    p["age"] = c3.number_input("Alter", 14, 90, int(p["age"]))
    p["sex"] = c4.selectbox("Geschlecht", ["Männlich", "Weiblich", "Divers"],
                            index=["Männlich", "Weiblich", "Divers"].index(p["sex"]))
    p["bodytype"] = st.selectbox("Körpertyp", ["Sehr dünn", "Normal", "Übergewichtig"],
                                 index=["Sehr dünn", "Normal", "Übergewichtig"].index(p["bodytype"]))
    p["goal"] = st.selectbox("Dein Ziel", ["Muskeln aufbauen", "Abnehmen", "Fitter werden", "Allgemeine Gesundheit"],
                             index=["Muskeln aufbauen", "Abnehmen", "Fitter werden", "Allgemeine Gesundheit"].index(p["goal"]))
    p["exp"] = st.selectbox("Gym-Erfahrung", ["Noch nie im Gym", "Kurz reingeschaut", "Leichte Erfahrung"],
                            index=["Noch nie im Gym", "Kurz reingeschaut", "Leichte Erfahrung"].index(p["exp"]))
    st.divider()
    if st.button("Plan berechnen ✨", type="primary"):
        if not ss.weight_log:
            ss.weight_log = [(datetime.date.today().isoformat(), p["weight"])]
        ss.pop("plan", None)
        ss.phase = "result"
        st.rerun()


def view_result():
    p = ss.profile
    with st.spinner("🤖 Dein Coach berechnet deinen Bedarf … (kann bis zu 1 Minute dauern)"):
        m = plan()
    st.markdown("<div class='badge'>🎯 Auf dich zugeschnitten</div>", unsafe_allow_html=True)
    st.markdown("## Dein Plan steht.")
    src = "🤖 Von deinem KI-Coach berechnet" if m.get("ai") else "📐 Berechnet (Mifflin-St Jeor)"
    card(f"<div style='text-align:center'><div class='muted' style='letter-spacing:1px;font-size:12px'>DEIN TAGESZIEL</div>"
         f"<div class='kcal'>{m['kcal']}</div><div class='muted'>kcal / Tag · {p['goal']}</div>"
         f"<div style='display:flex;justify-content:space-around;margin-top:16px'>"
         f"<div><div style='font-weight:800;color:#27AE60'>{m['protein']}g</div><div class='muted' style='font-size:11px'>PROTEIN</div></div>"
         f"<div><div style='font-weight:800;color:#FF7A1A'>{m['carbs']}g</div><div class='muted' style='font-size:11px'>CARBS</div></div>"
         f"<div><div style='font-weight:800;color:#C79A2E'>{m['fat']}g</div><div class='muted' style='font-size:11px'>FETT</div></div></div>"
         f"<div class='muted' style='font-size:11px;margin-top:12px'>{src}</div></div>")
    if m.get("reason"):
        st.markdown(f"<div class='tip'>💡 <b>So hat dein Coach gerechnet:</b> {m['reason']}</div>", unsafe_allow_html=True)
    card(f"<h3>🏋️ Dein Trainingsplan</h3><b>{plan_name(p)}</b><br>"
         f"<span class='pill'>{p['days']}× / Woche</span><span class='pill'>Start: Maschinen</span>"
         f"<span class='pill'>Progressive Overload</span>")
    if st.button("Weiter →", type="primary"):
        ss.phase = "days"
        st.rerun()


def days_editor(key):
    """Wochentag-Auswahl über 7 Umschalt-Buttons (robuster als Multiselect).
    Gibt True zurück, wenn gültig (≥2 Tage gewählt)."""
    p = ss.profile
    cur = set(p.get("train_days", [0, 2, 4]))
    st.markdown("<div class='muted' style='font-size:14px;margin-bottom:6px'>An welchen Tagen willst du ins Gym? "
                "(Tippe die Tage an)</div>", unsafe_allow_html=True)
    cols = st.columns(7)
    for i, wd in enumerate(WD):
        sel = i in cur
        if cols[i].button(wd, key=f"{key}_{i}", type="primary" if sel else "secondary"):
            if sel:
                cur.discard(i)
            else:
                cur.add(i)
            idx = sorted(cur)
            p["train_days"] = idx
            p["days"] = max(1, len(idx))
            ss.pop("plan", None)
            st.rerun()
    if len(cur) >= 2:
        return True
    st.warning("Bitte wähle mindestens 2 Trainingstage.")
    return False


def view_days():
    st.markdown("## Deine Trainingstage")
    st.caption("An welchen Wochentagen willst du trainieren? Danach richtet sich dein ganzer Wochenplan — "
               "und die Übungen passen sich an, je nachdem was du zuletzt trainiert hast.")
    ok = days_editor("days_pick")
    if ok:
        m = plan()
        st.markdown(f"<div class='tip'>👍 <b>{ss.profile['days']}× pro Woche.</b> Dein Tagesziel: "
                    f"<b>{m['kcal']} kcal</b> · {m['protein']} g Protein.</div>", unsafe_allow_html=True)
    st.divider()
    if st.button("Weiter →", type="primary", disabled=not ok):
        ss.phase = "commit"
        st.rerun()


def view_commit():
    p = ss.profile
    tage = ", ".join(WD[i] for i in p.get("train_days", []))
    st.markdown("<div style='text-align:center;margin-top:26px;font-size:60px'>🔥</div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center'>Du bist bereit.</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center'>Deine Journey beginnt <b>heute</b>. Kein Druck — ein Tag nach dem anderen.</p>", unsafe_allow_html=True)
    card(f"<span class='muted' style='font-size:13px'>Deine Trainingstage</span><br><b style='font-size:16px'>{tage}</b>"
         f"<br><span class='muted' style='font-size:13px'>Die ersten 14 Tage sind komplett kostenlos.</span>")
    if st.button("Journey starten 🚀", type="primary"):
        ss.phase = "journey"
        ss.start_date = datetime.date.today()
        st.rerun()


# =============================================================================
# JOURNEY – Menü + Tagesinhalt
# =============================================================================
NAV_LABELS = ["📅 Heute", "🗓 Woche", "📚 Wissen", "📊 Fortschritt", "⚙️ Menü"]
NAV_VIEWS = ["Heute", "Woche", "Wissen", "Fortschritt", "Menü"]


def top_nav():
    st.markdown("### Gym<span style='color:#FF7A1A'>Start</span>", unsafe_allow_html=True)
    # Programmatischen Ansichtswechsel (z.B. via goto_today) VOR dem Radio anwenden,
    # damit Navigations-Markierung und Inhalt immer synchron sind.
    pending = ss.pop("pending_view", None)
    if pending in NAV_VIEWS:
        ss.nav_choice = NAV_LABELS[NAV_VIEWS.index(pending)]
    if ss.get("nav_choice") not in NAV_LABELS:
        ss.nav_choice = NAV_LABELS[NAV_VIEWS.index(ss.get("view", "Heute"))]
    st.radio("nav", NAV_LABELS, key="nav_choice", horizontal=True, label_visibility="collapsed")
    ss.view = NAV_VIEWS[NAV_LABELS.index(ss.nav_choice)]
    st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True)


def day_tracker(day):
    dots = ""
    for i in range(max(1, day - 3), day + 4):
        cls = "done" if i in ss.completed else "today" if i == day else ""
        label = "✓" if i in ss.completed else ("🔒" if i > day else str(i))
        dots += f"<div class='dot {cls}'>{label}</div>"
    st.markdown(f"<div class='dots'>{dots}</div>", unsafe_allow_html=True)


def render_meals(m, meals):
    html = (f"<h3>🍽️ Ernährung heute · {m['kcal']} kcal</h3>"
            f"<div style='display:flex;justify-content:space-around;margin:2px 0 6px'>"
            f"<div><div style='font-weight:800;color:#27AE60'>{m['protein']}g</div><div class='muted' style='font-size:11px'>PROTEIN</div></div>"
            f"<div><div style='font-weight:800;color:#FF7A1A'>{m['carbs']}g</div><div class='muted' style='font-size:11px'>CARBS</div></div>"
            f"<div><div style='font-weight:800;color:#C79A2E'>{m['fat']}g</div><div class='muted' style='font-size:11px'>FETT</div></div></div>")
    for x in meals:
        html += (f"<div class='meal'><span class='mi'>{x.get('emoji','🍽️')}</span>"
                 f"<div><div class='mt'>{x.get('titel','')}</div><div class='md'>{x.get('beschreibung','')}</div></div>"
                 f"<div class='mk'>{x.get('kcal','')} kcal<br>{x.get('protein','')}g P</div></div>")
    card(html)


def render_exercise(day, i, base_name, sets, reps):
    """Eine Übung darstellen — inkl. Startgewicht und Alternativ-Auswahl,
    falls das Gerät im Gym fehlt. Ein Swap ersetzt die Übung nur für heute."""
    key = f"{day}|{base_name}"
    swap = ss.swaps.get(key)
    info = alt_info(base_name, swap) if swap else EXERCISES[base_name]
    if info is None:                       # Swap-Ziel nicht gefunden -> Original
        swap, info = None, EXERCISES[base_name]
    name = swap or base_name
    tag = " · Alternative" if swap else ""
    st.markdown(f"**{i}. {name}**{tag} · _{info['m']}_")
    st.markdown(f"<div class='setpill'>🔁 {sets} Sätze × {reps} Wiederholungen · ⏱ ~90 Sek. Pause</div>",
                unsafe_allow_html=True)
    sw = start_weight(name)
    if sw:
        st.markdown(f"<div class='muted' style='font-size:13px;margin:-4px 0 8px'>🏋️ Startgewicht ≈ "
                    f"<b>{fmt_kg(sw[0])}–{fmt_kg(sw[1])} kg</b> · taste dich langsam heran</div>",
                    unsafe_allow_html=True)
    elif info.get("wtxt"):
        st.markdown(f"<div class='muted' style='font-size:13px;margin:-4px 0 8px'>🏋️ {info['wtxt']}</div>",
                    unsafe_allow_html=True)
    if info.get("vid"):
        st.video(f"https://www.youtube.com/watch?v={info['vid']}")
        st.markdown(f"<a href='https://www.youtube.com/watch?v={info['vid']}' target='_blank' "
                    f"style='font-size:12px;color:#8A7E73;text-decoration:none'>Video lädt nicht? ▶️ Auf YouTube ansehen</a>",
                    unsafe_allow_html=True)
    else:
        st.markdown(f"<a href='{yt_search(name)}' target='_blank' "
                    f"style='color:#C2410C;font-weight:600;text-decoration:none'>▶️ {name} auf YouTube ansehen</a>",
                    unsafe_allow_html=True)
    st.markdown(f"<div class='tip'>✅ <b>Einstellung:</b> {info['setup']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='warn'>⚠️ {info['warn']}</div>", unsafe_allow_html=True)
    alts = ALTS.get(base_name, [])
    if alts:
        open_key = f"swopen_{key}"
        if st.button("🔄 Dieses Gerät hast du nicht? Alternative wählen", key=f"swbtn_{key}"):
            ss[open_key] = not ss.get(open_key, False)
            st.rerun()
        if ss.get(open_key):
            st.caption("Wähle, was dein Gym hat — alle trainieren denselben Muskel.")
            if st.button(f"{'✓ ' if not swap else ''}{base_name} (Original-Gerät)", key=f"sw0_{key}",
                         type="primary" if not swap else "secondary"):
                ss.swaps.pop(key, None)
                st.rerun()
            for a in alts:
                sel = swap == a["name"]
                if st.button(f"{'✓ ' if sel else ''}{a['name']}", key=f"sw_{key}_{a['name']}",
                             type="primary" if sel else "secondary"):
                    ss.swaps[key] = a["name"]
                    st.rerun()
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)


def workout_block(day):
    sets, reps = sets_reps(day)
    w = ai_workout(day)
    ex = [e for e in w["exercises"] if e in EXERCISES] or exercises_for(day)
    focus = w.get("focus") or " · ".join(dict.fromkeys(EXERCISES[n]["m"] for n in ex))
    st.markdown(f"### 🏋️ {w['name']}")
    st.markdown(f"<div class='badge'>Heute: {focus}</div>", unsafe_allow_html=True)
    if w.get("reason"):
        st.markdown(f"<div class='tip'>🤖 <b>Warum heute diese Übungen:</b> {w['reason']}</div>", unsafe_allow_html=True)

    # Eigener Wunsch: „Heute will ich lieber …“ — Coach passt das Workout an (nur mit KI-Key)
    if get_key():
        cur_wish = ss.get("workout_wish", {}).get(day, "")
        wt = st.text_input("🎯 Heute lieber etwas Bestimmtes üben? (optional)", value=cur_wish,
                           key=f"wish_in_{day}",
                           placeholder="z.B. „mehr Beine“, „Fokus Bauch“, „kein Rücken heute“, „nur Oberkörper“")
        c1, c2 = st.columns(2)
        if c1.button("Workout anpassen ✨", key=f"wish_go_{day}", type="primary"):
            ss.setdefault("workout_wish", {})[day] = (wt or "").strip()
            ss.get("ai_workout", {}).pop(day, None)   # mit Wunsch neu generieren
            st.rerun()
        if cur_wish and c2.button("Wunsch zurücksetzen", key=f"wish_clr_{day}"):
            ss.setdefault("workout_wish", {})[day] = ""
            ss.get("ai_workout", {}).pop(day, None)
            st.rerun()
        if cur_wish:
            st.markdown(f"<div class='tip'>🎯 <b>Dein Wunsch heute:</b> „{cur_wish}“ — dein Coach hat das Workout darauf abgestimmt.</div>",
                        unsafe_allow_html=True)

    st.caption("Aufwärmen: 5 Min lockeres Cardio, dann bei jeder Übung 1 leichter Aufwärmsatz.")
    st.markdown("<div class='tip'>ℹ️ <b>Was bedeutet Sätze × Wiederholungen?</b> Eine <b>Wiederholung</b> ist eine "
                "komplette Bewegung. Ein <b>Satz</b> ist eine Runde am Stück — danach 1–2 Min Pause, dann der nächste Satz.</div>",
                unsafe_allow_html=True)
    st.markdown("<div class='tip'>🏋️ <b>Wie viel Gewicht?</b> Die Kilo-Angaben sind gesunde <b>Startwerte</b> zum "
                "Herantasten. Richtig ist das Gewicht, wenn sich die letzten 2 Wiederholungen anstrengend, aber "
                "technisch sauber anfühlen — <b>nicht zu viel, nicht zu wenig</b>. Im Zweifel lieber leichter beginnen.</div>",
                unsafe_allow_html=True)
    if overload_ready():
        st.markdown("<div class='badge'>🚀 Progressive Overload: Zeit, das Gewicht leicht zu erhöhen!</div>", unsafe_allow_html=True)
    for i, name in enumerate(ex, 1):
        render_exercise(day, i, name, sets, reps)
    st.markdown("<div class='tip'>📈 <b>So baust du Muskeln auf:</b> Schaffst du alle Sätze mit sauberer Technik locker, "
                "nimm beim nächsten Mal die kleinste Gewichtsstufe mehr. Genau dieses schrittweise Steigern "
                "(Progressive Overload) + genug Protein + Schlaf lässt den Muskel wachsen.</div>", unsafe_allow_html=True)


def feedback_block(day):
    st.markdown("### Wie war das Training?")
    st.caption("Dein Feedback steuert die Schwierigkeit von morgen.")
    fb = ss.feedback.get(day)
    c1, c2, c3 = st.columns(3)
    for col, label, val in [(c1, "😌 Zu leicht", "zu leicht"), (c2, "💪 Passt", "passt"), (c3, "🥵 Zu schwer", "zu schwer")]:
        if col.button(label, key=f"fb_{day}_{val}", type=("primary" if fb == val else "secondary")):
            ss.feedback[day] = val
            st.rerun()
    if fb:
        st.success("Notiert — fließt in deinen morgigen Plan ein.")


def checklist_block():
    st.markdown("### 🎒 Gym-Tasche packen")
    for i, it in enumerate(BAG_ITEMS):
        ss.checklist[i] = st.checkbox(it, value=ss.checklist.get(i, False), key=f"cl_{i}")
    if all(ss.checklist.get(i) for i in range(len(BAG_ITEMS))):
        st.success("🎉 Alles eingepackt — du bist startklar für morgen!")


def missed_banner(day):
    """Verpasster Tag -> App fragt 'Was war los?'"""
    prev = day - 1
    if prev >= 1 and prev not in ss.completed and prev not in ss.missed_handled:
        st.markdown(f"<div class='warn'>😕 Tag {prev} hast du nicht abgeschlossen. Was war los?</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        if c1.button("🤒 Krank", key=f"miss_sick_{prev}"):
            ss.missed_handled.add(prev)
            ss.feedback[prev] = "zu schwer"
            st.toast("Erholung geht vor. Wir nehmen es sanfter.")
            st.rerun()
        if c2.button("⏳ Keine Zeit", key=f"miss_time_{prev}"):
            ss.missed_handled.add(prev)
            st.toast("Kein Problem — wir machen genau hier weiter.")
            st.rerun()
        if c3.button("✅ Nachgeholt", key=f"miss_done_{prev}"):
            ss.completed.add(prev)
            ss.missed_handled.add(prev)
            st.rerun()


def view_today():
    day = current_day()
    # Paywall an Tag 14
    if day >= 14 and not ss.premium and 14 not in ss.completed:
        st.markdown("<div style='text-align:center;font-size:56px'>🏆</div>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center'>2 Wochen durchgehalten.</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center'>Das schaffen die wenigsten. Ab jetzt wird's richtig ernst — "
                    "dein Körper beginnt sich zu verändern.</p>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.markdown("<div class='card' style='text-align:center'><div class='badge green'>−50% 🎉</div>"
                    "<h3 style='margin:8px 0 0'>Jahr</h3><div style='font-size:22px;font-weight:800'>59,99 €</div>"
                    "<div class='muted' style='font-size:12px'>≈ 5 €/Monat</div></div>", unsafe_allow_html=True)
        c2.markdown("<div class='card' style='text-align:center'><h3 style='margin:0'>Monat</h3>"
                    "<div style='font-size:22px;font-weight:800'>9,99 €</div>"
                    "<div class='muted' style='font-size:12px'>monatlich kündbar</div></div>", unsafe_allow_html=True)
        if st.button("Weitermachen 🚀", type="primary"):
            ss.premium = True
            st.rerun()
        return

    day_tracker(day)
    weekday = (datetime.date.today() + datetime.timedelta(days=ss.day_offset)).strftime("%A")
    st.markdown(f"<div class='badge'>TAG {day} · {weekday}</div>", unsafe_allow_html=True)
    if streak() > 0:
        st.markdown(f"<div class='streak'>🔥 {streak()} Tage Streak</div>", unsafe_allow_html=True)
    missed_banner(day)

    m = plan()
    training = is_training_day(day)
    need = get_key() and (day not in ss.ai_cache or (training and day not in ss.ai_workout))
    if need:
        with st.spinner("🤖 Dein Coach stellt deinen Tag zusammen … (kann bis zu 1 Minute dauern)"):
            ai = ai_day(day)
            if training:
                ai_workout(day)
    else:
        ai = ai_day(day)
        if training:
            ai_workout(day)

    # Titel je nach Tag
    titles = {1: "Mentale Vorbereitung", 2: "Ernährungs-Setup", 3: "Erster Gymbesuch"}
    if day in titles:
        title = titles[day]
    elif training and day == first_training_day():
        title = "Erste echte Übungen"
    elif training:
        title = f"Trainingstag · {ai_workout(day)['name']}"
    else:
        title = "Ruhetag & Erholung"
    st.markdown(f"## {title}")

    # Coaching-Nachricht (KI oder statisch)
    card(f"<p style='font-size:15px;margin:0'>{ai['coaching']}</p>")

    # --- Tagesspezifischer Content ---
    if day == 1:
        card("<h3>🧠 Was dich im Gym erwartet</h3><p>Kein Stress. Niemand schaut dich an — alle sind mit sich "
             "selbst beschäftigt. Jeder war mal Anfänger. Dein einziges Ziel heute: ankommen.</p>")
        html = "<h3>📜 Gym-Etikette</h3>"
        for i, (e, t, d) in enumerate(ETIKETTE[:3], 1):
            html += f"<div class='step'><div class='num'>{i}</div><div><b>{t}</b> — {d}</div></div>"
        card(html)
        card(f"<h3>🍽️ Deine erste Kalorien-Info</h3><p>Ab heute isst du <b style='color:#FF7A1A'>{m['kcal']} kcal</b> "
             "pro Tag. Details kommen morgen — heute reicht: damit starten.</p>")
        st.markdown("<div class='tip'>📅 <b>Dein Fahrplan:</b> Morgen die Ernährung, an Tag 3 dein erster Gymbesuch. "
                    "Wir bereiten dich Schritt für Schritt vor.</div>", unsafe_allow_html=True)

    elif day == 2:
        card(f"<h3>📊 Deine Makros — einfach erklärt</h3>"
             f"<p><b>Protein ({m['protein']}g)</b> baut Muskeln & hält satt. <b>Carbs ({m['carbs']}g)</b> geben "
             f"Energie fürs Training. <b>Fett ({m['fat']}g)</b> hält Hormone im Lot. Zähl nicht jedes Gramm — komm grob hin.</p>")
        card("<h3>🛒 Einkaufsliste</h3>" + "".join(
            f"<span class='pill'>{x}</span>" for x in ["Haferflocken", "Skyr", "Eier", "Hähnchen/Tofu", "Reis",
                                                       "Kartoffeln", "TK-Gemüse", "Beeren", "Nüsse", "Olivenöl"]))
        render_meals(m, ai["meals"])
        st.markdown("<div class='tip'>🎯 <b>Morgen ist dein erster Gymbesuch!</b> Pack heute schon deine Tasche, "
                    "damit du entspannt loslegen kannst.</div>", unsafe_allow_html=True)
        checklist_block()

    elif day == 3:
        html = "<h3>👣 Dein erster Besuch — Schritt für Schritt</h3>"
        steps = ["Empfang / Anmeldung — sag einfach: „Ich bin neu hier.“",
                 "Umkleide & Spind — Sachen einschließen.",
                 "Aufwärmen: 10 Min Laufband oder Fahrrad, locker.",
                 "Tour: Freie Gewichte, Maschinen, Cardio — schau dich um.",
                 "Diese 3 schaust du heute NUR an: Kniebeugen-Rack, Bankdrücken, Kreuzheben.",
                 "Cool-down: 5 Min lockeres Dehnen. Fertig."]
        for i, s in enumerate(steps, 1):
            html += f"<div class='step'><div class='num'>{i}</div><div>{s}</div></div>"
        card(html)
        st.markdown("<div class='tip'>🌱 <b>Ziel heute:</b> ankommen, schauen, Atmosphäre spüren. Kein Training, kein Druck.</div>", unsafe_allow_html=True)

    elif training:
        workout_block(day)
        render_meals(m, ai["meals"])

    else:  # Ruhetag
        html = "<h3>🧘 Heute ist Ruhetag</h3><p>Muskeln wachsen in der Pause. Nutze den Tag bewusst zur Erholung.</p>"
        for e, t, d in REGEN:
            html += f"<div class='step'><div class='num'>{e}</div><div><b>{t}</b> — {d}</div></div>"
        card(html)
        render_meals(m, ai["meals"])

    # Feedback nur an Trainingstagen
    if training:
        feedback_block(day)

    # Tagesabschluss
    st.divider()
    if day in ss.completed:
        st.success("✓ Heute erledigt — stark!")
    else:
        if st.button(f"Tag {day} abschließen ✓", type="primary"):
            ss.completed.add(day)
            for ms, txt in [(1, "🎉 Tag 1 geschafft!"), (3, "💪 Erster Gymbesuch!"),
                            (7, "🔥 Eine ganze Woche!"), (30, "🏆 30 Tage!")]:
                if day == ms:
                    st.balloons()
            st.rerun()


def view_week():
    p = ss.profile
    td = p.get("train_days", [0, 2, 4])
    sess = plan_sessions()
    st.markdown("## 🗓 Dein Wochenplan")
    st.caption(f"{plan_name(p)} · {len(td)}× pro Woche · deine gewählten Tage. "
               "Trainingstage änderst du im Menü ⚙️.")
    ti = 0
    for i, tag in enumerate(WD):
        if i in td:
            s = sess[ti % len(sess)]
            ti += 1
            exs = ", ".join(SESSIONS[s])
            st.markdown(f"<div class='wkrow train'><div class='wkday'>{tag}</div><div>"
                        f"<div class='wktitle'>🏋️ {s}</div><div class='wkfocus'>{exs}</div></div></div>",
                        unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='wkrow'><div class='wkday'>{tag}</div><div>"
                        f"<div class='wktitle' style='color:#8A7E73'>😴 Ruhetag</div>"
                        f"<div class='wkfocus'>Erholung — Muskeln wachsen in der Pause.</div></div></div>",
                        unsafe_allow_html=True)


GERAETE_GRUPPEN = ["Beine", "Brust", "Rücken", "Schultern", "Arme", "Bauch"]


def muscle_group(m):
    """Grobe Körperbereich-Zuordnung einer Übung anhand ihres Muskel-Textes."""
    s = m.lower()
    if "brust" in s:
        return "Brust"
    if "schulter" in s:
        return "Schultern"
    if "rücken" in s:
        return "Rücken"
    if "bizeps" in s or "trizeps" in s or "arme" in s:
        return "Arme"
    if "bauch" in s:
        return "Bauch"
    return "Beine"   # Beine & Po, Waden, Ab-/Adduktoren …


def view_knowledge():
    st.markdown("## 📚 Wissen")
    sub = st.radio("wsub", ["📜 Etikette", "🏋️ Geräte", "💊 Supplements", "🛌 Regeneration"],
                   horizontal=True, label_visibility="collapsed", key="know_sub")

    if sub == "📜 Etikette":
        st.caption("Die ungeschriebenen Regeln — damit du dich vom ersten Tag an sicher fühlst.")
        for e, t, d in ETIKETTE:
            card(f"<b style='font-size:15.5px'>{e} {t}</b><br><span class='muted'>{d}</span>")

    elif sub == "🏋️ Geräte":
        st.caption("Alle wichtigen Maschinen — nach Körperbereich sortiert, jede mit Video, "
                   "Einstellung und Sicherheits-Tipp.")
        grp = st.radio("gg", GERAETE_GRUPPEN, horizontal=True, label_visibility="collapsed", key="ger_grp")
        items = [(n, i) for n, i in EXERCISES.items() if muscle_group(i["m"]) == grp]
        st.caption(f"{len(items)} Maschinen für {grp}")
        for name, info in items:
            st.markdown(f"### {name}")
            st.markdown(f"<div class='badge'>{info['m']}</div>", unsafe_allow_html=True)
            st.markdown(f"<p style='margin:8px 0 4px;color:#3a3a3c'>{info['desc']}</p>", unsafe_allow_html=True)
            st.video(f"https://www.youtube.com/watch?v={info['vid']}")
            st.markdown(f"<div class='tip'>🔧 <b>So stellst du es ein:</b> {info['setup']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='warn'>⚠️ <b>Achte darauf:</b> {info['warn']}</div>", unsafe_allow_html=True)
            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    elif sub == "💊 Supplements":
        st.caption("Was wirklich sinnvoll ist — und was du dir sparen kannst.")
        cls = {"✅": "good", "🟡": "mid", "❌": "bad"}
        for e, t, d in SUPPLEMENTS:
            st.markdown(f"<div class='supp {cls.get(e, 'good')}'><span class='se'>{e}</span>"
                        f"<div><div class='st'>{t}</div><div class='sd'>{d}</div></div></div>",
                        unsafe_allow_html=True)

    else:
        st.caption("Erholung ist Teil des Trainings — hier steckt der eigentliche Fortschritt.")
        for e, t, d in REGEN:
            card(f"<b style='font-size:15.5px'>{e} {t}</b><br><span class='muted'>{d}</span>")


def stat_tile(col, emoji, value, label):
    col.markdown(f"<div class='stat'><div class='v'>{emoji} {value}</div><div class='l'>{label}</div></div>",
                 unsafe_allow_html=True)


def view_progress():
    st.markdown("## 📊 Dein Fortschritt")
    c1, c2, c3 = st.columns(3)
    stat_tile(c1, "🔥", streak(), "Streak")
    stat_tile(c2, "✅", len(ss.completed), "Tage erledigt")
    stat_tile(c3, "📅", current_day(), "Aktueller Tag")
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    sub = st.radio("psub", ["🏅 Meilensteine", "⚖️ Gewicht", "📏 Maße", "🍴 Makro-Log"],
                   horizontal=True, label_visibility="collapsed", key="prog_sub")

    if sub == "🏅 Meilensteine":
        for need, txt, emo in [(1, "Erster Tag", "👟"), (7, "Eine Woche", "🔥"),
                               (14, "Zwei Wochen", "💪"), (30, "Ein Monat", "🏆")]:
            done = len(ss.completed) >= need
            st.markdown(f"<div class='mile {'on' if done else 'off'}'><span style='font-size:20px'>"
                        f"{emo if done else '🔒'}</span><span>{txt}{' — geschafft!' if done else ''}</span></div>",
                        unsafe_allow_html=True)
        if overload_ready():
            st.markdown("<div class='mile on'><span style='font-size:20px'>🏋️</span>"
                        "<span>Erstes Gewicht erhöht! (3× zu leicht)</span></div>", unsafe_allow_html=True)

    elif sub == "⚖️ Gewicht":
        st.caption("Miss dich alle 1–2 Wochen. Die App passt deine Kalorien automatisch an.")
        c1, c2 = st.columns([2, 1])
        nw = c1.number_input("Aktuelles Gewicht (kg)", 35, 250, int(ss.profile["weight"]), key="nw")
        if c2.button("Speichern", key="save_w"):
            ss.profile["weight"] = nw
            ss.weight_log.append((datetime.date.today().isoformat(), nw))
            ss.pop("plan", None)      # Kalorien neu berechnen lassen
            ss.ai_cache.clear()       # Coaching/Mahlzeiten an neue Zahlen anpassen
            st.toast(f"Gespeichert — neues Ziel: {plan()['kcal']} kcal/Tag")
            st.rerun()
        if len(ss.weight_log) >= 2:
            try:
                import pandas as pd
                df = pd.DataFrame(ss.weight_log, columns=["Datum", "kg"]).set_index("Datum")
                st.line_chart(df, color="#FF7A1A")
            except Exception:
                pass
        else:
            st.caption("Ab dem zweiten Eintrag siehst du hier deinen Verlauf als Kurve.")

    elif sub == "📏 Maße":
        st.caption("Nicht nur die Waage zählt — Umfänge zeigen echte Veränderung.")
        c1, c2, c3 = st.columns(3)
        waist = c1.number_input("Taille cm", 40, 200, 80, key="ms_w")
        arm = c2.number_input("Arm cm", 15, 70, 32, key="ms_a")
        chest = c3.number_input("Brust cm", 60, 200, 95, key="ms_c")
        if st.button("Maße speichern"):
            ss.measure_log.append(dict(date=datetime.date.today().isoformat(), waist=waist, arm=arm, chest=chest))
            st.toast("Maße gespeichert.")
            st.rerun()
        for e in reversed(ss.measure_log[-5:]):
            card(f"<b>{e['date']}</b><br><span class='muted'>Taille {e['waist']} cm · "
                 f"Arm {e['arm']} cm · Brust {e['chest']} cm</span>")

    else:
        st.caption("Logge, was du heute isst — sieh, wie viel Protein noch fehlt.")
        today = datetime.date.today().isoformat()
        log = ss.food_log.setdefault(today, [])
        m = plan()
        got_p = sum(x["protein"] for x in log)
        got_k = sum(x["kcal"] for x in log)
        pct = min(100, round(got_p / m["protein"] * 100)) if m["protein"] else 0
        st.markdown(f"<div class='card' style='text-align:center'>"
                    f"<div style='font-size:26px;font-weight:800;color:#27AE60'>{got_p} / {m['protein']} g</div>"
                    f"<div class='muted'>Protein heute · {got_k} / {m['kcal']} kcal</div>"
                    f"<div style='height:9px;background:#F0E7DE;border-radius:99px;margin-top:10px;overflow:hidden'>"
                    f"<div style='height:100%;width:{pct}%;background:#27AE60'></div></div></div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([2, 1, 1])
        fname = c1.text_input("Lebensmittel", key="food_name")
        fprot = c2.number_input("Protein g", 0, 200, 20, key="food_prot")
        fkcal = c3.number_input("kcal", 0, 2000, 300, key="food_kcal")
        if st.button("Hinzufügen", key="add_food") and fname:
            log.append(dict(name=fname, protein=fprot, kcal=fkcal))
            st.rerun()
        for x in log:
            st.markdown(f"- **{x['name']}** · {x['protein']} g P · {x['kcal']} kcal")


def goto_today():
    """Zum aktuellen Tag springen und Inhalte (bei API-Key) VOR dem Neurendern
    laden – so erscheint direkt die fertige Heute-Seite statt der alten Menü-UI.
    Ansichtswechsel via pending_view (top_nav wendet es vor dem Radio an)."""
    ss.pending_view = "Heute"
    d = current_day()
    if get_key():
        with st.spinner("🤖 Dein Coach stellt deinen Tag zusammen … (kann bis zu 1 Minute dauern)"):
            ai_day(d)
            if is_training_day(d):
                ai_workout(d)
    st.rerun()


def view_settings():
    st.markdown("## ⚙️ Menü & Einstellungen")
    st.markdown("### 🗓 Deine Trainingstage")
    st.caption("Ändere jederzeit, an welchen Tagen du trainierst — der Wochenplan passt sich an.")
    days_editor("settings_days")

    st.divider()
    st.markdown("### 🤖 KI-Coach")
    src = key_source()
    st.caption(f"Workout & Kalorien: **{MODEL_WORKOUT}** · Texte: **{MODEL_TEXT}** · "
               f"Key: {src or 'KEINER gefunden'}")
    if st.button("KI-Modell jetzt testen"):
        with st.spinner(f"Teste {MODEL_WORKOUT} …"):
            r = _openai({"model": MODEL_WORKOUT,
                         "response_format": {"type": "json_object"},
                         "messages": [{"role": "user",
                                       "content": "Antworte nur mit diesem JSON: {\"ok\":true}"}]})
        if r and "choices" in r:
            st.success(f"✅ {MODEL_WORKOUT} funktioniert! Dein Coach rechnet mit KI.")
        else:
            st.error(f"❌ {MODEL_WORKOUT} antwortet nicht — die App nutzt daher die "
                     "Formel/Regel-Berechnung. Fehlermeldung von OpenAI:")
            st.code(ss.get("_last_ai_error") or "Unbekannt (kein Key?)")
            st.caption("Häufigste Ursache: Dein OpenAI-Konto hat noch keinen Zugriff auf dieses "
                       "Modell. Dann in app.py oben `MODEL_WORKOUT`/`MODEL_CALORIES` auf ein "
                       "freigeschaltetes Modell setzen (z.B. \"gpt-4o-mini\" oder \"gpt-4.1-mini\").")

    st.divider()
    st.markdown("### ⏱ Journey (Demo-Steuerung)")
    st.caption("Im echten Betrieb schaltet sich täglich ein neuer Tag frei. Zum Ausprobieren:")
    c1, c2 = st.columns(2)
    if c1.button("⏭ Nächster Tag"):
        ss.day_offset += 1
        goto_today()
    if c2.button("⏮ Vorheriger Tag", disabled=ss.day_offset <= 0):
        ss.day_offset = max(0, ss.day_offset - 1)
        goto_today()

    if ss.get("_user_email"):
        st.divider()
        st.markdown("### 👤 Konto")
        st.caption(f"Angemeldet als **{ss.get('_user_name') or ss['_user_email']}**. "
                   "Dein Fortschritt wird automatisch gespeichert.")
        if ss.get("_db_error"):
            st.caption(f"⚠️ {ss['_db_error']}")
        if st.button("Abmelden"):
            for k in ("_user_email", "_user_name", "_token", "_loaded", "_last_saved"):
                ss.pop(k, None)
            st.rerun()

    st.divider()
    if st.button("🔁 App komplett zurücksetzen"):
        keep = {k: ss[k] for k in ("_user_email", "_user_name") if k in ss}
        for k in list(ss.keys()):
            del ss[k]
        ss.update(keep)
        if keep:
            ss["_loaded"] = True   # nicht erneut aus DB laden -> echter Reset
        st.rerun()


def view_journey():
    top_nav()
    {"Heute": view_today, "Woche": view_week, "Wissen": view_knowledge,
     "Fortschritt": view_progress, "Menü": view_settings}[ss.view]()


# =============================================================================
# KONTO: Google-Login (st.login) + Speicherung pro Nutzer (Supabase) — OPTIONAL
# Aktiv NUR, wenn in den Secrets [auth] bzw. SUPABASE_* konfiguriert sind.
# Ohne Konfiguration läuft die App unverändert (ohne Login) weiter.
# =============================================================================
PERSIST_KEYS = ["phase", "profile", "start_date", "completed", "checklist",
                "feedback", "day_offset", "premium", "weight_log", "measure_log",
                "food_log", "missed_handled", "swaps", "workout_wish", "plan",
                "ai_cache", "ai_workout"]   # KI-Tag mitspeichern -> bleibt beim Re-Login gleich
INT_KEY_DICTS = ["feedback", "workout_wish", "checklist", "ai_cache", "ai_workout"]


GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_REVOKE_URL = "https://oauth2.googleapis.com/revoke"


def oauth_configured():
    """Google-Login (Popup via streamlit-oauth) nur aktiv, wenn Paket + Secrets da."""
    if not OAUTH_AVAILABLE:
        return False
    try:
        a = st.secrets.get("auth", {})
        return bool(a.get("client_id") and a.get("client_secret") and a.get("redirect_uri"))
    except Exception:
        return False


def supabase_cfg():
    try:
        url = str(st.secrets.get("SUPABASE_URL", "")).strip().rstrip("/")
        key = str(st.secrets.get("SUPABASE_KEY", "")).strip()
        return (url, key) if url and key else None
    except Exception:
        return None


def _decode_id_token(id_token):
    """E-Mail & Name aus dem Google id_token (JWT) lesen — ohne Signaturprüfung
    (Token kam direkt von Google über TLS via die OAuth-Komponente)."""
    try:
        payload = id_token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        d = json.loads(base64.urlsafe_b64decode(payload.encode()))
        return (d.get("email") or "").lower(), (d.get("name") or d.get("email") or "")
    except Exception:
        return None, None


def _serialize():
    out = {}
    for k in PERSIST_KEYS:
        if k not in ss:
            continue
        v = ss[k]
        if isinstance(v, set):
            out[k] = {"__set__": sorted(v, key=str)}
        elif isinstance(v, datetime.date):
            out[k] = v.isoformat()
        else:
            out[k] = v
    return out


def _deserialize(data):
    if not isinstance(data, dict):
        return
    for k, v in data.items():
        if isinstance(v, dict) and "__set__" in v:
            v = set(v["__set__"])
        ss[k] = v
    sd = ss.get("start_date")
    if isinstance(sd, str) and sd:
        try:
            ss["start_date"] = datetime.date.fromisoformat(sd)
        except Exception:
            ss["start_date"] = None
    # Ganzzahl-Schlüssel wiederherstellen (JSON macht daraus Strings)
    for k in INT_KEY_DICTS:
        d = ss.get(k)
        if isinstance(d, dict):
            ss[k] = {(int(kk) if str(kk).lstrip("-").isdigit() else kk): vv
                     for kk, vv in d.items()}


def _sb_headers(key, extra=None):
    h = {"apikey": key, "Authorization": "Bearer " + key, "Content-Type": "application/json"}
    if extra:
        h.update(extra)
    return h


def load_profile(email):
    cfg = supabase_cfg()
    if not cfg:
        return
    url, key = cfg
    q = f"{url}/rest/v1/profiles?email=eq.{urllib.parse.quote(email)}&select=data"
    try:
        req = urllib.request.Request(q, headers=_sb_headers(key), method="GET")
        with urllib.request.urlopen(req, timeout=15) as r:
            rows = json.loads(r.read())
        if rows and rows[0].get("data"):
            _deserialize(rows[0]["data"])
    except Exception as e:
        ss["_db_error"] = f"Laden fehlgeschlagen: {e}"


def save_profile(email):
    cfg = supabase_cfg()
    if not cfg:
        return
    url, key = cfg
    body = json.dumps([{"email": email, "data": _serialize(),
                        "updated_at": datetime.datetime.utcnow().isoformat()}]).encode()
    try:
        req = urllib.request.Request(
            f"{url}/rest/v1/profiles?on_conflict=email", data=body,
            headers=_sb_headers(key, {"Prefer": "resolution=merge-duplicates,return=minimal"}),
            method="POST")
        with urllib.request.urlopen(req, timeout=15) as r:
            r.read()
        ss["_db_error"] = ""
    except Exception as e:
        ss["_db_error"] = f"Speichern fehlgeschlagen: {e}"


def auth_gate():
    """Login-Screen mit Google-Popup (streamlit-oauth) + Laden des Stands bei Login."""
    if not oauth_configured():
        return
    # Bereits in dieser Sitzung eingeloggt?
    if ss.get("_user_email"):
        if not ss.get("_loaded"):
            load_profile(ss["_user_email"])
            ss["_loaded"] = True
        return
    # Login-Screen
    a = st.secrets["auth"]
    st.markdown("# Gym<span style='color:#FF7A1A'>Start</span>", unsafe_allow_html=True)
    st.markdown("### Willkommen 👋")
    st.markdown("<p>Melde dich mit Google an — so bleiben dein aktueller Tag, deine Erfolge "
                "und dein Plan auf jedem Gerät gespeichert. Es öffnet sich ein kleines Google-Fenster.</p>",
                unsafe_allow_html=True)
    oauth2 = OAuth2Component(a["client_id"], a["client_secret"], GOOGLE_AUTH_URL,
                             GOOGLE_TOKEN_URL, GOOGLE_TOKEN_URL, GOOGLE_REVOKE_URL)
    result = oauth2.authorize_button(
        name="Mit Google anmelden",
        redirect_uri=a["redirect_uri"],
        scope="openid email profile",
        key="google_login",
        extras_params={"prompt": "select_account"},
    )
    if result and "token" in result:
        email, name = _decode_id_token(result["token"].get("id_token", ""))
        if email:
            ss["_user_email"] = email
            ss["_user_name"] = name
            ss["_loaded"] = False
            st.rerun()
        else:
            st.error("Anmeldung ok, aber keine E-Mail erhalten. Ist der Scope email/openid freigegeben?")
    st.stop()


def persist_if_changed():
    """Speichert den Stand nach jeder Änderung (nur eingeloggt + Supabase da)."""
    email = ss.get("_user_email")
    if not email or not supabase_cfg():
        return
    try:
        cur = json.dumps(_serialize(), sort_keys=True, default=str)
    except Exception:
        return
    if cur != ss.get("_last_saved"):
        save_profile(email)
        ss["_last_saved"] = cur


# =============================================================================
# ROUTER
# =============================================================================
auth_gate()   # zeigt ggf. Login-Screen (st.stop) und lädt den gespeicherten Stand

{"onboarding": view_onboarding, "result": view_result, "days": view_days,
 "commit": view_commit, "journey": view_journey}[ss.phase]()

persist_if_changed()   # speichert Änderungen automatisch (wenn eingeloggt)
