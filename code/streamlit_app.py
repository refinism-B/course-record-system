import streamlit as st
import pandas as pd
from mod import O_general as gr
from mod import O_config as cfg
from mod.O_general import Student

import os

# 設定頁面配置
st.set_page_config(page_title="和散那課程記錄系統", layout="wide")

# 初始化 session state
if 'df_dict' not in st.session_state:
    st.session_state['df_dict'] = None
if 'client' not in st.session_state:
    st.session_state['client'] = None
if 'manager' not in st.session_state:
    st.session_state['manager'] = None
if 'page' not in st.session_state:
    st.session_state['page'] = '首頁'

@st.cache_resource
def get_client():
    return gr.create_client()

def load_data():
    if st.session_state['client'] is None:
        st.session_state['client'] = get_client()
    
    # 系統啟動時就讀取資料
    if st.session_state['df_dict'] is None:
        with st.spinner('連接資料庫中...'):
            st.session_state['df_dict'] = gr.connect_and_read_all_sheets(st.session_state['client'])

def save_data(group, df):
    """儲存資料到 Google Sheets 並更新 session_state"""
    try:
        client = st.session_state['client']
        worksheet = gr.connect_sheet_file(client, group)
        gr.save_to_sheet(worksheet, df)
        st.success("資料儲存成功！")
        # 更新 session_state 中的資料
        st.session_state['df_dict'][group] = df
    except Exception as e:
        st.error(f"資料儲存失敗: {e}")

def get_announcement_content():
    """讀取公告檔案內容"""
    try:
        # 假設 announcement.md 位於上一層目錄的 doc 資料夾下
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        file_path = os.path.join(project_root, 'doc', 'announcement.md')
        
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 簡單過濾掉 YAML front matter (--- ... ---)
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                     return parts[2].strip()
            return content
        return "找不到公告檔案。"
    except Exception as e:
        return f"讀取公告失敗: {e}"

# 立即執行資料載入 (符合"系統啟動時就馬上讀取資料庫"的需求)
load_data()

# Global CSS Styles
st.markdown("""
    <style>
    /* Increase button size (+20%) */
    .block-container div.stButton > button:first-child {
        font-size: 120% !important;
        padding: 0.75rem 1.7rem !important;
    }
    
    /* Increase Tab Group Labels by 25% */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
            font-size: 125% !important;
    }
    
    /* Increase Dataframe font size by 2px (assuming default is ~14px, setting to 16px) */
    [data-testid="stDataFrame"] * {
        font-size: 16px !important;
    }

    /* Specific fix for table headers if needed */
    [data-testid="stDataFrame"] th {
        font-size: 16px !important;
    }
    
    /* Specific fix for table cells if needed */
    [data-testid="stDataFrame"] td {
        font-size: 16px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 側邊欄導航 (改為按鈕)
st.sidebar.title("功能列表")
if st.sidebar.button("首頁", use_container_width=True):
    st.session_state['page'] = "首頁"
    st.rerun()

if st.sidebar.button("學生總覽", use_container_width=True):
    st.session_state['page'] = "學生總覽"
    st.rerun()

if st.sidebar.button("輸入上課情況", use_container_width=True):
    st.session_state['page'] = "輸入上課情況"
    st.rerun()

# 頁面邏輯
now_page = st.session_state['page']

if now_page == "首頁":
    st.title("和散那課程記錄系統")
    


    col1, col2 = st.columns(2)
    
    container_style = """
        padding: 10px 10px 30px 20px; 
        line-height: 1.6;
    """

    header_style = """
        font-size: 30px; 
        font-weight: bold; 
        margin-bottom: 30px; 
        border-bottom: 1px solid #ddd; 
        padding-bottom: 15px;
        text-align: center;
    """

    content_style = "font-size: 17px; text-align: left; margin-top: 10px;"
    
    with col1:
        with st.container(border=True):
            announcement = get_announcement_content()
            # Insert styles and structure. 
            # Note: Putting markdown inside a div in st.markdown with unsafe_allow_html=True
            # requires extra newlines to trigger markdown processing for lists.
            st.markdown(f"""
                <div style="{container_style}">
                    <div style="{header_style}">課程公告</div>
                    <div style="{content_style}">
                    
{announcement}
                """, unsafe_allow_html=True)
        
    with col2:
        with st.container(border=True):
            content_text = """
1. 點擊開始使用
2. 選擇一位負責人，查看負責人管理的學生列表
3. 使用左側「輸入上課情況」功能填寫學生上課情況
4. 選擇學生、月份並輸入上課情況後點擊確認送出
            """
            st.markdown(f"""
                <div style="{container_style}">
                    <div style="{header_style}">功能說明</div>
                    <div style="{content_style}">
                    
{content_text}
                """, unsafe_allow_html=True)

    # Button at bottom, centered
    st.write("") # Spacer
    st.write("")
    _, mid, _ = st.columns([1, 1, 1])
    with mid:
        if st.button("開始使用", use_container_width=True):
            # 點擊後跳轉到 學生總覽
            st.session_state['page'] = "學生總覽"
            st.rerun()

elif now_page == "學生總覽":
    st.title("學生總覽")

    # 選擇負責人
    manager_list = list(cfg.MANAGER_DICT.keys())
    # 初始化 session_state 若不在選項中
    options = ["請選擇負責人", "總覽"] + manager_list
    if st.session_state.get('manager') not in options:
         st.session_state['manager'] = "請選擇負責人"
    
    # Callback to sync widget state to global state
    def update_manager():
        st.session_state['manager'] = st.session_state['sb_manager_overview']

    # Calculate index based on persistent state
    try:
        index = options.index(st.session_state['manager'])
    except ValueError:
        index = 0

    # Selectbox logic: 獨立 key 以避免換頁時狀態遺失，並透過 callback 同步
    selected_option = st.selectbox(
        "負責人", 
        options, 
        index=index,
        key='sb_manager_overview',
        on_change=update_manager
    )
    
    if st.session_state['manager'] != "請選擇負責人":
        # 使用全局狀態
        manager = st.session_state['manager']
        
        if manager == "總覽":
             st.subheader(f"總覽所有課程")
        else:
             course = cfg.MANAGER_DICT[manager]
        
        # 標籤切換組別 (Group)
        groups = cfg.GROUP_LIST
        tabs = st.tabs(groups)
        
        for i, group in enumerate(groups):
            with tabs[i]:
                df = st.session_state['df_dict'][group]
                # 篩選課程
                if manager == "總覽":
                    filtered_df = df
                else:
                    mask = df["課程"] == course
                    filtered_df = df[mask]
                st.dataframe(filtered_df, use_container_width=True)
    else:
        # 如果切換回"請選擇"，也可以把 session 清空或就保持不顯示下半部
        st.info("請先選擇一位負責人以檢視資料")
        st.session_state['manager'] = None

elif now_page == "輸入上課情況":
    st.title("輸入上課情況")
    
    # 定義 callback 更新 session state
    def update_manager_input():
        st.session_state['manager'] = st.session_state['sb_manager_input']

    # 取得負責人列表
    manager_list = list(cfg.MANAGER_DICT.keys())
    # 這裡不包含"總覽"，因為輸入頁面不支援總覽功能
    options = ["請選擇負責人"] + manager_list

    # 計算目前的 index
    # 如果 manager 是 "總覽" (從總覽頁過來)，在輸入頁面視為未選擇 ("請選擇負責人")
    current_manager = st.session_state.get('manager')
    if current_manager == "總覽":
        index = 0
    else:
        try:
            index = options.index(current_manager)
        except ValueError:
            index = 0

    # 顯示下拉選單 (總是顯示)
    st.selectbox(
        "負責人",
        options,
        index=index,
        key='sb_manager_input',
        on_change=update_manager_input
    )

    # 檢查是否選擇了有效的負責人
    if st.session_state['manager'] in [None, "請選擇負責人", "總覽"]:
        if st.session_state['manager'] == "總覽":
             st.warning("「總覽」模式下無法輸入上課情況，請上方選擇特定負責人。")
        else:
             st.warning("請先選擇負責人以開始輸入上課情況。")
        st.stop() # 停止執行下方代碼
    
    # 若已選擇負責人，顯示當前負責人 (debug/info用途，可選)
    # st.info(f"當前負責人：{st.session_state['manager']}")

    manager = st.session_state['manager']
    course = cfg.MANAGER_DICT[manager]
    
    groups = cfg.GROUP_LIST
    tabs = st.tabs(groups)
    
    # 定義彈出視窗 (Dialog) - Python function
    # 注意：st.dialog 在 function 內部定義或外部皆可，這裡為了方便傳參放在 loop 裡或外都行
    # 但 @st.dialog 裝飾器需要放在 global 或 function scope 上層
    # 為了避免重複定義，我們把它放在主邏輯外或這裡引用
    
    @st.dialog("確認修改內容")
    def confirm_dialog(student_name, month_tw, comment, group, df, row_idx):
        st.write(f"**學生**：{student_name}")
        st.write(f"**月份**：{month_tw}")
        st.write(f"**內容**：{comment}")
        st.warning("確定要儲存此修改嗎？")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("確認儲存"):
                try:
                    # 更新邏輯
                    # 1. 對應 Student 物件屬性 (英文)
                    month_attr = cfg.MONTH_DICT[month_tw] # e.g. 'jan'
                    
                    # 2. 更新 DataFrame
                    # 需存回對應欄位，這裡要直接存入中文欄位 "一月", "二月" 等
                    # 因為 df 的 columns 是中文
                    df.at[row_idx, month_tw] = comment
                    
                    # 儲存
                    save_data(group, df)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
        with col2:
            if st.button("取消"):
                st.rerun()

    for i, group in enumerate(groups):
        with tabs[i]:
            df = st.session_state['df_dict'][group]
            # 篩選該課程的學生
            mask = df["課程"] == course
            target_df = df[mask]
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                student_names = target_df["姓名"].tolist()
                selected_students = st.multiselect(
                    "搜尋並選擇學生 (限選一位)", 
                    student_names, 
                    key=f"student_multiselect_{group}"
                )
                
                comment = st.text_input(
                    "上課情況 (上限50字)", 
                    max_chars=50,
                    key=f"comment_input_{group}"
                )


            
            with col2:
                select_month = st.selectbox(
                    "修改月份", 
                    ["一月", "二月", "三月", "四月"],
                    key=f"month_select_{group}"
                )
            
            if st.button("確認送出", key=f"submit_btn_{group}"):
                if not selected_students:
                    st.error("請選擇一位學生")
                elif len(selected_students) > 1:
                    st.error("一次僅能修改一位學生資料")
                elif not comment:
                    st.error("請輸入上課情況內容")
                else:
                    target_student = selected_students[0]
                    # 找到原始 index
                    # 這裡假設姓名唯一
                    row_idx = df[df["姓名"] == target_student].index[0]
                    
                    # 呼叫彈出視窗
                    confirm_dialog(target_student, select_month, comment, group, df, row_idx)
            
            st.write("---")
            st.write("#### 該組別課程學生列表")
            st.dataframe(target_df, use_container_width=True)
