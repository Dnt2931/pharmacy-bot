from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class MedicineCreate(BaseModel):
    name: str
    category: str = "General"
    description: str = ""
    price: float
    profit_margin: float = 0.0
    stock: int = 0
    unit: str = "pcs"
    is_active: bool = True

class Medicine(MedicineCreate):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class OrderItemCreate(BaseModel):
    medicine_id: int
    quantity: int

class OrderCreate(BaseModel):
    doctor_telegram_id: str
    doctor_name: str
    doctor_phone: str = ""
    notes: str = ""
    items: List[OrderItemCreate]

class OrderItem(BaseModel):
    id: int
    medicine_id: int
    quantity: int
    unit_price: float
    class Config:
        from_attributes = True

class Order(BaseModel):
    id: int
    doctor_telegram_id: str
    doctor_name: str
    doctor_phone: str
    total_amount: float
    status: str
    notes: str
    created_at: datetime
    items: List[OrderItem] = []
    class Config:
        from_attributes = True

class StatusUpdate(BaseModel):
    status: str
