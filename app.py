from flask import Flask, render_template, request, jsonify, Response
import openai
import config
import time
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key=config.OPENAI_API_KEY,
    base_url="https://api.chatanywhere.tech/v1"
)

# 定义指令
commands = {
    "daily_news": "今日新闻",
    "chinese_yuan": "人民币",
    "usd": "美元",
    # 添加更多指令
}

@app.route('/')
def index():
    return render_template('index.html', commands=commands)

@app.route('/send_command', methods=['POST'])
def send_command():
    command = request.json.get('command')
    return Response(generate_response(commands[command]), content_type='text/event-stream')

def generate_response(command_content):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system", 
                "content": "现在你是一个帮助用户搜集并整理新闻的小助手，默认的网站有以下几个：https://www.chinanews.com.cn/finance/，https://finance.sina.com.cn/，https://finance.eastmoney.com/，https://www.caijing.com.cn/https://www.forbes.com/，如果用户有指定网站，你要从用户指定网站中搜索，根据用户给的关键词在该网站中搜索并提取相关新闻信息，并分条整理给出。另外，当你收到今日新闻指令时，整理出今日最新以及最热的新闻并分条给出。如果用户向你输入关键词，请整理出该关键词相关的新闻信息并分条给出。"
            },
            {
                "role": "user",
                "content": command_content
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
            yield content  # EventSource格式要求以'data:'开头和双换行结束
    
    time.sleep(2)

if __name__ == '__main__':
    app.run(debug=True)
