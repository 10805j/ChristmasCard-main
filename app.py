import os
import random
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate

# Flask 앱 설정
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # 파일 업로드 경로
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 최대 파일 크기 16MB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///letters.db'  # SQLite 데이터베이스 설정
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'mysecretkey'  # flash 메시지 처리 위한 비밀 키 설정

# SQLAlchemy 객체 생성
db = SQLAlchemy(app)
migrate = Migrate(app, db)  # 마이그레이션 초기화

# 데이터베이스 모델 정의
class Letter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_name = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_filename = db.Column(db.String(100), nullable=True)
    date_sent = db.Column(db.DateTime, default=datetime.utcnow)
    likes = db.Column(db.Integer, default=0)  # 좋아요 수를 위한 필드 추가
    icon = db.Column(db.String(100), nullable=True)  # 랜덤 아이콘을 위한 필드 추가

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
            flash("편지 내용은 100자 이하로 작성해 주세요.", "error")
            return render_template('create_letter.html')

        # 파일 업로드가 없으면 이미지 없이 저장
        if file and allowed_file(file.filename):  # 파일이 있고, 허용된 파일인지 확인
            filename = secure_filename(file.filename)  # 안전한 파일명으로 변환
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))  # 파일 저장
            letter = Letter(sender_name=sender_name, content=content, image_filename=filename, icon=random.choice(icons))
        else:
            letter = Letter(sender_name=sender_name, content=content, icon=random.choice(icons))

        # 데이터베이스에 편지 저장 (Letter 모델을 사용)
        db.session.add(letter)
        db.session.commit()

        flash("편지가 성공적으로 작성되었습니다!", "success")
        return redirect(url_for('index'))  # 편지 작성 후, 목록 페이지로 리다이렉트

    return render_template('create_letter.html')

@app.route('/like_letter/<int:letter_id>', methods=['POST'])
def like_letter(letter_id):
    letter = Letter.query.get(letter_id)
    if letter:
        if letter.likes != None :
            letter.likes += 1  # 좋아요 수 증가
        else:
            letter.likes = 1

        db.session.commit()  # 변경 사항 커밋
    return redirect(url_for('index'))  # 홈으로 리디렉션

@app.route('/')
def index():
    sort_by = request.args.get('sort_by', 'newest')  # 기본 정렬 기준은 최신순
    if sort_by == 'likes':
        letters = Letter.query.order_by(Letter.likes.desc()).all()  # 좋아요 수 기준 정렬
    elif sort_by == 'oldest':
        letters = Letter.query.order_by(Letter.date_sent).all()  # 오래된 순
    elif sort_by == 'newest':
        letters = Letter.query.order_by(Letter.date_sent.desc()).all()  # 최신 순
    elif sort_by == 'random':
        letters = random.sample(Letter.query.all(), len(Letter.query.all()))  # 랜덤 추천
    else:
        letters = Letter.query.all()  # 기본값 (모든 편지 가져오기)

    return render_template('index.html', letters=letters)

@app.route('/view_image/<filename>')
def view_image(filename):
    return render_template('view_image.html', filename=filename)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 데이터베이스 테이블 생성
    app.run(debug=True)  # 디버그 모드를 활성화하여 오류 메시지 확인
