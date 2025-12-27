# from mod import O_general as gr
from mod.O_config import GROUP_LIST, MANAGER_DICT, MONTH_DICT
from mod.O_general import Student


def manager_login(df_dict):
    user = input("請輸入使用者名稱")  # 提供選項["林玲", "桂丹", "善美", 總覽]
    group = input("請輸入查詢小組")  # 提供選項["社青小組", "善牧小組"]
    if user in list(MANAGER_DICT) and group in GROUP_LIST:
        course = MANAGER_DICT[user]
        df = df_dict[group]

        mask = (df["課程"] == course)
        return df, df[mask], group
    else:
        print("使用者名稱或小組名稱輸入錯誤")


def select_update_target(df, df_temp):
    search_name = input("請輸入欲修改的對象")  # 使用st.multiselect方式搜尋所有姓名

    mask = (df_temp["姓名"] == search_name)
    result = df_temp[mask]
    result_idx = result.index[0]

    search_student = Student.from_series(df.loc[result_idx])

    return result_idx, search_student


def update_comment(search_student):
    select_month = input("請輸入欲修改的月份")  # 提供選項：["一月", "二月", "三月", "四月"]
    update_month = MONTH_DICT[select_month]

    comment = input("請輸入說明")  # 可輸入任意字串，上限100字

    search_student.update_record(update_month, comment)
    return search_student
