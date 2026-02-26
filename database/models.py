from datetime import datetime
import enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    BigInteger,
    DateTime,
    ForeignKey,
    Float,
    Boolean,
    Enum,
    Table
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


# ASSOCIATION TABLE (Many-to-Many)

user_cars = Table(
    "user_cars",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("car_id", Integer, ForeignKey("cars.id"))
)


#  USER ROLE ENUM

class UserRole(enum.Enum):
    user = "user"
    admin = "admin"


# USERS

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    full_name = Column(String, nullable=True)

    role = Column(
        Enum(UserRole, name="user_role"),
        default=UserRole.user,
        nullable=False
    )
    
    created_at = Column(DateTime, default=datetime.utcnow)

    cars = relationship(
        "Car",
        secondary=user_cars,
        back_populates="owners"
    )

    orders = relationship("Order", back_populates="user")


# CARS

class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True)
    plate_number = Column(String, unique=True, index=True, nullable=False)
    brand = Column(String, nullable=True)
    color = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    owners = relationship(
        "User",
        secondary=user_cars,
        back_populates="cars"
    )

    orders = relationship("Order", back_populates="car")


# WASHERS

class Washer(Base):
    __tablename__ = "washers"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=True)
    full_name = Column(String, nullable=True)
    active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    orders = relationship("Order", back_populates="washer")


# ORDER STATUS ENUM

class OrderStatus(enum.Enum):
    washing = "washing"
    done = "done"
    cancelled = "cancelled"


# ORDERS

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)

    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    washer_id = Column(Integer, ForeignKey("washers.id"), nullable=True)

    status = Column(
        Enum(OrderStatus, name="order_status"),
        default=OrderStatus.washing,
        nullable=False
    )

    estimated_time = Column(DateTime, nullable=True)
    price = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="orders")
    car = relationship("Car", back_populates="orders")
    washer = relationship("Washer", back_populates="orders")


# SERVICES

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)