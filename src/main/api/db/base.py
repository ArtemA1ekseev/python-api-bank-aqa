from sqlalchemy.orm import declarative_base

"""
Это называется Declarative Base (или просто Base). 
Именно от него наследуются все модели (классы), 
которые затем сопоставляются с таблицами в базе данных.
"""
Base = declarative_base()