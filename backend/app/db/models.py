# ✅ models.py
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float
from .session import Base  # use Base from session.py
import datetime

class Document(Base):
    __tablename__ = "documents"
    
    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String,  index=True,   nullable=True)
    filename    = Column(String,  unique=True,  index=True)
    file_path   = Column(String,  unique=True)
    content     = Column(Text,    nullable=True)
    status      = Column(String,  default="new")
    author      = Column(String,  nullable=True)  # uploader/author information
    source      = Column(String,  nullable=True)  # document source or metadata
    doc_type    = Column(String,  nullable=True)  # type/category of document
    ocr_text    = Column(Text,    nullable=True)  # full OCR extracted text
    upload_time = Column(DateTime, default=datetime.datetime.utcnow)  # timestamp

    # New relationship to chunks
    chunks     = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")
    citations   = relationship("Citation", back_populates="document")
    query_logs  = relationship("QueryLog", back_populates="document")

class Chunk(Base):
    __tablename__ = "chunks"

    id          = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), index=True)
    chunk_id    = Column(String, index=True)  # e.g. "doc1_0", "doc1_50"
    text        = Column(Text, nullable=False)
    start_char  = Column(Integer, nullable=True)  # character start in full doc text
    end_char    = Column(Integer, nullable=True)  # character end in full doc text

    document    = relationship("Document", back_populates="chunks")

class Citation(Base):
    __tablename__ = "citations"
    
    id          = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    text        = Column(Text)

    document    = relationship("Document", back_populates="citations")

class QueryLog(Base):
    __tablename__ = "query_logs"

    id            = Column(Integer, primary_key=True, index=True)
    timestamp     = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    question      = Column(Text,    nullable=False)
    document_id   = Column(Integer, ForeignKey("documents.id"))
    document_name = Column(String)
    vector_path   = Column(String)
    answer        = Column(Text)
    citations     = Column(Text)
    themes        = Column(Text)

    document      = relationship("Document", back_populates="query_logs")
