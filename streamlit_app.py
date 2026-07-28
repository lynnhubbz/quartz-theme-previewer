
import json
import urllib.request
import streamlit as st
from st_copy import copy_button
import math
import streamlit.components.v1 as cp

# ======================================================================== #
# NOTES                                                                    #
# ======================================================================== #

# TODO Refine Description
#   Add comments here and there
#   Forward information from the repo themes (EMBED SOURCE OF DATA)
#   DONE Add copy button next to the theme name for quick npm installation
#   DONE Shorten text for link preview 
#   Make it wide instead of long 
# TODO Optimize loading
#   Add description that the site are paged because of the performance
#   Refactor codes
# TODO tidy up sidebar
#   Use mainly st.pagination instead st.number_input alone
#   Options for view how much items in a page
# TODO Add filters
#   for: mode, license, and compatibility

# ======================================================================== #
# LOADING DATA                                                             #
# ======================================================================== #

# @note The data were scrapped from https://github.com/saberzero1/quartz-themes, from the `themes.json` file

def themes_forloop(themes_dict, parsed_themes):
        # Loop through every theme item entry inside the JSON
    for theme_name, theme_info in themes_dict.items():
        # Safely extract only your three required variable attributes
        compatibility = theme_info.get("compatibility", [])
        modes = theme_info.get("modes", [])
        
        # Extract license name string safely from its sub-dictionary
        license_info = theme_info.get("license", {})
        license_name = license_info.get("name", "Unknown License")
        
        # Append the flattened dictionary to our clean list structure
        parsed_themes.append({
            "name": theme_name,
            "compatibility": compatibility,
            "modes": modes,
            "license": license_name
        })
        
    return parsed_themes

@st.cache_data
def load_and_parse_themes():
    # Replace with the actual URL pointing to your online JSON file
    url = "https://raw.githubusercontent.com/saberzero1/quartz-themes/44dd81094c0dd982b67f93d91ef8c80da3f583e6/themes.json"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            # Access the primary parent "themes" dictionary wrapper safely
            themes_dict = data.get("themes", {})
            
            parsed_themes = []
            parsed_themes = themes_forloop(themes_dict, parsed_themes)
            return parsed_themes
            
    except Exception as e:
        st.error(f"Failed to extract JSON properties: {e}")
        return []

# Execution -------------------------------------------------------------- #

extracted_themes = load_and_parse_themes()


# ======================================================================== #
# SIDEBAR CONFIG                                                           #
# ======================================================================== #


# 2. Configure Virtualization Limits
ITEMS_PER_PAGE = 60
total_pages = math.ceil(len(extracted_themes) / ITEMS_PER_PAGE)

# 3. Structural Header Filter Configuration Interface Panel layout
st.sidebar.header("🎯 Navigation Matrix")
search_query = st.sidebar.text_input("Search Themes:", "").strip().lower()

# FIX 1: Access the theme name string key inside the dictionary object for search matching
if search_query:
    filtered_themes = [t for t in extracted_themes if search_query in t["name"].lower()]
else:
    filtered_themes = extracted_themes

total_filtered_pages = math.ceil(len(filtered_themes) / ITEMS_PER_PAGE)

if total_filtered_pages == 0:
    st.warning("No themes found matching your search term criteria.")
    st.stop()

# Clean page boundaries fallback indicator mechanism
current_page = st.sidebar.number_input(
    f"Page (1 to {total_filtered_pages}):", 
    min_value=1, 
    max_value=total_filtered_pages, 
    value=1,
    step=1
)

# 4. Extract target index boundaries slice range formulas
start_idx = (current_page - 1) * ITEMS_PER_PAGE
end_idx = start_idx + ITEMS_PER_PAGE
active_page_chunk = filtered_themes[start_idx:end_idx]

st.write(f"Showing items **{start_idx + 1}** to **{min(end_idx, len(filtered_themes))}** out of **{len(filtered_themes)}** records.")

if "unfrozen_cards" not in st.session_state:
    st.session_state.unfrozen_cards = {}

# ======================================================================== #
# PAGE CONFIGS AND CONTENTS                                                 #
# ======================================================================== #

st.set_page_config(layout="wide")
st.title("🚀 Mass Scale Theme Previewer (860+ Items Optimized)")

# ======================================================================== #
# GENERATING WIDGET WITH FOR LOOP                                          #
# ======================================================================== #

def html_format(target_lnk):
    html_format = f"""
        <!-- Parent box 4w:3h -->
        <div style="width: 100%; height: 280px; border-radius: 12px; overflow: hidden; position: relative; background: #111;">
            
            <!-- The Iframe is made 133.33% larger, then scaled back down by 0.75 to fill the box edge-to-edge -->
            <iframe src="{target_lnk}" 
                    scrolling="no"
                    style="border: none; 
                        position: absolute; 
                        width: 140%; 
                        height: 140%; 
                        transform: scale(0.75); 
                        transform-origin: top left;
                        ">
            </iframe>
            
            <!-- Interactive glass click shield 
            <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.01); cursor: pointer;"></div> -->   
        </div>
    """
    return html_format


def header_and_copybutton(theme_name):
    col1, col2 = st.columns([5,1], vertical_alignment="bottom")
    col1.markdown(f"#### {theme_name}")
    
    with col2:
        copy_button(f"npm i @quartz-themes/{theme_name}")

# 5. Render performance-isolated grid layout structure safely
N_COLS = 4
for row_idx in range(0, len(active_page_chunk), N_COLS):
    chunk = active_page_chunk[row_idx:row_idx + N_COLS]
    cols = st.columns(N_COLS)
    
    # FIX 2: Rename list item parameter to handle dictionary properties cleanly
    for col_idx, theme_data in enumerate(chunk):
        # Extract variables from extracted JSON schema keys
        theme_name = theme_data["name"]
        compatibility = ", ".join(theme_data["compatibility"]).upper()
        modes = ", ".join(theme_data["modes"]).title()
        license_type = theme_data["license"]
        
        # FIX 3: Bind state tracking keys directly to the theme name string identifier
        # This keeps state logic locked accurately even when pagination indices recalculate
        card_key = f"card_{theme_name}"
        is_active = st.session_state.unfrozen_cards.get(card_key, False)
        
        # Clean URL string formatting pointing toward the target destination
        target_lnk = f"https://quartz-themes.github.io/{theme_name}"
        
        with cols[col_idx]:
            itemcontainer = st.container(border=True)
            with itemcontainer:
                
                header_and_copybutton(theme_name)
                    
                st.iframe(
                    html_format(target_lnk),
                    width="stretch",
                    height="content"
                )
                st.write(f"[link preview]({target_lnk})")

                # Display metadata extracted from JSON schema underneath each layout window
                st.caption(f"🔧 **Compat:** {compatibility} | 🎨 **Modes:** {modes} | 📜 **License:** {license_type}")
