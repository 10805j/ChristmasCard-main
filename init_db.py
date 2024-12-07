from app import db

# 데이터베이스 및 테이블 생성
def init_db():
    db.create_all()

if __name__ == '__main__':
    init_db()
