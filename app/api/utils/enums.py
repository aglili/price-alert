from enum import Enum


class ListingStatus(Enum):
    AVAILABLE = "available"
    SOLD = "sold"
    EXPIRED = "expired"
    PENDING = "pending"
