from flask import Flask, render_template, session, redirect, url_for,request,jsonify
from flask import get_template_attribute
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, SelectField, BooleanField, IntegerField
from wtforms.validators import DataRequired
from StockWebUtility import MySqlObject
from StockWebUtility import StockUpdate
from flask_socketio import SocketIO, emit
import datetime
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
thread = None  

bootstrap = Bootstrap(app)
moment = Moment(app)

#turn the flask app into a socketio app
socketio = SocketIO(app)


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    example = RadioField('Label', choices=[('value','description'),('value_two','whatever')])
    submit = SubmitField('Submit')


class QueryForm(FlaskForm):
    QueryP1 = SelectField('Query Param1', choices=[('op0', 'price'),('op1', '5d_price'), ('op2', '20d_price'), ('op3', '60d_price')])
    QueryOP = SelectField('Query OP', choices=[('op1', 'Large'), ('op2', 'Small')])
    QueryP2 = SelectField('Query Param2', choices=[('op0', 'price'),('op1', '5d_price'), ('op2', '20d_price'), ('op3', '60d_price')])
    AndVolumn = BooleanField('And volumn')
    QueryVo = SelectField('Query Option', choices=[('op0', 'Over'),('op1', 'Over 2x'), ('op2', 'Over 3x')])
    submit = SubmitField('QueryData')

class UpdateForm(FlaskForm):
    Result = RadioField('Label', choices=[('v0','Update All'),('v1','Update 上市'),('v2','Update 上櫃')])
    UpdataFrom = IntegerField('Updata from')
    submit = SubmitField('QueryData')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/', methods=['GET', 'POST'])
def index():
    name = None
    result = None
    strQuery = None
#    form1 = NameForm()
    form = QueryForm()
    if form.validate_on_submit():
        QP1 = dict(form.QueryP1.choices).get(form.QueryP1.data)
        QOP = dict(form.QueryOP.choices).get(form.QueryOP.data)
        QP2 = dict(form.QueryP2.choices).get(form.QueryP2.data)
        strQuery = QP1 + " " + QOP + " " + QP2

        Mysqlobject = MySqlObject('TWSTOCKDB', 'twstock')
        Mysqlobject.ConnectDB()
        result = Mysqlobject.QueryCondiction(QP1, QOP, QP2)
#        result = Mysqlobject.Query5avOver20av()[0]
        query_result=result
        print(query_result)
    return render_template('Analyze.html', form=form, Query_result=result, Query_condiction=strQuery)

@socketio.on('connect')
def testconnect():
    print("receive io connect")    
    socketio.emit('log', 'socket server-client connect')
#    print("Progress update")
#    socketio.emit('Progress', '20/110')

@socketio.on('ConsoleAP_Connect')
def ConsoleCnt():
    print("Welcome Console AP")
    socketio.emit('Console_push', 'I see you, console AP')
    
#    print("Progress update")
#    socketio.emit('Progress', '20/110')


@socketio.on('AddWatch')
def handle_message(id):
    print('AddWatch id: ' + id)
    thisdict = dict(tablieid = id, name = "test")
    jasondata = json.dumps(thisdict)
    socketio.emit('Console_push_parson', jasondata)

@app.route('/Update')
def Update():
    form = UpdateForm()
    return render_template('index.html',form=form)

@app.route('/Test')
def Test():
    return render_template('test.html')

def background_thread(param1, param2):
      
      print("start query")
      socketio.emit('Progress', '40')
      
      Mysqlobject = MySqlObject('TWSTOCKDB', 'twstock')
#      Mysqlobject.ConnectDB(sockioCallBack)
      Mysqlobject.ConnectDBWCB(socketio)
      StockObject = StockUpdate(Mysqlobject)
      
      if param1 == 'v0' :          
          StockObject.UpdateAll('上市', 0, socketio)
          StockObject.UpdateAll('上櫃', 0, socketio)
      elif param1 == 'v1':            
          StockObject.UpdateAll('上市', param2, socketio)
      else:          
          StockObject.UpdateAll('上櫃', param2, socketio)


@app.route('/QueryData2',methods = ['POST', 'GET'])
def QueryData2():

    form = UpdateForm()

    if form.validate_on_submit():
        global thread
        if thread is None:
            thread = socketio.start_background_task(background_thread, form.Result.data,form.UpdataFrom.data)
    return render_template('index.html',form=form)

@app.route('/QueryData',methods = ['POST', 'GET'])
def QueryData():

    form = UpdateForm()

    if form.validate_on_submit():
         print("start query")
         socketio.emit('log', 'start query')
         Mysqlobject = MySqlObject('TWSTOCKDB', 'twstock')
         Mysqlobject.ConnectDB()
         StockObject = StockUpdate(Mysqlobject)
 
         if form.Result.data == 'v0' :
            StockObject.UpdateAll('上市', 0)
            StockObject.UpdateAll('上櫃', 0)
         elif form.Result.data == 'v1':           
             StockObject.UpdateAll('上市', form.UpdataFrom.data)
         else:
             StockObject.UpdateAll('上櫃', form.UpdataFrom.data)
 

    return render_template('index.html',form=form)


#app.run('localhost', 5100)
if __name__ == '__main__':
    socketio.run(app,'localhost',5000)