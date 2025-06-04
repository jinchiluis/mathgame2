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
if 'show_result' not in st.session_state:
    st.session_state.show_result = False
if 'result_message' not in st.session_state:
    st.session_state.result_message = ""
if 'is_correct' not in st.session_state:
    st.session_state.is_correct = False

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
        


# 开始界面
if st.session_state.stage == 'start':
    display_highscores()
    
    st.markdown("---")
    
    # 游戏说明
    with st.expander("🎮 游戏规则", expanded=False):
        st.markdown("""
        - 🎯 从4个选项中选择正确的数学答案
        - 📈 每答对一题得1分，难度会逐渐增加
        - 🔢 达到10分解锁减法，20分解锁乘法，30分解锁除法
        - ❌ 答错一题游戏结束
        - 🏆 挑战高分榜，成为数学之王！
        """)
    
    if st.button("🚀 开始游戏", type="primary", use_container_width=True):
        st.session_state.stage = 'playing'
        st.session_state.game.reset()
        st.session_state.selected_answer = None
        st.session_state.show_result = False
        st.session_state.result_message = ""
        st.session_state.is_correct = False
        st.rerun()

# 游戏界面
elif st.session_state.stage == 'playing':
    game = st.session_state.game
    question = game.current_question
    if not question:
        question = game.generate_question()

    # 游戏状态显示
    st.metric("当前得分", game.score, delta=None)
    
    st.markdown("---")
    
    # 题目显示
    st.markdown(f"""
    <div style="text-align: center; padding: 30px; background-color: #e8f4fd; border-radius: 15px; margin: 20px 0;">
        <h2 style="color: #1f77b4; margin-bottom: 20px;">📝 题目</h2>
        <h1 style="color: #333; font-size: 3em;">{question['text']}</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # 显示上一题的结果（如果有）
    if st.session_state.show_result:
        if st.session_state.is_correct:
            st.success(st.session_state.result_message)
            st.balloons()
        else:
            st.error(st.session_state.result_message)
    
    # Multiple Choice Options
    st.markdown("### 🤔 选择正确答案:")
    
    # 创建按钮选项
    selected_option = None
    cols = st.columns(2)

    for i, option in enumerate(question['options']):
        col_idx = i % 2
        with cols[col_idx]:
            if st.button(str(option), key=f"option_{i}", use_container_width=True, type="secondary"):
                selected_option = option
                
    # 处理答案选择
    if selected_option is not None:
        if game.check_answer(selected_option):
            # 正确答案
            st.session_state.game.increment_score()
            st.session_state.result_message = f"🎉 正确！{question['text'].replace('?', '')} {selected_option}"
            st.session_state.is_correct = True
            st.session_state.show_result = True
            st.session_state.game.generate_question()  # 生成新题目
            st.rerun()
        else:
            # 错误答案
            st.session_state.result_message = f"❌ 错误！正确答案是: {question['answer']}"
            st.session_state.is_correct = False
            st.session_state.show_result = True
            st.session_state.stage = 'game_over'
            st.rerun()
    
    st.markdown("---")
    
    # 显示当前可用的运算类型
    current_ops = game.get_current_operations()
    st.info(f"当前解锁运算: {' • '.join(current_ops)}")
    
    # 返回按钮
    if st.button("🏠 返回主菜单"):
        st.session_state.stage = 'start'
        st.session_state.show_result = False
        st.rerun()

# 游戏结束界面
elif st.session_state.stage == 'game_over':
    score = st.session_state.game.score
    
    # 显示最后一题的结果
    if st.session_state.show_result and not st.session_state.is_correct:
        st.error(st.session_state.result_message)
        st.session_state.show_result = False  # 重置以避免重复显示
    
    # 游戏结束界面
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
                # 延迟跳转，让用户看到成功消息
                if st.button("🏠 返回主菜单", key="return_after_save"):
                    st.session_state.stage = 'start'
                    st.rerun()
            else:
                st.warning("⚠️ 请输入你的名字")
    
    with col2:
        if st.button("🔄 重新开始", use_container_width=True):
            st.session_state.stage = 'start'
            st.session_state.show_result = False
            st.rerun()
