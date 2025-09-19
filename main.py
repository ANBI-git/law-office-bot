import streamlit as st
import pandas as pd
import re
import io
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
import time
from datetime import datetime
import numpy as np

# Set page config
st.set_page_config(
    page_title="Japanese Phone Caller Pro",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .metric-container {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

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
            # Likely missing leading 0, add it
            digits_only = '0' + digits_only
        elif len(digits_only) == 10:
            # Perfect length
            pass
        elif len(digits_only) == 11 and digits_only.startswith('81'):
            # International format without +, remove 81 and add 0
            digits_only = '0' + digits_only[2:]
        elif len(digits_only) > 11:
            # Too long, truncate from the right
            digits_only = digits_only[:10]
        else:
            # Other lengths, try to make sense of it
            if len(digits_only) < 9:
                return None
        
        return digits_only
    
    def validate_japanese_number(self, number):
        """Validate if number is a valid Japanese phone number"""
        if not number or len(number) != 10:
            return False
        
        if not number.startswith('0'):
            return False
        
        # Check mobile prefixes
        if number[:3] in self.mobile_prefixes:
            return True
        
        # Check landline patterns
        for pattern in self.landline_patterns:
            if re.match(pattern, number):
                return True
        
        return False
    
    def format_for_twilio(self, number):
        """Convert Japanese number to international format for Twilio"""
        if not self.validate_japanese_number(number):
            return None
        
        # Remove leading 0 and add +81
        international_number = '+81' + number[1:]
        return international_number
    
    def process_numbers(self, numbers_list):
        """Process a list of phone numbers"""
        results = []
        for idx, number in enumerate(numbers_list):
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
                'Original': original,
                'Cleaned': cleaned if cleaned else "N/A",
                'International': formatted if formatted else "N/A",
                'Status': status
            })
        
        return results

class TwilioCaller:
    def __init__(self, account_sid, auth_token, from_number):
        try:
            self.client = Client(account_sid, auth_token)
            self.from_number = from_number
            self.is_configured = True
        except Exception as e:
            self.is_configured = False
            self.error = str(e)
    
    def make_call(self, to_number, message="Hello, this is a test call from your Twilio application."):
        """Make an outbound call"""
        if not self.is_configured:
            return False, "Twilio not configured properly"
        
        try:
            call = self.client.calls.create(
                twiml=f'<Response><Say>{message}</Say></Response>',
                to=to_number,
                from_=self.from_number
            )
            return True, f"Call initiated successfully. SID: {call.sid}"
        except TwilioException as e:
            return False, f"Twilio error: {str(e)}"
        except Exception as e:
            return False, f"Error: {str(e)}"

# Main App
def main():
    st.markdown('<h1 class="main-header">📞 Japanese Phone Caller Pro</h1>', unsafe_allow_html=True)
    
    # Sidebar for Twilio configuration
    with st.sidebar:
        st.header("🔧 Twilio Configuration")
        account_sid = st.text_input("Account SID", type="password", help="Your Twilio Account SID")
        auth_token = st.text_input("Auth Token", type="password", help="Your Twilio Auth Token")
        from_number = st.text_input("From Number", placeholder="+1234567890", help="Your Twilio phone number")
        
        st.header("📋 Call Settings")
        custom_message = st.text_area(
            "Call Message", 
            value="Hello, this is a test call from your application.",
            help="Message that will be spoken during the call"
        )
        
        if account_sid and auth_token and from_number:
            twilio_caller = TwilioCaller(account_sid, auth_token, from_number)
            if twilio_caller.is_configured:
                st.success("✅ Twilio configured successfully!")
            else:
                st.error(f"❌ Twilio configuration error: {twilio_caller.error}")
        else:
            st.warning("⚠️ Please configure Twilio settings")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📂 Upload Phone Numbers")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose an Excel file",
            type=['xlsx', 'xls'],
            help="Upload an Excel file containing phone numbers"
        )
        
        # Sample data info
        with st.expander("📋 Supported Number Formats"):
            st.markdown("""
            **Japanese Phone Number Formats:**
            - Mobile: `070-1234-5678`, `080-1234-5678`, `090-1234-5678`
            - Landline: `03-1234-5678`, `06-1234-5678`, etc.
            - Numbers can be with or without hyphens
            - Excel may remove leading zeros (e.g., `312345678` → `03-1234-5678`)
            
            **Output Format:** `+81312345678` (international format for Twilio)
            """)
        
        if uploaded_file is not None:
            try:
                # Read Excel file
                df = pd.read_excel(uploaded_file)
                st.success(f"✅ File uploaded successfully! Found {len(df)} rows.")
                
                # Show column selection
                st.subheader("Select Phone Number Column")
                phone_column = st.selectbox("Choose the column containing phone numbers:", df.columns.tolist())
                
                if phone_column:
                    # Process numbers
                    processor = JapanesePhoneProcessor()
                    phone_numbers = df[phone_column].tolist()
                    
                    with st.spinner("Processing phone numbers..."):
                        results = processor.process_numbers(phone_numbers)
                    
                    # Store in session state
                    st.session_state.processed_numbers = results
                    
                    # Display results
                    st.subheader("📊 Processing Results")
                    results_df = pd.DataFrame(results)
                    
                    # Metrics
                    valid_count = len([r for r in results if r['Status'] == "✅ Valid"])
                    invalid_count = len([r for r in results if r['Status'] == "❌ Invalid"])
                    
                    col_m1, col_m2, col_m3 = st.columns(3)
                    with col_m1:
                        st.metric("Total Numbers", len(results))
                    with col_m2:
                        st.metric("Valid Numbers", valid_count)
                    with col_m3:
                        st.metric("Invalid Numbers", invalid_count)
                    
                    # Results table
                    st.dataframe(results_df, use_container_width=True)
                    
                    # Download processed data
                    csv = results_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Processed Numbers (CSV)",
                        data=csv,
                        file_name=f"processed_numbers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            
            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")
    
    with col2:
        st.header("📞 Make Calls")
        
        if st.session_state.processed_numbers:
            valid_numbers = [r for r in st.session_state.processed_numbers if r['Status'] == "✅ Valid"]
            
            if valid_numbers and account_sid and auth_token and from_number:
                twilio_caller = TwilioCaller(account_sid, auth_token, from_number)
                
                if twilio_caller.is_configured:
                    st.success(f"📋 {len(valid_numbers)} valid numbers ready for calling")
                    
                    # Call options
                    call_option = st.radio(
                        "Call Option:",
                        ["Single Call", "Bulk Call (All Numbers)"]
                    )
                    
                    if call_option == "Single Call":
                        # Single call interface
                        selected_number_data = st.selectbox(
                            "Select number to call:",
                            valid_numbers,
                            format_func=lambda x: f"{x['International']} (Original: {x['Original']})"
                        )
                        
                        if st.button("📞 Make Call", type="primary"):
                            with st.spinner("Making call..."):
                                success, message = twilio_caller.make_call(
                                    selected_number_data['International'],
                                    custom_message
                                )
                            
                            if success:
                                st.success(f"✅ {message}")
                                # Add to call history
                                st.session_state.call_history.append({
                                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                    'number': selected_number_data['International'],
                                    'status': 'Success',
                                    'message': message
                                })
                            else:
                                st.error(f"❌ {message}")
                                st.session_state.call_history.append({
                                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                    'number': selected_number_data['International'],
                                    'status': 'Failed',
                                    'message': message
                                })
                    
                    else:
                        # Bulk call interface
                        st.warning(f"⚠️ This will make {len(valid_numbers)} calls. Please ensure you have sufficient Twilio credits.")
                        
                        delay_seconds = st.slider("Delay between calls (seconds):", 1, 10, 3)
                        
                        if st.button("📞 Start Bulk Calling", type="primary"):
                            progress_bar = st.progress(0)
                            status_placeholder = st.empty()
                            
                            for i, number_data in enumerate(valid_numbers):
                                status_placeholder.text(f"Calling {number_data['International']}...")
                                
                                success, message = twilio_caller.make_call(
                                    number_data['International'],
                                    custom_message
                                )
                                
                                # Update call history
                                st.session_state.call_history.append({
                                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                    'number': number_data['International'],
                                    'status': 'Success' if success else 'Failed',
                                    'message': message
                                })
                                
                                # Update progress
                                progress_bar.progress((i + 1) / len(valid_numbers))
                                
                                # Delay between calls
                                if i < len(valid_numbers) - 1:
                                    time.sleep(delay_seconds)
                            
                            status_placeholder.success("✅ Bulk calling completed!")
                
                else:
                    st.error("❌ Twilio configuration error")
            else:
                if not valid_numbers:
                    st.info("📋 No valid numbers to call. Please upload and process phone numbers first.")
                else:
                    st.warning("⚠️ Please configure Twilio settings in the sidebar.")
        else:
            st.info("📋 Upload and process phone numbers to start making calls.")
    
    # Call History
    if st.session_state.call_history:
        st.header("📋 Call History")
        history_df = pd.DataFrame(st.session_state.call_history)
        st.dataframe(history_df, use_container_width=True)
        
        # Download call history
        history_csv = history_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Call History (CSV)",
            data=history_csv,
            file_name=f"call_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
        # Clear history button
        if st.button("🗑️ Clear Call History"):
            st.session_state.call_history = []
            st.rerun()

if __name__ == "__main__":
    main()
