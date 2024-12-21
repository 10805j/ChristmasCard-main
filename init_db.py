from app import create_app, db  # app.py에서 Flask 애플리케이션과 db 객체를 가져옵니다.

app = create_app()  # Flask 애플리케이션을 초기화합니다.

with app.app_context():  # 앱 컨텍스트를 활성화합니다.
    db.create_all()  # 데이터베이스에 테이블을 생성합니다.
    print("Database tables created")
