import pytest
import os
from sahelper.database.session import init_db, SessionLocal
from sahelper.database.models import Portfolio, Holding

def test_package_structure():
    """Verify all necessary __init__.py files exist."""
    dirs = ['', 'database', 'ui', 'services', 'utils']
    for d in dirs:
        path = os.path.join('sahelper', d, '__init__.py')
        assert os.path.exists(path), f"Missing {path}"

def test_db_initialization():
    """Verify database and tables are created."""
    init_db()
    assert os.path.exists('sahelper_data.db')

def test_model_crud():
    """Verify basic CRUD operations on models."""
    init_db()
    with SessionLocal() as session:
        # Create
        p = Portfolio(name="Test Portfolio", description="JUnit Test")
        session.add(p)
        session.commit()
        
        # Read
        p_db = session.query(Portfolio).filter_by(name="Test Portfolio").first()
        assert p_db is not None
        assert p_db.description == "JUnit Test"
        
        # Update
        p_db.description = "Updated"
        session.commit()
        assert session.query(Portfolio).filter_by(name="Test Portfolio").first().description == "Updated"
        
        # Delete
        session.delete(p_db)
        session.commit()
        assert session.query(Portfolio).filter_by(name="Test Portfolio").first() is None

def test_holding_requires_portfolio():
    """Verify that a Holding cannot be created without a valid Portfolio ID."""
    from sqlalchemy.exc import IntegrityError
    init_db()
    with SessionLocal() as session:
        h = Holding(ticker="MSFT", quantity=5, avg_cost=300.0)
        session.add(h)
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()
