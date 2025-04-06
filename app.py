import streamlit as st
import pandas as pd
import qrcode
from datetime import datetime
import os

# File paths
labs_file = "labs.xlsx"
tools_file = "tools.xlsx"
borrow_file = "borrowed_equipment.xlsx"

# Load labs
@st.cache_data
def load_labs():
    try:
        labs_df = pd.read_excel(labs_file)
        return labs_df['שם מעבדה'].tolist()
    except FileNotFoundError:
        st.error("קובץ המעבדות לא נמצא")
        return []
    except Exception as e:
        st.error(f"שגיאה בטעינת המעבדות: {str(e)}")
        return []

# Main screen
def main_screen():
    # RTL CSS for entire app
    st.markdown("""
        <style>
        .rtl {
            direction: rtl;
            text-align: right;
        }
        .stTextInput, .stNumberInput, .stSelectbox {
            direction: rtl;
            text-align: right;
        }
        .stButton>button {
            height: 38px;
            width: 100%;
            direction: rtl;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 class="rtl">מערכת השאלת ציוד</h1>', unsafe_allow_html=True)
    
    # QR Code for login
    qr = qrcode.QRCode()
    qr.add_data(st.secrets.get("app_url", "http://localhost:8501"))
    qr.make()
    qr_img = qr.make_image(fill='black', back_color='white')
    qr_img.save("qr_login.png")
    st.image("qr_login.png", caption="סרוק כדי לגשת")

    st.markdown('<div class="rtl">שם משתמש:</div>', unsafe_allow_html=True)
    username = st.text_input("", key="username")
    labs = load_labs()
    st.markdown('<div class="rtl">בחר מעבדה:</div>', unsafe_allow_html=True)
    lab = st.selectbox("", labs, key="lab")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("השאל כלים"):
            if username and lab:
                st.session_state['username'] = username
                st.session_state['lab'] = lab
                st.session_state['screen'] = 'borrow'
            else:
                st.error("יש להזין שם משתמש ומעבדה")
    with col2:
        if st.button("החזר כלים"):
            if username and lab:
                st.session_state['username'] = username
                st.session_state['lab'] = lab
                st.session_state['screen'] = 'return'
            else:
                st.error("יש להזין שם משתמש ומעבדה")

# Borrow screen
def borrow_screen():
    st.markdown('<h2 class="rtl">השאלת כלים</h2>', unsafe_allow_html=True)
    
    # Input area
    with st.container():
        st.markdown('<div class="rtl">שם הכלי:</div>', unsafe_allow_html=True)
        tool_name = st.text_input("", key="new_tool")
        st.markdown('<div class="rtl">כמות להשאיל:</div>', unsafe_allow_html=True)
        quantity = st.number_input("", min_value=1, step=1, key="new_qty")
        
        if st.button("הוסף לרשימה"):
            if tool_name:
                if 'borrow_session' not in st.session_state:
                    st.session_state['borrow_session'] = []
                st.session_state['borrow_session'].append({
                    'שם משתמש': st.session_state['username'],
                    'שם מעבדה': st.session_state['lab'],
                    'שם הכלי': tool_name,
                    'כמות': quantity,
                    'תאריך השאלה': None  # Will be set on confirmation
                })
                st.success(f"נוסף: {tool_name} - כמות: {quantity}")
            else:
                st.error("יש לרשום שם כלי")

    # Divider
    st.divider()

    # Borrow session area
    if 'borrow_session' in st.session_state and st.session_state['borrow_session']:
        st.markdown('<div class="rtl">כלים שנבחרו ב-Session זה:</div>', unsafe_allow_html=True)
        edited_session = []
        for i, item in enumerate(st.session_state['borrow_session']):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                new_tool_name = st.text_input("", value=item['שם הכלי'], key=f"tool_{i}")
            with col2:
                new_quantity = st.number_input("", min_value=1, step=1, value=item['כמות'], key=f"qty_{i}")
            with col3:
                if st.button("מחק", key=f"del_{i}"):
                    continue
            edited_session.append({
                'שם משתמש': item['שם משתמש'],
                'שם מעבדה': item['שם מעבדה'],
                'שם הכלי': new_tool_name,
                'כמות': new_quantity,
                'תאריך השאלה': item['תאריך השאלה']
            })
        st.session_state['borrow_session'] = edited_session

    col_confirm, col_back = st.columns(2)
    with col_confirm:
        if st.button("אשר את כל ההשאלות"):
            if 'borrow_session' in st.session_state and st.session_state['borrow_session']:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                for item in st.session_state['borrow_session']:
                    item['תאריך השאלה'] = current_time
                borrow_df = pd.DataFrame(st.session_state['borrow_session'])
                try:
                    existing_borrows = pd.read_excel(borrow_file)
                    borrow_df = pd.concat([existing_borrows, borrow_df])
                except FileNotFoundError:
                    pass
                borrow_df.to_excel(borrow_file, index=False)
                st.success("כל ההשאלות בוצעו בהצלחה")
                st.session_state['borrow_session'] = []
                st.session_state['screen'] = 'main'
            else:
                st.error("לא נבחרו כלים להשאלה")
    with col_back:
        if st.button("חזור"):
            st.session_state['screen'] = 'main'

# Return screen
def return_screen():
    st.markdown('<h2 class="rtl">החזרת כלים</h2>', unsafe_allow_html=True)
    
    try:
        borrow_df = pd.read_excel(borrow_file)
        user_borrows = borrow_df[(borrow_df['שם משתמש'] == st.session_state['username']) & 
                                 (borrow_df['שם מעבדה'] == st.session_state['lab'])]
        if not user_borrows.empty:
            st.markdown('<div class="rtl">כלים שהושאלו בעבר:</div>', unsafe_allow_html=True)
            st.dataframe(user_borrows)
            tool_options = user_borrows.apply(lambda row: f"{row['שם הכלי']} (כמות: {row['כמות']}, תאריך: {row['תאריך השאלה']})", axis=1).tolist()
            st.markdown('<div class="rtl">בחר כלי להחזרה:</div>', unsafe_allow_html=True)
            selected_tool = st.selectbox("", tool_options)
            st.markdown('<div class="rtl">כמות להחזיר:</div>', unsafe_allow_html=True)
            quantity_to_return = st.number_input("", min_value=1, step=1)
            
            if st.button("הוסף להחזרה"):
                if quantity_to_return <= int(selected_tool.split("כמות: ")[1].split(",")[0]):
                    tool_name = selected_tool.split(" (")[0]
                    if 'return_session' not in st.session_state:
                        st.session_state['return_session'] = []
                    st.session_state['return_session'].append({
                        'שם משתמש': st.session_state['username'],
                        'שם מעבדה': st.session_state['lab'],
                        'שם הכלי': tool_name,
                        'כמות להחזיר': quantity_to_return,
                        'תאריך השאלה': selected_tool.split("תאריך: ")[1].rstrip(")")
                    })
                    st.success(f"נוסף להחזרה: {tool_name} - כמות: {quantity_to_return}")
                else:
                    st.error("כמות ההחזרה גדולה מהכמות המושאלת")

            if 'return_session' in st.session_state and st.session_state['return_session']:
                st.markdown('<div class="rtl">כלים להחזרה ב-Session זה:</div>', unsafe_allow_html=True)
                for item in st.session_state['return_session']:
                    st.markdown(f'<div class="rtl">{item["שם הכלי"]} - כמות: {item["כמות להחזיר"]}</div>', unsafe_allow_html=True)

            if st.button("אשר את כל ההחזרות"):
                for return_item in st.session_state['return_session']:
                    mask = (borrow_df['שם משתמש'] == return_item['שם משתמש']) & \
                           (borrow_df['שם מעבדה'] == return_item['שם מעבדה']) & \
                           (borrow_df['שם הכלי'] == return_item['שם הכלי']) & \
                           (borrow_df['תאריך השאלה'] == return_item['תאריך השאלה'])
                    borrow_df.loc[mask, 'כמות'] -= return_item['כמות להחזיר']
                borrow_df = borrow_df[borrow_df['כמות'] > 0]
                borrow_df.to_excel(borrow_file, index=False)
                st.success("כל ההחזרות בוצעו בהצלחה")
                st.session_state['return_session'] = []
                st.session_state['screen'] = 'main'
        else:
            st.markdown('<div class="rtl">אין השאלות קודמות</div>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.markdown('<div class="rtl">אין השאלות קודמות</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"שגיאה בטעינת ההשאלות: {str(e)}")

    if st.button("חזור"):
        st.session_state['screen'] = 'main'

# History screen
def history_screen():
    st.markdown('<h2 class="rtl">היסטוריית השאלות</h2>', unsafe_allow_html=True)
    try:
        borrow_df = pd.read_excel(borrow_file)
        st.dataframe(borrow_df)
    except FileNotFoundError:
        st.markdown('<div class="rtl">אין נתונים זמינים</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"שגיאה בטעינת ההיסטוריה: {str(e)}")
    if st.button("חזור"):
        st.session_state['screen'] = 'main'

# Main app logic
if 'screen' not in st.session_state:
    st.session_state['screen'] = 'main'

if st.session_state['screen'] == 'main':
    main_screen()
elif st.session_state['screen'] == 'borrow':
    borrow_screen()
elif st.session_state['screen'] == 'return':
    return_screen()
elif st.session_state['screen'] == 'history':
    history_screen()

# Sidebar for navigation
st.sidebar.markdown('<h2 class="rtl">ניווט</h2>', unsafe_allow_html=True)
if st.sidebar.button("דף ראשי"):
    st.session_state['screen'] = 'main'
if st.sidebar.button("היסטוריה"):
    st.session_state['screen'] = 'history'
