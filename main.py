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

    # গ্যারেনা লাইক এন্ডপয়েন্ট এবং ব্যাকআপ রুট
    garena_like_url = "https://client.ind.garena.com/api/player/like"
    
    headers = {
        "Authorization": f"Bearer {token}" if not token.startswith("Bearer") else token,
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; M2004J19CI Build/RP1A.200720.011)",
        "Content-Type": "application/json",
        "Connection": "Keep-Alive",
        "X-Requested-With": "com.dts.freefireth"
    }
    
    payload = {"target_uid": str(uid)}

    try:
        # রেন্ডারের আইপি প্রটেকশন এড়ানোর জন্য সঠিক টাইমআউট ও হেডার কনফিগারেশন
        response = requests.post(garena_like_url, json=payload, headers=headers, timeout=15)
        
        return jsonify({
            "status": "success",
            "http_status_code": response.status_code,
            "garena_response": response.json() if response.content else "Empty response"
        }), 200

    except Exception as e:
        # যদি সরাসরি ডোমেন রিজলভ না হয়, তবে ফ্রি প্রক্সি রাউটিং ব্যবহার করে ট্রাই করা হবে
        try:
            proxy_url = f"https://api.allorigins.win/raw?url=https://client.ind.garena.com/api/player/like"
            proxy_res = requests.post(proxy_url, json=payload, headers=headers, timeout=15)
            return jsonify({
                "status": "success_via_proxy",
                "http_status_code": proxy_res.status_code,
                "garena_response": proxy_res.json() if proxy_res.content else "Empty response"
            }), 200
        except Exception as proxy_err:
            return jsonify({
                "status": "error", 
                "message": "সার্ভার থেকে গ্যারেনারে রিকোয়েস্ট পাঠানো যায়নি।",
                "details": str(proxy_err)
            }), 500

if __name__ == '__main__':
    app.run(debug=True)
    
