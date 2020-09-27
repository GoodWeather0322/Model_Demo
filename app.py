from flask import Flask, Blueprint, render_template
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO
from models.wordsegment.word_seg import wordseg
from models.newsgenerate.news_gen import newsgen
from models.create_socket import socketio

app = Flask(__name__, 
    template_folder='templates', 
    static_folder='templates/static',
    static_url_path='/static')

app.config['JSON_AS_ASCII'] = False
app.config['SECRET_KEY'] = '13gr4og-#ped'

Bootstrap(app)
app.register_blueprint(wordseg, url_prefix='/wordseg')
app.register_blueprint(newsgen, url_prefix='/newsgen')

socketio.init_app(app)
  
@app.route('/', methods=['GET'])
def app_index():
    return render_template('home_index.html')

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=13599)