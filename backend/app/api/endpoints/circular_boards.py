# kairanban.py

from datetime import date, datetime
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, Date, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker

# ------------------------------
# データベース設定
# ------------------------------
SQLALCHEMY_DATABASE_URL = "sqlite:///./kairanban.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


# ------------------------------
# モデル定義 (SQLAlchemy)
# ------------------------------
class Member(Base):
    __tablename__ = "members"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)

    # 回覧板投稿とのリレーション
    circulars = relationship("CircularBoard", back_populates="author")


class CircularBoard(Base):
    __tablename__ = "circular_board"
    id = Column(Integer, primary_key=True, index=True)
    posted_at = Column(Date, nullable=False)
    author_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)

    author = relationship("Member", back_populates="circulars")


# テーブル作成
Base.metadata.create_all(bind=engine)


# ------------------------------
# Pydantic スキーマ定義
# ------------------------------
class MemberSchema(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        orm_mode = True


class CircularBase(BaseModel):
    posted_at: date
    author_id: int
    title: str
    content: str


class CircularCreate(CircularBase):
    pass


class Circular(CircularBase):
    id: int
    author: MemberSchema  # リレーション先を含める場合

    class Config:
        orm_mode = True


# ------------------------------
# DBセッション依存関係
# ------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ------------------------------
# CRUD 操作
# ------------------------------
def get_circulars(db: Session, skip: int = 0, limit: int = 100) -> List[CircularBoard]:
    return db.query(CircularBoard).offset(skip).limit(limit).all()


def get_circular(db: Session, circular_id: int) -> Optional[CircularBoard]:
    return db.query(CircularBoard).filter(CircularBoard.id == circular_id).first()


def create_circular(db: Session, circular: CircularCreate) -> CircularBoard:
    db_obj = CircularBoard(
        posted_at=circular.posted_at,
        author_id=circular.author_id,
        title=circular.title,
        content=circular.content,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


# ------------------------------
# FastAPI アプリケーション
# ------------------------------
app = FastAPI(title="町内会 回覧板 API")


@app.get("/circular_boards", response_model=List[Circular])
def read_circulars(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    回覧板一覧を取得（ページネーション対応）
    """
    return get_circulars(db, skip=skip, limit=limit)


@app.get("/circular_boards/{circular_id}", response_model=Circular)
def read_circular(circular_id: int, db: Session = Depends(get_db)):
    """
    指定 ID の回覧板を取得
    """
    db_obj = get_circular(db, circular_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="CircularBoard not found")
    return db_obj


@app.post("/circular_boards", response_model=Circular, status_code=201)
def create_new_circular(circular: CircularCreate, db: Session = Depends(get_db)):
    """
    新しい回覧板を作成
    """
    # author_id の存在チェック
    author = db.query(Member).filter(Member.id == circular.author_id).first()
    if not author:
        raise HTTPException(status_code=400, detail="Invalid author_id")
    return create_circular(db, circular)
