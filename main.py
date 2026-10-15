from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "success",
        "message": "Free Fire Like API is running successfully!",
        "test_usage": "/test_like?uid=YOUR_UID&token=YOUR_TOKEN"
    })

@app.route('/test_like', methods=['GET', 'POST'])
def test_like():
    if request.method == 'POST':
        data = request.get_json() or {}
        uid = data.get("uid")
        token = data.get("token")
    else:
        uid = request.args.get("uid")
        token = request.args.get("token")

    if not uid or not token:
        return jsonify({
            "status": "error", 
            "message": "দয়া করে UID এবং Token উভয়ই প্রদান করুন!"
        }), 400

    # গ্যারেনা অফিশিয়াল এপিআই ইউআরএল
    garena_like_url = "https://client.ind.garena.com/api/player/like"
    
    # টোকেন ফরম্যাট হ্যান্ডেলিং
    auth_token = token if token.startswith("Bearer ") else f"Bearer {token}"

    # গেম অ্যাপ্লিকেশনের হুবহু হেডার সেটআপ
    headers = {
        "Authorization": auth_token,
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; M2004J19CI Build/RP1A.200720.011)",
        "Content-Type": "application/json; charset=UTF-8",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "X-Requested-With": "com.dts.freefireth"
    }
    
    payload = {"target_uid": str(uid)}

    # ১. প্রথম চেষ্টা: সরাসরি কানেকশন
    try:
        response = requests.post(garena_like_url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200 and response.text.strip():
            return jsonify({
                "status": "success",
                "method": "direct",
                "http_status": response.status_code,
                "garena_response": response.json()
            }), 200
    except Exception:
        pass  # সরাসরি ফেইল করলে ব্যাকআপ প্রক্সিতে চলে যাবে

    # ২. দ্বিতীয় চেষ্টা: CORS-Proxy / Alternative Route বাইপাস
    try:
        proxy_gateway = f"https://corsproxy.io/?{garena_like_url}"
        proxy_response = requests.post(proxy_gateway, json=payload, headers=headers, timeout=12)
        
        if proxy_response.content:
            return jsonify({
                "status": "success",
                "method": "proxy_gateway",
                "http_status": proxy_response.status_code,
                "garena_response": proxy_response.json()
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "গ্যারেনা সার্ভার থেকে খালি উত্তর পাওয়া গেছে। টোকেনটি মেয়াদোত্তীর্ণ (expired) হতে পারে।"
            }), 400

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "গ্যারেনা সার্ভারে সংযোগ করা সম্ভব হয়নি।",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
    
