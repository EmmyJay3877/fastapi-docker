from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Identity, NUMERIC, Sequence
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False)
    image = Column(String)
    price = Column(NUMERIC(12, 2), nullable=False)
    available = Column(String(), server_default='AVAILABLE')
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, 
    server_default=text('now()'))
    admin_id = Column(Integer, ForeignKey("admin.id", ondelete="CASCADE"), 
    nullable=False)

    admin = relationship("Admin", back_populates="items")
    orders = relationship("OrderItem", back_populates="item")

# association table
class OrderItem(Base):
    __tablename__ = "orderitems"
    id = Column(Integer, Sequence('orderitems_id_seq'), primary_key=True)
    item_id = Column(Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False)
    total_price = Column(NUMERIC(12, 2), nullable=False)
    order_date = Column(TIMESTAMP(timezone=True), nullable=False, 
    server_default=text('now()'))

    order = relationship("Order", back_populates="item_association")
    item = relationship("Item", back_populates="orders")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(), nullable=False, server_default='PENDING')
    order_date = Column(TIMESTAMP(timezone=True), nullable=False, 
    server_default=text('now()'))

    item_association = relationship("OrderItem", back_populates="order")

    # where item_association is an instance of OrderItems model and item is a feild on the Orderitem model
    items = association_proxy("item_association", "item")
    customer = relationship("Customer", back_populates="orders")

class Admin(Base):
    __tablename__ = "admin"
    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String(), nullable=False, unique=True)
    email = Column(String(), nullable=False, unique=True) #unique, so cant have 2 admins with same emails
    password = Column(String(), nullable=False)
    is_verified = Column(Boolean, server_default='False')
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, 
    server_default=text('now()'))
    items = relationship("Item", back_populates="admin")

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, Identity(start=100, always=True), primary_key=True, nullable=False)
    role = Column(String(), server_default="CUSTOMER")
    username = Column(String(), nullable=False, unique=True)
    email = Column(String(), nullable=False, unique=True) #unique, so cant have 2 customers with same emails
    password = Column(String(), nullable=False)
    code = Column(String(), unique=True, nullable=True)
    is_verified = Column(Boolean, server_default='False')
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, 
    server_default=text('now()'))
    orders = relationship("Order", back_populates="customer")
    profile = relationship("Profile", backref="customer", uselist=False)
    history = relationship("History", backref="customer", uselist=False)

class Profile(Base):
    __tablename__ = "profiles"
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), primary_key=True)
    phone_number = Column(String(20), nullable=False)
    city = Column(String(), nullable=False)
    region = Column(String(), nullable=False)

class History(Base):
    __tablename__ = "history"
    id = Column(Integer, primary_key=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"))
    cu_history = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, 
    server_default=text('now()'))


class Notificaton(Base):
    __tablename__ = "notification"
    id = Column(Integer, primary_key=True, nullable=False)
    _notification = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, 
    server_default=text('now()'))

class New_notification_count(Base):
    __tablename__ = "new_notification_count"
    id = Column(Integer, primary_key=True, nullable=False)
    _new_notification_count = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, 
    server_default=text('now()'))

