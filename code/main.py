from mod import O_general as gr
from mod import A_write_record as wr


# step 0: 建立連線，並將所有分頁讀入
client = gr.create_client()
df_dict = gr.connect_and_read_all_sheets(client=client)

# step 1: 負責人登入，並選擇查看的小組
df, df_temp, group = wr.manager_login(df_dict=df_dict)

# step 1-2: 將符合條件的成員列出
print(df_temp)

# step 2: 輸入修改對象
result_idx, search_student = wr.select_update_target(df=df, df_temp=df_temp)

# step 3: 選擇修改月份
search_student = wr.update_comment(search_student=search_student)

# step 4: 將修改後資料存回df
df.loc[result_idx] = search_student.to_dict()

# step 5: 將df回存試算表檔案
worksheet = gr.connect_sheet_file(client=client, sheet_name=group)
gr.save_to_sheet(worksheet=worksheet, df=df)
