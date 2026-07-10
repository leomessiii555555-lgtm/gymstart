
"""
GymStart — dein täglicher KI-Coach fürs Gym (Streamlit).
Day-by-Day Journey für absolute Anfänger. Tagesinhalt wird von GPT-4o-mini
individuell erzeugt; Kalorien/Makros exakt per Mifflin-St-Jeor in Python.
"""
import json
import datetime
import urllib.request
import urllib.error
import streamlit as st

st.set_page_config(page_title="GymStart", page_icon="💪", layout="centered",
                   initial_sidebar_state="collapsed")

# ----------------------------------------------------------------------------
# STYLING – warmes Orange/Grün, mobil-zentriert
# ----------------------------------------------------------------------------
st.markdown("""
<style>
  /* Immer heller Look – unabhängig vom Dark-Mode des Geräts */
  :root { color-scheme: light; }
  html, body, .stApp { background-color:#FFF9F5 !important; }
  .block-container { max-width:520px; padding-top:1.2rem; padding-bottom:5rem; }
  #MainMenu, footer, header { visibility:hidden; }

  /* Grundtext IMMER dunkel (verhindert weiß-auf-weiß) */
  .stApp, .stApp p, .stApp li, .stApp label, .stApp span,
  [data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] p,
  [data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] *,
  .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5 { color:#231A12; }
  .stApp h1, .stApp h2, .stApp h3 { letter-spacing:-.3px; }
  [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] * { color:#8A7E73 !important; }

  /* Eingaben & Auswahl: dunkler Text auf weiß */
  .stApp input, .stApp textarea { color:#231A12 !important; background-color:#fff !important; }
  [data-baseweb="select"] > div { background-color:#fff !important; }
  [data-baseweb="select"] div, [data-baseweb="popover"] li, [role="option"] { color:#231A12 !important; }
  [data-baseweb="popover"] li, [role="option"] { background-color:#fff !important; }

  /* Buttons: sekundär weiß/dunkel, primär orange/weiß */
  div.stButton > button { border-radius:14px; font-weight:700; padding:.6rem 1rem;
      background:#fff; color:#231A12 !important; border:1.5px solid #F0E7DE; }
  div.stButton > button[kind="primary"], div.stButton > button[kind="primary"] * {
      background:#FF7A1A !important; color:#fff !important; border:none; }

  /* Karten & Elemente */
  .card { background:#fff; border:1px solid #F0E7DE; border-radius:20px;
          padding:18px 20px; margin:12px 0; box-shadow:0 8px 24px rgba(120,80,30,.07); }
  .card p { color:#4a3f36 !important; line-height:1.55; margin:0; }
  .badge { display:inline-block; background:#FFF1E6; color:#FF7A1A !important; font-weight:700;
           font-size:12px; padding:6px 12px; border-radius:99px; }
  .badge.green { background:#E9F9F0; color:#27AE60 !important; }
  .kcal { font-size:44px; font-weight:800; color:#FF7A1A !important; line-height:1; }
  .muted { color:#8A7E73 !important; }
  .pill { display:inline-block; background:#fff5ec; color:#FF7A1A !important; font-size:12px;
          font-weight:700; padding:5px 11px; border-radius:99px; margin:0 5px 5px 0;
          border:1px solid #ffe4cc; }
  .setpill { display:inline-block; background:#FFF1E6; color:#B5541A !important; font-weight:700;
             font-size:14px; padding:8px 13px; border-radius:12px; margin:4px 0 8px; }
  .tip { background:#E9F9F0; border:1px solid #CDEFD9; border-radius:14px;
         padding:12px 15px; color:#1c7a44 !important; font-size:14px; margin:10px 0; }
  .tip b { color:#1c7a44 !important; }
  .warn { background:#FFF3F0; border:1px solid #FFD9CF; border-radius:14px;
          padding:12px 15px; color:#B5482E !important; font-size:14px; margin:8px 0; }
  .warn b { color:#B5482E !important; }
  .streak { background:linear-gradient(100deg,#FF7A1A,#FF9A4D); color:#fff !important;
            border-radius:18px; padding:14px 20px; font-weight:800; font-size:20px;
            margin:6px 0 4px; }
  .streak, .streak * { color:#fff !important; }
  .meal { display:flex; gap:12px; align-items:center; padding:11px 13px; background:#fff8f2;
          border-radius:14px; margin:8px 0; }
  .meal .mi { font-size:24px; } .meal .mt { font-weight:700; font-size:14px; color:#231A12 !important; }
  .meal .md { font-size:12px; color:#8A7E73 !important; } .meal .mk { margin-left:auto; text-align:right;
          font-size:12px; font-weight:700; color:#FF7A1A !important; }
  .wkrow { display:flex; gap:14px; align-items:center; padding:12px; border-radius:14px;
           margin-bottom:8px; background:#fff8f2; border:1px solid #F0E7DE; }
  .wkrow.train { background:#FFF1E6; border-color:#ffe0c7; }
  .wkday { width:46px; height:46px; border-radius:12px; background:#fff; display:flex;
           align-items:center; justify-content:center; font-weight:800; border:1px solid #F0E7DE; color:#231A12; }
  .wkrow.train .wkday { background:#FF7A1A; color:#fff !important; border-color:#FF7A1A; }
  .wktitle { font-weight:700; font-size:14.5px; color:#231A12 !important; }
  .wkfocus { font-size:12.5px; color:#8A7E73 !important; }
</style>
""", unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# STATE
# ----------------------------------------------------------------------------
def init_state():
    ss = st.session_state
    ss.setdefault("phase", "onboarding")
    ss.setdefault("profile", dict(weight=75, height=175, age=26, sex="Männlich",
                                  bodytype="Normal", goal="Muskeln aufbauen",
                                  exp="Noch nie im Gym", days=3, budget="20–40 €"))
    ss.setdefault("gym", None)
    ss.setdefault("start_date", None)
    ss.setdefault("completed", set())
    ss.setdefault("checklist", {})
    ss.setdefault("feedback", {})
    ss.setdefault("ai_content", {})
    ss.setdefault("day_offset", 0)
    ss.setdefault("premium", False)
    ss.setdefault("view", "📅 Heute")
    default_key = ""
    try:
        default_key = st.secrets.get("OPENAI_API_KEY", "")
    except Exception:
        default_key = ""
    ss.setdefault("api_key", default_key)


init_state()
ss = st.session_state


# ----------------------------------------------------------------------------
# BERECHNUNGEN (Mifflin-St Jeor)
# ----------------------------------------------------------------------------
ACT = {2: 1.2, 3: 1.375, 4: 1.46, 5: 1.55}


def bmr(p):
    base = 10 * p["weight"] + 6.25 * p["height"] - 5 * p["age"]
    if p["sex"] == "Männlich":
        return round(base + 5)
    if p["sex"] == "Weiblich":
        return round(base - 161)
    return round(base - 78)  # divers: Mittelwert


def tdee(p):
    return round(bmr(p) * ACT.get(p["days"], 1.375))


def goal_kcal(p):
    t = tdee(p)
    if p["goal"] == "Abnehmen":
        return t - 350
    if p["goal"] == "Muskeln aufbauen":
        return t + 300
    return t


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


# ----------------------------------------------------------------------------
# ÜBUNGEN (mit echten YouTube-Anleitungen)
# ----------------------------------------------------------------------------
EXERCISES = {
    "Beinpresse":               dict(m="Beine & Po",       vid="dIhx9s2akVo", warn="Knie in Richtung Zehen — nie nach innen kippen."),
    "Brustpresse (Maschine)":   dict(m="Brust & Trizeps",  vid="vfWqWby1PZ0", warn="Nicht im Hohlkreuz drücken — Rücken an die Lehne."),
    "Latzug (Kabelzug)":        dict(m="Rücken & Bizeps",  vid="x4fHENgCi6o", warn="Nicht mit Schwung reißen — kontrolliert führen."),
    "Rudern (Maschine)":        dict(m="Oberer Rücken",    vid="qPiF6y_HOBs", warn="Rücken nicht rund machen — Brust bleibt stolz."),
    "Schulterpresse (Maschine)":dict(m="Schultern",        vid="3b3xodJR75U", warn="Nicht bis zum Anschlag durchdrücken."),
    "Beinbeuger":               dict(m="Beinrückseite",    vid="1aJCM5ewSv8", warn="Kein Ruckeln im Endpunkt."),
    "Bauchmaschine":            dict(m="Bauch",            vid="k3bF5LQAjB4", warn="Aus dem Bauch einrollen, nicht am Nacken ziehen."),
    "Beinstrecker":             dict(m="Beinvorderseite",  vid="fIyf6iLZn5U", warn="Kein Schwung — Kontrolle vor Gewicht."),
}


def find_exercise(name):
    if not name:
        return None
    if name in EXERCISES:
        return name, EXERCISES[name]
    low = name.lower()
    for k, v in EXERCISES.items():
        first = k.lower().split(" ")[0]
        if first in low or low.split(" ")[0] in k.lower():
            return k, v
    return None


# ----------------------------------------------------------------------------
# OPENAI (serverseitig via urllib – kein CORS, Key aus st.secrets/Session)
# ----------------------------------------------------------------------------
def call_openai(payload):
    key = ss.get("api_key", "")
    if not key:
        return {"error": "Kein API-Key. Trag ihn oben unter ⚙️ Menü ein "
                         "oder hinterlege ihn in den Streamlit-Secrets."}
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + key},
        method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:160]
        return {"error": f"HTTP {e.code} — {body}"}
    except Exception as e:
        return {"error": str(e)}


def generate_day(day):
    p = ss.profile
    m = macros(p)
    st_ = streak()
    day_type = ("vorbereitung" if day == 1 else "ernaehrung" if day == 2
                else "erster_gymbesuch" if day == 3 else "training")
    last_fb = ss.feedback.get(day - 1)
    allowed = ", ".join(EXERCISES.keys())
    focus = {
        "vorbereitung": "Fokus: mentale Vorbereitung fürs Gym, was den Anfänger erwartet, Gym-Etikette. KEIN Workout. 2-3 Abschnitte.",
        "ernaehrung": "Fokus: Ernährung einfach erklären (Makros, Einkaufstipps). KEIN Workout. 2-3 Abschnitte.",
        "erster_gymbesuch": "Fokus: der allererste Gymbesuch, Schritt für Schritt, nur orientieren. 3-4 Abschnitte als Schritte.",
        "training": f"Fokus: Workout. Wähle 3-5 Übungen AUSSCHLIESSLICH aus dieser Liste (exakte Namen): {allowed}. Passe Sätze/Wiederholungen an — Anfänger starten leicht.",
    }[day_type]
    if day_type == "training":
        schema = ('{"titel":"kurz (max 4 Wörter)","untertitel":"kurzer Fokus","motivation":"2-3 persönliche Sätze",'
                  '"uebungen":[{"name":"EXAKT aus Liste","saetze":Zahl,"wdh":Zahl,"hinweis":"kurzer Formtipp"}],'
                  '"mahlzeiten":[{"emoji":"🍳","titel":"...","beschreibung":"max 6 Wörter","kcal":Zahl,"protein":Zahl}],"tipp":"..."}')
    else:
        schema = ('{"titel":"kurz (max 4 Wörter)","untertitel":"kurzer Fokus","motivation":"2-3 persönliche Sätze",'
                  '"abschnitte":[{"emoji":"🧠","ueberschrift":"...","text":"1-2 Sätze"}],'
                  '"mahlzeiten":[{"emoji":"🍳","titel":"...","beschreibung":"max 6 Wörter","kcal":Zahl,"protein":Zahl}],"tipp":"..."}')
    prompt = (
        f"Nutzer: {p['age']} Jahre, {p['sex']}, {p['weight']} kg, {p['height']} cm, "
        f"Körpertyp {p['bodytype']}. Ziel: {p['goal']}. Erfahrung: {p['exp']}. "
        f"Trainiert {p['days']}× pro Woche.\n"
        f"Tagesziel (bereits exakt berechnet — VERWENDE GENAU DIESE ZAHLEN, nicht selbst rechnen): "
        f"{m['kcal']} kcal, {m['protein']} g Protein, {m['carbs']} g Carbs, {m['fat']} g Fett.\n"
        f"Heute ist Tag {day} der Journey. Aktuelle Streak: {st_} Tage."
        + (f" Feedback vom letzten Training: {last_fb}." if last_fb else "") + "\n"
        f"{focus}\n"
        f"Erzeuge personalisierten, auf genau diese Person zugeschnittenen Inhalt. "
        f"Antworte NUR als JSON nach diesem Schema: {schema}")
    payload = {
        "model": "gpt-4o-mini", "temperature": 0.85,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": "Du bist ein persönlicher Fitness-Coach für absolute Gym-Anfänger. Warm, motivierend, per Du, ohne Fachjargon. Antworte ausschließlich mit gültigem JSON."},
            {"role": "user", "content": prompt},
        ],
    }
    data = call_openai(payload)
    if "error" in data:
        return {"error": data["error"]}
    try:
        parsed = json.loads(data["choices"][0]["message"]["content"])
        parsed["dayType"] = day_type
        return parsed
    except Exception as e:
        return {"error": f"Antwort nicht lesbar: {e}"}


# ----------------------------------------------------------------------------
# ZEIT / STREAK
# ----------------------------------------------------------------------------
def current_day():
    if not ss.start_date:
        return 1
    delta = (datetime.date.today() - ss.start_date).days
    return max(1, delta + 1 + ss.day_offset)


def streak():
    d = current_day()
    best = run = 0
    for i in range(1, d + 1):
        if i in ss.completed:
            run += 1
            best = max(best, run)
        else:
            run = 0
    return best


def week_plan():
    p = ss.profile
    days = p["days"]
    slots = {
        2: [("Mo", 1), ("Do", 2)],
        3: [("Mo", 1), ("Mi", 2), ("Fr", 3)],
        4: [("Mo", 1), ("Di", 2), ("Do", 3), ("Fr", 4)],
        5: [("Mo", 1), ("Di", 2), ("Mi", 3), ("Do", 4), ("Fr", 5)],
    }.get(days, [("Mo", 1), ("Mi", 2), ("Fr", 3)])
    splits = {
        "Muskeln aufbauen": {
            2: ["Ganzkörper A", "Ganzkörper B"],
            3: ["Push · Brust, Schultern, Trizeps", "Pull · Rücken, Bizeps", "Beine & Bauch"],
            4: ["Oberkörper", "Unterkörper", "Oberkörper", "Unterkörper"],
            5: ["Push", "Pull", "Beine", "Oberkörper", "Unterkörper"],
        }
    }

    def focus(i):
        if p["goal"] == "Muskeln aufbauen":
            return splits["Muskeln aufbauen"][days][i - 1]
        if p["goal"] == "Abnehmen":
            return "Ganzkörper + 15 Min Cardio"
        return "Ganzkörper-Basis"

    train = {tag: (i, focus(i)) for tag, i in slots}
    out = []
    for tag in ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]:
        if tag in train:
            out.append((tag, "train", train[tag][0], train[tag][1]))
        else:
            out.append((tag, "rest", None, "Erholung — Muskeln wachsen in der Pause."))
    return out


# ----------------------------------------------------------------------------
# GYMS (Mock + Empfehlung)
# ----------------------------------------------------------------------------
GYMS = [
    dict(id="g1", n="FitBox Discount",   dist=0.6, price=19, rating=4.1, feat=["Geräte", "Cardio", "24/7"]),
    dict(id="g2", n="PowerHouse Gym",    dist=1.2, price=35, rating=4.6, feat=["Freie Gewichte", "Kurse", "Sauna", "Trainer"]),
    dict(id="g3", n="Vital Club Premium",dist=2.1, price=59, rating=4.8, feat=["Sauna", "Pool", "Personal Trainer", "Kurse"]),
    dict(id="g4", n="CityFit Basic",     dist=0.9, price=25, rating=4.0, feat=["Geräte", "Cardio", "Kurse"]),
]


def budget_max():
    return {"Bis 20 €": 20, "20–40 €": 40, "40 €+": 999}.get(ss.profile["budget"], 40)


def ranked_gyms():
    bmax = budget_max()
    goal = ss.profile["goal"]
    scored = []
    for g in GYMS:
        s = g["rating"] * 10 - g["dist"] * 4
        s += 25 if g["price"] <= bmax else -30
        if goal == "Muskeln aufbauen" and "Freie Gewichte" in g["feat"]:
            s += 15
        if goal == "Abnehmen" and "Kurse" in g["feat"]:
            s += 10
        scored.append((s, g))
    scored.sort(key=lambda x: -x[0])
    return [g for _, g in scored]


# ----------------------------------------------------------------------------
# VIEWS
# ----------------------------------------------------------------------------
def view_onboarding():
    st.markdown("## Gym<span style='color:#FF7A1A'>Start</span>", unsafe_allow_html=True)
    st.markdown("#### Erzähl uns von dir")
    st.caption("Damit wir alles exakt für dich berechnen.")
    p = ss.profile
    c1, c2 = st.columns(2)
    p["weight"] = c1.number_input("Gewicht (kg)", 35, 250, p["weight"])
    p["height"] = c2.number_input("Größe (cm)", 130, 220, p["height"])
    c3, c4 = st.columns(2)
    p["age"] = c3.number_input("Alter", 14, 90, p["age"])
    p["sex"] = c4.selectbox("Geschlecht", ["Männlich", "Weiblich", "Divers"],
                            index=["Männlich", "Weiblich", "Divers"].index(p["sex"]))
    p["bodytype"] = st.selectbox("Aktueller Körpertyp", ["Sehr dünn", "Normal", "Übergewichtig"],
                                 index=["Sehr dünn", "Normal", "Übergewichtig"].index(p["bodytype"]))
    p["goal"] = st.selectbox("Dein Ziel", ["Muskeln aufbauen", "Abnehmen", "Fitter werden", "Allgemeine Gesundheit"],
                             index=["Muskeln aufbauen", "Abnehmen", "Fitter werden", "Allgemeine Gesundheit"].index(p["goal"]))
    p["exp"] = st.selectbox("Deine Gym-Erfahrung", ["Noch nie im Gym", "Kurz reingeschaut", "Leichte Erfahrung"],
                            index=["Noch nie im Gym", "Kurz reingeschaut", "Leichte Erfahrung"].index(p["exp"]))
    p["days"] = st.select_slider("Tage pro Woche", [2, 3, 4, 5], p["days"])
    p["budget"] = st.selectbox("Budget fürs Gym", ["Bis 20 €", "20–40 €", "40 €+"],
                               index=["Bis 20 €", "20–40 €", "40 €+"].index(p["budget"]))
    st.divider()
    if st.button("Plan berechnen ✨", type="primary", use_container_width=True):
        ss.phase = "result"
        st.rerun()


def view_result():
    p, m = ss.profile, macros(ss.profile)
    st.markdown("<div class='badge'>🎯 Auf dich zugeschnitten</div>", unsafe_allow_html=True)
    st.markdown("## Dein Plan steht.")
    st.markdown(
        f"<div class='card' style='text-align:center'>"
        f"<div class='muted' style='letter-spacing:1px;font-size:12px'>DEIN TAGESZIEL</div>"
        f"<div class='kcal'>{m['kcal']}</div><div class='muted'>kcal / Tag · {p['goal']}</div>"
        f"<div style='display:flex;justify-content:space-around;margin-top:16px'>"
        f"<div><div style='font-size:20px;font-weight:800;color:#27AE60'>{m['protein']}g</div><div class='muted' style='font-size:11px'>PROTEIN</div></div>"
        f"<div><div style='font-size:20px;font-weight:800;color:#FF7A1A'>{m['carbs']}g</div><div class='muted' style='font-size:11px'>CARBS</div></div>"
        f"<div><div style='font-size:20px;font-weight:800;color:#C79A2E'>{m['fat']}g</div><div class='muted' style='font-size:11px'>FETT</div></div>"
        f"</div></div>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='card'><h3 style='margin:0 0 6px'>🏋️ Dein Trainingsplan</h3>"
        f"<b>{plan_name(p)}</b><br><span class='pill'>{p['days']}× / Woche</span>"
        f"<span class='pill'>Start: Maschinen</span><span class='pill'>Progressive Overload</span></div>",
        unsafe_allow_html=True)
    st.caption(f"So berechnet: Grundumsatz {bmr(p)} kcal × Aktivität ({p['days']} Tage) "
               f"= {tdee(p)} kcal → Ziel {m['kcal']} kcal.")
    if st.button("Passendes Gym finden →", type="primary", use_container_width=True):
        ss.phase = "gym"
        st.rerun()


def view_gym():
    st.markdown("## Wähle dein Gym")
    st.caption(f"Empfehlung nach Ziel & Budget (bis {ss.profile['budget']}).")
    gyms = ranked_gyms()
    best = gyms[0]["id"]
    for g in gyms:
        rec = " · ✅ Beste Wahl" if g["id"] == best else ""
        st.markdown(
            f"<div class='card'><div style='display:flex;justify-content:space-between'>"
            f"<div><b>{g['n']}</b>{rec}<br><span class='muted' style='font-size:13px'>"
            f"{g['dist']} km · {'⭐'*round(g['rating'])} {g['rating']}</span></div>"
            f"<div style='font-weight:800;color:#FF7A1A'>{g['price']} €<br>"
            f"<span class='muted' style='font-size:11px;font-weight:400'>/Monat</span></div></div>"
            f"<div style='margin-top:8px'>{''.join(f'<span class=pill>{f}</span>' for f in g['feat'])}</div></div>",
            unsafe_allow_html=True)
        if st.button(("✓ Ausgewählt" if ss.gym == g["id"] else "Dieses Gym wählen"),
                     key="gym_" + g["id"], use_container_width=True,
                     type=("primary" if ss.gym == g["id"] else "secondary")):
            ss.gym = g["id"]
            st.rerun()
    st.divider()
    if st.button("Weiter →", type="primary", use_container_width=True, disabled=not ss.gym):
        ss.phase = "commit"
        st.rerun()


def view_commit():
    gym = next((g for g in GYMS if g["id"] == ss.gym), None)
    st.markdown("<div style='text-align:center;margin-top:30px'><div style='font-size:60px'>🔥</div></div>",
                unsafe_allow_html=True)
    st.markdown("## Du bist bereit.")
    st.markdown("Deine Journey beginnt **heute**. Kein Druck — ein Tag nach dem anderen.")
    st.markdown(f"<div class='card'><span class='muted' style='font-size:13px'>Dein Gym</span><br>"
                f"<b style='font-size:16px'>{gym['n'] if gym else ''}</b><br>"
                f"<span class='muted' style='font-size:13px'>Erste 14 Tage komplett kostenlos.</span></div>",
                unsafe_allow_html=True)
    if st.button("Gym-Journey starten 🚀", type="primary", use_container_width=True):
        ss.phase = "journey"
        ss.start_date = datetime.date.today()
        st.rerun()


def top_nav():
    st.markdown("### Gym<span style='color:#FF7A1A'>Start</span>", unsafe_allow_html=True)
    views = ["📅 Heute", "🗓 Wochenplan", "📈 Verlauf", "⚙️ Einstellungen"]
    labels = ["📅 Heute", "🗓 Woche", "📈 Verlauf", "⚙️ Menü"]
    cols = st.columns(4)
    for col, lbl, v in zip(cols, labels, views):
        if col.button(lbl, key="nav_" + v, use_container_width=True,
                      type=("primary" if ss.view == v else "secondary")):
            ss.view = v
            st.rerun()
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)


def render_meals(ai, m):
    html = (f"<div class='card'><h3 style='margin:0 0 6px'>🍽️ Ernährung heute · {m['kcal']} kcal</h3>"
            f"<div style='display:flex;justify-content:space-around;margin:6px 0 4px'>"
            f"<div><div style='font-weight:800;color:#27AE60'>{m['protein']}g</div><div class='muted' style='font-size:11px'>PROTEIN</div></div>"
            f"<div><div style='font-weight:800;color:#FF7A1A'>{m['carbs']}g</div><div class='muted' style='font-size:11px'>CARBS</div></div>"
            f"<div><div style='font-weight:800;color:#C79A2E'>{m['fat']}g</div><div class='muted' style='font-size:11px'>FETT</div></div></div>")
    for x in ai.get("mahlzeiten", []):
        html += (f"<div class='meal'><span class='mi'>{x.get('emoji','🍽️')}</span>"
                 f"<div><div class='mt'>{x.get('titel','')}</div><div class='md'>{x.get('beschreibung','')}</div></div>"
                 f"<div class='mk'>{x.get('kcal','')} kcal<br>{x.get('protein','')}g P</div></div>")
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_day(day, ai):
    m = macros(ss.profile)
    if ai.get("motivation"):
        st.markdown(f"<div class='card'><p style='font-size:15px'>{ai['motivation']}</p></div>",
                    unsafe_allow_html=True)

    for sec in ai.get("abschnitte", []):
        st.markdown(f"<div class='card'><h3 style='margin:0 0 6px'>{sec.get('emoji','•')} "
                    f"{sec.get('ueberschrift','')}</h3><p>{sec.get('text','')}</p></div>",
                    unsafe_allow_html=True)

    uebungen = ai.get("uebungen", [])
    if uebungen:
        st.markdown("### 🏋️ Heutiges Workout")
        st.markdown(
            "<div class='tip'>ℹ️ <b>Was bedeutet Sätze × Wiederholungen?</b> Eine "
            "<b>Wiederholung</b> ist eine komplette Bewegung (z.B. einmal drücken und "
            "zurück). Ein <b>Satz</b> ist eine Runde dieser Wiederholungen am Stück — "
            "danach 1–2 Min Pause, dann der nächste Satz.</div>", unsafe_allow_html=True)
        for u in uebungen:
            found = find_exercise(u.get("name", ""))
            name = found[0] if found else u.get("name", "")
            info = found[1] if found else None
            st.markdown(f"**{name}**" + (f" · _{info['m']}_" if info else ""))
            st.markdown(f"<div class='setpill'>🔁 {u.get('saetze',3)} Sätze × "
                        f"{u.get('wdh',10)} Wiederholungen · ⏱ ~90 Sek. Pause</div>",
                        unsafe_allow_html=True)
            if info:
                st.video(f"https://www.youtube.com/watch?v={info['vid']}")
            if u.get("hinweis"):
                st.markdown(f"<div class='tip'>✅ {u['hinweis']}</div>", unsafe_allow_html=True)
            if info:
                st.markdown(f"<div class='warn'>⚠️ {info['warn']}</div>", unsafe_allow_html=True)
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    render_meals(ai, m)

    if ai.get("tipp"):
        st.markdown(f"<div class='tip'>📌 <b>Tipp des Tages:</b> {ai['tipp']}</div>",
                    unsafe_allow_html=True)

    # Tag 1: interaktive Gym-Tasche
    if day == 1:
        st.markdown("### 🎒 Gym-Tasche packen")
        items = ["🧻 Handtuch", "💧 Wasserflasche", "👟 Sportschuhe",
                 "👕 Sportklamotten", "🔒 Schloss für den Spind", "🎧 Kopfhörer (optional)"]
        for i, it in enumerate(items):
            ss.checklist[i] = st.checkbox(it, value=ss.checklist.get(i, False), key=f"cl_{i}")
        if all(ss.checklist.get(i) for i in range(len(items))):
            st.success("🎉 Alles eingepackt — du bist startklar!")

    # Feedback an Trainingstagen
    if uebungen:
        st.markdown("### Wie war das Training?")
        st.caption("Dein Feedback steuert, was dein Coach dir morgen gibt.")
        cols = st.columns(3)
        for col, (label, val) in zip(cols, [("😌 Zu leicht", "zu leicht"),
                                            ("💪 Passt", "passt"), ("🥵 Zu schwer", "zu schwer")]):
            active = ss.feedback.get(day) == val
            if col.button(label, key=f"fb_{day}_{val}", use_container_width=True,
                          type=("primary" if active else "secondary")):
                ss.feedback[day] = val
                st.rerun()


def view_today():
    day = current_day()

    # Paywall an Tag 14
    if day >= 14 and not ss.premium and 14 not in ss.completed:
        st.markdown("<div style='text-align:center'><div style='font-size:56px'>🏆</div></div>",
                    unsafe_allow_html=True)
        st.markdown("## 2 Wochen durchgehalten.")
        st.markdown("Das schaffen die wenigsten. Ab jetzt wird's richtig ernst — dein Körper "
                    "beginnt sich zu verändern.")
        c1, c2 = st.columns(2)
        c1.markdown("<div class='card' style='text-align:center'><div class='badge green'>−50% 🎉</div>"
                    "<h3 style='margin:8px 0 0'>Jahr</h3><div style='font-size:22px;font-weight:800'>59,99 €</div>"
                    "<div class='muted' style='font-size:12px'>≈ 5 €/Monat</div></div>", unsafe_allow_html=True)
        c2.markdown("<div class='card' style='text-align:center'><h3 style='margin:0'>Monat</h3>"
                    "<div style='font-size:22px;font-weight:800'>9,99 €</div>"
                    "<div class='muted' style='font-size:12px'>monatlich kündbar</div></div>", unsafe_allow_html=True)
        if st.button("Weitermachen 🚀", type="primary", use_container_width=True):
            ss.premium = True
            st.rerun()
        return

    st.markdown(f"<div class='badge'>TAG {day} · "
                f"{(datetime.date.today()+datetime.timedelta(days=ss.day_offset)).strftime('%A')}</div>",
                unsafe_allow_html=True)
    if streak() > 0:
        st.markdown(f"<div class='streak'>🔥 {streak()} Tage Streak</div>", unsafe_allow_html=True)

    ai = ss.ai_content.get(day)
    if not ai or "error" in ai:
        if not ss.api_key:
            st.markdown("## Dein KI-Coach fehlt noch")
            st.warning("Trag oben unter **⚙️ Menü** deinen OpenAI-Key ein — dann "
                       "erstellt dein Coach den heutigen Tag individuell für dich.")
            return
        with st.spinner("🤖 Dein Coach stellt deinen Tag zusammen …"):
            ai = generate_day(day)
            ss.ai_content[day] = ai
        if "error" in ai:
            st.error(f"Konnte den Tag nicht laden: {ai['error']}")
            if st.button("🔄 Nochmal versuchen"):
                ss.ai_content.pop(day, None)
                st.rerun()
            return

    st.markdown(f"## {ai.get('titel','Dein Tag')}")
    if ai.get("untertitel"):
        st.caption(ai["untertitel"])

    render_day(day, ai)

    st.divider()
    if day in ss.completed:
        st.success("✓ Heute erledigt — stark!")
    else:
        if st.button(f"Tag {day} abschließen ✓", type="primary", use_container_width=True):
            ss.completed.add(day)
            st.balloons()
            st.rerun()
    if st.button("🔄 Tag neu generieren", use_container_width=True):
        ss.ai_content.pop(day, None)
        st.rerun()


def view_week():
    st.markdown("## 🗓 Dein Wochenplan")
    st.caption(f"{plan_name(ss.profile)} · {ss.profile['days']}× Training pro Woche. "
               "So sieht eine typische Woche aus:")
    for tag, typ, num, focus in week_plan():
        if typ == "train":
            st.markdown(f"<div class='wkrow train'><div class='wkday'>{tag}</div><div>"
                        f"<div class='wktitle'>🏋️ Training {num}</div>"
                        f"<div class='wkfocus'>{focus}</div></div></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='wkrow'><div class='wkday'>{tag}</div><div>"
                        f"<div class='wktitle' style='color:#8A7E73'>😴 Ruhetag</div>"
                        f"<div class='wkfocus'>{focus}</div></div></div>", unsafe_allow_html=True)


def view_history():
    st.markdown("## 📈 Dein Verlauf")
    d = current_day()
    titles = {1: "Mentale Vorbereitung", 2: "Ernährungs-Setup", 3: "Erster Gymbesuch"}
    for i in range(1, max(d + 2, 8)):
        done = i in ss.completed
        icon = "✅" if done else ("📍" if i == d else ("🔒" if i > d else "—"))
        name = titles.get(i, "Trainingstag") if i > 3 or i in titles else "Trainingstag"
        style = "opacity:.5" if i > d else ""
        st.markdown(f"<div class='wkrow' style='{style}'><div class='wkday'>{icon}</div>"
                    f"<div><div class='wktitle'>Tag {i} · {name}</div></div></div>",
                    unsafe_allow_html=True)


def view_settings():
    st.markdown("## ⚙️ Einstellungen")
    st.markdown("#### OpenAI API-Key")
    ss.api_key = st.text_input("API-Key (sk-...)", value=ss.api_key, type="password",
                               help="Nötig, damit dein Coach die Tage generiert.")
    st.info("🔒 Beim Hosting auf Streamlit Cloud legst du den Key besser in den **Secrets** "
            "ab (Menü → Settings → Secrets: `OPENAI_API_KEY=\"sk-...\"`). Dann müssen Nutzer "
            "nichts eingeben. Kosten ~0,002 € pro Tag.")
    st.divider()
    st.markdown("#### Journey (Demo-Steuerung)")
    st.caption("Im echten Betrieb schaltet sich täglich ein neuer Tag frei. Zum Ausprobieren:")
    c1, c2 = st.columns(2)
    if c1.button("⏭ Nächster Tag", use_container_width=True):
        ss.day_offset += 1
        st.rerun()
    if c2.button("⏮ Vorheriger Tag", use_container_width=True, disabled=ss.day_offset <= 0):
        ss.day_offset = max(0, ss.day_offset - 1)
        st.rerun()
    st.divider()
    st.markdown("#### Profil")
    st.write(ss.profile)
    if st.button("🔁 App komplett zurücksetzen"):
        for k in list(ss.keys()):
            del ss[k]
        st.rerun()


def view_journey():
    top_nav()
    {"📅 Heute": view_today, "🗓 Wochenplan": view_week,
     "📈 Verlauf": view_history, "⚙️ Einstellungen": view_settings}[ss.view]()


# ----------------------------------------------------------------------------
# ROUTER
# ----------------------------------------------------------------------------
{"onboarding": view_onboarding, "result": view_result, "gym": view_gym,
 "commit": view_commit, "journey": view_journey}[ss.phase]()
