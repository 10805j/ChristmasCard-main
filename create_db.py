from app import app, db  # app과 db를 import합니다.

# 애플리케이션 컨텍스트를 사용하여 db.create_all() 호출
with app.app_context():
    db.create_all()  # 데이터베이스 테이블 생성
