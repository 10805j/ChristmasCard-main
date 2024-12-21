import os
import random
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Flask 앱 설정
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # 파일 업로드 경로
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 최대 파일 크기 16MB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///letters.db'  # SQLite 데이터베이스 설정
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# SQLAlchemy 객체 생성
db = SQLAlchemy(app)

# 데이터베이스 모델 정의
class Letter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_name = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_filename = db.Column(db.String(100), nullable=True)
    date_sent = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Letter {self.sender_name}>'

# 허용된 파일 확장자 설정
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# 파일이 허용된 확장자인지 확인하는 함수
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 업로드 폴더가 존재하지 않으면 생성
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# 랜덤 아이콘 리스트 (아이콘 파일명은 '1.png', '2.png', 등으로 설정)
icons = ['1.png', '2.png', '3.png', '4.png', '5.png', '6.png', '7.png']

@app.route('/create_letter', methods=['GET', 'POST'])
def create_letter():
    if request.method == 'POST':
        # POST 요청에 파일이 포함되었는지 확인
        file = request.files.get('image')
        sender_name = request.form['sender_name']
        content = request.form['content']

        # 편지 내용 글자수 100자 이하로 제한
        if len(content) > 100:
            error_message = "편지 내용은 100자 이하로 작성해 주세요."
            return render_template('create_letter.html', error_message=error_message)

        # 파일 업로드가 없으면 이미지 없이 저장
        if file and allowed_file(file.filename):  # 파일이 있고, 허용된 파일인지 확인
            filename = secure_filename(file.filename)  # 안전한 파일명으로 변환
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))  # 파일 저장
            letter = Letter(sender_name=sender_name, content=content, image_filename=filename)
        else:
            letter = Letter(sender_name=sender_name, content=content)

        # 데이터베이스에 편지 저장 (Letter 모델을 사용)
        db.session.add(letter)
        db.session.commit()

        return redirect(url_for('index'))  # 편지 작성 후, 목록 페이지로 리다이렉트

    return render_template('create_letter.html')

@app.route('/')
def index():
    letters = Letter.query.all()  # 데이터베이스에서 모든 편지 가져오기
    
    # 각 편지에 대해 랜덤으로 1개의 아이콘 선택
    for letter in letters:
        letter.icon = random.choice(icons)  # 랜덤 아이콘 1개 선택
    
    return render_template('index.html', letters=letters)

@app.route('/view_image/<filename>')
def view_image(filename):
    return render_template('view_image.html', filename=filename)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 데이터베이스 테이블 생성
    app.run(debug=True)  # 디버그 모드를 활성화하여 오류 메시지 확인
