import streamlit as st
import pandas as pd
import re
import time
from datetime import datetime
from twilio.rest import Client
from twilio.base.exceptions import TwilioException

# ページ設定
st.set_page_config(
    page_title="東京山王法律事務所 - コールシステム",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# アクセシブルなライトテーマ（日本語UI＋Browse files＋metric修正込み）
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

/* ファイル選択ボタン（Browse files）を明るく */
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

/* ====== ここから metric の白文字問題の修正 ====== */
[data-testid="metric-container"]{
  background:var(--bg)!important;
  color:var(--text)!important;
}
[data-testid="metric-container"] *{color:var(--text)!important;}
[data-testid="stMetricValue"],[data-testid="stMetricLabel"]{color:var(--text)!important;}
[data-testid="stMetricDelta"] *,[data-testid="stMetricDeltaIcon-Up"],[data-testid="stMetricDeltaIcon-Down"]{
  color:var(--text)!important; fill:var(--text)!important;
}
</style>
""", unsafe_allow_html=True)

# セッションステート初期化
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
if 'voicemail_sids' not in st.session_state:
    st.session_state.voicemail_sids = {}  # contact_id -> voicemail call SID

# クラス
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

    # メイン通話用（相手が出たらオペレーターへ橋渡し）
    def twiml_for_call(self):
        return f"""
<Response>
  <Dial timeout="30" record="record-from-answer">
    <Number>{self.operator_number}</Number>
  </Dial>
</Response>
""".strip()

    # 留守電通話用（相手が出たらメッセージを流す）
    def twiml_for_voicemail(self, voicemail_text: str, max_seconds: int = 60, do_record: bool = False):
        # do_record=True にするとメッセージの後に相手の留守電へ録音指示も可能
        record_tag = f'<Record maxLength="{max_seconds}" playBeep="true" />' if do_record else ''
        return f"""
<Response>
  <Pause length="1"/>
  <Say language="en-US">{voicemail_text}</Say>
  {record_tag}
  <Hangup/>
</Response>
""".strip()

    def make_call(self, to_number, person_name=""):
        if not self.is_configured:
            return False, "Twilioの設定が見つかりません", None
        try:
            call = self.client.calls.create(
                twiml=self.twiml_for_call(),
                to=to_number,
                from_=self.from_number
            )
            return True, f"{person_name} へ発信を開始しました", call.sid
        except TwilioException as e:
            return False, f"Twilioエラー: {str(e)}", None
        except Exception as e:
            return False, f"エラー: {str(e)}", None

    def make_voicemail_call(self, to_number, voicemail_text: str, max_seconds: int = 60):
        """
        留守電用に、相手へ自動メッセージ通話を発信
        AMD（Answering Machine Detection）を有効化して、ボイスメールに繋がった場合でも再生確度を上げる
        """
        if not self.is_configured:
            return False, "Twilioの設定が見つかりません", None
        try:
            call = self.client.calls.create(
                twiml=self.twiml_for_voicemail(voicemail_text, max_seconds=max_seconds, do_record=False),
                to=to_number,
                from_=self.from_number,
                machine_detection='Enable'  # AMD を有効化（Twilio側のプラン要件に依存）
                # amd_status_callback=...  # 必要ならコールバックURLを設定
            )
            return True, "留守電メッセージの送信を開始しました", call.sid
        except TwilioException as e:
            return False, f"Twilioエラー(留守電): {str(e)}", None
        except Exception as e:
            return False, f"エラー(留守電): {str(e)}", None

    def poll_status(self, sid):
        try:
            call = self.client.calls(sid).fetch()
            return True, call.status
        except Exception as e:
            return False, str(e)

# ヘルパー
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
        "completed": ("✅", "完了", "status-completed"),
        "failed": ("❌", "失敗", "status-failed"),
        "no-answer": ("❌", "不在", "status-failed"),
        "busy": ("❌", "話し中", "status-failed"),
        "canceled": ("❌", "キャンセル", "status-failed"),
    }
    return status_map.get(status, ("⏳", status, "status-waiting"))

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

def poll_call_until_complete(twilio_caller, call_sid, contact, delay_between_calls,
                             enable_voicemail: bool, voicemail_text: str, vm_max_seconds: int):
    terminal_statuses = {'completed', 'failed', 'busy', 'no-answer', 'canceled'}
    status_display = st.empty()
    current_status = "queued"

    # ---- 1st call status loop ----
    while True:
        ok, status = twilio_caller.poll_status(call_sid)
        if not ok:
            current_status = 'failed'
            status_display.error(f"❌ ステータスの取得に失敗: {status}")
            break

        current_status = status or 'unknown'
        st.session_state.contact_statuses[st.session_state.current_calling_id] = current_status

        icon, status_text, _ = get_status_display(current_status)
        status_display.info(f"{icon} {contact['name']}：{status_text}")

        if current_status in terminal_statuses:
            break
        time.sleep(3)

    human_status = current_status.replace('-', ' ').title()
    if current_status == 'completed':
        status_display.success(f"✅ {contact['name']}：通話完了")
        log_status = "完了"
    else:
        status_display.error(f"❌ {contact['name']}：{human_status}")
        log_status = human_status

    # ---- Voicemail trigger on non-completed ----
    vm_sid = None
    vm_outcome = None
    if enable_voicemail and current_status in {'no-answer', 'busy', 'failed', 'canceled'}:
        st.info("📩 不在のため、留守電メッセージを送信します…")
        vm_ok, vm_msg, vm_sid = twilio_caller.make_voicemail_call(
            contact['international'],
            voicemail_text=voicemail_text,
            max_seconds=vm_max_seconds
        )
        if vm_ok:
            st.session_state.voicemail_sids[contact['id']] = vm_sid
            # poll voicemail call quickly (optional)
            vm_terminal = {'completed', 'failed', 'busy', 'no-answer', 'canceled'}
            while True:
                ok2, st2 = twilio_caller.poll_status(vm_sid)
                if not ok2:
                    vm_outcome = f"留守電ステータス取得失敗: {st2}"
                    st.warning(f"⚠️ {vm_outcome}")
                    break
                if st2 in vm_terminal:
                    vm_outcome = f"留守電送信結果: {st2}"
                    if st2 == 'completed':
                        st.success("✅ 留守電メッセージの再生が完了しました")
                    else:
                        st.warning(f"⚠️ {vm_outcome}")
                    break
                time.sleep(3)
        else:
            vm_outcome = vm_msg
            st.error(f"❌ 留守電の送信に失敗: {vm_msg}")

    # ---- log ----
    details = [f"Call SID: {call_sid}"]
    if vm_sid:
        details.append(f"Voicemail SID: {vm_sid}")
    if vm_outcome:
        details.append(vm_outcome)

    st.session_state.call_history.append({
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'name': contact['name'],
        'number': contact['international'],
        'status': "完了" if current_status == 'completed' else human_status,
        'details': " | ".join(details)
    })

    # dequeue and proceed
    if st.session_state.call_queue and st.session_state.call_queue[0] == st.session_state.current_calling_id:
        st.session_state.call_queue.pop(0)

    st.session_state.current_calling_id = None

    if not st.session_state.call_queue:
        st.session_state.calling_in_progress = False
        st.success("🎉 全ての発信が完了しました")
        st.rerun()
    else:
        time.sleep(delay_between_calls)
        st.rerun()

# メインアプリ
def main():
    st.markdown("""
    <div class="custom-header">
        <div>
            <h1>📞 東京山王法律事務所</h1>
            <p>ダイレクト接続コールシステム</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # サイドバー
    with st.sidebar:
        st.markdown("### ⚙️ 設定")

        operator_number = st.text_input(
            "オペレーター番号（接続先）",
            value="+815017420037",
            help="通話を転送するオペレーターの電話番号（E.164形式）"
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
                st.success("✅ Twilio 接続済み")
                st.info(f"📱 発信元: {from_number}")
                st.info(f"👤 転送先（オペレーター）: {operator_number}")
            else:
                st.error("❌ Twilio 設定エラー")
                twilio_caller = None
        except Exception:
            st.error("❌ 設定の読み込みに失敗しました")
            twilio_caller = None

        st.markdown("---")
        call_delay = st.slider("通話間隔（秒）", 1, 30, 5)

        # ===== Voicemail Settings =====
        st.markdown("---")
        st.markdown("### 📩 留守電設定")
        enable_voicemail = st.checkbox("不在時に留守電メッセージを自動送信する", value=True)
        voicemail_text = st.text_area(
            "留守電メッセージ（読み上げ）",
            value="Hello, this is voicemail.",
            help="相手が出なかった場合に自動で再生されるメッセージです。"
        )
        vm_max_seconds = st.number_input(
            "留守電の最大長（秒）",
            min_value=5, max_value=180, value=60, step=5,
            help="録音を有効にした場合の最大長。現状は読み上げのみ。"
        )

        st.markdown("---")
        st.caption("💡 アップロード → 選択 → 発信")

    # ステップ1：連絡先アップロード
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

    # ステップ2：選択と発信
    if st.session_state.processed_numbers:
        valid_contacts = [c for c in st.session_state.processed_numbers if c['status'] == 'valid']

        if valid_contacts:
            with st.expander("📞 ステップ2：選択して発信", expanded=True):
                total = len(valid_contacts)
                selected = len(st.session_state.selected_contacts)
                completed = sum(1 for c in valid_contacts if st.session_state.contact_statuses.get(c['id']) == 'completed')
                failed = sum(1 for c in valid_contacts if st.session_state.contact_statuses.get(c['id']) in ('failed', 'no-answer', 'busy', 'canceled'))
                calling = 1 if st.session_state.calling_in_progress else 0

                m1, m2, m3, m4, m5 = st.columns(5)
                m1.metric("📋 総件数", total)
                m2.metric("🔵 選択中", selected)
                m3.metric("📞 発信中", calling)
                m4.metric("✅ 完了", completed)
                m5.metric("❌ 失敗", failed)

                if st.session_state.current_calling_id is not None:
                    current_contact = next((c for c in valid_contacts if c['id'] == st.session_state.current_calling_id), None)
                    if current_contact:
                        current_status = st.session_state.contact_statuses.get(current_contact['id'], 'calling')
                        icon, status_text, _ = get_status_display(current_status)
                        st.markdown(f"""
                        <div class="current-call-banner">
                            <span>{icon} 現在の通話：{current_contact['name']} - {status_text}</span>
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown("---")

                b1, b2, b3, b4 = st.columns(4)

                # ✅ すべて選択
                with b1:
                    if st.button("✅ すべて選択", use_container_width=True, disabled=st.session_state.calling_in_progress):
                        st.session_state.selected_contacts = set(c['id'] for c in valid_contacts)
                        for c in valid_contacts:
                            st.session_state[f"select_{c['id']}"] = True
                        st.rerun()

                # ❌ 選択を全解除
                with b2:
                    if st.button("❌ 選択を全解除", use_container_width=True, disabled=st.session_state.calling_in_progress):
                        st.session_state.selected_contacts.clear()
                        for c in valid_contacts:
                            st.session_state[f"select_{c['id']}"] = False
                        st.rerun()

                # 📞 発信開始
                with b3:
                    can_start = (selected > 0 and not st.session_state.calling_in_progress and 'twilio_caller' in locals() and twilio_caller)
                    if st.button("📞 発信開始", type="primary", use_container_width=True, disabled=not can_start):
                        st.session_state.call_queue = [c['id'] for c in valid_contacts if c['id'] in st.session_state.selected_contacts]
                        st.session_state.calling_in_progress = True
                        st.rerun()

                # 🔄 全てリセット
                with b4:
                    if st.button("🔄 全てリセット", use_container_width=True, disabled=st.session_state.calling_in_progress):
                        st.session_state.selected_contacts.clear()
                        st.session_state.call_queue = []
                        st.session_state.contact_statuses = {c['id']: 'waiting' for c in valid_contacts}
                        st.session_state.call_history = []
                        st.session_state.calling_in_progress = False
                        st.session_state.current_calling_id = None
                        for c in valid_contacts:
                            st.session_state[f"select_{c['id']}"] = False
                        st.rerun()

                if st.session_state.calling_in_progress and st.session_state.call_queue:
                    total_to_call = len([c for c in valid_contacts if c['id'] in st.session_state.selected_contacts])
                    remaining = len(st.session_state.call_queue)
                    progress = (total_to_call - remaining) / total_to_call if total_to_call else 0

                    st.markdown(f"""
                    <div class="progress-container">
                        <div class="progress-bar" style="width: {progress * 100}%"></div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.info(f"📊 進捗：{total_to_call - remaining} / {total_to_call}")

            # 連絡先リスト
            with st.expander("👥 連絡先リスト", expanded=True):
                for contact in valid_contacts:
                    is_selected = contact['id'] in st.session_state.selected_contacts
                    status = st.session_state.contact_statuses.get(contact['id'], 'waiting')
                    render_contact_card(contact, is_selected, status)

            # 発信フロー
            if (st.session_state.calling_in_progress and
                st.session_state.call_queue and
                st.session_state.current_calling_id is None):

                next_id = st.session_state.call_queue[0]
                current_contact = next((c for c in valid_contacts if c['id'] == next_id), None)

                if current_contact and 'twilio_caller' in locals() and twilio_caller:
                    st.session_state.contact_statuses[next_id] = 'ringing'
                    st.session_state.current_calling_id = next_id

                    success, message, sid = twilio_caller.make_call(
                        current_contact['international'],
                        current_contact['name']
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
                        st.success(f"✅ {current_contact['name']} へ発信中…")
                        poll_call_until_complete(
                            twilio_caller, sid, current_contact, call_delay,
                            enable_voicemail=enable_voicemail,
                            voicemail_text=voicemail_text.strip() or "Hello, this is voicemail.",
                            vm_max_seconds=int(vm_max_seconds)
                        )

    # 通話履歴
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
