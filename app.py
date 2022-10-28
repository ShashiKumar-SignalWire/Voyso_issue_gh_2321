import os
from flask import Flask
from flask import render_template, flash, request, Response
import sqlite3
import json
from signalwire.voice_response import VoiceResponse, Redirect, Play, Enqueue
from signalwire.rest import Client as signalwire_client

app = Flask(__name__)
app.debug=True


project = os.getenv('PROJECT_ID')
token = os.getenv('REST_API_TOKEN')
space = os.getenv('SIGNALWIRE_SPACE')
sip_username =os.getenv('SIGNALWIRE_SIP_ENDPOINT_USERNAME')
sip_password= os.getenv('SIGNALWIRE_SIP_ENDPOINT_PASSWORD')
sip_uri = os.getenv('SIGNALWIRE_SIP_ENDPOINT_URI')
signalwire_number = os.getenv('SIGNALWIRE_NUMBER')
# read menus from json file
with open('config/config.json') as f:
     config = json.load(f)

@app.route("/new_call", methods=['GET','POST'])
def new_call():
    response = VoiceResponse()
    response.redirect('/enqueue')
    return Response(str(response), mimetype='text/xml')


@app.route("/enqueue", methods=['GET','POST'])
def enqueue():
    with sqlite3.connect(config['settings']['database_file']) as con:
        cur = con.cursor()
        cur.execute(
            "INSERT into queued_calls (from_no,to_no,call_sid) values (?,?,?)", [request.form["From"],request.form["To"],request.form["CallSid"]])
        con.commit()
    response = VoiceResponse()
    response.enqueue('support', wait_url='enqueue_wait_url_redirect')
    return Response(str(response), mimetype='text/xml')
@app.route("/enqueue_wait_url_redirect", methods=['GET','POST'])
def enqueue_wait_url_redirect():
    response = VoiceResponse()
    response.redirect('wait_url_play')
    return Response(str(response), mimetype='text/xml')


@app.route("/wait_url_play", methods=['GET','POST'])
def wait_url_play():
    response = VoiceResponse()
    response.play(url='https://d2hafg2emkw2gv.cloudfront.net/hold_music_urban_sunrise.mp3',loop=100)
    return Response(str(response), mimetype='text/xml')

@app.route('/queued_calls', )
def queued_calls():

    conn = sqlite3.connect(config['settings']['database_file'])
    conn.row_factory = sqlite3.Row
    curs = conn.cursor()
    curs.execute("SELECT * from queued_calls order by id desc limit 2")
    rows = curs.fetchall()
    return render_template("queued_calls.html", rows=rows)

@app.route('/take_call/<id>', )
def take_call(id):
    conn = sqlite3.connect(config['settings']['database_file'])
    conn.row_factory = sqlite3.Row
    curs = conn.cursor()
    curs.execute("SELECT * from queued_calls where  id=?",[id])
    row = curs.fetchone()
    return render_template("take_call.html", row=row,sip_username=str(sip_username),sip_password=str(sip_password),sip_uri=str(sip_uri))

@app.route("/call_web_client/<call_sid>", methods=['GET','POST'])
def call_web_client(call_sid):
    client = signalwire_client(project, token, signalwire_space_url = space+'.signalwire.com')
    call = client.calls.create(
        url='https://shashi-fs.signalwire.com/laml-bins/3bb52a90-fb14-4aee-a7da-00b785aebfca?conferenceName='+call_sid,
        to= 'sip:'+ sip_username+'@'+sip_uri,
        from_= signalwire_number
    )
    return call.sid

@app.route("/call_pstn_number/<call_sid>/<number>", methods=['GET','POST'])
def call_pstn_number(call_sid,number):
    client = signalwire_client(project, token, signalwire_space_url = space+'.signalwire.com')
    call = client.calls.create(
        url='https://shashi-fs.signalwire.com/laml-bins/3bb52a90-fb14-4aee-a7da-00b785aebfca?conferenceName='+call_sid,
        to= number,
        from_= signalwire_number
    )    
    return call.sid

@app.route("/update_caller_to_join_call/<call_sid>", methods=['GET','POST'])
def update_caller_to_join_call(call_sid):
    client = signalwire_client(project, token, signalwire_space_url = space+'.signalwire.com')  
    call = client.calls(call_sid).update(
        url='https://shashi-fs.signalwire.com/laml-bins/3bb52a90-fb14-4aee-a7da-00b785aebfca?conferenceName='+call_sid
    )
    return call.sid


if __name__ == "__main__":
  app.run(host='0.0.0.0',port=8080,threaded=True)


