import streamlit as st
import pandas as pd
import re
import time
from datetime import datetime
from twilio.rest import Client
from twilio.base.exceptions import TwilioException

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="東京山王法律事務所 - コールシステム",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# CSS (UNCHANGED)
# =========================
st.markdown("""
<style>
:root {
  --bg: #ffffff;
  --bg-soft: #f8f9fa;
  --bg-muted: #f3f4f6;
  --text: #1a1a1a;
  --text-muted: #6b7280;
  --primary: #3b82f6;
  --primary-600: #2563eb;
  --success: #10b981;
  --warning: #f59e0b;
  --danger: #ef4444;
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.1);
  --shadow-md: 0 4px 12px rgba(0,0,0,0.12);
}

.stApp,[data-testid="stAppViewContainer"],[data-testid="stHeader"],[data-testid="stSidebar"]{
  background-color:var(--bg)!important;color:var(--text)!important;
}

[data-testid="stSidebar"]{background-color:var(--bg-soft)!important;}
[data-testid="stSidebar"] *{color:var(--text)!important;}

#MainMenu, footer {display:none;}
header{visibility:hidden;}

.custom-header{
  background:linear-gradient(135deg,#1e40af 0%,#3b82f6 50%,#60a5fa 100%);
  padding:2.25rem;margin:-1rem -1rem 1.5rem -1rem;border-radius:0 0 20px 20px;
  text-align:center;box-shadow:var(--shadow-md);
}
.custom-header *{color:#ffffff!important;}
.custom-header h1{font-size:2.25rem;font-weight:700;margin:0;text-shadow:0 2px 4px rgba(0,0,0,0.1);}
.custom-header p{margin:.5rem 0 0 0;opacity:.95;}

.upload-section{
  background:linear-gradient(135deg,#dbeafe 0%,#e0e7ff 100%);
  border:2px dashed var(--primary);border-radius:12px;padding:1.25rem;text-align:center;margin:.75rem 0;
  box-shadow:var(--shadow-sm);
}
.upload-section h4{color:#1e40af;margin:0 0 .25rem 0;font-weight:700;}

.contact-card{
  background:var(--bg);border-radius:12px;padding:1rem;border:2px solid #e5e7eb;margin-bottom:.6rem;
  display:flex;align-items:center;gap:1rem;transition:transform .2s ease,border-color .2s ease,box-shadow .2s ease;
  box-shadow:var(--shadow-sm);
}
.contact-card:hover{border-color:var(--primary);transform:translateX(2px);box-shadow:0 4px 12px rgba(59,130,246,0.18);}
.contact-avatar{
  width:50px;height:50px;border-radius:50%;
  background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
  display:flex;align-items:center;justify-content:center;color:#ffffff;font-weight:700;font-size:18px;flex-shrink:0;
}
.contact-name{font-weight:700;color:var(--text);margin-bottom:4px;font-size:1.05rem;}
.contact-phone{color:var(--text-muted);font-variant-numeric:tabular-nums;}

.contact-status{
  display:flex;align-items:center;gap:8px;padding:8px 12px;border-radius:20px;background:var(--bg-muted);
  font-weight:600;color:var(--text);margin-left:auto;
}
.status-dot{width:10px;height:10px;border-radius:50%;}
.status-waiting{background:#9ca3af;}
.status-ringing{background:var(--warning);animation:pulse 1.5s infinite;}
.status-connected{background:var(--primary);animation:pulse 1.5s infinite;}
.status-completed{background:var(--success);}
.status-failed{background:var(--danger);}

.contact-selected{border-color:var(--primary);background:rgba(59,130,246,0.06);}
.contact-calling{border-color:var(--warning);background:rgba(245,158,11,0.06);}
.contact-completed{border-color:var(--success);background:rgba(16,185,129,0.06);}
.contact-failed{border-color:var(--danger);background:rgba(239,68,68,0.06);}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.7;transform:scale(1.05)}}

.progress-container{background:#e5e7eb;border-radius:10px;height:12px;overflow:hidden;margin:.8rem 0;}
.progress-bar{height:100%;background:linear-gradient(90deg,var(--primary) 0%,#1d4ed8 100%);border-radius:10px;transition:width .3s ease;}

.current-call-banner{
  background:linear-gradient(135deg,#f59e0b 0%,#f97316 100%);
  color:#ffffff;padding:.9rem 1.2rem;border-radius:12px;margin:.75rem 0;font-size:1.05rem;font-weight:700;text-align:center;
  box-shadow:0 4px 12px rgba(245,158,11,0.3);
}
.current-call-banner *{color:#ffffff!important;}

.stButton>button{
  border-radius:10px!important;font-weight:700!important;
  transition:transform .15s ease,box-shadow .2s ease,border-color .2s ease!important;
  background-color:var(--bg)!important;border:2px solid #e5e7eb!important;color:var(--text)!important;box-shadow:var(--shadow-sm)!important;
}
.stButton>button:hover{transform:translateY(-1px)!important;box-shadow:var(--shadow-md)!important;border-color:var(--primary)!important;}
.stButton>button[kind="primary"]{background-color:var(--primary)!important;border-color:var(--primary)!important;color:#ffffff!important;}

input,textarea,select,.stTextInput input,.stNumberInput input{
  background-color:var(--bg)!important;color:var(--text)!important;border:1px solid #d1d5db!important;border-radius:8px!important;
}
.stSlider,.stRadio,.stCheckbox,label{color:var(--text)!important;}

[data-testid="stExpander"]{background-color:var(--bg)!important;border:2px solid #e5e7eb!important;border-radius:10px!important;}
[data-testid="stExpander"] summary{background-color:var(--bg-soft)!important;color:var(--text)!important;font-weight:700!important;padding:.9rem!important;}

.stInfo,.stSuccess,.stWarning,.stError{background-color:var(--bg-soft)!important;color:var(--text)!important;border-radius:10px!important;}
.stInfo *,.stSuccess *,.stWarning *,.stError *{color:var(--text)!important;}

[data-testid="stDataFrame"] *{color:var(--text)!important;}
div[data-testid="stDataFrame"] table{background:var(--bg)!important;}
div[data-testid="stDataFrame"] thead tr th{background:var(--bg-muted)!important;color:var(--text)!important;font-weight:700!important;}

[data-testid="stDownloadButton"] button{
  background-color:var(--primary)!important;color:#ffffff!important;border-radius:10px!important;font-weight:700!important;
}

.stFileUploader > div > button,
[data-testid="stFileUploader"] button{
  background-color:var(--primary)!important;color:#ffffff!important;border:2px solid var(--primary)!important;border-radius:10px!important;
  font-weight:700!important;box-shadow:var(--shadow-sm)!important;
}
.stFileUploader > div > button:hover,
[data-testid="stFileUploader"] button:hover{background-color:var(--primary-600)!important;border-color:var(--primary-600)!important;transform:translateY(-1px);box-shadow:var(--shadow-md)!important;}
.stFileUploader > div > button:focus,
[data-testid="stFileUploader"] button:focus{outline:none!important;box-shadow:0 0 0 3px rgba(59,130,246,.35)!important;}
.stFileUploader > div > button:disabled,
[data-testid="stFileUploader"] button:disabled{background-color:#9ca3af!important;border-color:#9ca3af!important;color:#ffffff!important;box-shadow:none!important;transform:none!important;}
[data-testid="stFileUploader"] label,[data-testid="stFileUploader"] span,[data-testid="stFileUploader"] p{color:var(--text)!important;}
[data-testid="stFileUploader"]{background-color:var(--bg)!important;}
[data-testid="stFileUploader"] label,
[data-testid="stFileUploader"] span,
[data-testid="stFileUploader"] p,
[data-testid="stFileUploaderDropzone"] * {
  color: #ffffff !important;
}

[data-testid="metric-container"]{background:var(--bg)!important;color:var(--text)!important;}
[data-testid="metric-container"] *{color:var(--text)!important;}
[data-testid="stMetricValue"],[data-testid="stMetricLabel"]{color:var(--text)!important;}
[data-testid="stMetricDelta"] *,[data-testid="stMetricDeltaIcon-Up"],[data-testid="stMetricDeltaIcon-Down"]{color:var(--text)!important; fill:var(--text)!important;}
</style>
""", unsafe_allow_html=True)

# =========================
# SESSION STATE INIT
# =========================
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
if 'paused' not in st.session_state:
    st.session_state.paused = False
if 'pause_snapshot_csv' not in st.session_state:
    st.session_state.pause_snapshot_csv = None

# =========================
# PHONE PROCESSOR (UNCHANGED)
# =========================
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
                name = str(row.get('Name', row.get('name', f'担当者 {idx+1}')))
                number = row.get('Phone_Number', row.get('phone_number', row.get('phone', '')))
            else:
                name = str(row[0]) if len(row) > 0 else f'担当者 {idx+1}'
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

# =========================
# TWILIO STUDIO CALLER (UPDATED)
# =========================
class TwilioStudioCaller:
    """
    Triggers a Twilio Studio Flow execution (REST API trigger),
    then polls Execution Context to surface CallStatus / CallSid.
    """
    def __init__(self, account_sid, auth_token, from_number, operator_number, flow_sid: str):
        try:
            self.client = Client(account_sid, auth_token)
            self.account_sid = account_sid
            self.from_number = from_number
            self.operator_number = operator_number
            self.flow_sid = flow_sid
            self.is_configured = True
        except Exception as e:
            self.is_configured = False
            self.error = str(e)

    def start_execution(self, to_number: str, person_name: str, voicemail_text: str, enable_voicemail: bool):
        """
        Start Studio Flow via Executions API.
        - To/From are required and become {{contact.channel.address}} and {{flow.channel.address}}.
        - parameters become {{flow.data.*}}.
        """
        if not self.is_configured:
            return False, "Twilioの設定が見つかりません", None

        try:
            params = {
                "operator_number": self.operator_number,
                "contact_name": person_name or "",
                "enable_voicemail": bool(enable_voicemail),
                "voicemail_text": (voicemail_text or "").strip(),
            }

            execution = self.client.studio.v2.flows(self.flow_sid).executions.create(
                to=to_number,
                from_=self.from_number,
                parameters=params
            )
            return True, f"{person_name} へ発信（Studio Flow）を開始しました", execution.sid

        except TwilioException as e:
            return False, f"Twilioエラー: {str(e)}", None
        except Exception as e:
            return False, f"エラー: {str(e)}", None

    @staticmethod
    def _walk_find_call_widget(context_obj, expected_to: str):
        """
        Recursively find dicts containing CallSid/CallStatus, prefer the one whose 'To' matches expected_to.
        """
        candidates = []

        def walk(o):
            if isinstance(o, dict):
                # candidate if it looks like a Make Outgoing Call widget data block
                call_sid = o.get("CallSid") or o.get("call_sid")
                call_status = o.get("CallStatus") or o.get("call_status")
                if call_sid and str(call_sid).startswith("CA"):
                    candidates.append(o)
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)

        walk(context_obj)

        if not candidates:
            return None

        # Prefer candidate whose "To" equals expected_to
        for c in candidates:
            to_val = c.get("To") or c.get("to")
            if to_val and expected_to and str(to_val).strip() == expected_to.strip():
                return c

        return candidates[0]

    def poll_status(self, execution_sid: str, expected_to: str):
        """
        Returns (ok, call_status, call_sid, answered_by, execution_status)
        """
        try:
            exec_obj = self.client.studio.v2.flows(self.flow_sid).executions(execution_sid).fetch()
            execution_status = getattr(exec_obj, "status", None)  # usually 'active' or 'ended'

            ctx_obj = self.client.studio.v2.flows(self.flow_sid).executions(execution_sid).execution_context().fetch()
            ctx = getattr(ctx_obj, "context", None) or {}

            widget_block = self._walk_find_call_widget(ctx, expected_to=expected_to)
            if widget_block:
                call_sid = widget_block.get("CallSid") or widget_block.get("call_sid")
                call_status = widget_block.get("CallStatus") or widget_block.get("call_status")
                answered_by = widget_block.get("AnsweredBy") or widget_block.get("answered_by")
                return True, (call_status or "unknown"), call_sid, answered_by, (execution_status or "unknown")

            # If we can't see CallStatus yet, fallback to execution status
            return True, "queued" if execution_status == "active" else (execution_status or "unknown"), None, None, (execution_status or "unknown")

        except Exception as e:
            return False, str(e), None, None, None

# =========================
# HELPERS (UNCHANGED)
# =========================
def get_initials(name):
    words = name.split()
    if len(words) >= 2:
        return words[0][0].upper() + words[1][0].upper()
    if len(words) == 1:
        return words[0][:2].upper()
    return "??"

def get_status_display(status):
    status_map = {
        "waiting": ("⏳", "待機中", "status-waiting"),
        "queued": ("⏳", "キュー", "status-waiting"),
        "ringing": ("📳", "呼び出し中", "status-ringing"),
        "in-progress": ("📞", "通話中", "status-connected"),
        "active": ("📞", "実行中", "status-connected"),
        "completed": ("✅", "完了", "status-completed"),
        "ended": ("✅", "終了", "status-completed"),
        "failed": ("❌", "失敗", "status-failed"),
        "no-answer": ("❌", "不在", "status-failed"),
        "busy": ("❌", "話し中", "status-failed"),
        "canceled": ("❌", "キャンセル", "status-failed"),
        "unknown": ("⏳", "不明", "status-waiting"),
    }
    return status_map.get(status, ("⏳", status, "status-waiting"))

def render_contact_card(contact, is_selected, contact_status):
    icon, status_text, status_class = get_status_display(contact_status)
    initials = get_initials(contact['name'])

    card_class = "contact-card"
    if contact_status in ("ringing", "queued", "in-progress", "active"):
        card_class += " contact-calling"
    elif contact_status in ("completed", "ended"):
        card_class += " contact-completed"
    elif contact_status in ("failed", "no-answer", "busy", "canceled"):
        card_class += " contact-failed"
    elif is_selected:
        card_class += " contact-selected"

    col1, col2 = st.columns([0.08, 0.92])

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
        st.markdown(
            f"""
            <div class="{card_class}">
                <div class="contact-avatar">{initials}</div>
                <div class="contact-info">
                    <div class="contact-name">{contact['name']}</div>
                    <div class="contact-phone">{contact['international']}</div>
                </div>
                <div class="contact-status">
                    <div class="status-dot {status_class}"></div>
                    <span>{status_text}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

def _make_pause_snapshot_csv():
    if not st.session_state.call_history:
        return None
    df = pd.DataFrame(st.session_state.call_history)
    return df.to_csv(index=False).encode('utf-8')

def poll_call_until_complete(twilio_caller: TwilioStudioCaller, execution_sid, contact, delay_between_calls):
    """
    Poll Studio Execution Context until the call finishes.
    We map widget CallStatus (completed/failed/no-answer/busy/etc.) to the UI.
    """
    terminal_statuses = {'completed', 'failed', 'busy', 'no-answer', 'canceled', 'ended'}
    status_display = st.empty()
    current_status = "queued"

    call_sid = None
    answered_by = None

    while True:
        ok, status_or_err, csid, ab, exec_status = twilio_caller.poll_status(execution_sid, expected_to=contact['international'])
        if not ok:
            current_status = 'failed'
            status_display.error(f"❌ ステータスの取得に失敗: {status_or_err}")
            break

        current_status = status_or_err or 'unknown'
        call_sid = csid or call_sid
        answered_by = ab or answered_by

        st.session_state.contact_statuses[st.session_state.current_calling_id] = current_status

        icon, status_text, _ = get_status_display(current_status)
        extra = f"（AnsweredBy={answered_by}）" if answered_by else ""
        status_display.info(f"{icon} {contact['name']}：{status_text} {extra}")

        if current_status in terminal_statuses:
            break

        # If execution ended but we didn't see a final call status yet
        if exec_status == "ended":
            break

        time.sleep(3)

    human_status = str(current_status).replace('-', ' ').title()
    if current_status in ('completed', 'ended'):
        status_display.success(f"✅ {contact['name']}：完了（Studio Flow）")
        log_status = "完了"
    else:
        status_display.error(f"❌ {contact['name']}：{human_status}")
        log_status = human_status

    st.session_state.call_history.append({
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'name': contact['name'],
        'number': contact['international'],
        'status': log_status,
        'details': f"Execution SID: {execution_sid} | Call SID: {call_sid or 'N/A'} | AnsweredBy: {answered_by or 'N/A'}"
    })

    if st.session_state.call_queue and st.session_state.call_queue[0] == st.session_state.current_calling_id:
        st.session_state.call_queue.pop(0)

    st.session_state.current_calling_id = None

    if st.session_state.paused:
        st.info("⏸️ 一時停止中：次の発信は停止しています（再開を押すまで進みません）")
        st.session_state.pause_snapshot_csv = _make_pause_snapshot_csv()
        st.stop()

    if not st.session_state.call_queue:
        st.session_state.calling_in_progress = False
        st.success("🎉 全ての発信が完了しました")
        st.rerun()
    else:
        time.sleep(delay_between_calls)
        st.rerun()

# =========================
# MAIN APP (UNCHANGED except caller)
# =========================
def main():
    st.markdown("""
    <div class="custom-header">
        <div>
            <h1>📞 東京山王法律事務所</h1>
            <p>ダイレクト接続コールシステム</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    DEFAULT_FLOW_SID = "FW124b086acf26790e8ea4a7ed661362d5"

    with st.sidebar:
        st.markdown("### ⚙️ 設定")

        operator_number = st.text_input(
            "オペレーター番号（接続先）",
            value="+815017420037",
            help="通話を転送するオペレーターの電話番号（E.164形式）"
        )

        flow_sid = st.text_input(
            "Studio Flow SID",
            value=DEFAULT_FLOW_SID,
            help="Twilio Studio Flow SID（FW...）"
        )

        twilio_caller = None
        try:
            if "twilio" in st.secrets:
                account_sid = st.secrets["twilio"]["account_sid"]
                auth_token = st.secrets["twilio"]["auth_token"]
                from_number = st.secrets["twilio"]["from_number"]
            else:
                account_sid = st.secrets["account_sid"]
                auth_token = st.secrets["auth_token"]
                from_number = st.secrets["from_number"]

            twilio_caller = TwilioStudioCaller(account_sid, auth_token, from_number, operator_number, flow_sid)

            if twilio_caller.is_configured:
                st.success("✅ Twilio 接続済み")
                st.info(f"📱 発信元: {from_number}")
                st.info(f"👤 転送先: {operator_number}")
                st.info(f"🧩 Flow: {flow_sid}")
            else:
                st.error("❌ Twilio 設定エラー")
                twilio_caller = None
        except Exception as e:
            st.error(f"❌ 設定の読み込みに失敗: {e}")
            twilio_caller = None

        st.markdown("---")
        call_delay = st.slider("通話間隔（秒）", 1, 30, 5)

        st.markdown("---")
        st.markdown("### 📩 留守電設定")
        enable_voicemail = st.checkbox("留守電メッセージを有効にする", value=True)

        voicemail_text = st.text_area(
            "留守電メッセージ（日本語）",
            value="こちらは、弁護士法人はるかと申します。大切なご用件がありますので、折り返し御連絡下さい。宜しくお願い致します。",
            help="Studio Flow側で {{flow.data.voicemail_text}} を使って再生してください。"
        )

        st.markdown("---")
        st.caption("💡 アップロード → 選択 → 発信")

        with st.expander("📖 動作説明"):
            st.markdown("""
            **通話の流れ（Studio）**
            1. Streamlit → Studio Execution を作成
            2. Flow内の Make Outgoing Call (AMD ON) で相手へ発信
            3. AnsweredBy が human の時だけ Connect Call To でオペレーター接続
            4. machine/unknown なら Say/Play で留守電を再生し Flow 終了（通話終了）
            """)

    with st.expander("📂 ステップ1：連絡先リストをアップロード", expanded=True):
        st.markdown("""
        <div class="upload-section">
            <h4>📋 Excelファイルをアップロード</h4>
            <p><strong>Name</strong> と <strong>Phone_Number</strong> の列が必要です</p>
        </div>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader("Excelファイルを選択", type=['xlsx', 'xls'], label_visibility="collapsed")

        if uploaded_file:
            try:
                df = pd.read_excel(uploaded_file)
                st.success(f"✅ {len(df)} 件の連絡先を読み込みました")

                if 'Name' in df.columns and 'Phone_Number' in df.columns:
                    processor = JapanesePhoneProcessor()
                    results = processor.process_numbers_with_names(df.to_dict('records'))
                    st.session_state.processed_numbers = results

                    for c in results:
                        st.session_state.contact_statuses.setdefault(c['id'], 'waiting')

                    valid_count = sum(1 for r in results if r['status'] == 'valid')
                    invalid_count = len(results) - valid_count

                    col1, col2, col3 = st.columns(3)
                    col1.metric("📋 総件数", len(results))
                    col2.metric("✅ 有効", valid_count)
                    col3.metric("❌ 無効", invalid_count)
                else:
                    st.warning("⚠️ 必須列が不足しています：'Name' と 'Phone_Number'")
            except Exception as e:
                st.error(f"❌ ファイル読込エラー: {e}")

    if st.session_state.processed_numbers:
        valid_contacts = [c for c in st.session_state.processed_numbers if c['status'] == 'valid']

        if valid_contacts:
            with st.expander("📞 ステップ2：選択して発信", expanded=True):
                total = len(valid_contacts)
                selected = len(st.session_state.selected_contacts)
                completed = sum(1 for c in valid_contacts if st.session_state.contact_statuses.get(c['id']) in ('completed', 'ended'))
                failed = sum(1 for c in valid_contacts if st.session_state.contact_statuses.get(c['id']) in ('failed', 'no-answer', 'busy', 'canceled'))
                calling = 1 if st.session_state.calling_in_progress and not st.session_state.paused else 0

                m1, m2, m3, m4, m5 = st.columns(5)
                m1.metric("📋 総件数", total)
                m2.metric("🔵 選択中", selected)
                m3.metric("📞 発信中", calling)
                m4.metric("✅ 完了", completed)
                m5.metric("❌ 失敗", failed)

                st.markdown("---")
                b1, b2, b3, b4, b5, b6 = st.columns(6)

                with b1:
                    if st.button("✅ すべて選択", use_container_width=True, disabled=st.session_state.calling_in_progress):
                        st.session_state.selected_contacts = set(c['id'] for c in valid_contacts)
                        for c in valid_contacts:
                            st.session_state[f"select_{c['id']}"] = True
                        st.rerun()

                with b2:
                    if st.button("❌ 選択を全解除", use_container_width=True, disabled=st.session_state.calling_in_progress):
                        st.session_state.selected_contacts.clear()
                        for c in valid_contacts:
                            st.session_state[f"select_{c['id']}"] = False
                        st.rerun()

                with b3:
                    can_start = (selected > 0 and not st.session_state.calling_in_progress and twilio_caller is not None)
                    if st.button("📞 発信開始", type="primary", use_container_width=True, disabled=not can_start):
                        st.session_state.call_queue = [c['id'] for c in valid_contacts if c['id'] in st.session_state.selected_contacts]
                        st.session_state.calling_in_progress = True
                        st.session_state.paused = False
                        st.rerun()

                with b4:
                    if st.button("⏸️ 一時停止", use_container_width=True,
                                 disabled=not st.session_state.calling_in_progress or st.session_state.paused):
                        st.session_state.paused = True
                        st.session_state.pause_snapshot_csv = _make_pause_snapshot_csv()
                        st.rerun()

                with b5:
                    if st.button("▶️ 再開", use_container_width=True,
                                 disabled=not st.session_state.paused or not st.session_state.call_queue):
                        st.session_state.paused = False
                        st.rerun()

                with b6:
                    if st.button("🔄 全てリセット", use_container_width=True, disabled=st.session_state.calling_in_progress):
                        st.session_state.selected_contacts.clear()
                        st.session_state.call_queue = []
                        st.session_state.contact_statuses = {c['id']: 'waiting' for c in valid_contacts}
                        st.session_state.call_history = []
                        st.session_state.calling_in_progress = False
                        st.session_state.current_calling_id = None
                        st.session_state.paused = False
                        st.session_state.pause_snapshot_csv = None
                        for c in valid_contacts:
                            st.session_state[f"select_{c['id']}"] = False
                        st.rerun()

                if st.session_state.paused:
                    total_to_call = len([c for c in valid_contacts if c['id'] in st.session_state.selected_contacts])
                    attempted = 0
                    if st.session_state.call_history:
                        selected_intls = {c['international'] for c in valid_contacts if c['id'] in st.session_state.selected_contacts}
                        attempted = sum(1 for h in st.session_state.call_history if h['number'] in selected_intls)
                    st.warning(f"⏸️ 一時停止中：{attempted} / {total_to_call} 件まで発信済み。再開するには「再開▶️」を押してください。")

                    if st.session_state.pause_snapshot_csv:
                        st.download_button(
                            "📥 停止時点のCSVをダウンロード",
                            st.session_state.pause_snapshot_csv,
                            file_name=f"call_history_paused_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )

                if st.session_state.calling_in_progress and st.session_state.call_queue is not None:
                    total_to_call = len([c for c in valid_contacts if c['id'] in st.session_state.selected_contacts])
                    remaining = len(st.session_state.call_queue)
                    progress = (total_to_call - remaining) / total_to_call if total_to_call else 0
                    st.markdown(f"""
                    <div class="progress-container">
                        <div class="progress-bar" style="width: {progress * 100}%"></div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.info(f"📊 進捗：{total_to_call - remaining} / {total_to_call}")

            with st.expander("👥 連絡先リスト", expanded=True):
                for contact in valid_contacts:
                    is_selected = contact['id'] in st.session_state.selected_contacts
                    status = st.session_state.contact_statuses.get(contact['id'], 'waiting')
                    render_contact_card(contact, is_selected, status)

            # ====== CALLING PROCESS (UPDATED to Studio Execution) ======
            if (st.session_state.calling_in_progress and
                st.session_state.call_queue and
                st.session_state.current_calling_id is None and
                not st.session_state.paused):

                next_id = st.session_state.call_queue[0]
                current_contact = next((c for c in valid_contacts if c['id'] == next_id), None)

                if current_contact and twilio_caller:
                    st.session_state.contact_statuses[next_id] = 'queued'
                    st.session_state.current_calling_id = next_id

                    success, message, execution_sid = twilio_caller.start_execution(
                        to_number=current_contact['international'],
                        person_name=current_contact['name'],
                        voicemail_text=voicemail_text if enable_voicemail else "",
                        enable_voicemail=enable_voicemail
                    )

                    if not success:
                        st.session_state.contact_statuses[next_id] = 'failed'
                        st.error(f"❌ {current_contact['name']}：{message}")

                        st.session_state.call_history.append({
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'name': current_contact['name'],
                            'number': current_contact['international'],
                            'status': '失敗',
                            'details': message
                        })

                        st.session_state.call_queue.pop(0)
                        st.session_state.current_calling_id = None

                        if not st.session_state.call_queue:
                            st.session_state.calling_in_progress = False

                        st.rerun()
                    else:
                        st.success(f"✅ {current_contact['name']} へ発信中…（Studio Flow）")
                        poll_call_until_complete(
                            twilio_caller, execution_sid, current_contact, call_delay
                        )

    if st.session_state.call_history:
        with st.expander("📋 通話履歴・結果", expanded=False):
            history_df = pd.DataFrame(st.session_state.call_history)
            st.dataframe(history_df, use_container_width=True, height=400)

            col1, col2 = st.columns(2)
            with col1:
                csv = history_df.to_csv(index=False)
                st.download_button(
                    "📥 CSVをダウンロード",
                    csv,
                    file_name=f"call_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            with col2:
                if st.button("🗑️ 履歴をクリア", use_container_width=True):
                    st.session_state.call_history = []
                    st.rerun()

if __name__ == "__main__":
    main()
