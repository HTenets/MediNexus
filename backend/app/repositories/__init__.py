"""Data-access layer over the relational database.

Each repository function takes an explicit AsyncSession so callers control
transactions and session lifecycle.
"""
