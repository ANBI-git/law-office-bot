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

# Set page config
st.set_page_config(
    page_title="Tokyo Sanno Law Office - Call System",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for world-class design
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
        position: relative;
        overflow: hidden;
    }
    
    .logo-placeholder::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #d4af37, #ffd700, #d4af37);
        border-radius: 14px;
        z-index: -1;
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
    
    /* Cards and sections */
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 1rem;
    }
    
    .feature-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #c9b037 0%, #dcca2b 50%, #c9b037 100%);
    }
    
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
    }
    
    .card-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .card-subtitle {
        font-size: 0.9rem;
        color: #666;
        margin-bottom: 1.5rem;
        line-height: 1.5;
    }
    
    /* Metrics */
    .metrics-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: shimmer 3s ease-in-out infinite;
    }
    
    @keyframes shimmer {
        0%, 100% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        50% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
        font-weight: 500;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #c9b037 0%, #dcca2b 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(201, 176, 55, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(201, 176, 55, 0.4);
        background: linear-gradient(135deg, #dcca2b 0%, #c9b037 100%);
    }
    
    /* Tables */
    .dataframe {
        border: none !important;
        border-radius: 8px !important;
        overflow: hidden !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Status indicators */
    .status-valid {
        color: #10b981;
        font-weight: 600;
    }
    
    .status-invalid {
        color: #ef4444;
        font-weight: 600;
    }
    
    /* Upload area */
    .uploadedFile {
        border: 2px dashed #c9b037 !important;
        border-radius: 8px !important;
        background: linear-gradient(135deg, rgba(201, 176, 55, 0.05) 0%, rgba(220, 202, 43, 0.05) 100%) !important;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .header-content {
            flex-direction: column;
            gap: 1rem;
            text-align: center;
        }
        
        .logo-container {
            justify-content: center;
        }
        
        .custom-header {
            padding: 1.5rem;
            margin: -1rem -1rem 1rem -1rem;
        }
        
        .feature-card {
            padding: 1.5rem;
        }
        
        .metrics-container {
            grid-template-columns: 1fr;
        }
    }
    
    /* Success/Error messages */
    .stSuccess {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        border: none;
        border-radius: 8px;
        color: white;
    }
    
    .stError {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        border: none;
        border-radius: 8px;
        color: white;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        border: none;
        border-radius: 8px;
        color: white;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        border: none;
        border-radius: 8px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Logo display function
def display_logo():
    """Display logo with fallback to placeholder"""
    try:
        # Try to load the uploaded logo first
        logo_image = Image.open("logo.png")
        return logo_image
    except:
        # Return None if logo not found
        return None

# Initialize session state
if 'processed_numbers' not in st.session_state:
    st.session_state.processed_numbers = []
if 'call_history' not in st.session_state:
    st.session_state.call_history = []

class JapanesePhoneProcessor:
    def __init__(self):
        self.mobile_prefixes = ['070', '080', '090']
        self.landline_patterns = [
            r'0[1-9]\d{8,9}',  # Standard landline patterns
        ]
    
    def clean_number(self, number):
        """Clean and standardize phone number input"""
        if pd.isna(number):
            return None
        
        # Convert to string and remove all non-digits
        number_str = str(number).strip()
        digits_only = re.sub(r'[^\d]', '', number_str)
        
        # Handle different cases
        if len(digits_only) == 0:
            return None
        elif len(digits_only) == 9:
            # Could be mobile (missing 0) or landline (missing 0)
            # Check if it starts with mobile prefixes (90, 80, 70)
            if digits_only.startswith('9') or digits_only.startswith('8') or digits_only.startswith('7'):
                digits_only = '0' + digits_only  # Make it 10 digits, but mobile needs 11
            else:
                digits_only = '0' + digits_only  # Landline, perfect at 10 digits
        elif len(digits_only) == 10:
            # Check if it's missing the leading 0
            if not digits_only.startswith('0'):
                if digits_only.startswith('9') or digits_only.startswith('8') or digits_only.startswith('7'):
                    # Mobile number missing leading 0
                    digits_only = '0' + digits_only  # This makes it 11 digits (correct for mobile)
                else:
                    # Landline missing leading 0
                    digits_only = '0' + digits_only  # This makes it 11 digits (too long for landline)
                    # For landlines, we need to keep it at 10 digits
                    if not (digits_only.startswith('090') or digits_only.startswith('080') or digits_only.startswith('070')):
                        digits_only = digits_only  # Keep the 11 digits and validate will catch the error
            # If it already starts with 0, check if it needs adjustment
            elif digits_only.startswith('09') or digits_only.startswith('08') or digits_only.startswith('07'):
                # Mobile number but only 10 digits, needs to be 11
                # Actually this is wrong - 09XXXXXXXX should be 090XXXXXXX (11 digits)
                # The input 9012345678 becomes 09012345678 which is correct (11 digits)
                pass  # Keep as is
        elif len(digits_only) == 11:
            # Should be perfect length for mobile numbers
            if not digits_only.startswith('0'):
                if digits_only.startswith('81'):
                    # International format without +, remove 81 and add 0
                    digits_only = '0' + digits_only[2:]
        elif len(digits_only) > 11:
            # Too long, truncate from the right
            digits_only = digits_only[:11]
        else:
            # Other lengths, try to make sense of it
            if len(digits_only) < 8:
                return None
        
        return digits_only
    
    def validate_japanese_number(self, number):
        """Validate if number is a valid Japanese phone number"""
        if not number:
            return False
        
        if not number.startswith('0'):
            return False
        
        # Check mobile prefixes (090, 080, 070) - these are 11 digits
        if number[:3] in self.mobile_prefixes and len(number) == 11:
            return True
        
        # Check landline patterns - these are 10 digits
        # Tokyo area: 03-XXXX-XXXX (10 digits total)
        # Osaka area: 06-XXXX-XXXX (10 digits total)
        # Other areas: 0X-XXXX-XXXX where X is 1,2,3,4,5,6,7,8,9 but not 0,7,8,9 for first digit
        if len(number) == 10:
            if number.startswith('03') or number.startswith('06'):  # Tokyo, Osaka
                return True
            elif number.startswith('0') and number[1] in '123459':  # Other landline areas
                return True
        
        return False
    
    def format_for_twilio(self, number):
        """Convert Japanese number to international format for Twilio"""
        if not self.validate_japanese_number(number):
            return None
        
        # Remove leading 0 and add +81
        international_number = '+81' + number[1:]
        return international_number
    
    def process_numbers_with_names(self, data_list):
        """Process a list of data with names and phone numbers"""
        results = []
        for idx, row in enumerate(data_list):
            # Handle both dictionary and list formats
            if isinstance(row, dict):
                name = str(row.get('Name', row.get('name', f'Person {idx+1}')))
                number = row.get('Phone_Number', row.get('phone_number', row.get('phone', '')))
            else:
                # If it's a list, assume [name, phone] format
                name = str(row[0]) if len(row) > 0 else f'Person {idx+1}'
                number = row[1] if len(row) > 1 else ''
            
            original = str(number) if not pd.isna(number) else ""
            cleaned = self.clean_number(number)
            
            if cleaned and self.validate_japanese_number(cleaned):
                formatted = self.format_for_twilio(cleaned)
                status = "✅ Valid"
            else:
                formatted = None
                status = "❌ Invalid"
            
            results.append({
                'Index': idx + 1,
                'Name': name,
                'Original': original,
                'Cleaned': cleaned if cleaned else "N/A",
                'International': formatted if formatted else "N/A",
                'Status': status
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
        
        # Simple TwiML: Say forwarding message then forward
        twiml = f'''
        <Response>
            <Say language="ja-JP">お繋ぎしますのでお待ちください</Say>
            <Dial timeout="30" record="record-from-answer">
                <Number>{self.forward_number}</Number>
            </Dial>
            <!-- If no answer or forwarding fails, leave voicemail -->
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

# Main App
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
                <h1>Phone Call System</h1>
                <p>Upload Excel → Check Numbers → Call One by One → Forward to Operator</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


    # Sidebar for configuration
    with st.sidebar:
        st.markdown("### 🔧 **Twilio Configuration**")
        
        # First, define operator_number
        st.markdown("### ⚙️ **Settings**")
        operator_number = st.text_input(
            "Operator Forward Number",
            value="+817044448888",
            help="Number to forward calls to"
        )
        
        # Then load Twilio credentials from secrets
        try:
            # Try with [twilio] section first
            if "twilio" in st.secrets:
                account_sid = st.secrets["twilio"]["account_sid"]
                auth_token = st.secrets["twilio"]["auth_token"]
                from_number = st.secrets["twilio"]["from_number"]
            else:
                # Try without section (top-level secrets)
                account_sid = st.secrets["account_sid"]
                auth_token = st.secrets["auth_token"]
                from_number = st.secrets["from_number"]
            
            st.success("✅ **Twilio configured successfully!**")
            st.info(f"📞 **From:** {from_number}")
            twilio_configured = True
                
        except KeyError as e:
            st.error(f"❌ **Missing Twilio secret:** {e}")
            st.error("**Please configure Twilio secrets in Streamlit Cloud**")
            st.info("**Format should be:**\n```\naccount_sid = \"AC...\"\nauth_token = \"...\"\nfrom_number = \"+81...\"\n```")
            twilio_configured = False
            account_sid = auth_token = from_number = None
            
        except Exception as e:
            st.error(f"❌ **Error loading Twilio secrets:** {e}")
            twilio_configured = False
            account_sid = auth_token = from_number = None
        
        # Create TwilioCaller after operator_number is defined
        if twilio_configured:
            twilio_caller = TwilioCaller(account_sid, auth_token, from_number, operator_number)
            if not twilio_caller.is_configured:
                st.error(f"❌ **Twilio configuration error:** {twilio_caller.error}")
        else:
            twilio_caller = None
        
        st.markdown("### 📞 **Call Settings**")
        st.markdown(f"**Operator Number:** `{operator_number}`")
        
        st.markdown("### 🎯 **Call Flow**")
        st.markdown("""
        **1. Upload Excel** → Check numbers  
        **2. Call people one by one**  
        **3. If person picks up:**  
        ・Say: "お繋ぎしますのでお待ちください"  
        ・Forward to operator  
        **4. If no answer/voicemail:**  
        ・Leave message: "こちらは法律事務所です..."
        """)

    # Main content area
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1], gap="large")
    
    with col1:
        # Upload Section
        st.markdown("""
        <div class="feature-card">
            <h3 class="card-title">📂 Step 1: Upload Excel Sheet</h3>
            <p class="card-subtitle">Upload your Excel file with Name and Phone_Number columns for validation and calling</p>
        </div>
        """, unsafe_allow_html=True)
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose an Excel file",
            type=['xlsx', 'xls'],
            help="Upload an Excel file containing phone numbers"
        )
        
        # Sample data info
        with st.expander("📋 **Supported Formats & Features** (Click to view)", expanded=False):
            st.markdown("""
            **📊 Excel File Formats:**
            
            | Column Name | Example Data | Description |
            |-------------|--------------|-------------|
            | **Name** | `Yamada Tarou` | Client/Contact name |
            | **Phone_Number** | `9012345678` | Phone number (Excel format) |
            
            **🇯🇵 Phone Number Formats:**
            
            | Format Type | Example | Converted To | Length |
            |-------------|---------|--------------|---------|
            | **Excel Mobile** | `9012345678` | `+819012345678` | 11 digits |
            | **Excel Landline** | `312345678` | `+81312345678` | 10 digits |
            | **Mobile** | `070-1234-5678` | `+817012345678` | 11 digits |
            | **Landline** | `03-1234-5678` | `+81312345678` | 10 digits |
            | **No Hyphens** | `0312345678` | `+81312345678` | 10 digits |
            
            **🤖 Call Flow:**
            
            **📞 Simple & Effective Process:**
            - Upload Excel with Name + Phone_Number columns
            - System validates and formats all numbers
            - Click individual "Call" buttons for each person
            - **If person picks up:** "お繋ぎしますのでお待ちください" → Forward to operator
            - **If no answer/voicemail:** "こちらは法律事務所です。大切な用件がございますので、折り返しお電話ください。"
            - All calls are recorded and tracked
            
            **✨ Smart Processing:** Automatically handles Excel formatting issues, validates Japanese numbers, and provides one-click calling.
            """)
        
        if uploaded_file is not None:
            try:
                # Read Excel file
                df = pd.read_excel(uploaded_file)
                st.success(f"✅ **File uploaded successfully!** Found **{len(df)}** rows.")
                
                # Check if we have the expected columns
                if 'Name' in df.columns and 'Phone_Number' in df.columns:
                    st.info("📋 **Detected format:** Name + Phone_Number columns (Perfect!)")
                    
                    # Process data with names
                    processor = JapanesePhoneProcessor()
                    data_list = df.to_dict('records')  # Convert to list of dictionaries
                    
                    with st.spinner("🔄 Processing phone numbers with names..."):
                        results = processor.process_numbers_with_names(data_list)
                else:
                    # Show column selection for other formats
                    st.markdown("#### 📊 Select Columns")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        name_column = st.selectbox(
                            "Name Column:", 
                            ["None"] + df.columns.tolist(),
                            help="Select the column containing names (optional)"
                        )
                    
                    with col2:
                        phone_column = st.selectbox(
                            "Phone Number Column:", 
                            df.columns.tolist(),
                            help="Select the column containing phone numbers"
                        )
                    
                    if phone_column:
                        # Create data list with names if available
                        processor = JapanesePhoneProcessor()
                        data_list = []
                        
                        for idx, row in df.iterrows():
                            name = row[name_column] if name_column != "None" else f"Person {idx+1}"
                            phone = row[phone_column]
                            data_list.append({'Name': name, 'Phone_Number': phone})
                        
                        with st.spinner("🔄 Processing phone numbers..."):
                            results = processor.process_numbers_with_names(data_list)
                
                if 'results' in locals():
                    # Store in session state
                    st.session_state.processed_numbers = results
                    
                    # Display results
                    st.markdown("#### 📊 Processing Results")
                    
                    # Metrics
                    valid_count = len([r for r in results if r['Status'] == "✅ Valid"])
                    invalid_count = len([r for r in results if r['Status'] == "❌ Invalid"])
                    
                    # Create metrics display
                    st.markdown("""
                    <div class="metrics-container">
                        <div class="metric-card">
                            <div class="metric-value">{}</div>
                            <div class="metric-label">Total Numbers</div>
                        </div>
                        <div class="metric-card" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
                            <div class="metric-value">{}</div>
                            <div class="metric-label">Valid Numbers</div>
                        </div>
                        <div class="metric-card" style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);">
                            <div class="metric-value">{}</div>
                            <div class="metric-label">Invalid Numbers</div>
                        </div>
                    </div>
                    """.format(len(results), valid_count, invalid_count), unsafe_allow_html=True)
                    
                    # Results table
                    st.markdown("#### 📋 Detailed Results")
                    results_df = pd.DataFrame(results)
                    st.dataframe(results_df, use_container_width=True, height=400)
                    
                    # Download processed data
                    csv = results_df.to_csv(index=False)
                    st.download_button(
                        label="📥 **Download Processed Numbers (CSV)**",
                        data=csv,
                        file_name=f"processed_numbers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            
            except Exception as e:
                st.error(f"❌ **Error processing file:** {str(e)}")
    
    with col2:
        # Calling Section
        st.markdown("""
        <div class="feature-card">
            <h3 class="card-title">📞 Step 2: Call People</h3>
            <p class="card-subtitle">Call each person individually - forwards to operator if answered, leaves voicemail if not</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.processed_numbers:
            valid_numbers = [r for r in st.session_state.processed_numbers if r['Status'] == "✅ Valid"]
            
            if valid_numbers and twilio_caller and twilio_caller.is_configured:
                st.success(f"📋 **{len(valid_numbers)} valid numbers** ready for calling")
                
                # Simple call interface - one by one
                st.markdown("##### 📞 Call People One by One")
                
                # Show all valid numbers with individual call buttons
                for i, number_data in enumerate(valid_numbers):
                    with st.container():
                        col1, col2, col3 = st.columns([2, 2, 1])
                        
                        with col1:
                            st.markdown(f"**{number_data['Name']}**")
                        
                        with col2:
                            st.markdown(f"`{number_data['International']}`")
                        
                        with col3:
                            call_button_key = f"call_{i}"
                            if st.button("📞 Call", key=call_button_key, type="primary"):
                                with st.spinner(f"📞 Calling {number_data['Name']}..."):
                                    success, message = twilio_caller.make_call_with_forwarding(
                                        number_data['International'],
                                        number_data['Name']
                                    )
                                
                                if success:
                                    st.success(f"✅ **{message}**")
                                    # Add to call history
                                    st.session_state.call_history.append({
                                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                        'name': number_data['Name'],
                                        'number': number_data['International'],
                                        'status': 'Success',
                                        'message': message
                                    })
                                    st.rerun()  # Refresh to show updated history
                                else:
                                    st.error(f"❌ **{message}**")
                                    st.session_state.call_history.append({
                                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                        'name': number_data['Name'],
                                        'number': number_data['International'],
                                        'status': 'Failed',
                                        'message': message
                                    })
                        
                        st.markdown("---")
                
                # Optional bulk call
                st.markdown("##### 📞 Or Call All at Once")
                delay_seconds = st.slider("**Delay between calls (seconds):**", 1, 10, 5)
                
                if st.button("📞 **Call All Numbers**", type="secondary", use_container_width=True):
                    progress_bar = st.progress(0)
                    status_placeholder = st.empty()
                    
                    for i, number_data in enumerate(valid_numbers):
                        status_placeholder.info(f"📞 Calling **{number_data['Name']}** at **{number_data['International']}**...")
                        
                        success, message = twilio_caller.make_call_with_forwarding(
                            number_data['International'],
                            number_data['Name']
                        )
                        
                        # Update call history
                        st.session_state.call_history.append({
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'name': number_data['Name'],
                            'number': number_data['International'],
                            'status': 'Success' if success else 'Failed',
                            'message': message
                        })
                        
                        # Update progress
                        progress_bar.progress((i + 1) / len(valid_numbers))
                        
                        # Delay between calls
                        if i < len(valid_numbers) - 1:
                            time.sleep(delay_seconds)
                    
                    status_placeholder.success("✅ **All calls completed!**")
                    st.rerun()  # Refresh to show updated history
            else:
                if not valid_numbers:
                    st.info("📋 **No valid numbers to call.** Please upload and process phone numbers first.")
                elif not twilio_caller or not twilio_caller.is_configured:
                    st.error("❌ **Twilio not configured.** Please check your Streamlit Cloud secrets.")
        else:
            st.info("📋 **Upload and process phone numbers** to start making calls.")
    
    # Call History
    if st.session_state.call_history:
        st.markdown("""
        <div class="feature-card">
            <h3 class="card-title">📋 Step 3: Call History & Results</h3>
            <p class="card-subtitle">Complete history of all calls made with success/failure status</p>
        </div>
        """, unsafe_allow_html=True)
        
        history_df = pd.DataFrame(st.session_state.call_history)
        st.dataframe(history_df, use_container_width=True, height=300)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Download call history
            history_csv = history_df.to_csv(index=False)
            st.download_button(
                label="📥 **Download Call History (CSV)**",
                data=history_csv,
                file_name=f"call_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            # Clear history button
            if st.button("🗑️ **Clear Call History**", use_container_width=True):
                st.session_state.call_history = []
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
