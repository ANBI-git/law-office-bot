import streamlit as st
import pandas as pd
import re
import io
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
import time
from datetime import datetime
import numpy as np
import base64
from PIL import Image
import gspread
from google.oauth2.service_account import Credentials
import json
import asyncio
import threading

# Set page config
st.set_page_config(
    page_title="Tokyo Sanno Law Office - Call System",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main styling */
    .main {
        padding-top: 0rem;
        font-family: 'Inter', sans-serif;
    }
    
    /* Custom header */
    .custom-header {
        background: linear-gradient(135deg, #0f1419 0%, #1a2332 50%, #2c3e50 100%);
        padding: 2rem 3rem;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 20px 20px;
        position: relative;
        overflow: hidden;
    }
    
    .custom-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="8" height="8" patternUnits="userSpaceOnUse"><path d="M 8 0 L 0 0 0 8" fill="none" stroke="rgba(255,255,255,0.03)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
    }
    
    .header-content {
        position: relative;
        z-index: 2;
        display: flex;
        align-items: center;
        gap: 2rem;
    }
    
    .logo-container {
        display: flex;
        align-items: center;
        gap: 1rem;
        background: rgba(255, 255, 255, 0.95);
        padding: 1rem 1.5rem;
        border-radius: 15px;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .logo-placeholder {
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #c9b037 0%, #dcca2b 50%, #c9b037 100%);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        font-weight: 300;
        color: white;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .logo-text {
        display: flex;
        flex-direction: column;
    }
    
    .logo-japanese {
        font-size: 20px;
        font-weight: 600;
        color: #1a1a1a;
        letter-spacing: 1px;
        margin-bottom: 2px;
        font-family: 'Hiragino Sans', 'Yu Gothic', sans-serif;
    }
    
    .logo-english {
        font-size: 12px;
        color: #666;
        font-weight: 500;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    
    .header-title {
        color: white;
        margin-left: auto;
    }
    
    .header-title h1 {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        background: linear-gradient(135deg, #fff 0%, #c9b037 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .header-title p {
        font-size: 0.9rem;
        margin: 0;
        opacity: 0.8;
        font-weight: 400;
    }
    
    /* Modern Contact Cards */
    .contacts-grid {
        display: grid;
        gap: 1rem;
        margin-top: 2rem;
    }
    
    .contact-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(0, 0, 0, 0.06);
        transition: all 0.3s ease;
        position: relative;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .contact-card.selected {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        background: rgba(59, 130, 246, 0.02);
    }
    
    .contact-card.calling {
        border-color: #f59e0b;
        box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.2);
        background: rgba(245, 158, 11, 0.05);
        animation: pulse-calling 2s infinite;
    }
    
    .contact-card.completed {
        border-color: #10b981;
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
        background: rgba(16, 185, 129, 0.02);
    }
    
    .contact-card.failed {
        border-color: #ef4444;
        box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
        background: rgba(239, 68, 68, 0.02);
    }
    
    @keyframes pulse-calling {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    
    .contact-checkbox {
        width: 20px;
        height: 20px;
        border: 2px solid #d1d5db;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .contact-checkbox.checked {
        background: #3b82f6;
        border-color: #3b82f6;
        color: white;
    }
    
    .contact-avatar {
        width: 50px;
        height: 50px;
        border-radius: 12px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 600;
        font-size: 18px;
    }
    
    .contact-info {
        flex: 1;
    }
    
    .contact-name {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 4px;
    }
    
    .contact-phone {
        font-size: 0.9rem;
        color: #6b7280;
        font-family: 'SF Mono', 'Monaco', 'Inconsolata', monospace;
    }
    
    .contact-status {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
    }
    
    .status-waiting { background: #6b7280; }
    .status-calling { background: #f59e0b; }
    .status-completed { background: #10b981; }
    .status-failed { background: #ef4444; }
    
    /* Control Panel */
    .control-panel {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(0, 0, 0, 0.05);
        margin-bottom: 2rem;
    }
    
    .control-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #e5e7eb;
    }
    
    .control-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #1f2937;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .control-buttons {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
    }
    
    /* Modern buttons */
    .modern-button {
        padding: 0.75rem 1.5rem;
        border-radius: 10px;
        border: none;
        font-weight: 600;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        text-decoration: none;
        outline: none;
    }
    
    .btn-primary {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    .btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
    }
    
    .btn-success {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }
    
    .btn-success:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
    }
    
    .btn-danger {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
    }
    
    .btn-danger:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
    }
    
    .btn-secondary {
        background: #f8fafc;
        color: #64748b;
        border: 1px solid #e2e8f0;
    }
    
    .btn-secondary:hover {
        background: #f1f5f9;
        border-color: #cbd5e1;
    }
    
    /* Progress indicators */
    .progress-container {
        margin: 1.5rem 0;
    }
    
    .progress-bar {
        width: 100%;
        height: 8px;
        background: #f3f4f6;
        border-radius: 4px;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #3b82f6 0%, #1d4ed8 100%);
        border-radius: 4px;
        transition: width 0.3s ease;
    }
    
    .progress-text {
        font-size: 0.85rem;
        color: #6b7280;
        margin-top: 0.5rem;
        text-align: center;
    }
    
    /* Statistics cards */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        border: 1px solid rgba(0, 0, 0, 0.04);
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        font-size: 0.85rem;
        color: #6b7280;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stat-total { color: #6b7280; }
    .stat-selected { color: #3b82f6; }
    .stat-completed { color: #10b981; }
    .stat-failed { color: #ef4444; }
    .stat-calling { color: #f59e0b; }
    
    /* Upload area */
    .upload-area {
        border: 2px dashed #c9b037;
        border-radius: 12px;
        background: linear-gradient(135deg, rgba(201, 176, 55, 0.05) 0%, rgba(220, 202, 43, 0.05) 100%);
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .header-content {
            flex-direction: column;
            gap: 1rem;
        }
        
        .control-buttons {
            justify-content: center;
        }
        
        .custom-header {
            padding: 1.5rem;
        }
        
        .stats-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }
    
    /* Status animations */
    .calling-indicator {
        display: inline-block;
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'processed_numbers' not in st.session_state:
    st.session_state.processed_numbers = []
if 'call_history' not in st.session_state:
    st.session_state.call_history = []
if 'selected_contacts' not in st.session_state:
    st.session_state.selected_contacts = set()
if 'calling_in_progress' not in st.session_state:
    st.session_state.calling_in_progress = False
if 'current_calling_index' not in st.session_state:
    st.session_state.current_calling_index = None
if 'stop_calling' not in st.session_state:
    st.session_state.stop_calling = False
if 'call_queue' not in st.session_state:
    st.session_state.call_queue = []
if 'contact_statuses' not in st.session_state:
    st.session_state.contact_statuses = {}

class JapanesePhoneProcessor:
    def __init__(self):
        self.mobile_prefixes = ['070', '080', '090']
        self.landline_patterns = [
            r'0[1-9]\d{8,9}',
        ]
    
    def clean_number(self, number):
        """Clean and standardize phone number input"""
        if pd.isna(number):
            return None
        
        number_str = str(number).strip()
        digits_only = re.sub(r'[^\d]', '', number_str)
        
        if len(digits_only) == 0:
            return None
        elif len(digits_only) == 9:
            if digits_only.startswith('9') or digits_only.startswith('8') or digits_only.startswith('7'):
                digits_only = '0' + digits_only
            else:
                digits_only = '0' + digits_only
        elif len(digits_only) == 10:
            if not digits_only.startswith('0'):
                if digits_only.startswith('9') or digits_only.startswith('8') or digits_only.startswith('7'):
                    digits_only = '0' + digits_only
                else:
                    digits_only = '0' + digits_only
        elif len(digits_only) == 11:
            if not digits_only.startswith('0'):
                if digits_only.startswith('81'):
                    digits_only = '0' + digits_only[2:]
        elif len(digits_only) > 11:
            digits_only = digits_only[:11]
        else:
            if len(digits_only) < 8:
                return None
        
        return digits_only
    
    def validate_japanese_number(self, number):
        """Validate if number is a valid Japanese phone number"""
        if not number:
            return False
        
        if not number.startswith('0'):
            return False
        
        if number[:3] in self.mobile_prefixes and len(number) == 11:
            return True
        
        if len(number) == 10:
            if number.startswith('03') or number.startswith('06'):
                return True
            elif number.startswith('0') and number[1] in '123459':
                return True
        
        return False
    
    def format_for_twilio(self, number):
        """Convert Japanese number to international format for Twilio"""
        if not self.validate_japanese_number(number):
            return None
        
        international_number = '+81' + number[1:]
        return international_number
    
    def process_numbers_with_names(self, data_list):
        """Process a list of data with names and phone numbers"""
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
                formatted = self.format_for_twilio(cleaned)
                status = "valid"
            else:
                formatted = None
                status = "invalid"
            
            results.append({
                'id': idx,
                'name': name,
                'original': original,
                'cleaned': cleaned if cleaned else "N/A",
                'international': formatted if formatted else "N/A",
                'status': status
            })
        
        return results

class TwilioCaller:
    def __init__(self, account_sid, auth_token, from_number, forward_number="+817044448888"):
        try:
            self.client = Client(account_sid, auth_token)
            self.from_number = from_number
            self.forward_number = forward_number
            self.is_configured = True
        except Exception as e:
            self.is_configured = False
            self.error = str(e)
    
    def make_call_with_forwarding(self, to_number, person_name=""):
        """Make call - if answered forward to operator, if not leave voicemail"""
        if not self.is_configured:
            return False, "Twilio not configured properly"
        
        twiml = f'''
        <Response>
            <Say language="ja-JP">お繋ぎしますのでお待ちください</Say>
            <Dial timeout="30" record="record-from-answer">
                <Number>{self.forward_number}</Number>
            </Dial>
            <Say language="ja-JP">こちらは法律事務所です。大切な用件がございますので、折り返しお電話ください。</Say>
        </Response>
        '''
        
        try:
            call = self.client.calls.create(
                twiml=twiml,
                to=to_number,
                from_=self.from_number,
                machine_detection="Enable",
                machine_detection_timeout=30
            )
            return True, f"Call to {person_name} initiated. SID: {call.sid}"
        except TwilioException as e:
            return False, f"Twilio error: {str(e)}"
        except Exception as e:
            return False, f"Error: {str(e)}"

class GoogleSheetsLogger:
    def __init__(self, credentials_json, spreadsheet_url):
        try:
            creds_dict = json.loads(credentials_json)
            self.creds = Credentials.from_service_account_info(creds_dict)
            self.client = gspread.authorize(self.creds)
            self.sheet = self.client.open_by_url(spreadsheet_url).sheet1
            self.is_configured = True
        except Exception as e:
            self.is_configured = False
            self.error = str(e)
    
    def log_call_result(self, name, phone, status, message, timestamp):
        if not self.is_configured:
            return False
        
        try:
            self.sheet.append_row([timestamp, name, phone, status, message])
            return True
        except Exception as e:
            return False

def render_contact_card(contact, index, is_selected, contact_status):
    """Render a modern contact card"""
    status_class = f"contact-card {contact_status}"
    if is_selected:
        status_class += " selected"
    
    status_indicators = {
        "waiting": ("⏳", "Waiting", "status-waiting"),
        "calling": ("📞", "Calling...", "status-calling"),
        "completed": ("✅", "Completed", "status-completed"),
        "failed": ("❌", "Failed", "status-failed")
    }
    
    icon, label, dot_class = status_indicators.get(contact_status, ("⏳", "Waiting", "status-waiting"))
    
    # Get initials for avatar
    initials = ''.join([word[0].upper() for word in contact['name'].split()[:2]])
    
    card_html = f"""
    <div class="{status_class}" data-contact-id="{contact['id']}">
        <div class="contact-checkbox {'checked' if is_selected else ''}" onclick="toggleContact({contact['id']})">
            {'✓' if is_selected else ''}
        </div>
        <div class="contact-avatar">{initials}</div>
        <div class="contact-info">
            <div class="contact-name">{contact['name']}</div>
            <div class="contact-phone">{contact['international']}</div>
        </div>
        <div class="contact-status">
            <div class="status-dot {dot_class}"></div>
            <span class="{'calling-indicator' if contact_status == 'calling' else ''}">{label}</span>
        </div>
    </div>
    """
    
    return card_html

def main():
    # Custom Header
    st.markdown("""
    <div class="custom-header">
        <div class="header-content">
            <div class="logo-container">
                <div class="logo-placeholder">M</div>
                <div class="logo-text">
                    <div class="logo-japanese">東京山王法律事務所</div>
                    <div class="logo-english">Tokyo Sanno Law Office</div>
                </div>
            </div>
            <div class="header-title">
                <h1>Advanced Call System</h1>
                <p>Upload → Select → Call → Track Results</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar Configuration
    with st.sidebar:
        st.markdown("### ⚙️ **Configuration**")
        
        # Operator number
        operator_number = st.text_input(
            "Operator Forward Number",
            value="+817044448888",
            help="Number to forward calls to"
        )
        
        # Twilio configuration
        try:
            if "twilio" in st.secrets:
                account_sid = st.secrets["twilio"]["account_sid"]
                auth_token = st.secrets["twilio"]["auth_token"]
                from_number = st.secrets["twilio"]["from_number"]
            else:
                account_sid = st.secrets["account_sid"]
                auth_token = st.secrets["auth_token"]
                from_number = st.secrets["from_number"]
            
            st.success("✅ **Twilio configured successfully!**")
            st.info(f"📞 **From:** {from_number}")
            twilio_configured = True
                
        except KeyError as e:
            st.error(f"❌ **Missing Twilio secret:** {e}")
            twilio_configured = False
            account_sid = auth_token = from_number = None
            
        except Exception as e:
            st.error(f"❌ **Error loading Twilio secrets:** {e}")
            twilio_configured = False
            account_sid = auth_token = from_number = None
        
        # Google Sheets configuration
        st.markdown("### 📊 **Spreadsheet Logging**")
        spreadsheet_url = st.text_input(
            "Google Sheets URL",
            help="URL of your Google Sheets for logging results"
        )
        
        try:
            if "google_sheets" in st.secrets:
                google_creds = st.secrets["google_sheets"]["credentials"]
                if spreadsheet_url:
                    sheets_logger = GoogleSheetsLogger(google_creds, spreadsheet_url)
                    if sheets_logger.is_configured:
                        st.success("✅ **Google Sheets connected!**")
                    else:
                        st.error(f"❌ **Sheets error:** {sheets_logger.error}")
                        sheets_logger = None
                else:
                    sheets_logger = None
            else:
                sheets_logger = None
                st.info("📝 **Google Sheets credentials not configured**")
        except Exception as e:
            st.error(f"❌ **Sheets configuration error:** {e}")
            sheets_logger = None
        
        # Create TwilioCaller
        if twilio_configured:
            twilio_caller = TwilioCaller(account_sid, auth_token, from_number, operator_number)
        else:
            twilio_caller = None
        
        st.markdown("### 📞 **Call Settings**")
        call_delay = st.slider("Delay between calls (seconds)", 1, 30, 5)
        
        st.markdown("### 🎯 **Call Flow**")
        st.markdown("""
        **1.** Upload Excel file  
        **2.** Select contacts to call  
        **3.** Click "Start Calling"  
        **4.** Calls made sequentially  
        **5.** Results logged to spreadsheet
        """)

    # Main content
    # Step 1: File Upload
    st.markdown("""
    <div class="control-panel">
        <div class="control-header">
            <div class="control-title">📂 Step 1: Upload Contact List</div>
        </div>
        <div class="upload-area">
            <h4>📋 Upload Excel File</h4>
            <p>Upload your Excel file with Name and Phone_Number columns</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose an Excel file",
        type=['xlsx', 'xls'],
        help="Upload an Excel file containing phone numbers"
    )
    
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            st.success(f"✅ **File uploaded successfully!** Found **{len(df)}** rows.")
            
            if 'Name' in df.columns and 'Phone_Number' in df.columns:
                processor = JapanesePhoneProcessor()
                data_list = df.to_dict('records')
                
                with st.spinner("🔄 Processing phone numbers..."):
                    results = processor.process_numbers_with_names(data_list)
                    st.session_state.processed_numbers = results
                    
                    # Initialize contact statuses
                    for contact in results:
                        if contact['id'] not in st.session_state.contact_statuses:
                            st.session_state.contact_statuses[contact['id']] = 'waiting'
        except Exception as e:
            st.error(f"❌ **Error processing file:** {str(e)}")
    
    # Step 2: Contact Selection and Calling
    if st.session_state.processed_numbers:
        valid_contacts = [c for c in st.session_state.processed_numbers if c['status'] == 'valid']
        
        if valid_contacts:
            # Statistics
            total_contacts = len(valid_contacts)
            selected_count = len(st.session_state.selected_contacts)
            completed_count = len([c for c in valid_contacts if st.session_state.contact_statuses.get(c['id']) == 'completed'])
            failed_count = len([c for c in valid_contacts if st.session_state.contact_statuses.get(c['id']) == 'failed'])
            calling_count = 1 if st.session_state.calling_in_progress else 0
            
            st.markdown(f"""
            <div class="control-panel">
                <div class="control-header">
                    <div class="control-title">📞 Step 2: Select & Call Contacts</div>
                </div>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value stat-total">{total_contacts}</div>
                        <div class="stat-label">Total Valid</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value stat-selected">{selected_count}</div>
                        <div class="stat-label">Selected</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value stat-calling">{calling_count}</div>
                        <div class="stat-label">Calling</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value stat-completed">{completed_count}</div>
                        <div class="stat-label">Completed</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value stat-failed">{failed_count}</div>
                        <div class="stat-label">Failed</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Control buttons
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                if st.button("✅ Select All", type="secondary", use_container_width=True):
                    st.session_state.selected_contacts = set([c['id'] for c in valid_contacts])
                    st.rerun()
            
            with col2:
                if st.button("❌ Deselect All", type="secondary", use_container_width=True):
                    st.session_state.selected_contacts.clear()
                    st.rerun()
            
            with col3:
                if st.button("📞 Start Calling", type="primary", use_container_width=True, 
                           disabled=not st.session_state.selected_contacts or st.session_state.calling_in_progress):
                    if twilio_caller and twilio_caller.is_configured:
                        st.session_state.call_queue = list(st.session_state.selected_contacts)
                        st.session_state.calling_in_progress = True
                        st.session_state.stop_calling = False
                        st.rerun()
                    else:
                        st.error("❌ Twilio not configured properly!")
            
            with col4:
                if st.button("🛑 Stop Calling", type="secondary", use_container_width=True,
                           disabled=not st.session_state.calling_in_progress):
                    st.session_state.stop_calling = True
                    st.session_state.calling_in_progress = False
                    st.session_state.call_queue = []
                    st.success("🛑 Calling stopped!")
                    st.rerun()
            
            with col5:
                if st.button("🔄 Reset All", type="secondary", use_container_width=True):
                    st.session_state.selected_contacts.clear()
                    st.session_state.calling_in_progress = False
                    st.session_state.call_queue = []
                    st.session_state.contact_statuses = {}
                    for contact in valid_contacts:
                        st.session_state.contact_statuses[contact['id']] = 'waiting'
                    st.rerun()
            
            # Progress bar
            if st.session_state.calling_in_progress and st.session_state.call_queue:
                total_to_call = len([c for c in valid_contacts if c['id'] in st.session_state.selected_contacts])
                remaining = len(st.session_state.call_queue)
                progress = (total_to_call - remaining) / total_to_call if total_to_call > 0 else 0
                
                st.markdown(f"""
                <div class="progress-container">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {progress * 100}%"></div>
                    </div>
                    <div class="progress-text">
                        Progress: {total_to_call - remaining} / {total_to_call} calls completed
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Contact cards
            st.markdown('<div class="contacts-grid">', unsafe_allow_html=True)
            
            for contact in valid_contacts:
                is_selected = contact['id'] in st.session_state.selected_contacts
                contact_status = st.session_state.contact_statuses.get(contact['id'], 'waiting')
                
                # Render contact card
                contact_html = render_contact_card(contact, contact['id'], is_selected, contact_status)
                
                # Create a container for each contact with click handling
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        st.markdown(contact_html, unsafe_allow_html=True)
                    
                    with col2:
                        # Individual call button
                        if st.button(f"📞", key=f"call_{contact['id']}", 
                                   disabled=st.session_state.calling_in_progress or contact_status in ['completed', 'failed']):
                            if twilio_caller and twilio_caller.is_configured:
                                st.session_state.contact_statuses[contact['id']] = 'calling'
                                st.rerun()
                                
                                # Make the call
                                success, message = twilio_caller.make_call_with_forwarding(
                                    contact['international'], contact['name']
                                )
                                
                                # Update status
                                if success:
                                    st.session_state.contact_statuses[contact['id']] = 'completed'
                                    st.success(f"✅ {contact['name']}: {message}")
                                else:
                                    st.session_state.contact_statuses[contact['id']] = 'failed'
                                    st.error(f"❌ {contact['name']}: {message}")
                                
                                # Log to Google Sheets
                                if sheets_logger and sheets_logger.is_configured:
                                    sheets_logger.log_call_result(
                                        contact['name'],
                                        contact['international'],
                                        'Success' if success else 'Failed',
                                        message,
                                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                    )
                                
                                # Add to call history
                                st.session_state.call_history.append({
                                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                    'name': contact['name'],
                                    'number': contact['international'],
                                    'status': 'Success' if success else 'Failed',
                                    'message': message
                                })
                                
                                time.sleep(1)  # Brief pause
                                st.rerun()
                        
                        # Checkbox for selection
                        checkbox_key = f"select_{contact['id']}"
                        if st.checkbox("", key=checkbox_key, value=is_selected, label_visibility="collapsed"):
                            st.session_state.selected_contacts.add(contact['id'])
                        else:
                            st.session_state.selected_contacts.discard(contact['id'])
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Handle sequential calling
            if st.session_state.calling_in_progress and st.session_state.call_queue and not st.session_state.stop_calling:
                if twilio_caller and twilio_caller.is_configured:
                    current_id = st.session_state.call_queue[0]
                    current_contact = next((c for c in valid_contacts if c['id'] == current_id), None)
                    
                    if current_contact:
                        st.session_state.contact_statuses[current_id] = 'calling'
                        st.session_state.current_calling_index = current_id
                        
                        with st.spinner(f"📞 Calling {current_contact['name']}..."):
                            success, message = twilio_caller.make_call_with_forwarding(
                                current_contact['international'],
                                current_contact['name']
                            )
                            
                            # Update status
                            if success:
                                st.session_state.contact_statuses[current_id] = 'completed'
                                st.success(f"✅ {current_contact['name']}: {message}")
                            else:
                                st.session_state.contact_statuses[current_id] = 'failed'
                                st.error(f"❌ {current_contact['name']}: {message}")
                            
                            # Log to Google Sheets
                            if sheets_logger and sheets_logger.is_configured:
                                sheets_logger.log_call_result(
                                    current_contact['name'],
                                    current_contact['international'],
                                    'Success' if success else 'Failed',
                                    message,
                                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                )
                            
                            # Add to call history
                            st.session_state.call_history.append({
                                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'name': current_contact['name'],
                                'number': current_contact['international'],
                                'status': 'Success' if success else 'Failed',
                                'message': message
                            })
                            
                            # Remove from queue
                            st.session_state.call_queue.pop(0)
                            st.session_state.current_calling_index = None
                            
                            # Check if more calls to make
                            if not st.session_state.call_queue:
                                st.session_state.calling_in_progress = False
                                st.success("🎉 All selected calls completed!")
                            else:
                                # Wait before next call
                                time.sleep(call_delay)
                            
                            st.rerun()
    
    # Call History
    if st.session_state.call_history:
        st.markdown("""
        <div class="control-panel">
            <div class="control-header">
                <div class="control-title">📋 Call History & Results</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        history_df = pd.DataFrame(st.session_state.call_history)
        st.dataframe(history_df, use_container_width=True, height=300)
        
        col1, col2 = st.columns(2)
        with col1:
            history_csv = history_df.to_csv(index=False)
            st.download_button(
                label="📥 **Download Call History**",
                data=history_csv,
                file_name=f"call_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            if st.button("🗑️ **Clear History**", use_container_width=True):
                st.session_state.call_history = []
                st.rerun()

    # JavaScript for contact selection
    st.markdown("""
    <script>
    function toggleContact(contactId) {
        // This would need to be implemented with Streamlit's component system
        // for proper JavaScript integration
        console.log('Toggle contact:', contactId);
    }
    </script>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
