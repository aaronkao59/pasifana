import streamlit as st
import random
from gtts import gTTS
from io import BytesIO
import time

# --- 10-5 阿美語詞彙規範與造句模組 (App-Lexicon-CRF v6.5) ---
# 權威鎖定：僅保留指定詞彙，並生成標準造句。
VOCABULARY = [
    {
        "amis": "salama",
        "ch": "玩耍",
        "sentence_amis": "Maolah koya wawa a misalama i lawac no riyar.",
        "sentence_ch": "那個小孩喜歡在海邊玩耍。"
    },
    {
        "amis": "lonan",
        "ch": "車子 / 交通工具",
        "sentence_amis": "Cahoay ka tayni koya lonan no siciw.",
        "sentence_ch": "市長的那輛車子還沒到。"
    },
    {
        "amis": "tafok",
        "ch": "沙子",
        "sentence_amis": "Adiadiay ko tafok itini i liyal.",
        "sentence_ch": "這裏海邊的沙子很多。"
    },
    {
        "amis": "dangoy",
        "ch": "游泳",
        "sentence_amis": "Matayal cingra adihay ko 'alo, maolah a midangoy.",
        "sentence_ch": "他工作的地方有很多河流，他喜歡游泳。"
    },
    {
        "amis": "ciaal",
        "ch": "肚子",
        "sentence_amis": "Adada ko ciaal no ruma a wawa.",
        "sentence_ch": "有些小孩肚子痛。"
    }
]

# --- 介面設定 (UIUX-CRF v9.0) ---
st.set_page_config(page_title="Pangcah 詞彙學習王", page_icon="🌴", layout="centered")

# 自定義 CSS (提升認知鎖定與空間適配)
st.markdown("""
<style>
    .main-title { font-size: 2.5rem; color: #2E7D32; text-align: center; font-weight: 700; margin-bottom: 20px; }
    .word-card { background-color: #F1F8E9; border-radius: 15px; padding: 25px; border-left: 5px solid #8BC34A; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
    .amis-word { font-size: 3rem; color: #1B5E20; font-weight: 800; }
    .amis-sentence { font-size: 1.2rem; color: #424242; font-style: italic; margin-top: 10px; }
    .ch-text { font-size: 1.2rem; color: #616161; margin-top: 5px; }
    .stButton>button { width: 100%; background-color: #8BC34A; color: white; border-radius: 20px; border: none; transition: all 0.3s; }
    .stButton>button:hover { background-color: #689F38; transform: scale(1.02); }
</style>
""", unsafe_allow_html=True)

# --- 核心功能函數 ---

def play_audio(text):
    """
    執行 API-B: 語音生成與播放
    使用 gTTS (印尼語 `id` 模擬南島語系發音)
    """
    try:
        # 清洗文本，只取單字部分或句子主體
        tts = gTTS(text=text, lang='id')
        fp = BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp, format='audio/mp3')
    except Exception as e:
        st.error(f"語音生成失敗 (安全邊際防禦觸發): {e}")

def get_next_word():
    """獲取與上次不同的新單字 (認知熵控制)"""
    if len(VOCABULARY) < 2:
        return VOCABULARY[0]
    
    current_word = st.session_state.get('current_word', None)
    next_word = random.choice(VOCABULARY)
    
    while current_word and next_word['amis'] == current_word['amis']:
        next_word = random.choice(VOCABULARY)
    return next_word

# --- Session State 初始化 ---
if 'current_word' not in st.session_state:
    st.session_state.current_word = random.choice(VOCABULARY)
if 'quiz_options' not in st.session_state:
    st.session_state.quiz_options = []
if 'quiz_feedback' not in st.session_state:
    st.session_state.quiz_feedback = ""

# --- 主介面渲染 ---
st.markdown("<div class='main-title'>Pangcah 詞彙學習王</div>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📖 單字學習", "📝 挑戰測驗"])

# --- Tab 1: 單字學習 ---
with tab1:
    word = st.session_state.current_word
    
    st.markdown(f"""
    <div class='word-card'>
        <div class='amis-word'>{word['amis']}</div>
        <div class='ch-text'>中文意思：<b>{word['ch']}</b></div>
        <hr style='border:1px solid #C5E1A5'>
        <div class='amis-sentence'>例句：{word['sentence_amis']}</div>
        <div class='ch-text'>（{word['sentence_ch']}）</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔊 聽單字發音", key="play_word"):
            play_audio(word['amis'])
            
    with col2:
        if st.button("🔊 聽例句發音", key="play_sentence"):
            # 句子較長，發音速度調整稍慢 (gTTS 暫不支持速度參數，此處為概念示意)
            play_audio(word['sentence_amis'])
            
    st.markdown("---")
    if st.button("換一個單字 ➡️", key="next_word"):
        st.session_state.current_word = get_next_word()
        # 切換單字時清空測驗狀態
        st.session_state.quiz_feedback = "" 
        st.rerun()

# --- Tab 2: 挑戰測驗 (測驗模型-CRF v1.2) ---
with tab2:
    st.subheader("看族語，選中文")
    quiz_word = st.session_state.current_word
    
    st.markdown(f"""
    <div style='text-align:center; padding: 20px; background:#E8F5E9; border-radius:10px; margin-bottom:20px;'>
        <span style='font-size:3rem; color:#1B5E20; font-weight:800;'>{quiz_word['amis']}</span>
    </div>
    """, unsafe_allow_html=True)

    # 生成選項 (需確保包含正確答案)
    if not st.session_state.quiz_options or st.session_state.feedback_triggered:
        correct_answer = quiz_word['ch']
        # 從所有單字中尋找錯誤選項
        all_ch = [w['ch'] for w in VOCABULARY if w['ch'] != correct_answer]
        # 隨機選2個錯誤答案，連同正確答案組成3個選項
        options = random.sample(all_ch, min(len(all_ch), 2)) + [correct_answer]
        random.shuffle(options)
        st.session_state.quiz_options = options
        st.session_state.feedback_triggered = False # 重設旗標

    # 顯示測驗選項
    for option in st.session_state.quiz_options:
        if st.button(option, key=f"btn_{option}"):
            if option == quiz_word['ch']:
                st.session_state.quiz_feedback = "🎉 太棒了！答對了！"
                st.balloons()
            else:
                st.session_state.quiz_feedback = f
