import os
import streamlit as st
from dotenv import load_dotenv
from game import Game
from highscores import HighscoreManager
import pandas as pd
import time

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
if 'question_start_time' not in st.session_state:
    st.session_state.question_start_time = None
if 'timer_expired' not in st.session_state:
    st.session_state.timer_expired = False

st.title("🧮 极限数学挑战")

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

def check_time_expired(game):
    """Check if time has expired for current question"""
    if st.session_state.question_start_time is None:
        return False
    
    current_time = time.time()
    elapsed_time = current_time - st.session_state.question_start_time
    return elapsed_time >= game.time_limit

def get_time_remaining(game):
    """Get remaining time for current question"""
    if st.session_state.question_start_time is None:
        return game.time_limit
    
    current_time = time.time()
    elapsed_time = current_time - st.session_state.question_start_time
    return max(0, game.time_limit - elapsed_time)

# 开始界面
if st.session_state.stage == 'start':
    display_highscores()
    
    st.markdown("---")
    
    # 游戏说明
    with st.expander("🎮 极限挑战规则", expanded=False):
        st.markdown("""
        ### 🔥 这是一个极具挑战性的数学游戏！
        
        **📚 题目类型:**
        - 🔢 前10题：乘法 (1-10的数字)
        - ➕ 第11题开始：乘法 + 除法混合
        
        **⏰ 时间压力:**
        - 第1-5题：⏱️ 10秒答题时间
        - 第6-10题：⏱️ 7秒答题时间  
        - 第11-20题：⏱️ 5秒答题时间
        - 第21-25题：⏱️ 3秒答题时间
        - 第26题起：⏱️ 1秒答题时间！
        
        **💀 失败条件:**
        - ❌ 答错任何一题 = 游戏结束
        - ⏰ 时间用完 = 游戏结束
        
        **🏆 目标:**
        - 在极限时间压力下保持准确性
        - 挑战你的数学反应速度！
        """)
    
    if st.button("🚀 开始极限挑战", type="primary", use_container_width=True):
        st.session_state.stage = 'playing'
        st.session_state.game.reset()
        st.session_state.question_start_time = time.time()
        st.session_state.timer_expired = False
        st.rerun()

# 游戏界面
elif st.session_state.stage == 'playing':
    game = st.session_state.game
    
    # Check if time expired before showing the interface
    if check_time_expired(game) and not st.session_state.timer_expired:
        st.session_state.timer_expired = True
        st.session_state.stage = 'game_over'
        st.rerun()
    
    question = game.current_question
    if not question:
        question = game.generate_question()
        st.session_state.question_start_time = time.time()  # Reset timer for new question

    # 游戏状态显示，仅展示当前得分
    st.metric("当前得分", game.score, delta=None)
    
    # 时间限制信息
    time_remaining = get_time_remaining(game)
    st.info(game.get_time_remaining_message())
    
    # JavaScript Timer Display
    st.markdown(f"""
    <div id="timer-container" style="text-align: center; margin: 20px 0;">
        <div id="timer-display" style="
            font-size: 2.5em; 
            font-weight: bold; 
            padding: 15px 30px; 
            border-radius: 10px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            margin-bottom: 10px;
        ">
            <span id="countdown">⏰ {time_remaining:.1f}</span>
        </div>
        <div id="timer-status" style="font-size: 1.1em; color: #666;">
            点击答案选择，倒计时会自动停止
        </div>
    </div>
    
    <script>
    (function() {{
        // Clear any existing timer
        if (window.gameTimer) {{
            clearInterval(window.gameTimer);
        }}
        
        let timeRemaining = {time_remaining};
        const timeLimit = {game.time_limit};
        let isExpired = false;
        
        function updateTimer() {{
            const display = document.getElementById('countdown');
            const container = document.getElementById('timer-display');
            const status = document.getElementById('timer-status');
            
            if (display && timeRemaining > 0 && !isExpired) {{
                display.textContent = '⏰ ' + timeRemaining.toFixed(1);
                
                // Change colors based on time remaining
                if (timeRemaining > timeLimit * 0.6) {{
                    container.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
                }} else if (timeRemaining > timeLimit * 0.3) {{
                    container.style.background = 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)';
                }} else {{
                    container.style.background = 'linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%)';
                    container.style.animation = 'pulse 0.5s infinite alternate';
                }}
                
                timeRemaining -= 0.1;
            }} else if (timeRemaining <= 0 && !isExpired) {{
                isExpired = true;
                display.textContent = '⏰ 0.0';
                status.textContent = '时间到！游戏结束...';
                container.style.background = 'linear-gradient(135deg, #333 0%, #666 100%)';
                clearInterval(window.gameTimer);
                
                // Auto-redirect when time is up
                setTimeout(() => {{
                    // Trigger a form submission to end the game
                    const form = document.createElement('form');
                    form.method = 'POST';
                    form.action = window.location.href;
                    const input = document.createElement('input');
                    input.type = 'hidden';
                    input.name = 'time_expired';
                    input.value = 'true';
                    form.appendChild(input);
                    document.body.appendChild(form);
                    form.submit();
                }}, 1500);
            }}
        }}
        
        // Add pulse animation CSS
        const style = document.createElement('style');
        style.textContent = `
            @keyframes pulse {{
                from {{ transform: scale(1); }}
                to {{ transform: scale(1.05); }}
            }}
        `;
        document.head.appendChild(style);
        
        // Start timer
        updateTimer(); // Initial call
        window.gameTimer = setInterval(updateTimer, 100);
        
        // Stop timer when any button is clicked
        document.addEventListener('click', function(e) {{
            if (e.target.tagName === 'BUTTON' && e.target.textContent.match(/^\d+$/)) {{
                clearInterval(window.gameTimer);
                const status = document.getElementById('timer-status');
                if (status) {{
                    status.textContent = '已选择答案，等待结果...';
                }}
            }}
        }});
    }})();
    </script>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 题目显示 - 根据时间紧迫程度改变背景色
    if time_remaining > 5:
        bg_color = "#e8f4fd"
        text_color = "#1f77b4"
        border_color = "#28a745"
    elif time_remaining > 2:
        bg_color = "#fff3cd"
        text_color = "#856404"
        border_color = "#ffc107"
    else:
        bg_color = "#f8d7da"
        text_color = "#721c24"
        border_color = "#dc3545"
    
    st.markdown(f"""
    <div style="text-align: center; padding: 30px; background-color: {bg_color}; border-radius: 15px; margin: 20px 0; border: 3px solid {border_color};">
        <h2 style="color: {text_color}; margin-bottom: 20px;">📝 题目 #{game.questions_answered + 1}</h2>
        <h1 style="color: #333; font-size: 3em;">{question['text']}</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Multiple Choice Options
    st.markdown("### 🤔 选择正确答案:")
    
    # Check for time expiry from form submission
    if st.query_params.get('time_expired') == 'true':
        st.session_state.timer_expired = True
        st.session_state.stage = 'game_over'
        st.rerun()
    
    # 创建选项按钮
    cols = st.columns(2)
    
    for i, option in enumerate(question['options']):
        col_idx = i % 2
        with cols[col_idx]:
            if st.button(str(option), key=f"option_{i}_{game.questions_answered}", use_container_width=True):
                # Check if time expired when button was clicked
                if check_time_expired(game):
                    st.session_state.timer_expired = True
                    st.session_state.stage = 'game_over'
                    st.rerun()
                
                # Process the answer
                if game.check_answer(option):
                    st.session_state.game.increment_score()
                    st.success(f"🎉 正确！{question['text'].replace('?', '')} {option}")
                    
                    # 生成新问题并重置计时器
                    st.session_state.game.generate_question()
                    st.session_state.question_start_time = time.time()
                    st.balloons()
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ 错误！正确答案是: {question['answer']}")
                    st.session_state.stage = 'game_over'
                    time.sleep(2)
                    st.rerun()
    
    st.markdown("---")
    
    # 返回按钮
    if st.button("🏠 返回主菜单"):
        st.session_state.stage = 'start'
        st.session_state.question_start_time = None
        st.session_state.timer_expired = False
        st.rerun()

# 游戏结束界面
elif st.session_state.stage == 'game_over':
    score = st.session_state.game.score
    questions_answered = st.session_state.game.questions_answered
    
    # 确定失败原因
    failure_reason = "⏰ 时间用完了！" if st.session_state.timer_expired else "❌ 答案错误！"
    
    # 游戏结束动画效果
    st.markdown(f"""
    <div style="text-align: center; padding: 40px; background: linear-gradient(135deg, #ff6b6b, #ee5a24); border-radius: 20px; color: white; margin: 20px 0;">
        <h1>🎮 游戏结束!</h1>
        <h2>{failure_reason}</h2>
        <h2>你的最终得分: {score} 分</h2>
        <h3>总共答对: {questions_answered} 题</h3>
        <p style="font-size: 1.2em; margin-top: 20px;">
            {'🔥 极限高手！' if score >= 20 else '⚡ 反应神速！' if score >= 15 else '💪 已经很棒了！' if score >= 10 else '🎯 继续挑战！'}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 成绩评价
    if score >= 25:
        st.balloons()
        st.success("🏆 数学闪电侠！你在极限压力下的表现令人惊叹！")
    elif score >= 20:
        st.success("⚡ 极速计算王！你的反应速度超乎常人！")
    elif score >= 15:
        st.success("🔥 时间战士！在高压下仍能保持准确性！")
    elif score >= 10:
        st.info("💫 不错的挑战！继续练习能做得更好！")
    else:
        st.info("🎯 勇敢的尝试！多练习基础乘法，提高反应速度！")
      
    st.markdown("---")
    
    name = st.text_input("🏷️ 请输入你的名字记录高分:", placeholder="输入你的游戏昵称...")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 提交成绩", type="primary", use_container_width=True):
            if name.strip():
                highscore_manager.record_highscore(name.strip(), score)
                st.success("✅ 成绩已保存到高分榜！")
                st.session_state.stage = 'start'
                st.session_state.timer_expired = False
                st.rerun()
            else:
                st.warning("⚠️ 请输入你的名字")
    
    with col2:
        if st.button("🔄 重新挑战", use_container_width=True):
            st.session_state.stage = 'start'
            st.session_state.timer_expired = False
            st.rerun()
