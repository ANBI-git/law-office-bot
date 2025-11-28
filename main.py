"""
===========================================
留守電テストアプリ（Streamlit版）
===========================================

シンプルな留守電テスト用アプリ
電話をかけて留守電メッセージを残すだけの機能

使い方:
streamlit run test_voicemail_app.py
"""

import streamlit as st
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
import time

st.set_page_config(
    page_title="留守電テスト",
    page_icon="📞",
    layout="centered"
)

st.title("📞 留守電テスト")
st.markdown("---")

# Twilio設定
st.header("1️⃣ Twilio設定")

col1, col2 = st.columns(2)
with col1:
    account_sid = st.text_input("Account SID", type="password")
with col2:
    auth_token = st.text_input("Auth Token", type="password")

from_number = st.text_input("発信元番号（Twilio番号）", value="+815012345678", help="E.164形式")
to_number = st.text_input("発信先番号（テスト用携帯）", value="+819012345678", help="E.164形式")

st.markdown("---")

# 留守電設定
st.header("2️⃣ 留守電メッセージ")

voicemail_text = st.text_area(
    "メッセージ（日本語）",
    value="こちらは、弁護士法人はるかと申します。大切なご用件がありますので、折り返し御連絡下さい。宜しくお願い致します。",
    height=100
)

# 音声設定
st.header("3️⃣ 音声設定")

voice_option = st.radio(
    "音声タイプ",
    options=[
        "Polly.Mizuki（日本語女性・自然）",
        "Polly.Takumi（日本語男性・自然）",
        "基本音声（無料・ロボット風）"
    ],
    index=0
)

# AMD設定
use_amd = st.checkbox("AMD（留守電検出）を使用", value=True, help="留守電のビープ音を待ってからメッセージを再生")

pause_length = st.slider("メッセージ前の待機時間（秒）", 1, 15, 3, help="留守電アナウンス用の待機時間")

st.markdown("---")

# テスト実行
st.header("4️⃣ テスト実行")

if st.button("📞 留守電テストを開始", type="primary", use_container_width=True):
    
    if not account_sid or not auth_token:
        st.error("❌ Account SIDとAuth Tokenを入力してください")
    elif not from_number or not to_number:
        st.error("❌ 電話番号を入力してください")
    else:
        # 音声設定
        if "Polly.Mizuki" in voice_option:
            voice_attr = 'language="ja-JP" voice="Polly.Mizuki"'
        elif "Polly.Takumi" in voice_option:
            voice_attr = 'language="ja-JP" voice="Polly.Takumi"'
        else:
            voice_attr = 'language="ja-JP"'
        
        # TwiML作成
        safe_text = voicemail_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        twiml = f"""
<Response>
  <Pause length="{pause_length}"/>
  <Say {voice_attr}>{safe_text}</Say>
  <Pause length="2"/>
  <Say {voice_attr}>{safe_text}</Say>
  <Hangup/>
</Response>
""".strip()
        
        # TwiML表示
        with st.expander("📄 生成されたTwiML"):
            st.code(twiml, language="xml")
        
        # 発信
        try:
            client = Client(account_sid, auth_token)
            
            call_params = {
                'twiml': twiml,
                'to': to_number,
                'from_': from_number
            }
            
            if use_amd:
                call_params['machine_detection'] = 'DetectMessageEnd'
                call_params['machine_detection_timeout'] = 45
            
            st.info(f"📞 {to_number} に発信中...")
            
            call = client.calls.create(**call_params)
            
            st.success(f"✅ 発信成功！")
            st.code(f"Call SID: {call.sid}")
            
            # ステータス監視
            st.markdown("### 📊 通話ステータス")
            status_container = st.empty()
            progress_bar = st.progress(0)
            
            terminal_statuses = {'completed', 'failed', 'busy', 'no-answer', 'canceled'}
            
            step = 0
            while step < 30:  # 最大90秒監視
                try:
                    call = client.calls(call.sid).fetch()
                    status = call.status
                    
                    status_container.info(f"📞 ステータス: **{status}**")
                    progress_bar.progress(min(step / 30, 1.0))
                    
                    if status in terminal_statuses:
                        progress_bar.progress(1.0)
                        
                        if status == 'completed':
                            st.success("✅ 通話完了！留守電を確認してください。")
                        elif status == 'no-answer':
                            st.warning("⚠️ 応答なし（留守電に転送されなかった可能性）")
                        elif status == 'busy':
                            st.warning("⚠️ 話し中でした")
                        else:
                            st.error(f"❌ 通話失敗: {status}")
                        
                        # 詳細情報
                        with st.expander("📋 通話詳細"):
                            st.write(f"- Call SID: {call.sid}")
                            st.write(f"- ステータス: {status}")
                            st.write(f"- 発信先: {to_number}")
                            st.write(f"- 発信元: {from_number}")
                            if hasattr(call, 'answered_by') and call.answered_by:
                                st.write(f"- AnsweredBy: {call.answered_by}")
                            if hasattr(call, 'duration') and call.duration:
                                st.write(f"- 通話時間: {call.duration}秒")
                        break
                    
                    time.sleep(3)
                    step += 1
                    
                except Exception as e:
                    st.error(f"❌ ステータス取得エラー: {e}")
                    break
            
        except TwilioException as e:
            st.error(f"❌ Twilioエラー: {e}")
        except Exception as e:
            st.error(f"❌ エラー: {e}")

st.markdown("---")

# 説明
with st.expander("❓ 使い方"):
    st.markdown("""
    ### テスト手順
    
    1. **Twilio認証情報を入力**
       - Twilioコンソールから取得
    
    2. **電話番号を設定**
       - 発信元: Twilioで購入した番号
       - 発信先: テスト用の携帯番号（自分の番号）
    
    3. **メッセージを設定**
       - 日本語で入力
    
    4. **テスト実行**
       - ボタンを押す
       - **電話に出ないでください！**
       - 留守電に転送されるまで待つ
    
    5. **結果確認**
       - 留守電を聞いて、メッセージが録音されているか確認
    
    ### AMD（Answering Machine Detection）とは？
    
    - Twilioが「人が出たか」「留守電が出たか」を判定する機能
    - `DetectMessageEnd` = 留守電のビープ音を待ってからメッセージを再生
    - これにより、留守電アナウンスとメッセージが被らない
    
    ### うまくいかない場合
    
    1. **AMDをオフにする** → 長い待機時間で対応
    2. **待機時間を長くする** → 10-15秒
    3. **基本音声を使う** → Pollyが使えない場合
    """)

with st.expander("⚠️ 日本の携帯留守電について"):
    st.markdown("""
    ### 日本の携帯キャリア留守電
    
    - **docomo**: 留守番電話サービス（有料オプション）
    - **au**: お留守番サービス（有料オプション）
    - **SoftBank**: 留守番電話（有料オプション）
    - **楽天モバイル**: 留守番電話（無料）
    
    ### 注意点
    
    1. **留守電が有効になっているか確認**
       - キャリアのオプションで有効化が必要
    
    2. **呼び出し時間の設定**
       - 短すぎると留守電に転送されない
       - 通常15-30秒程度
    
    3. **伝言メモ vs キャリア留守電**
       - 伝言メモ（端末機能）: Twilioからはアクセス不可
       - キャリア留守電（ネットワーク機能）: Twilioで対応可能
    """)
