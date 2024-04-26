from flask import Flask, render_template, request
from models import LVQ

# Create a flask app
app = Flask(
  __name__,
  template_folder='templates',
  static_folder='static'
)

# Index page
@app.route('/')
def hello():
  return render_template('index.html')

@app.route('/result', methods=['POST'])
def result():
  if request.method=='POST':
    umur = request.form['umur']
    jk = request.form['jk']
    ap = request.form['ap']
    af = request.form['af']
    mp = request.form['mp']
    dtest=[umur,jk,ap,af,mp,0]
    lvq = LVQ(dtest,maxepoch=3,learnRate=0.1,lr_reducer=0.1)
    lvq.normalize()
    lvq.train()
    lvq.test()
    return render_template('result.html',lvq=lvq)
  return render_template('index.html')
  
@app.route('/test',methods=['GET','POST'])
def test():
  # if request.method=='POST':
  umur = request.form['umur']
  jk = request.form['jk']
  ap = request.form['ap']
  af = request.form['af']
  mp = request.form['mp']
  out=[umur,jk,ap,af,mp]
  return render_template('test.html',text=out)

if __name__ == '__main__':
  # Run the Flask app
  app.run(
	host='0.0.0.0',
	debug=True,
	port=8080
  )
