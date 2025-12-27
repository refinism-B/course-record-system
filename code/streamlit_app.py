import streamlit as st
import pandas as pd
from mod import O_general as gr
from mod import O_config as cfg
from mod.O_general import Student

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

# 立即執行資料載入 (符合"系統啟動時就馬上讀取資料庫"的需求)
load_data()

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
    st.markdown("""
    功能說明：
    - **學生總覽**：查看各管理員負責課程的學生名單與詳細資料。
    - **輸入上課情況**：針對特定學生紀錄每個月的上課狀況。
    """)
    if st.button("開始使用"):
        # 點擊後跳轉到 學生總覽
        st.session_state['page'] = "學生總覽"
        st.rerun()

elif now_page == "學生總覽":
    st.title("學生總覽")

    # 選擇管理員
    manager_list = list(cfg.MANAGER_DICT.keys())
    # 如果還沒選，預設 None，UI 上顯示 "請選擇"
    current_manager = st.session_state['manager']
    
    # 為了實作"選擇後才顯示"，我們可以用一個 placeholder 或是檢查選單值
    # 如果已在 session 裡有值，就設為那個值，否則保持 None
    
    # Selectbox logic: 為了讓使用者明確感受到"選擇"這個動作，可以加一個空選項
    options = ["請選擇管理員"] + manager_list
    index = 0
    if current_manager in manager_list:
        index = options.index(current_manager)
    
    selected_option = st.selectbox("請選擇管理員", options, index=index)
    
    if selected_option != "請選擇管理員":
        st.session_state['manager'] = selected_option
        manager = selected_option
        course = cfg.MANAGER_DICT[manager]
        
        st.subheader(f"管理員：{manager} | 負責課程：{course}")
        
        # 標籤切換組別 (Group)
        groups = cfg.GROUP_LIST
        tabs = st.tabs(groups)
        
        for i, group in enumerate(groups):
            with tabs[i]:
                df = st.session_state['df_dict'][group]
                # 篩選課程
                mask = df["課程"] == course
                filtered_df = df[mask]
                st.dataframe(filtered_df, use_container_width=True)
    else:
        # 如果切換回"請選擇"，也可以把 session 清空或就保持不顯示下半部
        st.info("請先選擇一位管理員以檢視資料")
        st.session_state['manager'] = None

elif now_page == "輸入上課情況":
    st.title("輸入上課情況")
    
    # 檢查是否已選擇管理員，若無則提示
    if st.session_state['manager'] is None:
        st.warning("尚未選擇管理員，請先選擇：")
        manager_list = list(cfg.MANAGER_DICT.keys())
        options = ["請選擇管理員"] + manager_list
        selected_option = st.selectbox("請選擇管理員", options)
        if selected_option != "請選擇管理員":
             st.session_state['manager'] = selected_option
             st.rerun()
        else:
             st.stop() # 停止執行下方代碼直到選擇
    else:
        st.info(f"當前管理員：{st.session_state['manager']}")

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
