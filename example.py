from flask import Flask, request, make_response
import plivo

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return ""


@app.route('/response/sip/route/', methods=['GET', 'POST'])
def response_sip_route():
    if request.method == 'GET':
        to_number = request.args.get('To', None)
        from_number = request.args.get('CLID', None)
        if from_number is None:
            from_number = request.args.get('From', '')
        caller_name = request.args.get('CallerName', '')
    elif request.method == 'POST':
        to_number = request.form.get('To', None)
        from_number = request.form.get('CLID', None)
        if from_number is None:
            from_number = request.form.get('From', '')
        caller_name = request.form.get('CallerName', '')
    else:
        return make_response('Method not allowed.')

    response = plivo.Response()
    if not to_number:
        response.addHangup()
    else:
        if to_number[:4] == 'sip:':
            response.addDial(callerName=caller_name).addUser(to_number)
        else:
            response.addDial(callerId=from_number).addNumber(to_number)

    response = make_response(response.to_xml())
    response.headers['Content-Type'] = 'text/xml'

    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0')
