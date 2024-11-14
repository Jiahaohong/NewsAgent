from flask import Flask, render_template, request, jsonify, Response
import openai
import config
import time
from openai import OpenAI

# flask主程序
app = Flask(__name__)

# gpt
client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key=config.OPENAI_API_KEY,
    base_url="https://api.chatanywhere.tech/v1"
)

# 默认关键词
keywords = ["今日新闻", "人民币", "美元",]
# 默认网站
websites = ["https://www.chinanews.com.cn/finance/",
            "https://finance.sina.com.cn/",
            "https://finance.eastmoney.com/",
            "https://www.caijing.com.cn/",
            "https://www.forbes.com/",
            ]

@app.route('/')
def index():
    return render_template('index.html', keywords=keywords, websites=websites)

@app.route('/add_keyword', methods=['POST'])
def add_keyword():
    new_keyword = request.form.get('keyword')
    if new_keyword and new_keyword not in keywords:
        keywords.append(new_keyword)
    return jsonify(keywords=keywords)

@app.route('/delete_keyword', methods=['POST'])
def delete_keyword():
    keyword_to_delete = request.form.get('keyword')
    if keyword_to_delete in keywords:
        keywords.remove(keyword_to_delete)
    return jsonify(keywords=keywords)

@app.route('/add_website', methods=['POST'])
def add_website():
    new_website = request.form.get('website')
    if new_website and new_website not in websites:
        websites.append(new_website)
    return jsonify(websites=websites)

@app.route('/delete_website', methods=['POST'])
def delete_website():
    website_to_delete = request.form.get('website')
    if website_to_delete in websites:
        websites.remove(website_to_delete)
    return jsonify(websites=websites)

@app.route('/send_keyword', methods=['POST'])
def send_keyword():
    keyword = request.json.get('keyword')
    return Response(generate_response(keyword), content_type='text/event-stream')

def generate_response(keyword):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system", 
                "content": f"现在你是一个帮助用户搜集并整理新闻的小助手，你可以使用的默认的网站有以下几个：{', '.join(websites)}\n如果在某个网站上没有搜到相关内容就不要给出这个网站的回答，如果在一个网站上搜到多个答案请一并给出。你给出的回答一定要保持固定的分条陈述的格式，不能有任何改变。你给出的每条回答需要在句子最后添加上网站的链接。"
            },
            {
                "role": "user",
                "content": keyword
            }
        ],
        stream=True,
        max_tokens=1500
    )

    # 逐步发送GPT返回的数据
    for chunk in response:
        print(chunk)
        content = chunk.choices[0].delta.content
        if content:
            yield content


if __name__ == '__main__':
    app.run(debug=True)
