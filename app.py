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
import datetime
import urllib.request
import urllib.error
import streamlit as st

st.set_page_config(page_title="GymStart", page_icon="💪", layout="centered",
                   initial_sidebar_state="collapsed")

# =============================================================================
# STYLING – warmes helles Theme, erzwungen (auch bei Dark-Mode des Geräts)
# =============================================================================
st.markdown("""
<style>
  :root { color-scheme: light; }
  html, body, .stApp { background-color:#FFF9F5 !important; }
  .block-container { max-width:540px; padding-top:1.1rem; padding-bottom:5rem; }
  #MainMenu, footer, header { visibility:hidden; }

  .stApp, .stApp p, .stApp li, .stApp label, .stApp span,
  [data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] p,
  [data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] *,
  .stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp h5 { color:#231A12; }
  .stApp h1,.stApp h2,.stApp h3 { letter-spacing:-.3px; }
  [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] * { color:#8A7E73 !important; }

  .stApp input, .stApp textarea { color:#231A12 !important; background-color:#fff !important; }
  [data-baseweb="select"] > div { background-color:#fff !important; }
  [data-baseweb="select"] div, [data-baseweb="popover"] li, [role="option"] { color:#231A12 !important; }
  [data-baseweb="popover"] li, [role="option"] { background-color:#fff !important; }

  div.stButton > button { border-radius:14px; font-weight:700; padding:.55rem 1rem;
      background:#fff; color:#231A12 !important; border:1.5px solid #F0E7DE; width:100%; }
  div.stButton > button[kind="primary"], div.stButton > button[kind="primary"] * {
      background:#FF7A1A !important; color:#fff !important; border:none; }

  .card { background:#fff; border:1px solid #F0E7DE; border-radius:20px;
          padding:18px 20px; margin:12px 0; box-shadow:0 8px 24px rgba(120,80,30,.07); }
  .card p { color:#4a3f36 !important; line-height:1.55; margin:0 0 6px; }
  .card h3 { margin:0 0 8px; }
  .badge { display:inline-block; background:#FFF1E6; color:#FF7A1A !important; font-weight:700;
           font-size:12px; padding:6px 12px; border-radius:99px; }
  .badge.green { background:#E9F9F0; color:#27AE60 !important; }
  .kcal { font-size:46px; font-weight:800; color:#FF7A1A !important; line-height:1; }
  .muted { color:#8A7E73 !important; }
  .pill { display:inline-block; background:#fff5ec; color:#FF7A1A !important; font-size:12px;
          font-weight:700; padding:5px 11px; border-radius:99px; margin:0 5px 6px 0; border:1px solid #ffe4cc; }
  .setpill { display:inline-block; background:#FFF1E6; color:#B5541A !important; font-weight:700;
             font-size:14px; padding:8px 13px; border-radius:12px; margin:4px 0 8px; }
  .tip { background:#E9F9F0; border:1px solid #CDEFD9; border-radius:14px; padding:12px 15px;
         color:#1c7a44 !important; font-size:14px; margin:10px 0; }
  .tip b { color:#1c7a44 !important; }
  .warn { background:#FFF3F0; border:1px solid #FFD9CF; border-radius:14px; padding:12px 15px;
          color:#B5482E !important; font-size:14px; margin:8px 0; }
  .warn b { color:#B5482E !important; }
  .streak { background:linear-gradient(100deg,#FF7A1A,#FF9A4D); border-radius:18px;
            padding:14px 20px; font-weight:800; font-size:20px; margin:6px 0 4px; }
  .streak, .streak * { color:#fff !important; }
  .meal { display:flex; gap:12px; align-items:center; padding:11px 13px; background:#fff8f2;
          border-radius:14px; margin:8px 0; }
  .meal .mi { font-size:24px; } .meal .mt { font-weight:700; font-size:14px; color:#231A12 !important; }
  .meal .md { font-size:12px; color:#8A7E73 !important; }
  .meal .mk { margin-left:auto; text-align:right; font-size:12px; font-weight:700; color:#FF7A1A !important; }
  .step { display:flex; gap:12px; margin-bottom:10px; align-items:flex-start; }
  .step .num { min-width:26px; height:26px; border-radius:50%; background:#FFF1E6; color:#FF7A1A !important;
               font-weight:800; font-size:13px; display:flex; align-items:center; justify-content:center; }
  .wkrow { display:flex; gap:14px; align-items:center; padding:12px; border-radius:14px;
           margin-bottom:8px; background:#fff8f2; border:1px solid #F0E7DE; }
  .wkrow.train { background:#FFF1E6; border-color:#ffe0c7; }
  .wkday { width:46px; height:46px; border-radius:12px; background:#fff; display:flex; align-items:center;
           justify-content:center; font-weight:800; border:1px solid #F0E7DE; color:#231A12 !important; }
  .wkrow.train .wkday { background:#FF7A1A; color:#fff !important; border-color:#FF7A1A; }
  .wktitle { font-weight:700; font-size:14.5px; color:#231A12 !important; }
  .wkfocus { font-size:12.5px; color:#8A7E73 !important; }
  .dots { display:flex; gap:6px; flex-wrap:wrap; margin:4px 0 2px; }
  .dot { width:30px; height:30px; border-radius:50%; display:flex; align-items:center; justify-content:center;
         font-size:12px; font-weight:800; background:#fff; border:2px solid #F0E7DE; color:#8A7E73 !important; }
  .dot.done { background:#27AE60; border-color:#27AE60; color:#fff !important; }
  .dot.today { background:#FF7A1A; border-color:#FF7A1A; color:#fff !important; box-shadow:0 0 0 4px #FFF1E6; }
  .stat { background:#fff; border:1px solid #F0E7DE; border-radius:16px; padding:14px 6px; text-align:center;
          box-shadow:0 6px 16px rgba(120,80,30,.05); }
  .stat .v { font-size:26px; font-weight:800; color:#231A12; line-height:1; }
  .stat .l { font-size:11px; color:#8A7E73; margin-top:4px; }
  .mile { display:flex; align-items:center; gap:10px; padding:11px 14px; border-radius:14px; margin-bottom:8px; font-weight:600; }
  .mile.on { background:#E9F9F0; color:#1c7a44; border:1px solid #CDEFD9; }
  .mile.off { background:#faf6f1; color:#a89a8c; border:1px solid #F0E7DE; }
  .knav { display:flex; gap:8px; margin-bottom:6px; }
  .gcard { background:#fff; border:1px solid #F0E7DE; border-radius:20px; overflow:hidden;
           margin:12px 0; box-shadow:0 8px 24px rgba(120,80,30,.07); }
  .gcard img { width:100%; display:block; aspect-ratio:16/9; object-fit:cover; }
  .gcard .gbody { padding:14px 18px 16px; }
  .gcard .gname { font-weight:800; font-size:17px; color:#231A12; }
  .gcard .gmus { display:inline-block; background:#FFF1E6; color:#FF7A1A !important; font-weight:700;
                 font-size:11px; padding:3px 10px; border-radius:99px; margin-left:6px; }
  .supp { display:flex; gap:12px; align-items:flex-start; padding:13px 15px; border-radius:14px; margin-bottom:8px; border:1px solid #F0E7DE; }
  .supp .se { font-size:22px; } .supp .st { font-weight:700; color:#231A12; }
  .supp .sd { font-size:13px; color:#6b6055; }
  .supp.good { background:#E9F9F0; border-color:#CDEFD9; }
  .supp.mid { background:#FFF8E9; border-color:#F3E6C4; }
  .supp.bad { background:#FBF0EE; border-color:#F0DBD5; }
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
                                 exp="Noch nie im Gym", days=3, budget="20–40 €"))
    d.setdefault("gym", None)
    d.setdefault("start_date", None)
    d.setdefault("completed", set())
    d.setdefault("checklist", {})
    d.setdefault("feedback", {})       # day -> "zu leicht"/"passt"/"zu schwer"
    d.setdefault("ai_cache", {})       # day -> {"coaching":..,"meals":[..]}
    d.setdefault("day_offset", 0)
    d.setdefault("premium", False)
    d.setdefault("view", "Heute")
    d.setdefault("api_key", "")
    d.setdefault("weight_log", [])     # [(date, weight)]
    d.setdefault("measure_log", [])    # [{date, waist, arm, chest}]
    d.setdefault("photos", [])         # [(date, bytes)]
    d.setdefault("food_log", {})       # "YYYY-MM-DD" -> [{"name","protein","kcal"}]
    d.setdefault("missed_handled", set())


init_state()
ss = st.session_state


# =============================================================================
# BERECHNUNGEN (Mifflin-St Jeor, keine API)
# =============================================================================
ACT = {2: 1.2, 3: 1.375, 4: 1.46, 5: 1.55}


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
}
EX_LIST = list(EXERCISES.keys())


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


def training_day_number(day):
    """Wie oft wurde bis zu diesem Journey-Tag trainiert (für Progression)."""
    return sum(1 for d in range(4, day + 1) if is_training_day(d))


def exercises_for(day):
    n = training_day_number(day)
    count = 3 if n <= 2 else 4 if n <= 6 else 5
    start = (n * 2) % len(EX_LIST)
    return [EX_LIST[(start + i) % len(EX_LIST)] for i in range(count)]


def sets_reps(day):
    n = training_day_number(day)
    sets = 2 if n <= 3 else 3
    reps = int(round((10 + n // 3) * difficulty()))
    return sets, max(8, min(reps, 15))


# Trainingsrhythmus ab Tag 5 (Ruhetage eingebaut)
TRAIN_SLOTS = {2: {0, 3}, 3: {0, 2, 4}, 4: {0, 1, 3, 4}, 5: {0, 1, 2, 3, 4}}


def is_training_day(day):
    if day <= 3:
        return False
    if day == 4:
        return True
    idx = (day - 4) % 7
    return idx in TRAIN_SLOTS.get(ss.profile["days"], {0, 2, 4})


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
# KI (GPT-4o-mini) — NUR Coaching-Text & Mahlzeiten, mit statischem Fallback
# =============================================================================
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


def _openai(payload):
    key = get_key()
    if not key:
        return None
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + key},
        method="POST")
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return json.loads(r.read())
    except Exception:
        return None


def static_meals(m):
    d = [.28, .12, .35, .25]
    base = [("🥣", "Haferflocken + Skyr + Beeren", "Proteinreicher Start"),
            ("🥜", "Nüsse + Apfel", "Schneller Snack"),
            ("🍗", "Hähnchen/Tofu, Reis & Gemüse", "Klassiker fürs Ziel"),
            ("🐟", "Lachs/Tofu + Kartoffeln", "Protein + gute Fette")]
    return [dict(emoji=e, titel=t, beschreibung=b,
                 kcal=round(m["kcal"] * d[i]), protein=round(m["protein"] * d[i]))
            for i, (e, t, b) in enumerate(base)]


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
    p, m = ss.profile, macros(ss.profile)
    result = {"coaching": static_coaching(day), "meals": static_meals(m), "ai": False}
    if get_key():
        goal = p["goal"]
        prompt = (
            f"Person: {p['age']} J, {p['sex']}, {p['weight']}kg, {p['height']}cm, "
            f"Körpertyp {p['bodytype']}, Ziel {goal}, Erfahrung {p['exp']}, Streak {streak()} Tage, "
            f"heute Journey-Tag {day}. Tagesziel exakt: {m['kcal']} kcal, {m['protein']}g Protein, "
            f"{m['carbs']}g Carbs, {m['fat']}g Fett (VERWENDE GENAU DIESE ZAHLEN).\n"
            "Gib JSON: {\"coaching\":\"2-3 warme, motivierende Sätze, per Du, persönlich\","
            "\"meals\":[{\"emoji\":\"🍳\",\"titel\":\"...\",\"beschreibung\":\"max 6 Wörter\","
            "\"kcal\":Zahl,\"protein\":Zahl}]}. Genau 4 Mahlzeiten, deutsche Texte.")
        data = _openai({"model": "gpt-4o-mini", "temperature": 0.85,
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


GYMS = [
    dict(id="g1", n="FitBox Discount", dist=0.6, price=19, rating=4.1, lat=48.208, lon=16.363,
         feat=["Geräte", "Cardio", "24/7"], hours="24/7"),
    dict(id="g2", n="PowerHouse Gym", dist=1.2, price=35, rating=4.6, lat=48.216, lon=16.379,
         feat=["Freie Gewichte", "Kurse", "Sauna", "Trainer"], hours="6–23 Uhr"),
    dict(id="g3", n="Vital Club Premium", dist=2.1, price=59, rating=4.8, lat=48.198, lon=16.352,
         feat=["Sauna", "Pool", "Personal Trainer", "Kurse"], hours="7–22 Uhr"),
    dict(id="g4", n="CityFit Basic", dist=0.9, price=25, rating=4.0, lat=48.221, lon=16.371,
         feat=["Geräte", "Cardio", "Kurse"], hours="6–23 Uhr"),
]


def budget_max():
    return {"Bis 20 €": 20, "20–40 €": 40, "40 €+": 999}.get(ss.profile["budget"], 40)


def ranked_gyms():
    goal = ss.profile["goal"]
    bmax = budget_max()
    scored = []
    for g in GYMS:
        s = g["rating"] * 10 - g["dist"] * 4 + (25 if g["price"] <= bmax else -30)
        if goal == "Muskeln aufbauen" and "Freie Gewichte" in g["feat"]:
            s += 15
        if goal == "Abnehmen" and "Kurse" in g["feat"]:
            s += 10
        scored.append((s, g))
    scored.sort(key=lambda x: -x[0])
    return [g for _, g in scored]


def card(html):
    st.markdown(f"<div class='card'>{html}</div>", unsafe_allow_html=True)


# =============================================================================
# ONBOARDING / RESULT / GYM / COMMIT
# =============================================================================
def view_onboarding():
    st.markdown("# Gym<span style='color:#FF7A1A'>Start</span>", unsafe_allow_html=True)
    st.markdown("#### Erzähl uns von dir")
    st.caption("Damit wir alles exakt für dich berechnen — jeder erlebt eine andere App.")
    p = ss.profile
    c1, c2 = st.columns(2)
    p["weight"] = c1.number_input("Gewicht (kg)", 35, 250, p["weight"])
    p["height"] = c2.number_input("Größe (cm)", 130, 220, p["height"])
    c3, c4 = st.columns(2)
    p["age"] = c3.number_input("Alter", 14, 90, p["age"])
    p["sex"] = c4.selectbox("Geschlecht", ["Männlich", "Weiblich", "Divers"],
                            index=["Männlich", "Weiblich", "Divers"].index(p["sex"]))
    p["bodytype"] = st.selectbox("Körpertyp", ["Sehr dünn", "Normal", "Übergewichtig"],
                                 index=["Sehr dünn", "Normal", "Übergewichtig"].index(p["bodytype"]))
    p["goal"] = st.selectbox("Dein Ziel", ["Muskeln aufbauen", "Abnehmen", "Fitter werden", "Allgemeine Gesundheit"],
                             index=["Muskeln aufbauen", "Abnehmen", "Fitter werden", "Allgemeine Gesundheit"].index(p["goal"]))
    p["exp"] = st.selectbox("Gym-Erfahrung", ["Noch nie im Gym", "Kurz reingeschaut", "Leichte Erfahrung"],
                            index=["Noch nie im Gym", "Kurz reingeschaut", "Leichte Erfahrung"].index(p["exp"]))
    p["days"] = st.select_slider("Tage pro Woche", [2, 3, 4, 5], p["days"])
    p["budget"] = st.selectbox("Budget fürs Gym", ["Bis 20 €", "20–40 €", "40 €+"],
                               index=["Bis 20 €", "20–40 €", "40 €+"].index(p["budget"]))
    st.divider()
    if st.button("Plan berechnen ✨", type="primary"):
        if not ss.weight_log:
            ss.weight_log = [(datetime.date.today().isoformat(), p["weight"])]
        ss.phase = "result"
        st.rerun()


def view_result():
    p, m = ss.profile, macros(ss.profile)
    st.markdown("<div class='badge'>🎯 Auf dich zugeschnitten</div>", unsafe_allow_html=True)
    st.markdown("## Dein Plan steht.")
    card(f"<div style='text-align:center'><div class='muted' style='letter-spacing:1px;font-size:12px'>DEIN TAGESZIEL</div>"
         f"<div class='kcal'>{m['kcal']}</div><div class='muted'>kcal / Tag · {p['goal']}</div>"
         f"<div style='display:flex;justify-content:space-around;margin-top:16px'>"
         f"<div><div style='font-weight:800;color:#27AE60'>{m['protein']}g</div><div class='muted' style='font-size:11px'>PROTEIN</div></div>"
         f"<div><div style='font-weight:800;color:#FF7A1A'>{m['carbs']}g</div><div class='muted' style='font-size:11px'>CARBS</div></div>"
         f"<div><div style='font-weight:800;color:#C79A2E'>{m['fat']}g</div><div class='muted' style='font-size:11px'>FETT</div></div></div></div>")
    card(f"<h3>🏋️ Dein Trainingsplan</h3><b>{plan_name(p)}</b><br>"
         f"<span class='pill'>{p['days']}× / Woche</span><span class='pill'>Start: Maschinen</span>"
         f"<span class='pill'>Progressive Overload</span>")
    st.caption(f"So berechnet: Grundumsatz {bmr(p)} kcal × Aktivität ({p['days']} Tage) = {tdee(p)} kcal → Ziel {m['kcal']} kcal.")
    if st.button("Passendes Gym finden →", type="primary"):
        ss.phase = "gym"
        st.rerun()


def view_gym():
    st.markdown("## Wähle dein Gym")
    st.caption(f"Empfehlung nach Ziel & Budget (bis {ss.profile['budget']}).")
    try:
        import pandas as pd
        st.map(pd.DataFrame([{"lat": g["lat"], "lon": g["lon"]} for g in GYMS]), zoom=12)
    except Exception:
        pass
    gyms = ranked_gyms()
    best = gyms[0]["id"]
    for g in gyms:
        rec = "<div class='badge green' style='margin-top:8px'>✅ Für dein Ziel & Budget am besten</div>" if g["id"] == best else ""
        card(f"<div style='display:flex;justify-content:space-between'>"
             f"<div><b style='font-size:16px'>{g['n']}</b><br><span class='muted' style='font-size:13px'>"
             f"{g['dist']} km · {'⭐'*round(g['rating'])} {g['rating']} · {g['hours']}</span></div>"
             f"<div style='font-weight:800;color:#FF7A1A;text-align:right'>{g['price']} €<br>"
             f"<span class='muted' style='font-size:11px;font-weight:400'>/Monat</span></div></div>"
             f"<div style='margin-top:8px'>{''.join(f'<span class=pill>{f}</span>' for f in g['feat'])}</div>{rec}")
        if st.button(("✓ Ausgewählt" if ss.gym == g["id"] else "Dieses Gym wählen"),
                     key="gym_" + g["id"], type=("primary" if ss.gym == g["id"] else "secondary")):
            ss.gym = g["id"]
            st.rerun()
    st.divider()
    if st.button("Weiter →", type="primary", disabled=not ss.gym):
        ss.phase = "commit"
        st.rerun()


def view_commit():
    gym = next((g for g in GYMS if g["id"] == ss.gym), None)
    st.markdown("<div style='text-align:center;margin-top:26px;font-size:60px'>🔥</div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center'>Du bist bereit.</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center'>Deine Journey beginnt <b>heute</b>. Kein Druck — ein Tag nach dem anderen.</p>", unsafe_allow_html=True)
    card(f"<span class='muted' style='font-size:13px'>Dein Gym</span><br><b style='font-size:16px'>{gym['n'] if gym else ''}</b>"
         f"<br><span class='muted' style='font-size:13px'>Die ersten 14 Tage sind komplett kostenlos.</span>")
    if st.button("Gym-Journey starten 🚀", type="primary"):
        ss.phase = "journey"
        ss.start_date = datetime.date.today()
        st.rerun()


# =============================================================================
# JOURNEY – Menü + Tagesinhalt
# =============================================================================
def top_nav():
    st.markdown("### Gym<span style='color:#FF7A1A'>Start</span>", unsafe_allow_html=True)
    labels = ["📅 Heute", "🗓 Woche", "📚 Wissen", "📊 Fortschritt", "⚙️ Menü"]
    views = ["Heute", "Woche", "Wissen", "Fortschritt", "Menü"]
    if ss.view not in views:
        ss.view = "Heute"
    choice = st.radio("nav", labels, index=views.index(ss.view),
                      horizontal=True, label_visibility="collapsed")
    ss.view = views[labels.index(choice)]
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


def workout_block(day):
    sets, reps = sets_reps(day)
    st.markdown("### 🏋️ Heutiges Workout")
    st.markdown(f"<div class='tip'>ℹ️ <b>Was bedeutet Sätze × Wiederholungen?</b> Eine <b>Wiederholung</b> ist eine "
                f"komplette Bewegung. Ein <b>Satz</b> ist eine Runde am Stück — danach 1–2 Min Pause, dann der nächste Satz.</div>",
                unsafe_allow_html=True)
    if overload_ready():
        st.markdown("<div class='badge'>🚀 Progressive Overload: Zeit, das Gewicht leicht zu erhöhen!</div>", unsafe_allow_html=True)
    for name in exercises_for(day):
        info = EXERCISES[name]
        st.markdown(f"**{name}** · _{info['m']}_")
        st.markdown(f"<div class='setpill'>🔁 {sets} Sätze × {reps} Wiederholungen · ⏱ ~90 Sek. Pause</div>", unsafe_allow_html=True)
        st.video(f"https://www.youtube.com/watch?v={info['vid']}")
        st.markdown(f"<div class='tip'>✅ <b>Einstellung:</b> {info['setup']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='warn'>⚠️ {info['warn']}</div>", unsafe_allow_html=True)
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    st.markdown("<p class='muted' style='font-size:13px'>💡 Einstiegsregel: So leicht, dass du fast lachst. Nächste Woche mehr.</p>", unsafe_allow_html=True)


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

    m = macros(ss.profile)
    ai = ai_day(day)
    training = is_training_day(day)

    # Titel je nach Tag
    titles = {1: "Mentale Vorbereitung", 2: "Ernährungs-Setup", 3: "Erster Gymbesuch", 4: "Erste echte Übungen"}
    if day in titles:
        title = titles[day]
    elif training:
        title = "Trainingstag"
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
        checklist_block()

    elif day == 2:
        card(f"<h3>📊 Deine Makros — einfach erklärt</h3>"
             f"<p><b>Protein ({m['protein']}g)</b> baut Muskeln & hält satt. <b>Carbs ({m['carbs']}g)</b> geben "
             f"Energie fürs Training. <b>Fett ({m['fat']}g)</b> hält Hormone im Lot. Zähl nicht jedes Gramm — komm grob hin.</p>")
        card("<h3>🛒 Einkaufsliste</h3>" + "".join(
            f"<span class='pill'>{x}</span>" for x in ["Haferflocken", "Skyr", "Eier", "Hähnchen/Tofu", "Reis",
                                                       "Kartoffeln", "TK-Gemüse", "Beeren", "Nüsse", "Olivenöl"]))
        render_meals(m, ai["meals"])
        st.markdown("<div class='tip'>🎯 <b>Für morgen:</b> Nimm dir vor, tatsächlich ins Gym zu gehen — nur schauen. Tasche bereitlegen.</div>", unsafe_allow_html=True)

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
    st.markdown("## 🗓 Dein Wochenplan")
    st.caption(f"{plan_name(p)} · {p['days']}× Training pro Woche.")
    slots = TRAIN_SLOTS.get(p["days"], {0, 2, 4})
    focus_up = {2: ["Ganzkörper A", "Ganzkörper B"], 3: ["Push", "Pull", "Beine"],
                4: ["Oberkörper", "Unterkörper", "Oberkörper", "Unterkörper"],
                5: ["Push", "Pull", "Beine", "Oberkörper", "Unterkörper"]}.get(p["days"], ["Ganzkörper"])
    tnum = 0
    for i, tag in enumerate(["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]):
        if i in slots:
            f = focus_up[tnum % len(focus_up)] if p["goal"] == "Muskeln aufbauen" else \
                ("Ganzkörper + Cardio" if p["goal"] == "Abnehmen" else "Ganzkörper-Basis")
            tnum += 1
            st.markdown(f"<div class='wkrow train'><div class='wkday'>{tag}</div><div>"
                        f"<div class='wktitle'>🏋️ Training {tnum}</div><div class='wkfocus'>{f}</div></div></div>",
                        unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='wkrow'><div class='wkday'>{tag}</div><div>"
                        f"<div class='wktitle' style='color:#8A7E73'>😴 Ruhetag</div>"
                        f"<div class='wkfocus'>Erholung — Muskeln wachsen in der Pause.</div></div></div>",
                        unsafe_allow_html=True)


def view_knowledge():
    st.markdown("## 📚 Wissen")
    sub = st.radio("wsub", ["📜 Etikette", "🏋️ Geräte", "💊 Supplements", "🛌 Regeneration"],
                   horizontal=True, label_visibility="collapsed", key="know_sub")

    if sub == "📜 Etikette":
        st.caption("Die ungeschriebenen Regeln — damit du dich vom ersten Tag an sicher fühlst.")
        for e, t, d in ETIKETTE:
            card(f"<b style='font-size:15.5px'>{e} {t}</b><br><span class='muted'>{d}</span>")

    elif sub == "🏋️ Geräte":
        st.caption("Die wichtigsten Anfänger-Maschinen — mit Foto, wofür sie sind und worauf du achtest.")
        for name, info in EXERCISES.items():
            st.markdown(
                f"<div class='gcard'>"
                f"<img src='https://img.youtube.com/vi/{info['vid']}/hqdefault.jpg' alt='{name}'>"
                f"<div class='gbody'>"
                f"<div class='gname'>{name}<span class='gmus'>{info['m']}</span></div>"
                f"<p style='margin:8px 0 0;color:#4a3f36'>{info['desc']}</p>"
                f"<div class='tip'>🔧 <b>So stellst du es ein:</b> {info['setup']}</div>"
                f"<div class='warn'>⚠️ <b>Achte darauf:</b> {info['warn']}</div>"
                f"</div></div>", unsafe_allow_html=True)

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
        nw = c1.number_input("Aktuelles Gewicht (kg)", 35, 250, ss.profile["weight"], key="nw")
        if c2.button("Speichern", key="save_w"):
            ss.profile["weight"] = nw
            ss.weight_log.append((datetime.date.today().isoformat(), nw))
            st.toast(f"Gespeichert — neues Ziel: {macros(ss.profile)['kcal']} kcal/Tag")
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
        m = macros(ss.profile)
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


def view_settings():
    st.markdown("## ⚙️ Menü & Einstellungen")
    st.markdown("### 🎯 Dein Gym")
    gym = next((g for g in GYMS if g["id"] == ss.gym), None)
    st.write(gym["n"] if gym else "—")

    st.divider()
    st.markdown("### ⏱ Journey (Demo-Steuerung)")
    st.caption("Im echten Betrieb schaltet sich täglich ein neuer Tag frei. Zum Ausprobieren:")
    c1, c2 = st.columns(2)
    if c1.button("⏭ Nächster Tag"):
        ss.day_offset += 1
        st.rerun()
    if c2.button("⏮ Vorheriger Tag", disabled=ss.day_offset <= 0):
        ss.day_offset = max(0, ss.day_offset - 1)
        st.rerun()

    st.divider()
    if st.button("🔁 App komplett zurücksetzen"):
        for k in list(ss.keys()):
            del ss[k]
        st.rerun()


def view_journey():
    top_nav()
    {"Heute": view_today, "Woche": view_week, "Wissen": view_knowledge,
     "Fortschritt": view_progress, "Menü": view_settings}[ss.view]()


# =============================================================================
# ROUTER
# =============================================================================
{"onboarding": view_onboarding, "result": view_result, "gym": view_gym,
 "commit": view_commit, "journey": view_journey}[ss.phase]()
