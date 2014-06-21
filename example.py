from flask import Flask, request, make_response, render_template
import plivo
import os
import redis


g = g
app = Flask(__name__)


def get_db():
    if hasattr(g, 'redis_server'):
        g.redis_server = connect_db()
    return g.redis_server


def connect_db():
    """Connects to the specific database."""
    redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
    redis_server = redis.from_url(redis_url)
    return redis_server


@app.route('/')
def index():
    return render_template("web_taker.html")

def getFreeAgent():
    return g.redis_server


@app.route('/response/sip/route/', methods=['POST'])
def response_sip_route():
    print(request)
    print(request.form)
    print("OVER")
    if request.method == 'POST':
        from_number = request.form.get('CLID', None)
        if from_number is None:
            from_number = request.form.get('From', '')
        caller_name = request.form.get('CallerName', '')
        callUUID = request.form.get('CallUUID', '')
    else:
        return make_response('Method not allowed.')

    response = plivo.XML.Response()

    to_number = "sip:elricl140620163139@phone.plivo.com"
    print("4 level")
    if not to_number:
        response.addHangup()
    else:
        response.addDial(callerName=caller_name).addUser(to_number)
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
