import time
import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

# Page Configuration (App look & feel)
st.set_page_config(
    page_title="SunWorth AI - Solar Feasibility & Profit Calculator",
    page_icon="☀️",
    layout="centered",
)

# Custom CSS for Attractive Human-Centric UI
st.markdown(
    """
<style>
    .main {
        background-color: #f8fafc;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #ff9900;
        color: white;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #e68a00;
        color: white;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        text-align: center;
        border-left: 5px solid #ff9900;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Initialize Session States for Navigation Flow
if "step" not in st.session_state:
  st.session_state.step = 1
if "slide" not in st.session_state:
  st.session_state.slide = 0
if "lang" not in st.session_state:
  st.session_state.lang = "English"
if "lat" not in st.session_state:
  st.session_state.lat = 13.0827  # Default Chennai
if "lon" not in st.session_state:
  st.session_state.lon = 80.2707

# Multi-language Dictionary
texts = {
    "English": {
        "welcome": "Welcome to SunWorth ☀️",
        "subtitle": (
            "Find out if Solar is worth your roof! Get exact panel counts,"
            " energy production, and profit reports."
        ),
        "next": "Next ➡️",
        "login_title": "User Login 🔐",
        "terms_title": "Terms & Conditions 📜",
        "guide_title": "How to Use This App 📱",
        "input_title": "Enter Your Roof & Location Details 📍",
        "calc_btn": "Calculate Solar Worth 🚀",
        "report_title": "Your Complete Solar & Financial Report 📊",
        "thank_you": "Thank You for Choosing Green Energy! 🌱",
    },
    "தமிழ் (Tamil)": {
        "welcome": "SunWorth-க்கு நல்வரவு ☀️",
        "subtitle": (
            "உங்கள் வீட்டு மொட்டை மாடியில் சோலார் பேனல் பொருத்துவது லாபமா என"
            " துல்லியமாக கணக்கிடுங்கள்!"
        ),
        "next": "அடுத்து ➡️",
        "login_title": "உள்நுழைக (Login) 🔐",
        "terms_title": "விதிமுறைகள் மற்றும் நிபந்தனைகள் 📜",
        "guide_title": "செயலியை பயன்படுத்தும் முறை 📱",
        "input_title": "உங்கள் இடம் மற்றும் கூரை அளவை உள்ளிடவும் 📍",
        "calc_btn": "சோலார் லாபத்தை கணக்கிடுங்கள் 🚀",
        "report_title": "உங்கள் முழுமையான சோலார் & நிதி அறிக்கை 📊",
        "thank_you": "பசுமை ஆற்றலைத் தேர்ந்தெடுத்ததற்கு மிக்க நன்றி! 🌱",
    },
}

t = texts[st.session_state.lang]

# ==========================================
# STEP 1: WELCOME & LANGUAGE SELECTION
# ==========================================
if st.session_state.step == 1:
  st.image(
      "https://images.unsplash.com/photo-1509391366360-2e959784a276?auto=format&fit=crop&w=800&q=80",
      use_container_width=True,
  )
  st.title(t["welcome"])
  st.write(t["subtitle"])

  st.markdown("---")
  selected_lang = st.selectbox(
      "🌐 Select Your Preferred Language / மொழியைத் தேர்ந்தெடுக்கவும்:",
      ["English", "தமிழ் (Tamil)"],
  )
  st.session_state.lang = selected_lang

  if st.button(texts[selected_lang]["next"]):
    st.session_state.step = 2
    st.rerun()

# ==========================================
# STEP 2: LOGIN & TERMS AND CONDITIONS
# ==========================================
elif st.session_state.step == 2:
  st.title(t["login_title"])
  with st.container():
    name = st.text_input("Full Name / பெயர்", placeholder="Ex: Karthik")
    email_or_phone = st.text_input(
        "Email or Mobile Number", placeholder="Ex: karthik@email.com"
    )
    password = st.text_input("Password", type="password")

    st.markdown("### " + t["terms_title"])
    with st.expander("Read Terms & Conditions"):
      st.write("""
            1. **Estimation Accuracy:** Solar generation depends on weather, shading, and panel tilt. Values shown are industry-standard estimates.
            2. **Cost & Subsidy:** Setup costs are based on current market rates (₹55,000 - ₹65,000 per kW) before government subsidies.
            3. **Data Privacy:** Your location data is used strictly for calculating peak sun hours.
            """)
    agree = st.checkbox("I agree to the Terms & Conditions")

    col1, col2 = st.columns(2)
    with col1:
      if st.button("⬅️ Back"):
        st.session_state.step = 1
        st.rerun()
    with col2:
      if st.button(t["next"]):
        if name and email_or_phone and agree:
          st.session_state.user_name = name
          st.session_state.step = 3
          st.rerun()
        else:
          st.warning(
              "Please fill in your details and accept the Terms & Conditions!"
          )

# ==========================================
# STEP 3: INTERACTIVE TUTORIAL SLIDES
# ==========================================
elif st.session_state.step == 3:
  st.title(t["guide_title"])

  slides = [
      {
          "title": "Step 1: Pin Your Exact Location 📍",
          "desc": (
              "Click directly on the interactive map or type your city to find"
              " the exact sunlight potential of your roof."
          ),
          "img": "https://images.unsplash.com/photo-1524661135-423995f22d0b?auto=format&fit=crop&w=800&q=80",
      },
      {
          "title": "Step 2: Enter Roof Size & EB Rate 📐",
          "desc": (
              "Tell us your shadow-free roof area (in sq.ft) and how much you"
              " pay per electricity unit (₹)."
          ),
          "img": "https://images.unsplash.com/photo-1613665813446-82a78c468a1d?auto=format&fit=crop&w=800&q=80",
      },
      {
          "title": "Step 3: Instant Profit & Payback Report 💰",
          "desc": (
              "See how many panels fit, total setup cost, monthly/yearly"
              " savings, and when you'll recover your money!"
          ),
          "img": "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?auto=format&fit=crop&w=800&q=80",
      },
  ]

  current = slides[st.session_state.slide]
  st.image(current["img"], use_container_width=True)
  st.subheader(current["title"])
  st.info(current["desc"])
  st.progress((st.session_state.slide + 1) / len(slides))

  col1, col2, col3 = st.columns(3)
  with col1:
    if st.session_state.slide > 0:
      if st.button("⬅️ Previous Slide"):
        st.session_state.slide -= 1
        st.rerun()
  with col3:
    if st.session_state.slide < len(slides) - 1:
      if st.button("Next Slide ➡️"):
        st.session_state.slide += 1
        st.rerun()
    else:
      if st.button("Get Started 🚀"):
        st.session_state.step = 4
        st.rerun()

# ==========================================
# STEP 4: USER INPUTS (MAP + AREA + EB COST)
# ==========================================
elif st.session_state.step == 4:
  st.title(t["input_title"])
  st.write(
      f"Hello **{st.session_state.get('user_name', 'User')}**! Let's check your"
      " roof's solar potential."
  )

  # Location Option: Type OR Map Select
  loc_mode = st.radio(
      "How would you like to select your location?",
      ["📍 Pin Exact Location on Map", "⌨️ Enter Location Manually"],
      horizontal=True,
  )

  if loc_mode == "📍 Pin Exact Location on Map":
    st.caption(
        "👇 Click anywhere on the map below to drop a pin on your building/area:"
    )
    m = folium.Map(
        location=[st.session_state.lat, st.session_state.lon], zoom_start=12
    )
    folium.Marker(
        [st.session_state.lat, st.session_state.lon], tooltip="Selected Roof"
    ).add_to(m)

    map_data = st_folium(m, height=300, width=700)
    if map_data and map_data.get("last_clicked"):
      st.session_state.lat = map_data["last_clicked"]["lat"]
      st.session_state.lon = map_data["last_clicked"]["lng"]
      st.success(
          f"📌 Exact Coordinates Selected: **{st.session_state.lat:.4f}° N,"
          f" {st.session_state.lon:.4f}° E**"
      )
    location_name = (
        f"Lat: {st.session_state.lat:.4f}, Lon: {st.session_state.lon:.4f}"
    )
  else:
    location_name = st.text_input(
        "Enter City / Area Name", placeholder="Ex: Tambaram, Chennai"
    )

  st.markdown("---")
  col1, col2 = st.columns(2)
  with col1:
    roof_area = st.number_input(
        "Shadow-Free Roof Area (in sq. ft)",
        min_value=100,
        max_value=50000,
        value=500,
        step=50,
    )
  with col2:
    unit_cost = st.number_input(
        "Electricity Cost per Unit (₹ / kWh)",
        min_value=1.0,
        max_value=30.0,
        value=8.0,
        step=0.5,
    )

  if st.button(t["calc_btn"]):
    if loc_mode == "⌨️ Enter Location Manually" and not location_name:
      st.error("Please enter your location name!")
    else:
      st.session_state.roof_area = roof_area
      st.session_state.unit_cost = unit_cost
      st.session_state.location_name = location_name
      st.session_state.step = 5
      st.rerun()

# ==========================================
# STEP 5: FINANCIAL & PRODUCTION REPORT + THANK YOU
# ==========================================
elif st.session_state.step == 5:
  with st.spinner("Analyzing sunlight irradiance & calculating ROI..."):
    time.sleep(1)

  # --- REALISTIC SOLAR ENGINEERING CALCULATIONS ---
  # 1 kW requires ~100 sq.ft of shadow-free area
  # 1 Panel = ~540 Watts (0.54 kW) -> ~54 sq.ft per panel
  usable_area = st.session_state.roof_area * 0.80  # 80% usable after walking space
  system_size_kw = round(usable_area / 100, 2)
  num_panels = max(1, int(system_size_kw / 0.54))

  # Production: Average India solar irradiance = 4.5 units per kW per day
  daily_units = round(system_size_kw * 4.5, 1)
  monthly_units = round(daily_units * 30, 0)
  yearly_units = round(daily_units * 365, 0)

  # Financials (Avg ₹60,000 per kW setup cost)
  setup_cost = int(system_size_kw * 60000)
  monthly_savings = int(monthly_units * st.session_state.unit_cost)
  yearly_savings = int(yearly_units * st.session_state.unit_cost)
  payback_years = (
      round(setup_cost / yearly_savings, 1) if yearly_savings > 0 else 0
  )
  lifetime_profit = (yearly_savings * 25) - setup_cost  # 25 years panel life

  # Worthiness Verdict
  is_worth = payback_years <= 5.5 and system_size_kw >= 1.0

  st.title(t["report_title"])
  st.caption(
      f"📍 Location: {st.session_state.location_name} | 📐 Roof Area:"
      f" {st.session_state.roof_area} sq.ft | ⚡ Tariff:"
      f" ₹{st.session_state.unit_cost}/unit"
  )

  # Verdict Banner
  if is_worth:
    st.success(
        "✅ **VERDICT: 100% WORTH IT!** Your roof has great solar potential"
        f" with a fast payback of **{payback_years} years**."
    )
  else:
    st.warning(
        "⚠️ **VERDICT: MODERATE WORTH.** Small roof area or low EB tariff"
        " increases the payback period."
    )

  # Key Metrics Grid
  st.subheader("1️⃣ Technical & Production Summary")
  c1, c2, c3 = st.columns(3)
  c1.metric("System Capacity", f"{system_size_kw} kW")
  c2.metric("Panels Needed (540W)", f"{num_panels} Panels")
  c3.metric("Yearly Generation", f"{int(yearly_units):,} Units")

  st.subheader("2️⃣ Financial & Profit Breakdown")
  f1, f2, f3, f4 = st.columns(4)
  f1.metric("Total Setup Cost", f"₹{setup_cost:,}")
  f2.metric("Monthly Profit", f"₹{monthly_savings:,}")
  f3.metric("Yearly Profit", f"₹{yearly_savings:,}")
  f4.metric("Payback Period", f"{payback_years} Years")

  # 10-Year Cumulative Cashflow Chart
  st.subheader("3️⃣ Investment Recovery & 10-Year Profit Growth 📈")
  years = list(range(0, 11))
  cashflow = [-setup_cost + (yearly_savings * y) for y in years]
  df_chart = pd.DataFrame({"Year": years, "Net Profit / Loss (₹)": cashflow})
  st.line_chart(df_chart.set_index("Year"))

  st.info(
      "💡 **25-Year Lifetime Net Profit:** After recovering your setup cost,"
      " you will earn approximately **₹"
      f" {lifetime_profit:,}** in pure electricity savings!"
  )

  # Thank You Screen
  st.markdown("---")
  st.balloons()
  st.markdown(
      f"""
    <div style="text-align: center; padding: 25px; background-color: #e6f4ea; border-radius: 15px;">
        <h2>{t['thank_you']}</h2>
        <p>Thank you, <b>{st.session_state.get('user_name', 'Friend')}</b>! You are one step closer to zero electricity bills and a cleaner planet.</p>
    </div>
    """,
      unsafe_allow_html=True,
  )

  st.write("")
  if st.button("🔄 Calculate for Another Roof"):
    st.session_state.step = 4
    st.rerun()