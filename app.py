import os
import json
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai
import streamlit as st

load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key = google_api_key)

menu_df = pd.read_csv("menu.csv", index_col = [0], encoding = 'utf-8')

with open("config.json", "r", encoding='utf-8') as f:
    config = json.load(f)
    function_name = config.get("function", "giới thiệu nhà hàng")
    initial_bot_message = config.get("initial_bot_message", "Xin chào! Bạn cần hỗ trợ gì?")

model = genai.GenerativeModel("gemini-1.5-flash",
                              system_instruction=f"""
                              Bạn tên là PhoBot, một trợ lý AI có nhiệm vụ hỗ trợ giải đáp thông tin cho khách hàng đến nhà hàng Viet Cuisine.
                              Các chức năng mà bạn hỗ trợ gồm:
                              1. Giới thiệu nhà hàng Viet Cuisine: là một nhà hàng thành lập bởi người Việt, ở địa chỉ 329 Scottmouth, Georgia, USA
                              2. Giới thiệu menu của nhà hàng, gồm các món: {', '.join(menu_df['name'].to_list())}.
                              Ngoài hai chức năng trên, bạn không hỗ trợ chức năng nào khác. Đối với các câu hỏi ngoài chức năng mà bạn hỗ trợ, trả lời bằng 'Tôi đang không hỗ trợ chức năng này. Xin liên hệ nhân viên nhà hàng qua hotline 318-237-3870 để được trợ giúp.'
                              Hãy có thái độ thân thiện và lịch sự khi nói chuyện với khác hàng, vì khách hàng là thượng đế.
                              """)
def restaurant_chatbot():
    st.title("PhoBot")
    st.write("Ban can ho tro gi?")
    st.write("Ban co the hoi ve nha hang, menu")

    if 'conversation_log' not in st.session_state:
        st.session_state.conversation_log = [
            {"role": "system", "content": initial_bot_message}
        ]
    for message in st.session_state.conversation_log:
        if message['role'] == 'user':
            with st.chat_message(message['role']):
                st.write(message['content'])
    if prompt := st.chat_input("Nhap cau hoi cua ban tai day:"):
        st.write(prompt)
        st.session_state.conversation_log.append({"role": "system", "content": prompt})
        response = model.generate_content(prompt)
        bot_reply = response.text

        if "menu" in prompt.lower() or "món" in prompt.lower():
            bot_reply = '\n\n'.join([
                f"**{row['name']}**: {row['description']}" for idx, row in menu_df.interrows()
            ])
        else:
            response= model.generate_content(prompt)
            bot_reply = response.text

        if "menu" in prompt.lower() or "món" in prompt.lower():
            bot_reply = '\n\n'.join([
                f"**{row['name']}**: {row['ingredients']}" for idx, row in menu_df.interrows()
            ])
        else:
            response= model.generate_content(prompt)
            bot_reply = response.text

        with st.chat_message("assistant"):
            st.write(bot_reply)
        
        st.session_state.conversation_log.append({"role": "system", "content": bot_reply})



if __name__ == "__main__":
    restaurant_chatbot()