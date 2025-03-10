from flask import render_template, flash, redirect, url_for , request, jsonify

from maya import app, config, db, client
from maya.payment.models import Payment
from flask_login import current_user
from maya.image_to_image.models import ImageToImage
@app.route("/payment")
def payment():
    
    if not current_user.is_authenticated:
        flash("you are not log in",'danger')
        return redirect(url_for('home'))
    
    # ImageToImage.__table__.drop(db.engine)
    
    return render_template("payment/payment.html",
                           title=config.get('APP_NAME','text to image'),
                           app_name=config.get('APP_NAME','text to image')  )
    
    

@app.route('/basicpack', methods=['POST'])
def basicpack():
    print('basic pack:-----------')
    return create_order("basic")
    
@app.route('/propack', methods=['POST'])
def propack():
    print('pro pack:-----------')
    return create_order("pro")


@app.route('/premiumpack', methods=['POST'])
def premiumpack():
    print('premium pack:-----------')
    return create_order("premium")



# @app.route("/create_order", methods=["POST"])
def create_order(pack):
    if pack == "basic":
        amount = 9900
    if pack == "pro":
        amount = 49900
    if pack == "premium":
        amount = 99900# Amount in paise (₹999.00)
    currency = "INR"
    receipt = "order_rcptid_11"
    # description = f"purchase {pack} pack"

    order_data = {
        "amount": amount,
        "currency": currency,
        "receipt": receipt,
        "payment_capture": 1  # Auto-captures the payment
    }
    
    order = client.order.create(order_data)
    print(f"razorpay order: {order}")
    return jsonify(order)


@app.route("/verify_payment", methods=["POST"])
def verify_payment():
    data = request.json
    try:
        client.utility.verify_payment_signature({
            "razorpay_order_id": data["razorpay_order_id"],
            "razorpay_payment_id": data["razorpay_payment_id"],
            "razorpay_signature": data["razorpay_signature"]
        })
        return jsonify({"message": "Payment successful"})
    except razorpay.errors.SignatureVerificationError:
        return jsonify({"message": "Payment verification failed"}), 400


@app.route("/payment_result",methods=['POST'])
def payment_result():
    result = request.get_json()
    pack = result.get("pack")
    message = result.get("message")
    
    pack_mapping = {"basic": 100, "pro": 550, "premium": 1200}
    current_coins = pack_mapping.get(pack, 0) 
    
    print(f" pack :{pack}, message:{message}")
    
    if message == "Payment successful" :
        
        user_payment = Payment.query.filter_by(user_id=current_user.id).first()
        
        if user_payment: 
            # if user pay previously           
            user_payment.current_coins += current_coins            
        else:
            # if user pay first time
            user_payment = Payment(user_id=current_user.id, current_coins=current_coins)
            db.session.add(user_payment)
        
        db.session.commit()  
        print(f"Payment: {user_payment.current_coins}")
        return jsonify({"success": True, "message": "Payment successful!"}), 200    
           
            
        
    else:
        flash("Payment verification failed", "danger")
        return jsonify({"success": False, "message": "Payment verification failed"}), 400
    


@app.route("/payment_success",methods=['GET'])
def success():
     return render_template("payment/success.html") 