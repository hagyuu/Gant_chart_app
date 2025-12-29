import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import io

# ページ設定
st.set_page_config(
    page_title="プロジェクトタイムライン管理",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS（Shadow効果付き）
st.markdown("""
<style>
    /* メインコンテナ */
    .main {
        background-color: #f8f9fa;
    }
    
    /* カード風のスタイル */
    .stCard {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    
    /* ヘッダー */
    .header-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3);
        text-align: center;
        color: white;
        margin-bottom: 30px;
    }
    
    /* 統計カード */
    .stat-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        text-align: center;
        border: none;
        transition: transform 0.2s;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
    }
    
    /* ボタン */
    .stButton>button {
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        transform: translateY(-2px);
    }
    
    /* データエディタ */
    .stDataFrame {
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-radius: 10px;
    }
    
    /* ダウンロードボタン */
    .stDownloadButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
    }
</style>
""", unsafe_allow_html=True)


def get_default_table():
    """デフォルトデータを取得"""
    return pd.read_csv(
        "https://raw.githubusercontent.com/plotly/datasets/master/GanttChart.csv"
    )


def add_finish_column(df):
    """終了日を計算"""
    df = df.copy()
    df["Start"] = pd.to_datetime(df["Start"])
    df["Duration"] = df["Duration"].astype(int)
    df["Finish"] = df["Start"] + pd.to_timedelta(df["Duration"], unit="D")
    return df


def calculate_stats(df):
    """統計情報を計算"""
    total_tasks = len(df)
    total_days = df["Duration"].sum()
    resources = df["Resource"].nunique()
    earliest = df["Start"].min()
    latest = df["Finish"].max()
    return total_tasks, total_days, resources, earliest, latest


def create_gantt_chart(df):
    """ガントチャートを作成"""
    fig = px.timeline(
        df,
        x_start="Start",
        x_end="Finish",
        y="Task",
        color="Resource",
        color_discrete_sequence=px.colors.qualitative.Set2,
        title="プロジェクトガントチャート"
    )
    
    fig.update_layout(
        font=dict(size=14, family="'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        title_x=0.5,
        title_font_size=20,
        yaxis=dict(
            title="",
            automargin=True,
            autorange="reversed",
            categoryorder="array",
            categoryarray=df["Task"],
            gridcolor="#e9ecef",
        ),
        xaxis=dict(
            title="期間",
            gridcolor="#e9ecef",
            showgrid=True,
        ),
        legend=dict(
            title="担当者",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode="closest",
        margin=dict(l=20, r=20, t=60, b=20),
        height=500,
    )
    
    fig.update_traces(
        width=0.6,
        marker=dict(line=dict(color="white", width=2)),
    )
    
    return fig


def convert_df_to_csv(df):
    """DataFrameをCSVに変換"""
    return df.to_csv(index=False).encode('utf-8-sig')


def convert_df_to_excel(df):
    """DataFrameをExcelに変換"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='タスク一覧')
    return output.getvalue()


# セッション状態の初期化
if 'df' not in st.session_state:
    st.session_state.df = get_default_table()

# ヘッダー
st.markdown("""
<div class="header-card">
    <h1>📊 プロジェクトタイムライン管理</h1>
    <p>タスクを追加・編集してガントチャートを作成しよう！</p>
</div>
""", unsafe_allow_html=True)

# サイドバー
with st.sidebar:
    st.markdown("### ⚙️ コントロールパネル")
    
    # 新規タスク追加
    st.markdown("#### ➕ 新規タスク追加")
    new_task = st.text_input("タスク名", "新しいタスク")
    new_duration = st.number_input("日数", min_value=1, value=1)
    new_resource = st.selectbox("担当者", ["A", "B", "C", "D"])
    new_start = st.date_input("開始日", datetime.now())
    
    if st.button("✅ タスクを追加", use_container_width=True):
        new_row = pd.DataFrame({
            "Task": [new_task],
            "Start": [new_start],
            "Duration": [new_duration],
            "Resource": [new_resource]
        })
        st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
        st.success("タスクを追加しました！")
        st.rerun()
    
    st.divider()
    
    # リセット
    if st.button("🔄 データをリセット", use_container_width=True):
        st.session_state.df = get_default_table()
        st.success("データをリセットしました！")
        st.rerun()
    
    st.divider()
    
    # エクスポート
    st.markdown("#### 💾 データエクスポート")
    
    # 終了日を計算したデータフレーム
    df_with_finish = add_finish_column(st.session_state.df)
    
    # CSV エクスポート
    csv_data = convert_df_to_csv(df_with_finish)
    st.download_button(
        label="📄 CSV ダウンロード",
        data=csv_data,
        file_name=f"project_timeline_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    # Excel エクスポート
    excel_data = convert_df_to_excel(df_with_finish)
    st.download_button(
        label="📊 Excel ダウンロード",
        data=excel_data,
        file_name=f"project_timeline_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
    
    st.divider()
    
    # 印刷用PDF生成の案内
    st.markdown("#### 🖨️ 印刷について")
    st.info("ブラウザの印刷機能（Ctrl+P / Cmd+P）を使って、このページを印刷できます！")

# 統計情報
df_with_finish = add_finish_column(st.session_state.df)
total_tasks, total_days, resources, earliest, latest = calculate_stats(df_with_finish)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="stat-card">
        <h2 style="color: #1f77b4; margin: 0;">📋</h2>
        <h3 style="margin: 10px 0;">{}</h3>
        <p style="color: #6c757d; margin: 0;">総タスク数</p>
    </div>
    """.format(total_tasks), unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="stat-card">
        <h2 style="color: #2ca02c; margin: 0;">📅</h2>
        <h3 style="margin: 10px 0;">{}</h3>
        <p style="color: #6c757d; margin: 0;">総日数</p>
    </div>
    """.format(total_days), unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="stat-card">
        <h2 style="color: #ff7f0e; margin: 0;">👥</h2>
        <h3 style="margin: 10px 0;">{}</h3>
        <p style="color: #6c757d; margin: 0;">担当者数</p>
    </div>
    """.format(resources), unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="stat-card">
        <h2 style="color: #d62728; margin: 0;">⏰</h2>
        <h3 style="margin: 10px 0; font-size: 16px;">{}</h3>
        <p style="color: #6c757d; margin: 0;">開始日</p>
    </div>
    """.format(earliest.strftime('%Y-%m-%d')), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# データテーブル
st.markdown("### 📋 タスク一覧")
edited_df = st.data_editor(
    st.session_state.df,
    use_container_width=True,
    num_rows="dynamic",
    column_config={
        "Task": st.column_config.TextColumn("タスク名", width="medium"),
        "Duration": st.column_config.NumberColumn("日数", min_value=1, max_value=365),
        "Resource": st.column_config.SelectboxColumn("担当者", options=["A", "B", "C", "D"]),
        "Start": st.column_config.DateColumn("開始日", format="YYYY-MM-DD"),
    },
    hide_index=True,
)

# データの更新
if not edited_df.equals(st.session_state.df):
    st.session_state.df = edited_df
    st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ガントチャート
st.markdown("### 📊 ガントチャート")
df_with_finish = add_finish_column(st.session_state.df)
fig = create_gantt_chart(df_with_finish)
st.plotly_chart(fig, use_container_width=True)

# フッター
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6c757d; padding: 20px;">
    <p>Made with ❤️ using Streamlit | 友達と共有して使ってね！</p>
</div>
""", unsafe_allow_html=True)