from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import pytz

Base = declarative_base()

# Define the Bangladesh timezone
bangladesh_tz = pytz.timezone('Asia/Dhaka')

# Get the current time in Bangladesh timezone
def get_bangladesh_time():
    return datetime.now(bangladesh_tz)

class UploadedImage(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True, index=True)
    image_path = Column(String(50), nullable=False)
    class_name = Column(String(50), nullable=False)
    upload_date = Column(DateTime, default=get_bangladesh_time)