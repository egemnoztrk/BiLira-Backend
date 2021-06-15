import ftx
import functools
from flask_cors import CORS
from bson import json_util
import flask
from flask import Flask,request,jsonify
ftx_client=ftx.FtxClient()
app = flask.Flask(__name__)
CORS(app)
app.config.update( DEBUG=False, SECRET_KEY="65465f4a6s54f6as54g6a54ya687ytq9ew841963684")


@app.route("/get_order", methods=["POST"])
def get_order():
    orderBookDepthLevel=100
    total=0
    price=0
    status="normal"
    
    action=request.form['action']
    base_cur=request.form['base_cur']
    quote_cur=request.form['quote_cur']
    amount=request.form['amount']
    currency=quote_cur
    
    try:
        amount=float(amount)
    except:
        return(jsonify({"status":"Please Enter Valid Amount"}))
    
    if not any([action.upper() == "BUY", action.upper()=="SELL"]):
        return(jsonify({"status":"Please Enter Valid Action"}))
    side = "bids" if action.upper()=="SELL" else "asks"

    try:
        ftx_client.get_orderbook(base_cur+"/"+quote_cur, orderBookDepthLevel)
        status="normal"
    except Exception as e:
        try:
            ftx_client.get_orderbook(quote_cur+"/"+base_cur, orderBookDepthLevel)
            quote_cur,base_cur = base_cur,quote_cur
            status="reversed"
            side = "bids" if action.upper()=="BUY" else "asks"
        except:
            return (jsonify({"Status":"Please Enter Valid Currencies"}))

    while True:
        totalOrderAmount=0
        result = ftx_client.get_orderbook(base_cur+"/"+quote_cur, orderBookDepthLevel)
        if status=="normal":totalOrderAmount=functools.reduce(lambda a, b: a+b[1], result[side],0)
        elif status=="reversed":totalOrderAmount=functools.reduce(lambda a, b: a+b[1]*b[0], result[side],0)
        if totalOrderAmount>amount:
            remainingAmount=amount
            for el in result[side]:
                if status=="reversed":
                    el[1]= el[1]*el[0]
                    el[0] = 1/el[0]
                if remainingAmount>el[1]:
                    remainingAmount=remainingAmount-el[1]
                    total+=float(el[0])*float(el[1])
                    price = el[0] if price==0 else el[0]*el[1]/amount+(1-el[1]/amount)*price
                    print({"Price": "%.10f" %el[0],"Amount":el[1]})
                else:
                    total+=float(el[0])*float(remainingAmount)
                    price = el[0] if price==0 else remainingAmount/amount*el[0]+(1-remainingAmount/amount)*price
                    print({"Price":"%.10f" % el[0],"Amount":remainingAmount})
                    break
            break
        orderBookDepthLevel+=10
        if orderBookDepthLevel>100: 
            return (jsonify({"Status":"Liquidity Not Enough"}))
        
    response={
        "total":"%.10f" % total,
        "price":"%.10f" % price,
        "currency":currency
    } 
    res=jsonify(response)
    return res


app.run()