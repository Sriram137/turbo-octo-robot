from flask import Flask, request, make_response, render_template, g
import plivo
import os
import redis


app = Flask(__name__)

music_file = "https://s3.amazonaws.com/plivocloud/Trumpet.mp3"


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


def getPendingCall(callId):
    return get_db().lpop("callList")


def addPendingCall(callId):
    get_db().rpush("callList", callId)


def assignCall(callId, agentId):
    get_db().set(callId, agentId)


# def getAgentIdForCall(callId):
#     return g.redis_server.get(callId)


# def deleteCallDetails(callId):
#     g.redis_server.delete(callId)


@app.route('/agent/<agentId>')
def makeAgentAvailable(agentId):
    addAvailableAgent(agentId)
    return ""


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

    plivo_response = plivo.XML.Response()

    agentId = getFreeAgent()

    print("Agent Id", agentId)
    if agentId is not None:
        agentSip = "sip:%s@phone.plivo.com" % agentId
        print ("agentSip", agentSip)
        # assignCall(callUUID, agentId)
        print("Assigning call")
        plivo_response.addDial(caller_name=caller_name).addUser(agentSip)
    else:
        addPendingCall(callUUID)
        plivo_response.addPlay(music_file, {"loop": 0})

    print(plivo_response.to_xml())
    response = make_response(plivo_response.to_xml())
    response.headers['Content-Type'] = 'text/xml'

    return response


@app.route('/response/sip/hangup/', methods=['POST'])
def response_sip_hangup():
    print(request)
    print(request.form)
    print("HANGUP")
    if request.method == 'POST':
        from_number = request.form.get('CLID', None)
        if from_number is None:
            from_number = request.form.get('From', '')
        #callUUID = request.form.get('CallUUID', '')
    else:
        return make_response('Method not allowed.')

    #agentId = getAgentIdForCall(callUUID)
    #deleteCallDetails(callId)
    return

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
