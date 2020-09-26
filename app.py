from flask import Flask, Blueprint, render_template
from flask_bootstrap import Bootstrap
from models.wordsegment.word_seg import wordseg

app = Flask(__name__, 
    template_folder='templates', 
    static_folder='templates/static',
    static_url_path='/static')

Bootstrap(app)
app.register_blueprint(wordseg, url_prefix='/wordseg')
  
@app.route('/', methods=['GET'])
def app_index():
    return render_template('home_index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=13599)