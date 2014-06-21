from flask import Flask, request, make_response, render_template
import plivo

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("web_taker.html")


@app.route('/response/sip/route/', methods=['GET', 'POST'])
def response_sip_route():
    print(request.args)
    print(request)
    print(request.method)
    print(request.form)
    if request.method == 'GET':
        to_number = request.args.get('To', None)
        from_number = request.args.get('CLID', None)
        if from_number is None:
            from_number = request.args.get('From', '')
        # caller_name = request.args.get('CallerName', '')
    elif request.method == 'POST':
        to_number = request.form.get('To', None)
        from_number = request.form.get('CLID', None)
        if from_number is None:
            from_number = request.form.get('From', '')
        # caller_name = request.form.get('CallerName', '')
    else:
        print("Leaving")
        return make_response('Method not allowed.')

    print("Second level")
    response = plivo.Response()
    to_number = "sip:elricl140620163139@phone.plivo.com"
    print("third level")
    if not to_number:
        response.addHangup()
    else:
        response.addDial().addUser(to_number)
        # if to_number[:4] == 'sip:':
            # response.addDial().addUser(to_number)
        # else:
            # response.addDial().addNumber(to_number)

    print(response.to_xml())
    response = make_response(response.to_xml())
    response.headers['Content-Type'] = 'text/xml'

    return response

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
