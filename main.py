import streamlit as st
import pandas as pd
import re
import time
from datetime import datetime
from twilio.rest import Client
from twilio.base.exceptions import TwilioException

# FORCE LIGHT THEME
st.set_page_config(
    page_title="Tokyo Sanno Law Office - Call System",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# AGGRESSIVE LIGHT THEME CSS
st.markdown("""
<style>
    /* FORCE LIGHT THEME EVERYWHERE */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], 
    [data-testid="stSidebar"], section, div, .main, body {
        background-color: #ffffff !important;
    }
    
    /* Force all text to be dark EXCEPT in special areas */
    p, span, div, label, h1, h2, h3, h4, h5, h6, a {
        color: #1a1a1a !important;
    }
    
    /* White text in header */
    .custom-header h1,
    .custom-header p,
    .custom-header span,
    .custom-header * {
        color: #ffffff !important;
    }
    
    /* White text in call banner */
    .current-call-banner,
    .current-call-banner * {
        color: #ffffff !important;
    }
    
    /* Sidebar light */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa !important;
    }
    [data-testid="stSidebar"] * {
        color: #1a1a1a !important;
    }
    
    /* Remove dark backgrounds */
    .st-emotion-cache-16idsys, .st-emotion-cache-1y4p8pa,
    .st-emotion-cache-1dp5vir, [data-testid="stExpander"],
    [data-testid="stExpanderDetails"] {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* Expander styling */
    [data-testid="stExpander"] {
        background-color: #ffffff !important;
        border: 2px solid #e5e7eb !important;
        border-radius: 8px !important;
    }
    [data-testid="stExpander"] summary {
        background-color: #f8f9fa !important;
        color: #1a1a1a !important;
        font-weight: 600 !important;
        padding: 1rem !important;
    }
    [data-testid="stExpander"] p, 
    [data-testid="stExpander"] div,
    [data-testid="stExpander"] span {
        color: #1a1a1a !important;
    }
    
    /* Input fields */
    input, .stTextInput input, .stNumberInput input {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #d1d5db !important;
    }
    
    /* Slider */
    .stSlider {
        color: #1a1a1a !important;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #1a1a1a !important;
    }
    
    /* Hide Streamlit elements */
    #MainMenu, footer, header {visibility: hidden;}
    .main { padding-top: 0rem; }

    /* Header with gradient */
    .custom-header {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #60a5fa 100%);
        padding: 2.5rem;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 20px 20px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .custom-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        color: #ffffff !important;
    }
    .custom-header p {
        font-size: 1rem;
        margin: 0.5rem 0 0 0;
        color: #ffffff !important;
    }
    .custom-header * {
        color: #ffffff !important;
    }

    /* Contact Cards */
    .contact-card {
        background: white;
        border-radius: 12px;
        padding: 1.25rem;
        border: 2px solid #e5e7eb;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .contact-card:hover {
        border-color: #3b82f6;
        transform: translateX(4px);
        box-shadow: 0 4px 12px rgba(59,130,246,0.2);
    }

    .contact-avatar {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #ffffff !important;
        font-weight: 600;
        font-size: 18px;
        flex-shrink: 0;
    }

    .contact-info { flex: 1; min-width: 0; }
    .contact-name {
        font-weight: 600;
        color: #1a1a1a !important;
        margin-bottom: 4px;
        font-size: 1.1rem;
    }
    .contact-phone {
        color: #6b7280 !important;
        font-size: 0.95rem;
        font-family: 'Monaco', monospace;
    }

    .contact-status {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        border-radius: 20px;
        background: #f3f4f6;
        font-weight: 500;
        color: #1a1a1a !important;
    }
    .contact-status span {
        color: #1a1a1a !important;
    }
    .status-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
    }

    /* Status colors */
    .status-waiting { background: #9ca3af; }
    .status-ringing {
        background: #f59e0b;
        animation: pulse 1.5s infinite;
    }
    .status-connected {
        background: #3b82f6;
        animation: pulse 1.5s infinite;
    }
    .status-completed { background: #10b981; }
    .status-failed { background: #ef4444; }

    /* Card states */
    .contact-selected {
        border-color: #3b82f6;
        background: rgba(59,130,246,0.05);
    }
    .contact-calling {
        border-color: #f59e0b;
        background: rgba(245,158,11,0.05);
        animation: pulse-border 2s infinite;
    }
    .contact-completed {
        border-color: #10b981;
        background: rgba(16,185,129,0.03);
    }
    .contact-failed {
        border-color: #ef4444;
        background: rgba(239,68,68,0.03);
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.6; transform: scale(1.1); }
    }
    @keyframes pulse-border {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.01); }
    }

    /* Progress bar */
    .progress-container {
        background: #e5e7eb;
        border-radius: 10px;
        height: 12px;
        overflow: hidden;
        margin: 1rem 0;
    }
    .progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #3b82f6 0%, #1d4ed8 100%);
        border-radius: 10px;
        transition: width 0.3s ease;
    }

    /* Current call banner */
    .current-call-banner {
        background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
        color: #ffffff !important;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        font-size: 1.1rem;
        font-weight: 600;
        text-align: center;
        animation: pulse-border 2s infinite;
        box-shadow: 0 4px 12px rgba(245,158,11,0.3);
    }
    .current-call-banner * {
        color: #ffffff !important;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        background-color: #ffffff !important;
        border: 2px solid #e5e7eb !important;
        color: #1a1a1a !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
        border-color: #3b82f6 !important;
    }
    .stButton > button[kind="primary"] {
        background-color: #3b82f6 !important;
        border-color: #3b82f6 !important;
        color: #ffffff !important;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background-color: #ffffff !important;
    }
    [data-testid="stFileUploader"] label,
    [data-testid="stFileUploader"] button {
        color: #1a1a1a !important;
    }
    .stFileUploader > div > button {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    
    /* Upload section */
    .upload-section {
        background: linear-gradient(135deg, #dbeafe 0%, #e0e7ff 100%);
        border: 2px dashed #3b82f6;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
    }
    .upload-section h4 {
        color: #1e40af !important;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    .upload-section p {
        color: #1a1a1a !important;
        font-size: 0.95rem;
    }
    
    /* Info boxes */
    .stInfo, .stSuccess, .stWarning, .stError {
        background-color: #f8f9fa !important;
        color: #1a1a1a !important;
    }
    .stInfo *, .stSuccess *, .stWarning *, .stError * {
        color: #1a1a1a !important;
    }
    
    /* Make sure download button is visible */
    [data-testid="stDownloadButton"] button {
        background-color: #3b82f6 !important;
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'processed_numbers' not in st.session_state:
    st.session_state.processed_numbers = []
if 'call_history' not in st.session_state:
    st.session_state.call_history = []
if 'selected_contacts' not in st.session_state:
    st.session_state.selected_contacts = set()
if 'calling_in_progress' not in st.session_state:
    st.session_state.calling_in_progress = False
if 'current_calling_id' not in st.session_state:
    st.session_state.current_calling_id = None
if 'call_queue' not in st.session_state:
    st.session_state.call_queue = []
if 'contact_statuses' not in st.session_state:
    st.session_state.contact_statuses = {}

# Classes
class JapanesePhoneProcessor:
    def __init__(self):
        self.mobile_prefixes = ['070', '080', '090']

    def clean_number(self, number):
        if pd.isna(number):
            return None
        digits = re.sub(r'[^\d]', '', str(number).strip())
        if not digits:
            return None
        
        if len(digits) == 9:
            digits = '0' + digits
        elif len(digits) == 10:
            if not digits.startswith('0'):
                digits = '0' + digits
        elif len(digits) == 11:
            if digits.startswith('81'):
                digits = '0' + digits[2:]
        elif len(digits) > 11:
            digits = digits[:11]
        else:
            if len(digits) < 8:
                return None
        
        return digits

    def validate_japanese_number(self, number):
        if not number or not number.startswith('0'):
            return False
        if number[:3] in self.mobile_prefixes and len(number) == 11:
            return True
        if len(number) == 10:
            if number.startswith('03') or number.startswith('06'):
                return True
            if number[1] in '123459':
                return True
        return False

    def format_for_twilio(self, number):
        if not self.validate_japanese_number(number):
            return None
        return '+81' + number[1:]

    def process_numbers_with_names(self, data_list):
        results = []
        for idx, row in enumerate(data_list):
            if isinstance(row, dict):
                name = str(row.get('Name', row.get('name', f'Person {idx+1}')))
                number = row.get('Phone_Number', row.get('phone_number', row.get('phone', '')))
            else:
                name = str(row[0]) if len(row) > 0 else f'Person {idx+1}'
                number = row[1] if len(row) > 1 else ''
            
            original = str(number) if not pd.isna(number) else ""
            cleaned = self.clean_number(number)
            
            if cleaned and self.validate_japanese_number(cleaned):
                intl = self.format_for_twilio(cleaned)
                status = "valid"
            else:
                intl = None
                status = "invalid"
            
            results.append({
                'id': idx,
                'name': name,
                'original': original,
                'cleaned': cleaned if cleaned else "N/A",
                'international': intl if intl else "N/A",
                'status': status
            })
        return results

class TwilioCaller:
    def __init__(self, account_sid, auth_token, from_number, operator_number):
        try:
            self.client = Client(account_sid, auth_token)
            self.from_number = from_number
            self.operator_number = operator_number
            self.is_configured = True
        except Exception as e:
            self.is_configured = False
            self.error = str(e)

    def twiml_for_call(self):
        return f"""
<Response>
  <Dial timeout="30" record="record-from-answer">
    <Number>{self.operator_number}</Number>
  </Dial>
</Response>
""".strip()

    def make_call(self, to_number, person_name=""):
        if not self.is_configured:
            return False, "Twilio not configured", None
        try:
            call = self.client.calls.create(
                twiml=self.twiml_for_call(),
                to=to_number,
                from_=self.from_number
            )
            return True, f"Call initiated to {person_name}", call.sid
        except TwilioException as e:
            return False, f"Twilio error: {str(e)}", None
        except Exception as e:
            return False, f"Error: {str(e)}", None

    def poll_status(self, sid):
        try:
            call = self.client.calls(sid).fetch()
            return True, call.status
        except Exception as e:
            return False, str(e)

# Helper functions
def get_initials(name):
    words = name.split()
    if len(words) >= 2:
        return words[0][0].upper() + words[1][0].upper()
    if len(words) == 1:
        return words[0][:2].upper()
    return "??"

def get_status_display(status):
    status_map = {
        "waiting": ("⏳", "Waiting", "status-waiting"),
        "queued": ("⏳", "Queued", "status-waiting"),
        "ringing": ("📳", "Ringing", "status-ringing"),
        "in-progress": ("📞", "Connected", "status-connected"),
        "completed": ("✅", "Completed", "status-completed"),
        "failed": ("❌", "Failed", "status-failed"),
        "no-answer": ("❌", "No Answer", "status-failed"),
        "busy": ("❌", "Busy", "status-failed"),
        "canceled": ("❌", "Canceled", "status-failed"),
    }
    return status_map.get(status, ("⏳", status.title(), "status-waiting"))

def render_contact_card(contact, is_selected, contact_status):
    icon, status_text, status_class = get_status_display(contact_status)
    initials = get_initials(contact['name'])

    card_class = "contact-card"
    if contact_status in ("ringing", "queued", "in-progress"):
        card_class += " contact-calling"
    elif contact_status == "completed":
        card_class += " contact-completed"
    elif contact_status in ("failed", "no-answer", "busy", "canceled"):
        card_class += " contact-failed"
    elif is_selected:
        card_class += " contact-selected"

    col1, col2 = st.columns([0.05, 0.95])
    
    with col1:
        checkbox_key = f"select_{contact['id']}"
        new_selected = st.checkbox(
            "", 
            key=checkbox_key, 
            value=is_selected, 
            label_visibility="collapsed",
            disabled=st.session_state.calling_in_progress
        )
        if new_selected != is_selected:
            if new_selected:
                st.session_state.selected_contacts.add(contact['id'])
            else:
                st.session_state.selected_contacts.discard(contact['id'])
            st.rerun()

    with col2:
        html = f"""
        <div class="{card_class}">
            <div class="contact-avatar" style="color: #ffffff !important;">{initials}</div>
            <div class="contact-info">
                <div class="contact-name" style="color: #1a1a1a !important;">{contact['name']}</div>
                <div class="contact-phone" style="color: #6b7280 !important;">{contact['international']}</div>
            </div>
            <div class="contact-status">
                <div class="status-dot {status_class}"></div>
                <span style="color: #1a1a1a !important;">{status_text}</span>
            </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

def poll_call_until_complete(twilio_caller, call_sid, contact, delay_between_calls):
    terminal_statuses = {'completed', 'failed', 'busy', 'no-answer', 'canceled'}
    status_display = st.empty()
    
    current_status = "queued"
    
    while True:
        ok, status = twilio_caller.poll_status(call_sid)
        
        if not ok:
            current_status = 'failed'
            status_display.error(f"❌ Status check failed: {status}")
            break
        
        current_status = status or 'unknown'
        st.session_state.contact_statuses[st.session_state.current_calling_id] = current_status
        
        icon, status_text, _ = get_status_display(current_status)
        status_display.info(f"{icon} {contact['name']}: {status_text}")
        
        if current_status in terminal_statuses:
            break
        
        time.sleep(3)
    
    human_status = current_status.replace('-', ' ').title()
    
    if current_status == 'completed':
        status_display.success(f"✅ {contact['name']}: Call Completed")
        log_status = "Completed"
    else:
        status_display.error(f"❌ {contact['name']}: {human_status}")
        log_status = human_status
    
    st.session_state.call_history.append({
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'name': contact['name'],
        'number': contact['international'],
        'status': log_status,
        'details': f"Call SID: {call_sid}"
    })
    
    if st.session_state.call_queue and st.session_state.call_queue[0] == st.session_state.current_calling_id:
        st.session_state.call_queue.pop(0)
    
    st.session_state.current_calling_id = None
    
    if not st.session_state.call_queue:
        st.session_state.calling_in_progress = False
        st.success("🎉 All calls completed!")
        st.rerun()
    else:
        time.sleep(delay_between_calls)
        st.rerun()

# Main App
def main():
    st.markdown("""
    <div class="custom-header">
        <h1 style="color: #ffffff !important;">📞 Tokyo Sanno Law Office</h1>
        <p style="color: #ffffff !important;">Direct Connect Call System</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        
        operator_number = st.text_input(
            "Operator Number", 
            value="+817044448888",
            help="Number to connect calls to"
        )
        
        try:
            if "twilio" in st.secrets:
                account_sid = st.secrets["twilio"]["account_sid"]
                auth_token = st.secrets["twilio"]["auth_token"]
                from_number = st.secrets["twilio"]["from_number"]
            else:
                account_sid = st.secrets["account_sid"]
                auth_token = st.secrets["auth_token"]
                from_number = st.secrets["from_number"]
            
            twilio_caller = TwilioCaller(account_sid, auth_token, from_number, operator_number)
            
            if twilio_caller.is_configured:
                st.success("✅ Twilio Connected")
                st.info(f"📱 From: {from_number}")
                st.info(f"👤 To: {operator_number}")
            else:
                st.error(f"❌ Twilio Error")
                twilio_caller = None
        except Exception as e:
            st.error(f"❌ Configuration Error")
            twilio_caller = None
        
        st.markdown("---")
        call_delay = st.slider("Delay between calls (seconds)", 1, 30, 5)
        
        st.markdown("---")
        st.caption("💡 Upload → Select → Call")

    # Upload Section
    with st.expander("📂 Step 1: Upload Contact List", expanded=True):
        st.markdown("""
        <div class="upload-section">
            <h4 style="color: #1e40af !important;">📋 Upload Excel File</h4>
            <p style="color: #1a1a1a !important;">File must have <strong>Name</strong> and <strong>Phone_Number</strong> columns</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Choose Excel file", type=['xlsx', 'xls'], label_visibility="collapsed")
        
        if uploaded_file:
            try:
                df = pd.read_excel(uploaded_file)
                st.success(f"✅ Loaded {len(df)} contacts")
                
                if 'Name' in df.columns and 'Phone_Number' in df.columns:
                    processor = JapanesePhoneProcessor()
                    results = processor.process_numbers_with_names(df.to_dict('records'))
                    st.session_state.processed_numbers = results
                    
                    for c in results:
                        st.session_state.contact_statuses.setdefault(c['id'], 'waiting')
                    
                    valid_count = sum(1 for r in results if r['status'] == 'valid')
                    invalid_count = len(results) - valid_count
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("📋 Total", len(results))
                    col2.metric("✅ Valid", valid_count)
                    col3.metric("❌ Invalid", invalid_count)
                else:
                    st.warning("⚠️ Required columns: 'Name' and 'Phone_Number'")
            except Exception as e:
                st.error(f"❌ Error reading file: {e}")

    # Call Management
    if st.session_state.processed_numbers:
        valid_contacts = [c for c in st.session_state.processed_numbers if c['status'] == 'valid']
        
        if valid_contacts:
            with st.expander("📞 Step 2: Select & Call", expanded=True):
                total = len(valid_contacts)
                selected = len(st.session_state.selected_contacts)
                completed = sum(1 for c in valid_contacts 
                              if st.session_state.contact_statuses.get(c['id']) == 'completed')
                failed = sum(1 for c in valid_contacts 
                           if st.session_state.contact_statuses.get(c['id']) in 
                           ('failed', 'no-answer', 'busy', 'canceled'))
                calling = 1 if st.session_state.calling_in_progress else 0

                m1, m2, m3, m4, m5 = st.columns(5)
                m1.metric("📋 Total", total)
                m2.metric("🔵 Selected", selected)
                m3.metric("📞 Calling", calling)
                m4.metric("✅ Done", completed)
                m5.metric("❌ Failed", failed)

                if st.session_state.current_calling_id is not None:
                    current_contact = next((c for c in valid_contacts 
                                          if c['id'] == st.session_state.current_calling_id), None)
                    if current_contact:
                        current_status = st.session_state.contact_statuses.get(current_contact['id'], 'calling')
                        icon, status_text, _ = get_status_display(current_status)
                        
                        st.markdown(f"""
                        <div class="current-call-banner" style="color: #ffffff !important;">
                            <span style="color: #ffffff !important;">{icon} Currently calling: {current_contact['name']} - {status_text}</span>
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown("---")
                
                b1, b2, b3, b4 = st.columns(4)
                
                with b1:
                    if st.button("✅ Select All", use_container_width=True, 
                               disabled=st.session_state.calling_in_progress):
                        st.session_state.selected_contacts = set(c['id'] for c in valid_contacts)
                        st.rerun()
                
                with b2:
                    if st.button("❌ Clear Selection", use_container_width=True,
                               disabled=st.session_state.calling_in_progress):
                        st.session_state.selected_contacts.clear()
                        st.rerun()
                
                with b3:
                    can_start = (selected > 0 and not st.session_state.calling_in_progress 
                               and twilio_caller)
                    if st.button("📞 Start Calling", type="primary", 
                               use_container_width=True, disabled=not can_start):
                        st.session_state.call_queue = [c['id'] for c in valid_contacts 
                                                      if c['id'] in st.session_state.selected_contacts]
                        st.session_state.calling_in_progress = True
                        st.rerun()
                
                with b4:
                    if st.button("🔄 Reset All", use_container_width=True,
                               disabled=st.session_state.calling_in_progress):
                        st.session_state.selected_contacts.clear()
                        st.session_state.call_queue = []
                        st.session_state.contact_statuses = {c['id']: 'waiting' for c in valid_contacts}
                        st.session_state.call_history = []
                        st.session_state.calling_in_progress = False
                        st.session_state.current_calling_id = None
                        st.rerun()

                if st.session_state.calling_in_progress and st.session_state.call_queue:
                    total_to_call = len([c for c in valid_contacts 
                                       if c['id'] in st.session_state.selected_contacts])
                    remaining = len(st.session_state.call_queue)
                    progress = (total_to_call - remaining) / total_to_call if total_to_call else 0
                    
                    st.markdown(f"""
                    <div class="progress-container">
                        <div class="progress-bar" style="width: {progress * 100}%"></div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.info(f"📊 Progress: {total_to_call - remaining} / {total_to_call} completed")

            with st.expander("👥 Contact List", expanded=True):
                for contact in valid_contacts:
                    is_selected = contact['id'] in st.session_state.selected_contacts
                    status = st.session_state.contact_statuses.get(contact['id'], 'waiting')
                    render_contact_card(contact, is_selected, status)

            if (st.session_state.calling_in_progress and 
                st.session_state.call_queue and 
                st.session_state.current_calling_id is None):
                
                next_id = st.session_state.call_queue[0]
                current_contact = next((c for c in valid_contacts if c['id'] == next_id), None)
                
                if current_contact and twilio_caller:
                    st.session_state.contact_statuses[next_id] = 'ringing'
                    st.session_state.current_calling_id = next_id
                    
                    success, message, sid = twilio_caller.make_call(
                        current_contact['international'], 
                        current_contact['name']
                    )
                    
                    if not success:
                        st.session_state.contact_statuses[next_id] = 'failed'
                        st.error(f"❌ {current_contact['name']}: {message}")
                        
                        st.session_state.call_history.append({
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'name': current_contact['name'],
                            'number': current_contact['international'],
                            'status': 'Failed',
                            'details': message
                        })
                        
                        st.session_state.call_queue.pop(0)
                        st.session_state.current_calling_id = None
                        
                        if not st.session_state.call_queue:
                            st.session_state.calling_in_progress = False
                        
                        st.rerun()
                    else:
                        st.success(f"✅ Calling {current_contact['name']}...")
                        poll_call_until_complete(twilio_caller, sid, current_contact, call_delay)

    if st.session_state.call_history:
        with st.expander("📋 Call History & Results", expanded=False):
            history_df = pd.DataFrame(st.session_state.call_history)
            st.dataframe(history_df, use_container_width=True, height=400)
            
            col1, col2 = st.columns(2)
            with col1:
                csv = history_df.to_csv(index=False)
                st.download_button(
                    "📥 Download CSV", 
                    csv, 
                    file_name=f"call_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            with col2:
                if st.button("🗑️ Clear History", use_container_width=True):
                    st.session_state.call_history = []
                    st.rerun()

if __name__ == "__main__":
    main()
