from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Portfolio(Base):
    __tablename__ = 'portfolios'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    holdings = relationship("Holding", back_populates="portfolio", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Portfolio(name='{self.name}', total_holdings={len(self.holdings)})>"

class Holding(Base):
    __tablename__ = 'holdings'

    id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, ForeignKey('portfolios.id'), nullable=False)
    ticker = Column(String(10), nullable=False)
    quantity = Column(Float, nullable=False)
    avg_cost = Column(Float, default=0.0)
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="holdings")
    
    def current_value(self, current_price: float) -> float:
        return self.quantity * current_price

    def __repr__(self):
        return f"<Holding(ticker='{self.ticker}', qty={self.quantity})>"

class StockData(Base):
    """Cached stock information from Seeking Alpha."""
    __tablename__ = 'stock_data'

    ticker = Column(String(10), primary_key=True)
    full_name = Column(String)
    last_price = Column(Float)
    currency = Column(String(3), default='USD')
    daily_change_pct = Column(Float)
    pe_ratio = Column(Float)
    dividend_yield = Column(Float)
    sector = Column(String(50))
    rating = Column(String(20))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<StockData(ticker='{self.ticker}', price={self.last_price})>"

class LogEntry(Base):
    """Persisted application logs."""
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    level = Column(String(10))
    module = Column(String(50))
    message = Column(Text)
