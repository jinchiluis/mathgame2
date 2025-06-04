import os
import streamlit as st
from dotenv import load_dotenv
from game import Game
from highscores import HighscoreManager
import pandas as pd

# Load environment variables from .env if present
load_dotenv()

# 初始化 Supabase 高分管理器
supabase_url = os.getenv("SUPABASE_URL", st.secrets.get("SUPABASE_URL"))
supabase_key = os.getenv("SUPABASE_KEY", st.secrets.get("SUPABASE_KEY"))
highscore_manager = HighscoreManager(supabase_url, supabase_key)

# 在 Session State 中存储游戏对象和界面阶段
if 'stage' not in st.session_state:
    st.session_state.stage = 'start'
if 'game' not in st.session_state:
    st.session_state.game = Game()
if 'selected_answer' not in st.session_state:
    st.session_state.selected_answer = None

st.title("🧮 数学游戏")

def display_highscores():
    """显示高分榜的函数"""
    st.header("🏆 高分榜")
    
    scores = highscore_manager.get_highscores()
    
    if not scores:
        # 空状态显示
        st.markdown("""
        <div style="text-align: center; padding: 40px; background-color: #f0f2f6; border-radius: 10px; margin: 20px 0;">
            <h3 style="color: #666;">🎯 还没有高分记录</h3>
            <p style="color: #888;">成为第一个挑战者吧！</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # 创建DataFrame并添加排名
        df = pd.DataFrame(scores)
        df.index = df.index + 1  # 从1开始排名
        
        # 添加奖牌图标
        def get_medal(rank):
            if rank == 1:
                return "🥇"
            elif rank == 2:
                return "🥈"
            elif rank == 3:
                return "🥉"
            else:
                return f"#{rank}"
        
        df['排名'] = [get_medal(i) for i in df.index]
        df['玩家'] = df['name']
        df['得分'] = df['score']
        
        # 只显示需要的列
        display_df = df[['排名', '玩家', '得分']]
        
        # 使用自定义CSS样式
        st.markdown("""
        <style>
        .highscore-table {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
        }
        .highscore-table h3 {
            color: white;
            text-align: center;
            margin-bottom: 15px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # 显示表格
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "排名": st.column_config.TextColumn(
                    "排名",
                    width="small",
                ),
                "玩家": st.column_config.TextColumn(
                    "玩家",
                    width="medium",
                ),
                "得分": st.column_config.NumberColumn(
                    "得分",
                    width="small",
                    format="%d 分"
                ),
            }
        )
        
        # 统计信息
        total_players = len(scores)
        highest_score = max(score['score'] for score in scores)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("总玩家数", total_players, delta=None)
        with col2:
            st.metric("最高分", highest_score, delta=None)
        with col3:
            avg_score = sum(score['score'] for score in scores) / len(scores)
            st.metric("平均分", f"{avg_score:.1f}", delta=None)

# 开始界面
if st.session_state.stage == 'start':
    display_highscores()
    
    st.markdown("---")
    
    # 游戏说明
    with st.expander("🎮 游戏规则", expanded=False):
        st.markdown("""
        - 🎯 从5个选项中选择正确的数学答案
        - 📈 每答对一题得1分，难度会逐渐增加
        - 🔢 达到10分解锁减法，20分解锁乘法，30分解锁除法
        - ❌ 答错一题游戏结束
        - 🏆 挑战高分榜，成为数学之王！
        """)
    
    if st.button("🚀 开始游戏", type="primary", use_container_width=True):
        st.session_state.stage = 'playing'
        st.session_state.game.reset()
        st.session_state.selected_answer = None
        st.rerun()

# 游戏界面
elif st.session_state.stage == 'playing':
    game = st.session_state.game
    question = game.current_question
    if not question:
        question = game.generate_question()

    # 游戏状态显示
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("当前得分", game.score, delta=None)
    with col2:
        operations = game.get_current_operations()
        st.metric("可用运算", len(operations), delta=None)
    with col3:
        st.metric("当前运算", ", ".join(operations), delta=None)
    
    st.markdown("---")
    
    # 题目显示
    st.markdown(f"""
    <div style="text-align: center; padding: 30px; background-color: #e8f4fd; border-radius: 15px; margin: 20px 0;">
        <h2 style="color: #1f77b4; margin-bottom: 20px;">📝 题目</h2>
        <h1 style="color: #333; font-size: 3em;">{question['text']}</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Multiple Choice Optionen
    st.markdown("### 🤔 选择正确答案:")
    
    # Erstelle Buttons für jede Option
    option_labels = ['A', 'B', 'C', 'D', 'E']
    selected_option = None
    
    # Verwende Spalten für bessere Darstellung
    cols = st.columns(2)
    
    for i, option in enumerate(question['options']):
        col_idx = i % 2
        with cols[col_idx]:
            if st.button(f"{option_labels[i]}) {option}", 
                        key=f"option_{i}", 
                        use_container_width=True,
                        type="secondary"):
                selected_option = option
                
    # Wenn eine Option gewählt wurde, prüfe die Antwort
    if selected_option is not None:
        if game.check_answer(selected_option):
            st.session_state.game.increment_score()
            st.success(f"🎉 正确！{question['text'].replace('?', '')} {selected_option}")
            st.session_state.game.generate_question()
            st.balloons()
            # 短暂延迟以获得更好的用户体验
            import time
            time.sleep(1)
            st.rerun()
        else:
            st.error(f"❌ 错误！正确答案是: {question['answer']}")
            st.session_state.stage = 'game_over'
            # 短暂延迟以获得更好的用户体验
            import time
            time.sleep(2)
            st.rerun()
    
    st.markdown("---")
    
    # 返回按钮
    if st.button("🏠 返回主菜单"):
        st.session_state.stage = 'start'
        st.rerun()

# 游戏结束界面
elif st.session_state.stage == 'game_over':
    score = st.session_state.game.score
    
    # 游戏结束动画效果
    st.markdown(f"""
    <div style="text-align: center; padding: 40px; background: linear-gradient(135deg, #ff6b6b, #ee5a24); border-radius: 20px; color: white; margin: 20px 0;">
        <h1>🎮 游戏结束!</h1>
        <h2>你的最终得分: {score} 分</h2>
        <p style="font-size: 1.2em; margin-top: 20px;">
            {'🎉 太棒了！' if score >= 15 else '👍 不错的尝试！' if score >= 8 else '💪 继续努力！'}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 成绩评价
    if score >= 25:
        st.balloons()
        st.success("🏆 数学天才！你的表现令人惊叹！")
    elif score >= 15:
        st.success("⭐ 数学高手！表现很棒！")
    elif score >= 8:
        st.info("📚 继续练习，你会更棒的！")
    else:
        st.info("💡 多练习基础题目，下次一定能做得更好！")
    
    st.markdown("---")
    
    name = st.text_input("🏷️ 请输入你的名字记录高分:", placeholder="输入你的游戏昵称...")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 提交成绩", type="primary", use_container_width=True):
            if name.strip():
                highscore_manager.record_highscore(name.strip(), score)
                st.success("✅ 成绩已保存到高分榜！")
                st.session_state.stage = 'start'
                st.rerun()
            else:
                st.warning("⚠️ 请输入你的名字")
    
    with col2:
        if st.button("🔄 重新开始", use_container_width=True):
            st.session_state.stage = 'start'
            st.rerun()
