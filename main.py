from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "success",
        "message": "Free Fire Like API is running!",
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

    garena_like_url = "https://client.ind.garena.com/api/player/like"
    
    auth_token = token if token.startswith("Bearer ") else f"Bearer {token}"

    # গ্যারেনা সার্ভারকে বাইপাস করার জন্য আসল ফ্রি ফায়ার অ্যাপের ফিক্সড হেডার
    headers = {
        "Authorization": auth_token,
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; M2004J19CI Build/RP1A.200720.011)",
        "Content-Type": "application/json; charset=UTF-8",
        "Accept": "application/json",
        "X-Requested-With": "com.dts.freefireth"
    }
    
    payload = {"target_uid": str(uid)}

    try:
        # সেশন ব্যবহার করে সরাসরি রিকোয়েস্ট পাঠানো
        session = requests.Session()
        response = session.post(garena_like_url, json=payload, headers=headers, timeout=20)
        
        # গ্যারেনা থেকে সাকসেস বা যেকোনো রেসপন্স আসলে তা রিটার্ন করবে
        if response.text and response.text.strip():
            try:
                res_json = response.json()
            except:
                res_json = {"raw_text": response.text}

            return jsonify({
                "status": "success",
                "http_status": response.status_code,
                "garena_response": res_json
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "গ্যারেনা সার্ভার থেকে কোনো রেসপন্স পাওয়া যায়নি (টোকেন মেয়াদোত্তীর্ণ হতে পারে)।"
            }), 400

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "সার্ভার কানেকশন এরর!",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
    
