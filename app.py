import streamlit as st
import pandas as pd
import qrcode
from datetime import datetime
import os
from PIL import Image

# File paths
labs_file = "labs.xlsx"
tools_file = "tools.xlsx"
persistent_directory = "/home/storehouse/Documents/BorrowApp"  # Updated directory for persistent storage
borrow_file = os.path.join(persistent_directory, "borrowed_equipment.xlsx")

# Ensure the persistent directory exists
if not os.path.exists(persistent_directory):
    os.makedirs(persistent_directory)

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
    st.markdown("""
        <style>
        .rtl {
            direction: rtl;
            text-align: right;
        }
        .center {
            text-align: center !important;
        }
        .center-inputs {
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
        }
        .stTextInput, .stNumberInput, .stSelectbox {
            direction: rtl;
            text-align: center; /* Center-align text within inputs */
            max-width: 400px;
            margin: 0 auto;
        }
        .stTextInput input, .stNumberInput input {
            text-align: center;
        }
        .stButton>button {
            height: 50px; /* Taller buttons */
            width: 250px; /* Wider buttons to fit text in one row */
            direction: rtl;
            margin: 10px auto; /* Spacing and centering */
            display: block;
            font-size: 16px; /* Larger text */
            border-radius: 5px; /* Rounded corners */
        }
        .stButton>button:hover {
            background-color: #e0e0e0; /* Hover effect */
            cursor: pointer; /* Hand cursor */
        }
        .sidebar .stButton>button {
            width: 60px; /* Wider delete button in sidebar */
        }
        .sidebar .stButton {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
        }
        </style>
    """, unsafe_allow_html=True)

    if os.path.exists("mdde.jpg"):
        st.image("mdde.jpg", width=250, use_container_width=True)
    else:
        st.warning("הלוגו mdde.jpg לא נמצא - Logo mdde.jpg not found")

    st.markdown('<h1 class="center">מערכת השאלת ציוד</h1>', unsafe_allow_html=True)
    st.markdown('<h1 class="center">Equipment Borrowing System</h1>', unsafe_allow_html=True)
    
    st.markdown('<div class="center">שם משתמש - Username:</div>', unsafe_allow_html=True)
    with st.container():
        username = st.text_input("", key="username_input", label_visibility="collapsed")
    st.markdown('<div class="center">בחר מעבדה - Select Lab:</div>', unsafe_allow_html=True)
    with st.container():
        labs = load_labs()
        lab = st.selectbox("", labs, key="lab_input", label_visibility="collapsed")
    
    col1, col2 = st.columns([1, 1], gap="medium")  # Adjusted columns with gap
    with col1:
        if st.button("השאל כלים - Borrow Tools", key="borrow_btn", use_container_width=True):
            if username and lab:
                st.session_state['user'] = username
                st.session_state['selected_lab'] = lab
                st.session_state['screen'] = 'borrow'
            else:
                st.error("יש להזין שם משתמש ומעבדה - Please enter username and lab")
    with col2:
        if st.button("החזר כלים - Return Tools", key="return_btn", use_container_width=True):
            if username and lab:
                st.session_state['user'] = username
                st.session_state['selected_lab'] = lab
                st.session_state['screen'] = 'return'
            else:
                st.error("יש להזין שם משתמש ומעבדה - Please enter username and lab")

# Borrow screen
def borrow_screen():
    st.markdown("""
        <style>
        .stButton>button {
            margin-top: 10px; /* Add space between buttons */
            margin-left: auto;
            margin-right: auto;
        }
        .stTextInput, .stNumberInput, .stSelectbox {
            direction: rtl;
            text-align: center; /* Center-align text within inputs */
            max-width: 400px;
            margin: 0 auto;
        }
        .stTextInput input, .stNumberInput input {
            text-align: center;
        }
        .center-text {
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

    if os.path.exists("mdde.jpg"):
        st.image("mdde.jpg", width=250, use_container_width=True)
    else:
        st.warning("הלוגו mdde.jpg לא נמצא - Logo mdde.jpg not found")

    st.markdown('<h2 class="center">השאלת כלים</h2>', unsafe_allow_html=True)
    st.markdown('<h2 class="center">Borrow Tools</h2>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="center-text">שם הכלי - Tool Name:</div>', unsafe_allow_html=True)
        tool_name = st.text_input("", key="new_tool_input", label_visibility="collapsed")
        st.markdown('<div class="center-text">כמות להשאיל - Quantity to Borrow:</div>', unsafe_allow_html=True)
        quantity = st.number_input("", min_value=1, step=1, key="new_qty_input", label_visibility="collapsed")
        
    center_button_style = """
    <style>
    .stButton>button {
        margin-left: auto;
        margin-right: auto;
        display: block;
    }
    </style>
    """
    st.markdown(center_button_style, unsafe_allow_html=True)

    if st.button("הוסף לרשימה - Add to List"):
        if tool_name:
            if 'borrow_session' not in st.session_state:
                st.session_state['borrow_session'] = []
            st.session_state['borrow_session'].append({
                'שם משתמש': st.session_state['user'],
                'שם מעבדה': st.session_state['selected_lab'],
                'שם הכלי': tool_name,
                'כמות': quantity
            })
            st.success(f"נוסף - Added: {tool_name} - כמות - Quantity: {quantity}")
        else:
            st.error("יש לרשום שם כלי - Please enter a tool name")

    # Move cart to sidebar if items exist
    if 'borrow_session' in st.session_state and st.session_state['borrow_session']:
        with st.sidebar:
            st.markdown('<div class="center">כלים שנבחרו - Tools Selected</div>', unsafe_allow_html=True)
            edited_session = []
            for i, item in enumerate(st.session_state['borrow_session']):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    new_tool_name = st.text_input("", value=item['שם הכלי'], key=f"tool_{i}_input", label_visibility="collapsed")
                with col2:
                    new_quantity = st.number_input("", min_value=1, step=1, value=item['כמות'], key=f"qty_{i}_input", label_visibility="collapsed")
                with col3:
                    if st.button("🗑️", key=f"del_{i}", help="Delete tool"):
                        continue
                edited_session.append({
                    'שם משתמש': item['שם משתמש'],
                    'שם מעבדה': item['שם מעבדה'],
                    'שם הכלי': new_tool_name,
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
                    if not os.path.exists(persistent_directory):
                        os.makedirs(persistent_directory)
                    if os.path.exists(borrow_file):
                        existing_borrows = pd.read_excel(borrow_file)
                        borrow_df = pd.concat([existing_borrows, borrow_df])
                    borrow_df.to_excel(borrow_file, index=False, engine='openpyxl')
                    st.success("כל ההשאלות בוצעו בהצלחה - All borrowings completed successfully")
                    st.session_state['borrow_session'] = []
                    st.session_state['screen'] = 'main'
                except Exception as e:
                    st.error(f"שגיאה בשמירת הנתונים - Error saving data: {str(e)}")
            else:
                st.error("לא נבחרו כלים להשאלה - No tools selected for borrowing")
    with col_back:
        if st.button("חזור - Back"):
            st.session_state['screen'] = 'main'

# Return screen
def return_screen():
    st.markdown("""
        <style>
        .stButton>button {
            margin-top: 10px; /* Add space between buttons */
            margin-left: auto;
            margin-right: auto;
        }
        .stTextInput, .stNumberInput, .stSelectbox {
            direction: rtl;
            text-align: center; /* Center-align text within inputs */
            max-width: 400px;
            margin: 0 auto;
        }
        .stTextInput input, .stNumberInput input {
            text-align: center;
        }
        .center-text {
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

    if os.path.exists("mdde.jpg"):
        st.image("mdde.jpg", width=250, use_container_width=True)
    else:
        st.warning("הלוגו mdde.jpg לא נמצא - Logo mdde.jpg not found")

    st.markdown('<h2 class="center">החזרת כלים</h2>', unsafe_allow_html=True)
    st.markdown('<h2 class="center">Return Tools</h2>', unsafe_allow_html=True)
    
    try:
        borrow_df = pd.read_excel(borrow_file)
        user_borrows = borrow_df[(borrow_df['שם משתמש'] == st.session_state['user']) & 
                                 (borrow_df['שם מעבדה'] == st.session_state['selected_lab'])]
        if not user_borrows.empty:
            st.markdown('<div class="center">כלים שהושאלו בעבר - Previously Borrowed Tools:</div>', unsafe_allow_html=True)
            st.dataframe(user_borrows)
            st.divider()
            st.markdown('<div class="center-text">בחר כלי להחזרה - Select Tool to Return:</div>', unsafe_allow_html=True)
            with st.container():
                tool_options = user_borrows.apply(lambda row: f"{row['שם הכלי']} (כמות: {row['כמות']}, תאריך: {row['תאריך השאלה']})", axis=1).tolist()
                selected_tool = st.selectbox("", tool_options, key="return_tool_input", label_visibility="collapsed")
            st.markdown('<div class="center-text">כמות להחזיר - Quantity to Return:</div>', unsafe_allow_html=True)
            with st.container():
                quantity_to_return = st.number_input("", min_value=1, step=1, key="return_qty_input", label_visibility="collapsed")
            
            st.markdown(center_button_style, unsafe_allow_html=True)

            if st.button("הוסף להחזרה - Add to Return"):
                if quantity_to_return <= int(selected_tool.split("כמות: ")[1].split(",")[0]):
                    tool_name = selected_tool.split(" (")[0]
                    if 'return_session' not in st.session_state:
                        st.session_state['return_session'] = []
                    st.session_state['return_session'].append({
                        'שם משתמש': st.session_state['user'],
                        'שם מעבדה': st.session_state['selected_lab'],
                        'שם הכלי': tool_name,
                        'כמות להחזיר': quantity_to_return,
                        'תאריך השאלה': selected_tool.split("תאריך: ")[1].rstrip(")")
                    })
                    st.success(f"נוסף להחזרה - Added to Return: {tool_name} - כמות - Quantity: {quantity_to_return}")
                else:
                    st.error("כמות ההחזרה גדולה מהכמות המושאלת - Return quantity exceeds borrowed quantity")

            if 'return_session' in st.session_state and st.session_state['return_session']:
                st.markdown('<div class="center-text">כלים להחזרה ב-Session זה - Tools to Return in This Session:</div>', unsafe_allow_html=True)
                for item in st.session_state['return_session']:
                    st.markdown(f'<div class="center-text">{item["שם הכלי"]} - כמות - Quantity: {item["כמות להחזיר"]}</div>', unsafe_allow_html=True)

            if st.button("אשר את כל ההחזרות - Confirm All Returns"):
                for return_item in st.session_state['return_session']:
                    mask = (borrow_df['שם משתמש'] == return_item['שם משתמש']) & \
                           (borrow_df['שם מעבדה'] == return_item['שם מעבדה']) & \
                           (borrow_df['שם הכלי'] == return_item['שם הכלי']) & \
                           (borrow_df['תאריך השאלה'] == return_item['תאריך השאלה'])
                    borrow_df.loc[mask, 'כמות'] -= return_item['כמות להחזיר']
                borrow_df = borrow_df[borrow_df['כמות'] > 0]
                borrow_df.to_excel(borrow_file, index=False, engine='openpyxl')
                st.success("כל ההחזרות בוצעו בהצלחה - All returns completed successfully")
                st.session_state['return_session'] = []
                st.session_state['screen'] = 'main'
        else:
            st.markdown('<div class="center">אין השאלות קודמות - No previous borrowings</div>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.markdown('<div class="center">אין השאלות קודמות - No previous borrowings</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"שגיאה בטעינת ההשאלות - Error loading borrowings: {str(e)}")

    if st.button("חזור - Back"):
        st.session_state['screen'] = 'main'

# History screen
def history_screen():
    st.markdown("""
        <style>
        .stButton>button {
            margin-top: 10px; /* Add space between buttons */
        }
        </style>
    """, unsafe_allow_html=True)

    if os.path.exists("mdde.jpg"):
        st.image("mdde.jpg", width=250, use_container_width=True)
    else:
        st.warning("הלוגו mdde.jpg לא נמצא - Logo mdde.jpg not found")

    st.markdown('<h2 class="center">היסטוריית השאלות</h2>', unsafe_allow_html=True)
    st.markdown('<h2 class="center">Borrowing History</h2>', unsafe_allow_html=True)
    try:
        borrow_df = pd.read_excel(borrow_file)
        user_borrows = borrow_df[borrow_df['שם משתמש'] == st.session_state['user']]
        st.dataframe(user_borrows)
    except FileNotFoundError:
        st.markdown('<div class="center">אין נתונים זמינים - No data available</div>', unsafe_allow_html=True)
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
st.sidebar.markdown('<h2 class="center">ניווט - Navigation</h2>', unsafe_allow_html=True)
if st.sidebar.button("דף ראשי - Main Page"):
    st.session_state['screen'] = 'main'
if st.sidebar.button("Borrow History of the User"):
    st.session_state['screen'] = 'history'
