from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Reader
from ..schemas import ReaderCreate

router = APIRouter(prefix="/readers", tags=["Readers"])


@router.post("/")
def create_reader(reader: ReaderCreate, db: Session = Depends(get_db)):
    new_reader = Reader(**reader.dict())
    db.add(new_reader)
    db.commit()
    db.refresh(new_reader)
    return new_reader


@router.get("/")
def get_readers(db: Session = Depends(get_db)):
    return db.query(Reader).all()


@router.get("/{reader_id}")
def get_reader(reader_id: int, db: Session = Depends(get_db)):
    reader = db.query(Reader).filter(Reader.id == reader_id).first()
    if not reader:
        raise HTTPException(status_code=404, detail="Reader not found")
    return reader


@router.delete("/{reader_id}")
def delete_reader(reader_id: int, db: Session = Depends(get_db)):
    reader = db.query(Reader).filter(Reader.id == reader_id).first()
    if not reader:
        raise HTTPException(status_code=404, detail="Reader not found")
    db.delete(reader)
    db.commit()
    return {"message": "Reader deleted"}
