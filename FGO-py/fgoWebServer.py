import json
from flask import Flask,redirect,render_template,request,url_for
from zmq import device
import fgoKernel
from fgoLogging import getLogger
from fgoIniParser import IniParser

logger=getLogger('fgo.Web')
teamup=IniParser('fgoTeamup.ini')
with open('fgoConfig.json','r')as f:
    config=json.load(f)
app=Flask(__name__,static_folder='fgoWebUI', template_folder='fgoWebUI')

@app.route('/')
def root():
    return redirect('/index')

@app.route('/index')
def index():
    return render_template('index.html',teamups=teamup.sections(),config=config,device=fgoKernel.device.name)

@app.route('/api/connect',methods=['POST'])
def connect():
    fgoKernel.device=fgoKernel.Device(request.form['serial'])
    return fgoKernel.device.name

@app.route('/api/teamup/load',methods=['POST'])
def teamupLoad():
    return {i:eval(j)for i,j in teamup[request.form['teamName']].items()}

@app.route('/api/teamup/save',methods=['POST'])
def teamupSave():
    teamup[request.form['teamName']]=json.loads(request.form['data'])
    with open('fgoTeamup.ini','w')as f:
        teamup.write(f)
    return ''

@app.route('/api/apply',methods=['POST'])
def apply():
    data=json.loads(request.form['data'])
    fgoKernel.Main.teamIndex=data['teamIndex']
    fgoKernel.Turn.skillInfo=data['skillInfo']
    fgoKernel.Turn.houguInfo=data['houguInfo']
    fgoKernel.Turn.masterSkill=data['masterSkill']
    return ''

@app.route('/api/run/<action>',methods=['POST'])
def run(action):
    if not fgoKernel.device.avaliable:
        return 'Device not avaliable'
    getattr(fgoKernel,action)(**{i:int(j)for i,j in request.form})()
    return 'Done'


def main():
    app.run(host='0.0.0.0')