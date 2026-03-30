import streamlit as st
import time
import os
import random
from gtts import gTTS
from io import BytesIO

# --- 0. 系統配置 (維持原始視覺設定) ---
st.set_page_config(
    page_title="AKA PATELAS - 阿美語學習", 
    page_icon="🌊", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# --- CSS 視覺魔法 (維持原始深海螢光科技風) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&family=Noto+Sans+TC:wght@400;700&display=swap');

    .stApp { 
        background-color: #000810;
        background-image: radial-gradient(circle at 50% 0%, #0D47A1 0%, #000810 80%);
        font-family: 'Noto Sans TC', sans-serif;
        color: #E0F7FA;
    }
    
    .header-container {
        background: rgba(13, 71, 161, 0.3);
        border: 1px solid #00E5FF;
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.3);
        border-radius: 15px;
        padding: 30px;
        text-align: center;
        margin-bottom: 40px;
        backdrop-filter: blur(10px);
    }
    
    .main-title {
        font-family: 'Roboto Mono', monospace;
        color: #00E5FF;
        font-size: 40px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 3px;
        text-shadow: 0 0 10px #00E5FF;
        margin: 0;
    }
    
    .teacher-tag { 
        display: inline-block; 
        margin-top: 15px; 
        padding: 5px 15px; 
        border: 1px solid #FF4081; 
        color: #FF4081; 
        border-radius: 50px; 
        font-size: 14px; 
        font-weight: bold; 
    }

    .word-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 20px 10px;
        text-align: center;
        border: 1px solid rgba(0, 229, 255, 0.2);
        height: 100%;
        margin-bottom: 15px;
    }

    .amis-word { font-size: 22px; font-weight: 700; color: #FFFFFF; margin-bottom: 5px; font-family: 'Roboto Mono', monospace; }
    .zh-word { font-size: 16px; color: #80DEEA; }

    .sentence-box {
        background: linear-gradient(90deg, rgba(0,229,255,0.05) 0%, rgba(0,0,0,0) 100%);
        border-left: 4px solid #FF4081;
        padding: 20px;
        margin-bottom: 20px;
        border-radius: 0 10px 10px 0;
    }
    .sentence-amis { font-size: 18px; color: #FF80AB; font-weight: 700; margin-bottom: 8px; }
    .sentence-zh { font-size: 15px; color: #B2EBF2; }

    .stButton>button { width: 100%; border-radius: 5px; background: transparent; border: 2px solid #00E5FF; color: #00E5FF !important; font-weight: bold; }
    .stButton>button:hover { background: #00E5FF; color: #000 !important; }

    .stTabs [data-baseweb="tab"] {
        color: #FFFFFF !important; 
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: bold;
    }

    .stTabs [aria-selected="true"] {
        background-color: #00E5FF !important;
        color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. 資料更新 (App-Lexicon-CRF v6.4 [cite: 29]) ---
VOCABULARY = [
    {"amis": "salama", "zh": "玩耍", "emoji": "🎮", "s_amis": "Maolah koya wawa a misalama i lawac no riyar.", "s_zh": "那個小孩喜歡在海邊玩耍。"},
    {"amis": "lonan", "zh": "車子", "emoji": "🚗", "s_amis": "Cahoay ka tayni koya lonan no siciw.", "s_zh": "市長的那輛車子還沒到。"},
    {"amis": "tafok", "zh": "沙子", "emoji": "🏖️", "s_amis": "Adiadiay ko tafok itini i liyal.", "s_zh": "這裏海邊的沙子很多。"},
    {"amis": "dangoy", "zh": "游泳", "emoji": "🏊", "s_amis": "Matayal cingra adihay ko 'alo, maolah a midangoy.", "s_zh": "他工作的地方有很多河流，他喜歡游泳。"},
    {"amis": "tiyad", "zh": "肚子", "emoji": "🍕", "s_amis": "Adada ko tiyad no ruma a wawa.", "s_zh": "有些小孩肚子痛。"}
]

# --- 2. 語音核心 (診斷優化版 [cite: 1, 34]) ---
def play_audio(text):
    try:
        # 使用印尼語 (id) 模擬南島語系發音 [cite: 1]
        tts = gTTS(text=text, lang='id') 
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        st.audio(fp, format='audio/mp3')
    except:
        st.caption("🔇 語音生成失敗")

# --- 3. 隨機出題邏輯 [cite: 41, 42] ---
def init_quiz():
    st.session_state.score = 0
    st.session_state.current_q = 0
    st.session_state.quiz_pool = random.sample(VOCABULARY, 3)

if 'quiz_pool' not in st.session_state:
    init_quiz()

# --- 4. 介面呈現函數 ---
def show_learning_mode():
    st.markdown("<h3 style='color:#00E5FF; text-align:center;'>資料庫：單字模組</h3>", unsafe_allow_html=True)
    cols = st.columns(len(VOCABULARY))
    for idx, item in enumerate(VOCABULARY):
        with cols[idx]:
            st.markdown(f"""
            <div class="word-card">
                <div style="font-size:30px;">{item['emoji']}</div>
                <div class="amis-word">{item['amis']}</div>
                <div class="zh-word">{item['zh']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🔊", key=f"v_{idx}"):
                play_audio(item['amis'])

    st.markdown("---")
    st.markdown("<h3 style='color:#00E5FF; text-align:center;'>資料庫：語法模組</h3>", unsafe_allow_html=True)
    for idx, item in enumerate(VOCABULARY):
        st.markdown(f"""
        <div class="sentence-box">
            <div class="sentence-amis">{item['emoji']} {item['s_amis']}</div>
            <div class="sentence-zh">{item['s_zh']}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("播放例句語音", key=f"s_{idx}"):
            play_audio(item['s_amis'])

def show_quiz_mode():
    st.markdown("<h3 style='text-align: center; color: #FF4081;'>任務：知識檢測</h3>", unsafe_allow_html=True)
    if st.session_state.current_q < 3:
        target = st.session_state.quiz_pool[st.session_state.current_q]
        st.markdown(f"### 挑戰任務 {st.session_state.current_q + 1} / 3")
        st.markdown(f"<div style='background:rgba(255,64,129,0.1); padding:20px; border-radius:10px; border:1px solid #FF4081; text-align:center;'><h2 style='color:#FF4081; margin:0;'>{target['amis']}</h2></div>", unsafe_allow_html=True)
        
        # 產生選項 [cite: 41]
        others = [v['zh'] for v in VOCABULARY if v['zh'] != target['zh']]
        opts = random.sample(others, 2) + [target['zh']]
        random.shuffle(opts)

        st.write("")
        cols = st.columns(3)
        for i, opt in enumerate(opts):
            with cols[i]:
                if st.button(opt, key=f"quiz_opt_{i}"):
                    if opt == target['zh']:
                        st.balloons()
                        st.session_state.score += 1
                        st.session_state.current_q += 1
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("數據不符，請重新辨識")
    else:
        st.markdown(f"""
        <div style='text-align:center; padding:30px; border:2px solid #00E5FF; border-radius:15px; background:rgba(0,229,255,0.1);'>
            <h1 style='color:#00E5FF;'>任務全數完成</h1>
            <p style='font-size:20px;'>目前積分：{st.session_state.score} / 3</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("重啟任務"):
            init_quiz()
            st.rerun()

# --- 5. 主程式入口 [cite: 15, 20] ---
def main():
    st.markdown(f"""
    <div class="header-container">
        <h1 class="main-title">AKA PATELAS</h1>
        <div style="color:#B2EBF2; margin-top:5px; font-weight:bold;">生活詞彙與句型學習系統</div>
        <div class="teacher-tag">講師：sawmAh 旓瑪赫赫</div>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🌊 海洋筆記", "🎮 挑戰任務"])
    
    with tab1:
        show_learning_mode()
    with tab2:
        show_quiz_mode()

if __name__ == "__main__":
    main()
