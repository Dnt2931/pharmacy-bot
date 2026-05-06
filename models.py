from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Medicine(Base):
    __tablename__ = "medicines"

    id           = Column(Integer, primary_key=True, index=True)
    name         = Column(String, nullable=False)
    category     = Column(String, default="General")
    description  = Column(Text, default="")
    price        = Column(Float, nullable=False)
    profit_margin = Column(Float, default=0.0)   # percentage %
    stock        = Column(Integer, default=0)
    unit         = Column(String, default="pcs")  # pcs, box, strip
    is_active    = Column(Boolean, default=True)
    created_at   = Column(DateTime, default=datetime.utcnow)

    order_items  = relationship("OrderItem", back_populates="medicine")


class Order(Base):
    __tablename__ = "orders"

    id                  = Column(Integer, primary_key=True, index=True)
    doctor_telegram_id  = Column(String, nullable=False)
    doctor_name         = Column(String, nullable=False)
    doctor_phone        = Column(String, default="")
    total_amount        = Column(Float, default=0.0)
    status              = Column(String, default="pending")
    # pending | processing | delivered | cancelled
    notes               = Column(Text, default="")
    created_at          = Column(DateTime, default=datetime.utcnow)

    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id           = Column(Integer, primary_key=True, index=True)
    order_id     = Column(Integer, ForeignKey("orders.id"))
    medicine_id  = Column(Integer, ForeignKey("medicines.id"))
    quantity     = Column(Integer, nullable=False)
    unit_price   = Column(Float, nullable=False)

    order    = relationship("Order", back_populates="items")
    medicine = relationship("Medicine", back_populates="order_items")
