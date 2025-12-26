import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from mod.O_config import DATABASE_NAME, CRED_PATH, GROUP_LIST


def create_client():
    # 設定使用服務：google drive以及讀取修改的權限
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
    # 設定檔名
    file_name = DATABASE_NAME
    spread_sheet = client.open(file_name)

    # 設定分頁名
    worksheet = spread_sheet.worksheet(sheet_name)

    return worksheet


def turn_sheet_to_df(worksheet):
    # 以key/value方式讀取檔案，並轉換成df
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    df["生日"] = pd.to_datetime(df["生日"] + "/1900", format="mixed")
    df["生日"] = df["生日"].dt.strftime("%m/%d")

    return df


def save_to_sheet(worksheet, df):
    try:
        worksheet.clear()
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())
        print("資料儲存成功！")
    except Exception as e:
        print(f"資料儲存失敗：{e}")


def connect_and_read_all_sheets(client):
    df_dict = {}

    for group in GROUP_LIST:
        worksheet = connect_sheet_file(client=client, sheet_name=group)
        df = turn_sheet_to_df(worksheet=worksheet)
        df_dict[group] = df

    return df_dict


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
            "執行狀況：一月": self.jan,
            "執行狀況：二月": self.feb,
            "執行狀況：三月": self.mar,
            "執行狀況：四月": self.apr
        }

    @classmethod
    def from_series(cls, series):
        return cls(
            name=series["姓名"],
            course=series["課程"],
            birthday=series["生日"],
            jan=series["執行狀況：一月"],
            feb=series["執行狀況：二月"],
            mar=series["執行狀況：三月"],
            apr=series["執行狀況：四月"]
        )
