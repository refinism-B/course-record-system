import pandas as pd
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
from mod.O_config import DATABASE_NAME, CRED_PATH, GROUP_LIST
import streamlit as st
from streamlit_gsheets import GSheetsConnection


def create_client():
    """設定使用服務：google drive以及讀取修改的權限"""
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    # 設定憑證
    cred_path = CRED_PATH
    cred = ServiceAccountCredentials.from_json_keyfile_name(
        filename=cred_path, scopes=scope)
    client = gspread.authorize(cred)

    return client


def connect_sheet_file(client, sheet_name):
    """指定試算表名稱及分頁名稱"""
    # 設定檔名
    file_name = DATABASE_NAME
    spread_sheet = client.open(file_name)

    # 設定分頁名
    worksheet = spread_sheet.worksheet(sheet_name)

    return worksheet


def turn_sheet_to_df(worksheet):
    """先以key/value方式讀取檔案，再轉換成df"""
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    df["生日"] = pd.to_datetime(df["生日"] + "/1900", format="mixed")
    df["生日"] = df["生日"].dt.strftime("%m/%d")

    return df


def save_to_sheet(worksheet, df):
    """資料驗證後，直接更新試算表內容（不清除）"""
    if df is None or df.empty:
        raise ValueError("DataFrame 為空，為防止資料遺失，拒絕執行儲存動作。")

    try:
        # 修改為僅更新，不進行 clear()，以防止執行失敗導致資料遺失
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())
        print("資料儲存成功！")
    except Exception as e:
        print(f"資料儲存失敗：{e}")
        # 將錯誤拋出，以便上層 (streamlit) 能夠捕捉並顯示錯誤
        raise e


def connect_and_read_all_sheets(client):
    """讀取檔案後將所有分頁都轉換成df並放入dict"""
    df_dict = {}

    for group in GROUP_LIST:
        worksheet = connect_sheet_file(client=client, sheet_name=group)
        df = turn_sheet_to_df(worksheet=worksheet)
        df_dict[group] = df

    return df_dict


def st_connection():
    """建立 Streamlit Google Sheets 連線"""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        return conn
    except Exception as e:
        st.error(f"連線失敗：{e}")
        return None


def st_read_df(conn, sheet_name):
    """
    使用 st.connection 讀取分頁並轉換為 DataFrame
    包含資料清洗邏輯：將"生日"欄位格式化為 "MM/DD"
    """
    try:
        # 使用 ttl=0 或較短時間確保資料新鮮度，依需求調整
        df = conn.read(worksheet=sheet_name, ttl="10m")
        
        # 資料清洗 (參考原 turn_sheet_to_df 邏輯)
        if "生日" in df.columns:
            # 確保生日欄位為字串型態以免報錯，並補上年份進行轉換
            df["生日"] = df["生日"].astype(str)
            # 排除空值或異常值
            df["生日"] = pd.to_datetime(df["生日"] + "/1900", format="mixed", errors='coerce')
            df["生日"] = df["生日"].dt.strftime("%m/%d")
            # 處理轉換失敗的 NaT，轉回空字串或其他預設值
            df["生日"] = df["生日"].fillna("")
            
        return df
    except Exception as e:
        st.error(f"讀取分頁 {sheet_name} 失敗：{e}")
        return pd.DataFrame()


def st_read_all_df(conn):
    """讀取所有群組分頁"""
    df_dict = {}
    try:
        for group in GROUP_LIST:
            df = st_read_df(conn=conn, sheet_name=group)
            df_dict[group] = df
        return df_dict
    except Exception as e:
        st.error(f"讀取所有分頁失敗：{e}")
        return {}


def st_save_sheet(conn, df, sheet_name):
    """使用 st.connection 更新分頁資料"""
    if df is None or df.empty:
        st.warning("DataFrame 為空，略過儲存。")
        return

    try:
        # update 方法會覆蓋資料
        conn.update(worksheet=sheet_name, data=df)
        # st.success("資料儲存成功！") # 這裡不顯示 success，交由 UI 層決定顯示
    except Exception as e:
        st.error(f"儲存分頁 {sheet_name} 失敗：{e}")
        raise e


class Student:
    def __init__(self, name, course, birthday, jan, feb, mar, apr):
        self.name = name
        self.course = course
        self.birthday = birthday
        self.jan = jan
        self.feb = feb
        self.mar = mar
        self.apr = apr

        pass

    def update_record(self, month, text):
        setattr(self, month, text)

    def to_dict(self):
        return {
            "姓名": self.name,
            "課程": self.course,
            "生日": self.birthday,
            "一月": self.jan,
            "二月": self.feb,
            "三月": self.mar,
            "四月": self.apr
        }

    @classmethod
    def from_series(cls, series):
        return cls(
            name=series["姓名"],
            course=series["課程"],
            birthday=series["生日"],
            jan=series["一月"],
            feb=series["二月"],
            mar=series["三月"],
            apr=series["四月"]
        )
