# tests/test_token_blacklist_model.py

from datetime import UTC, datetime
from secure_logout.secure_logout_schema import TokenBlacklist



def test_create_token_blacklist_entry(db):

    entry = TokenBlacklist(
        token_signature="abc123",
        blacklisted_on=datetime.now(UTC)
    )

    db.add(entry)
    db.commit()
    db.refresh(entry)

    assert entry.id is not None
    assert entry.token_signature == "abc123"
    assert isinstance(entry.blacklisted_on, datetime)


def test_query_token_blacklist_entry(db):
    # Insert test data
    entry = TokenBlacklist(
        token_signature="abc123",
        blacklisted_on=datetime.now(UTC)
    )
    db.add(entry)
    db.commit()

    # Now query
    result = db.query(TokenBlacklist).filter_by(token_signature="abc123").first()

    assert result is not None
    assert result.token_signature == "abc123"
