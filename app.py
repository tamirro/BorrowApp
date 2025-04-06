import streamlit as st
import pandas as pd
import qrcode
from PIL import Image
from datetime import datetime
import os

# File paths
labs_file = "labs.xlsx"
tools_file = "tools.xlsx"
borrow_file = "borrowed_equipment.xlsx"

# Load tools dictionary for Hebrew-to-English mapping
@st.cache_data
def load_tools():
    try:
        tools_df = pd.read_excel(tools_file)
        tools_df = tools_df.sort_values(by='שם הכלי')
        tools_dict = {row['שם הכלי']: row['שם הכלי באנגלית'] for _, row in tools_df.iterrows()}
        return tools_dict
    except FileNotFoundError:
        st.error("קובץ הכלים לא נמצא - Tools file not found")
        return {}
    except Exception as e:
        st.error(f"שגיאה בטעינת הכלים: {str(e)} - Error loading tools: {str(e)}")
        return {}

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
    st.title("מערכת השאלת ציוד - Equipment Borrowing System")
    
    # QR Code for login
    qr = qrcode.QRCode()
    qr.add_data(st.secrets.get("app_url", "http://localhost:8501"))
    qr.make()
    qr_img = qr.make_image(fill='black', back_color='white')
    qr_img.save("qr_login.png")
    st.image("qr_login.png", caption="סרוק כדי לגשת - Scan to Access")

    username = st.text_input("שם משתמש - Username")
    labs = load_labs()
    lab = st.selectbox("בחר מעבדה - Select Lab", labs)
    
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

# Borrow screen with improved visual interface
def borrow_screen(tools_dict):
    # CSS for RTL and button alignment
    st.markdown("""
        <style>
        .rtl {
            direction: rtl;
            text-align: right;
        }
        .stButton>button {
            height: 38px;  /* Match height of text/number inputs */
            width: 100%;
        }
        </style>
    """, unsafe_allow_html=True)

    st.subheader("השאלת כלים - Borrow Tools")
    
    # Input area
    with st.container():
        st.markdown('<div class="rtl">שם הכלי (עברית או אנגלית) - Tool Name (Hebrew or English):</div>', unsafe_allow_html=True)
        tool_name = st.text_input("", key="new_tool")  # Empty label, handled by markdown
        st.markdown('<div class="rtl">כמות להשאיל - Quantity to Borrow:</div>', unsafe_allow_html=True)
        quantity = st.number_input("", min_value=1, step=1, key="new_qty")  # Empty label
        
        if st.button("הוסף לרשימה - Add to List"):
            if tool_name:
                tool_english = tools_dict.get(tool_name, "")
                display_name = f"{tool_name} - {tool_english}" if tool_english else tool_name
                if 'borrow_session' not in st.session_state:
                    st.session_state['borrow_session'] = []
                st.session_state['borrow_session'].append({
                    'שם משתמש': st.session_state['username'],
                    'שם מעבדה': st.session_state['lab'],
                    'שם הכלי': tool_name,
                    'שם הכלי באנגלית': tool_english,
                    'כמות': quantity
                })
                st.success(f"נוסף: {display_name} - כמות: {quantity} - Quantity: {quantity}")
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
                if item['שם הכלי באנגלית']:
                    st.markdown(f'<div class="rtl">{new_tool_name} - {item["שם הכלי באנגלית"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="rtl">{new_tool_name}</div>', unsafe_allow_html=True)
            with col2:
                new_quantity = st.number_input("", min_value=1, step=1, value=item['כמות'], key=f"qty_{i}")
            with col3:
                if st.button("מחק - Delete", key=f"del_{i}"):
                    continue
            new_tool_english = tools_dict.get(new_tool_name, "")
            edited_session.append({
                'שם משתמש': item['שם משתמש'],
                'שם מעבדה': item['שם מעבדה'],
                'שם הכלי': new_tool_name,
                'שם הכלי באנגלית': new_tool_english,
                'כמות': new_quantity
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
    st.subheader("החזרת כלים - Return Tools")
    
    try:
        borrow_df = pd.read_excel(borrow_file)
        user_borrows = borrow_df[(borrow_df['שם משתמש'] == st.session_state['username']) & 
                                 (borrow_df['שם מעבדה'] == st.session_state['lab'])]
        if not user_borrows.empty:
            st.write("כלים שהושאלו בעבר - Previously Borrowed Tools:")
            st.dataframe(user_borrows)
            tool_options = user_borrows.apply(lambda row: f"{row['שם הכלי']} - {row['שם הכלי באנגלית']} (כמות: {row['כמות']}, תאריך: {row['תאריך השאלה']})", axis=1).tolist()
            selected_tool = st.selectbox("בחר כלי להחזרה - Select Tool to Return", tool_options)
            quantity_to_return = st.number_input("כמות להחזיר - Quantity to Return", min_value=1, step=1)
            
            if st.button("הוסף להחזרה - Add to Return"):
                if quantity_to_return <= int(selected_tool.split("כמות: ")[1].split(",")[0]):
                    tool_name = selected_tool.split(" - ")[0]
                    if 'return_session' not in st.session_state:
                        st.session_state['return_session'] = []
                    st.session_state['return_session'].append({
                        'שם משתמש': st.session_state['username'],
                        'שם מעבדה': st.session_state['lab'],
                        'שם הכלי': tool_name,
                        'כמות להחזיר': quantity_to_return,
                        'תאריך השאלה': selected_tool.split("תאריך: ")[1].rstrip(")")
                    })
                    st.success(f"נוסף להחזרה: {tool_name} - כמות: {quantity_to_return} - Quantity: {quantity_to_return}")
                else:
                    st.error("כמות ההחזרה גדולה מהכמות המושאלת - Return quantity exceeds borrowed quantity")

            if 'return_session' in st.session_state and st.session_state['return_session']:
                st.write("כלים להחזרה ב-Session זה - Tools to Return in This Session:")
                for item in st.session_state['return_session']:
                    st.write(f"{item['שם הכלי']} - כמות: {item['כמות להחזיר']} - Quantity: {item['כמות להחזיר']}")

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
            st.write("אין השאלות קודמות - No previous borrowings")
    except FileNotFoundError:
        st.write("אין השאלות קודמות - No previous borrowings")
    except Exception as e:
        st.error(f"שגיאה בטעינת ההשאלות: {str(e)} - Error loading borrowings: {str(e)}")

    if st.button("חזור - Back"):
        st.session_state['screen'] = 'main'

# History screen
def history_screen():
    st.subheader("היסטוריית השאלות - Borrowing History")
    try:
        borrow_df = pd.read_excel(borrow_file)
        st.dataframe(borrow_df)
    except FileNotFoundError:
        st.write("אין נתונים זמינים - No data available")
    except Exception as e:
        st.error(f"שגיאה בטעינת ההיסטוריה: {str(e)} - Error loading history: {str(e)}")
    if st.button("חזור - Back"):
        st.session_state['screen'] = 'main'

# Main app logic
if 'screen' not in st.session_state:
    st.session_state['screen'] = 'main'

tools_dict = load_tools()

if st.session_state['screen'] == 'main':
    main_screen()
elif st.session_state['screen'] == 'borrow':
    borrow_screen(tools_dict)
elif st.session_state['screen'] == 'return':
    return_screen()
elif st.session_state['screen'] == 'history':
    history_screen()

# Sidebar for navigation
st.sidebar.title("ניווט - Navigation")
if st.sidebar.button("דף ראשי - Main Page"):
    st.session_state['screen'] = 'main'
if st.sidebar.button("היסטוריה - History"):
    st.session_state['screen'] = 'history'
