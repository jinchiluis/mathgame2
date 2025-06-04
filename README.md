# mathgame2

数学游戏。使用 Streamlit 构建界面，并通过 Supabase 存储高分。

## 运行
1. 安装依赖：`pip install -r requirements.txt`
2. 复制 `.env.example` 为 `.env` 并填写 `SUPABASE_URL` 与 `SUPABASE_KEY` 值。
   本地运行时会通过 `python-dotenv` 自动加载 `.env`。
   部署到 Streamlit Cloud 时可改用 `st.secrets` 存放这些值。
3. 运行应用：`streamlit run ui.py`
