from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import database, models, schemas
from datetime import datetime

app = FastAPI(title="Pharmacy Ordering System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ── MEDICINES ──────────────────────────────────────────────
@app.get("/medicines", response_model=List[schemas.Medicine])
def get_medicines(search: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Medicine).filter(models.Medicine.is_active == True)
    if search:
        query = query.filter(models.Medicine.name.ilike(f"%{search}%"))
    return query.all()

@app.post("/medicines", response_model=schemas.Medicine)
def create_medicine(medicine: schemas.MedicineCreate, db: Session = Depends(get_db)):
    db_med = models.Medicine(**medicine.dict())
    db.add(db_med)
    db.commit()
    db.refresh(db_med)
    return db_med

@app.put("/medicines/{med_id}", response_model=schemas.Medicine)
def update_medicine(med_id: int, medicine: schemas.MedicineCreate, db: Session = Depends(get_db)):
    db_med = db.query(models.Medicine).filter(models.Medicine.id == med_id).first()
    if not db_med:
        raise HTTPException(status_code=404, detail="Medicine not found")
    for key, value in medicine.dict().items():
        setattr(db_med, key, value)
    db.commit()
    db.refresh(db_med)
    return db_med

@app.delete("/medicines/{med_id}")
def delete_medicine(med_id: int, db: Session = Depends(get_db)):
    db_med = db.query(models.Medicine).filter(models.Medicine.id == med_id).first()
    if not db_med:
        raise HTTPException(status_code=404, detail="Medicine not found")
    db_med.is_active = False
    db.commit()
    return {"message": "Medicine deactivated"}

# ── ORDERS ─────────────────────────────────────────────────
@app.post("/orders", response_model=schemas.Order)
async def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    # Create order
    db_order = models.Order(
        doctor_telegram_id=order.doctor_telegram_id,
        doctor_name=order.doctor_name,
        doctor_phone=order.doctor_phone,
        notes=order.notes,
        status="pending",
        created_at=datetime.utcnow()
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # Add order items + update stock
    total = 0
    for item in order.items:
        med = db.query(models.Medicine).filter(models.Medicine.id == item.medicine_id).first()
        if not med:
            raise HTTPException(status_code=404, detail=f"Medicine {item.medicine_id} not found")
        if med.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {med.name}")

        db_item = models.OrderItem(
            order_id=db_order.id,
            medicine_id=item.medicine_id,
            quantity=item.quantity,
            unit_price=med.price
        )
        db.add(db_item)
        med.stock -= item.quantity
        total += med.price * item.quantity

    db_order.total_amount = total
    db.commit()
    db.refresh(db_order)

    # Send Telegram notification to pharmacy
    await notify_pharmacy(db_order, order.items, db)

    return db_order

@app.get("/orders", response_model=List[schemas.Order])
def get_orders(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Order)
    if status:
        query = query.filter(models.Order.status == status)
    return query.order_by(models.Order.created_at.desc()).all()

@app.get("/orders/{doctor_id}", response_model=List[schemas.Order])
def get_doctor_orders(doctor_id: str, db: Session = Depends(get_db)):
    return db.query(models.Order).filter(
        models.Order.doctor_telegram_id == doctor_id
    ).order_by(models.Order.created_at.desc()).all()

@app.put("/orders/{order_id}/status")
def update_order_status(order_id: int, status: schemas.StatusUpdate, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = status.status
    db.commit()
    return {"message": f"Order {order_id} updated to {status.status}"}

# ── NOTIFY PHARMACY ────────────────────────────────────────
async def notify_pharmacy(order, items, db: Session):
    import os, httpx
    bot_token = os.getenv("BOT_TOKEN")
    pharmacy_chat_id = os.getenv("PHARMACY_CHAT_ID")
    if not bot_token or not pharmacy_chat_id:
        return

    lines = [
        f"🆕 *New Order #{order.id}*",
        f"👨‍⚕️ Doctor: {order.doctor_name}",
        f"📞 Phone: {order.doctor_phone}",
        f"",
        f"📦 *Items:*"
    ]
    for item in items:
        med = db.query(models.Medicine).filter(models.Medicine.id == item.medicine_id).first()
        if med:
            lines.append(f"  • {med.name} x{item.quantity} = Rs.{med.price * item.quantity:,.0f}")

    lines += [
        f"",
        f"💰 *Total: Rs.{order.total_amount:,.0f}*",
        f"📝 Notes: {order.notes or 'None'}",
    ]

    msg = "\n".join(lines)
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    async with httpx.AsyncClient() as client:
        await client.post(url, json={
            "chat_id": pharmacy_chat_id,
            "text": msg,
            "parse_mode": "Markdown"
        })

# ── HEALTH ─────────────────────────────────────────────────
@app.get("/")
def health():
    return {"status": "Pharmacy API running ✅"}
