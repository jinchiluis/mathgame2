import os
import streamlit as st
from game import Game
from highscores import HighscoreManager

# 初始化 Supabase 高分管理器
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
highscore_manager = HighscoreManager(supabase_url, supabase_key)

# 在 Session State 中存储游戏对象和界面阶段
if 'stage' not in st.session_state:
    st.session_state.stage = 'start'
if 'game' not in st.session_state:
    st.session_state.game = Game()

st.title("数学游戏")

# 开始界面
if st.session_state.stage == 'start':
    st.header("高分榜")
    scores = highscore_manager.get_highscores()
    for s in scores:
        st.write(f"{s['name']}: {s['score']}")

    if st.button("开始游戏"):
        st.session_state.stage = 'playing'
        st.session_state.game.reset()
        st.experimental_rerun()

# 游戏界面
elif st.session_state.stage == 'playing':
    game = st.session_state.game
    question = game.current_question
    if not question:
        question = game.generate_question()

    st.write(f"题目: {question['text']}")
    answer = st.text_input("你的答案", key='answer')
    if st.button("提交"):
        if game.check_answer(answer):
            st.session_state.game.increment_score()
            st.success("正确！")
            st.session_state.game.generate_question()
            st.experimental_rerun()
        else:
            st.session_state.stage = 'game_over'
            st.experimental_rerun()

# 游戏结束界面
elif st.session_state.stage == 'game_over':
    score = st.session_state.game.score
    st.error(f"游戏结束！你的得分: {score}")
    name = st.text_input("请输入你的名字记录高分:")
    if st.button("提交成绩"):
        if name:
            highscore_manager.record_highscore(name, score)
        st.session_state.stage = 'start'
        st.experimental_rerun()
