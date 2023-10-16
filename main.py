import requests
from pprint import pprint
from langchain.document_loaders import UnstructuredHTMLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import openai
from vars import OPEN_API_KEY
from flask import Flask, request, jsonify
app = Flask(__name__)
openai.api_key = OPEN_API_KEY
# Step 1, if policy.html does not exists, create one.
# Step 2, use policy.html to create multiple documents
# Step 3, Listen to the API
# Step 4, When we get a website, fetch its content
# Step 5, use full content to get action items against each part of policy
# Step 6, use each of those results to summarize action items
# Step 7, Send it as result

def initialize():
    url = "https://stripe.com/docs/treasury/marketing-treasury"
    r = requests.get(url, allow_redirects=True)
    open("policy.html", "wb").write(r.content)
    loader = UnstructuredHTMLLoader("policy.html")
    data = loader.load()
    ts = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    return ts.split_documents(data)

def get_website_content(website):
    r = requests.get(website, allow_redirects=True)
    open("temp.html", "wb").write(r.content)
    return UnstructuredHTMLLoader("temp.html").load()[0].page_content

def get_part_actions(content, policy_data):
    res = []
    for policy_part in policy_data:
        messages = [
            {
                "role": "system",
                "content": "You are a compliance checker bot which has to check compliance of the give user text against part of a compliance policy which is given below - \n\n        " + policy_part.page_content
            },
            {
                "role": "user",
                "content": content
            }
        ]
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        res.append(completion.choices[0].message.content)
    return res

def get_summarized_actions(parts):
    messages = [
        {
            "role": "system",
            "content": "You are a summarizer for a bunch of compliance checking workers. You need to summarize action items given below to a list of unique action items"
        },
        {
            "role": "user",
            "content": "\n\n\n".join(parts)
        }
    ]
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return completion.choices[0].message.content

def get_compliance_actions(website, policy_data):
    # Step 4, When we get a website, fetch its content
    content = get_website_content(website)
    # Step 5, use full content to get action items against each part of policy
    part_actions = get_part_actions(content, policy_data)
    # Step 6, use each of those results to summarize action items
    result = get_summarized_actions(part_actions)
    # Step 7, Send it as result
    return result

@app.route('/compliancegpt')
def compliance_check():
    url_param = request.args.get('url')
    if url_param:
        return jsonify({'result': get_compliance_actions(url_param, initialize())})
    else:
        return jsonify({'error': 'URL parameter is missing'}), 400

if __name__ == '__main__':
    app.run(debug=True)