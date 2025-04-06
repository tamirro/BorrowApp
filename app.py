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
        st.error("קובץ המעבדות לא נמצא - Lab file not found")
        return []
    except Exception as e:
        st.error(f"שגיאה בטעינת המעבדות: {str(e)} - Error loading labs: {str(e)}")
        return []

# Main screen
def main_screen():
    # RTL and centering CSS
    st.markdown("""
        <style>
        .rtl {
            direction: rtl;
            text-align: right;
        }
        .center-inputs {
            display: flex;
            justify-content: center;
            width: 100%;
        }
        .stTextInput, .stNumberInput, .stSelectbox {
            direction: rtl;
            text-align: right;
            max-width: 400px; /* Limit width for better centering */
            margin: 0 auto;
        }
        .stTextInput input, .stNumberInput input {
            text-align: center; /* Center existing text */
        }
        .stButton>button {
            height: 38px;
            width: 100%;
            direction: rtl;
        }
        </style>
    """, unsafe_allow_html=True)

    # Logo
    if os.path.exists("mdde.jpg"):
        st.image("mdde.jpg", width=300, use_column_width="auto")
    else:
        st.warning("הלוגו mdde.jpg לא נמצא - Logo mdde.jpg not found")

    st.markdown('<h1 class="rtl">מערכת השאלת ציוד - Equipment Borrowing System</h1>', unsafe_allow_html=True)
    
    # QR Code for login
    qr = qrcode.QRCode()
    qr.add_data(st.secrets.get("app_url", "http://localhost:8501"))
    qr.make()
    qr_img = qr.make_image(fill='black', back_color='white')
    qr_img.save("qr_login.png")
    st.image("qr_login.png", caption="סרוק כדי לגשת - Scan to Access", width=200)

    st.markdown('<div class="rtl">שם משתמש - Username:</div>', unsafe_allow_html=True)
    with st.container():
        username = st.text_input("", key="username")
    labs = load_labs()
    st.markdown('<div class="rtl">בחר מעבדה - Select Lab:</div>', unsafe_allow_html=True)
    with st.container():
        lab = st.selectbox("", labs, key="lab")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("השאל כלים - Borrow Tools"):
            if username and lab:
                st.session_state['username'] = username
                st.session_state['lab'] = lab
                st.session_state['screen'] = 'borrow'
            else:
                st.error("יש להזין שם משתמש ומעבדה - Please enter username and lab")
    with col2:
        if st.button("החזר כלים - Return Tools"):
            if username and lab:
                st.session_state['username'] = username
                st.session_state['lab'] = lab
                st.session_state['screen'] = 'return'
            else:
                st.error("יש להזין שם משתמש ומעבדה - Please enter username and lab")

# Borrow screen
def borrow_screen():
    # Logo
    if os.path.exists("mdde.jpg"):
        st.image("mdde.jpg", width=600, use_column_width="auto")
    else:
        st.warning("הלוגו mdde.jpg לא נמצא - Logo mdde.jpg not found")

    st.markdown('<h2 class="rtl">השאלת כלים - Borrow Tools</h2>', unsafe_allow_html=True)
    
    # Input area
    with st.container():
        st.markdown('<div class="rtl">שם הכלי - Tool Name:</div>', unsafe_allow_html=True)
        tool_name = st.text_input("", key="new_tool")
        st.markdown('<div class="rtl">כמות להשאיל - Quantity to Borrow:</div>', unsafe_allow_html=True)
        quantity = st.number_input("", min_value=1, step=1, key="new_qty")
        
        if st.button("הוסף לרשימה - Add to List"):
            if tool_name:
                if 'borrow_session' not in st.session_state:
                    st.session_state['borrow_session'] = []
                st.session_state['borrow_session'].append({
                    'שם משתמש': st.session_state['username'],
                    'שם מעבדה': st.session_state['lab'],
                    'שם הכלי': tool_name,
                    'כמות': quantity,
                    'תאריך השאלה': None
                })
                st.success(f"נוסף - Added: {tool_name} - כמות - Quantity: {quantity}")
            else:
                st.error("יש לרשום שם כלי - Please enter a tool name")

    # Divider
    st.divider()

    # Borrow session area
    if 'borrow_session' in st.session_state and st.session_state['borrow_session']:
        st.markdown('<div class="rtl">כלים שנבחרו ב-Session זה - Tools Selected in This Session:</div>', unsafe_allow_html=True)
        edited_session = []
        for i, item in enumerate(st.session_state['borrow_session']):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                new_tool_name = st.text_input("", value=item['שם הכלי'], key=f"tool_{i}")
            with col2:
                new_quantity = st.number_input("", min_value=1, step=1, value=item['כמות'], key=f"qty_{i}")
            with col3:
                if st.button("מחק - Delete", key=f"del_{i}"):
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
        if st.button("אשר את כל ההשאלות - Confirm All Borrowings"):
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
                st.success("כל ההשאלות בוצעו בהצלחה - All borrowings completed successfully")
                st.session_state['borrow_session'] = []
                st.session_state['screen'] = 'main'
            else:
                st.error("לא נבחרו כלים להשאלה - No tools selected for borrowing")
    with col_back:
        if st.button("חזור - Back"):
            st.session_state['screen'] = 'main'

# Return screen
def return_screen():
    # Logo
    if os.path.exists("mdde.jpg"):
        st.image("mdde.jpg", width=300, use_column_width="auto")
    else:
        st.warning("הלוגו mdde.jpg לא נמצא - Logo mdde.jpg not found")

    st.markdown('<h2 class="rtl">החזרת כלים - Return Tools</h2>', unsafe_allow_html=True)
    
    try:
        borrow_df = pd.read_excel(borrow_file)
        user_borrows = borrow_df[(borrow_df['שם משתמש'] == st.session_state['username']) & 
                                 (borrow_df['שם מעבדה'] == st.session_state['lab'])]
        if not user_borrows.empty:
            st.markdown('<div class="rtl">כלים שהושאלו בעבר - Previously Borrowed Tools:</div>', unsafe_allow_html=True)
            st.dataframe(user_borrows)
            tool_options = user_borrows.apply(lambda row: f"{row['שם הכלי']} (כמות: {row['כמות']}, תאריך: {row['תאריך השאלה']})", axis=1).tolist()
            st.markdown('<div class="rtl">בחר כלי להחזרה - Select Tool to Return:</div>', unsafe_allow_html=True)
            with st.container():
                selected_tool = st.selectbox("", tool_options)
            st.markdown('<div class="rtl">כמות להחזיר - Quantity to Return:</div>', unsafe_allow_html=True)
            with st.container():
                quantity_to_return = st.number_input("", min_value=1, step=1)
            
            if st.button("הוסף להחזרה - Add to Return"):
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
                    st.success(f"נוסף להחזרה - Added to Return: {tool_name} - כמות - Quantity: {quantity_to_return}")
                else:
                    st.error("כמות ההחזרה גדולה מהכמות המושאלת - Return quantity exceeds borrowed quantity")

            if 'return_session' in st.session_state and st.session_state['return_session']:
                st.markdown('<div class="rtl">כלים להחזרה ב-Session זה - Tools to Return in This Session:</div>', unsafe_allow_html=True)
                for item in st.session_state['return_session']:
                    st.markdown(f'<div class="rtl">{item["שם הכלי"]} - כמות - Quantity: {item["כמות להחזיר"]}</div>', unsafe_allow_html=True)

            if st.button("אשר את כל ההחזרות - Confirm All Returns"):
                for return_item in st.session_state['return_session']:
                    mask = (borrow_df['שם משתמש'] == return_item['שם משתמש']) & \
                           (borrow_df['שם מעבדה'] == return_item['שם מעבדה']) & \
                           (borrow_df['שם הכלי'] == return_item['שם הכלי']) & \
                           (borrow_df['תאריך השאלה'] == return_item['תאריך השאלה'])
                    borrow_df.loc[mask, 'כמות'] -= return_item['כמות להחזיר']
                borrow_df = borrow_df[borrow_df['כמות'] > 0]
                borrow_df.to_excel(borrow_file, index=False)
                st.success("כל ההחזרות בוצעו בהצלחה - All returns completed successfully")
                st.session_state['return_session'] = []
                st.session_state['screen'] = 'main'
        else:
            st.markdown('<div class="rtl">אין השאלות קודמות - No previous borrowings</div>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.markdown('<div class="rtl">אין השאלות קודמות - No previous borrowings</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"שגיאה בטעינת ההשאלות - Error loading borrowings: {str(e)}")

    if st.button("חזור - Back"):
        st.session_state['screen'] = 'main'

# History screen
def history_screen():
    # Logo
    if os.path.exists("mdde.jpg"):
        st.image("mdde.jpg", width=300, use_column_width="auto")
    else:
        st.warning("הלוגו mdde.jpg לא נמצא - Logo mdde.jpg not found")

    st.markdown('<h2 class="rtl">היסטוריית השאלות - Borrowing History</h2>', unsafe_allow_html=True)
    try:
        borrow_df = pd.read_excel(borrow_file)
        st.dataframe(borrow_df)
    except FileNotFoundError:
        st.markdown('<div class="rtl">אין נתונים זמינים - No data available</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"שגיאה בטעינת ההיסטוריה - Error loading history: {str(e)}")
    if st.button("חזור - Back"):
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
st.sidebar.markdown('<h2 class="rtl">ניווט - Navigation</h2>', unsafe_allow_html=True)
if st.sidebar.button("דף ראשי - Main Page"):
    st.session_state['screen'] = 'main'
if st.sidebar.button("היסטוריה - History"):
    st.session_state['screen'] = 'history'
