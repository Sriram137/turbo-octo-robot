from flask import Flask, request, make_response, render_template, g
import plivo
import os
import redis


app = Flask(__name__)
auth_id = "MAN2QYMDI4NGJKOTFMNG"
auth_token = "MjQ5ZjI1NDZjM2JiYjU2MGMyNDc4MmEzZWY4MzM3"
music_file = "https://s3.amazonaws.com/plivocloud/Trumpet.mp3"
plivo_rest = plivo.RestAPI(auth_id, auth_token)
call_transfer_url_templ = "http://shrouded-lake-4745.herokuapp.com/transfer/%s"


def get_db():
    if not hasattr(g, 'redis_server'):
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
    return get_db().spop("agentPool")


def addAvailableAgent(agentId):
    get_db().sadd("agentPool", agentId)


def getPendingCall():
    return get_db().lpop("callList")


def addPendingCall(callId):
    print ("INSERTINGcccc", callId)
    get_db().rpush("callList", callId)


def assignCall(callId, agentId):
    get_db().set(callId, agentId)


@app.route('/agent/<agentId>')
def makeAgentAvailable(agentId):
    callId = getPendingCall()
    print (callId)
    if callId is not None:
        params = {
            'call_uuid': callId,
            'aleg_url': call_transfer_url_templ % agentId
        }
        response = plivo_rest.transfer_call(params)
        print (response)
    else:
        addAvailableAgent(agentId)
    return ""


@app.route('/transfer/<agentId>', methods=['POST'])
def handle_transer(agentId):
    try:
        print ("TRANSER REQUEST RECIEVED", agentId)
        agentSip = "sip:%s@phone.plivo.com" % agentId
        plivo_response = plivo.XML.Response()
        plivo_response.addDial().addUser(agentSip)
        return make_http_response(plivo_response)
    except Exception as e:
        print e


@app.route('/response/sip/route/', methods=['POST'])
def response_sip_route():
    try:
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

        plivo_response = plivo.XML.Response()

        agentId = getFreeAgent()

        print("Agent Id", agentId)
        if agentId is not None:
            agentSip = "sip:%s@phone.plivo.com" % agentId
            print ("agentSip", agentSip)
            print("Assigning call")
            plivo_response.addDial(callerName=caller_name).addUser(agentSip)
        else:
            print ("INSERTING", callUUID)
            addPendingCall(callUUID)
            plivo_response.addPlay(music_file, loop=0)
        return make_http_response(plivo_response)

    except Exception as e:
        print e


def make_http_response(plivo_response):
    print(plivo_response.to_xml())
    response = make_response(plivo_response.to_xml())
    response.headers['Content-Type'] = 'text/xml'

    return response


@app.route('/response/sip/hangup/', methods=['POST'])
def response_sip_hangup():
    # print(request)
    # print(request.form)
    # print("HANGUP")
    if request.method == 'POST':
        from_number = request.form.get('CLID', None)
        if from_number is None:
            from_number = request.form.get('From', '')
        #callUUID = request.form.get('CallUUID', '')
    else:
        return make_response('Method not allowed.')

    #agentId = getAgentIdForCall(callUUID)
    #deleteCallDetails(callId)
    return ""

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
