
from enum import Enum

class UserRole(str, Enum):
    FARMER = "farmer"
    AGENT = "agent"
    BUSINESS = "business"
    PERSONAL = "personal"
    ADMIN = "admin" # Implicitly used

class BusinessCategory(str, Enum):
    FOOD_SERVICING = "food_servicing"
    FOOD_PROCESSOR = "food_processor" 
    FARM_INPUT = "farm_input"
    FINTECH = "fintech"
    AGRICULTURE = "agriculture"
    SUPPLIER = "supplier"
    OTHERS = "others"

class BusinessRegistrationStatus(str, Enum):
    REGISTERED = "registered"
    UNREGISTERED = "unregistered"

class KYCStatus(str, Enum):
    NOT_STARTED = "not_started"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class ProductCategory(str, Enum):
    GRAINS_LEGUMES = "grains_legumes"
    FISH_MEAT = "fish_meat"
    SPICES_VEGETABLES = "spices_vegetables" 
    TUBERS_ROOTS = "tubers_roots"

# Subcategories
class GrainsLegumesSubcategory(str, Enum):
    RICE = "rice"
    WHEAT = "wheat"
    CORN_MAIZE = "corn_maize"
    BEANS = "beans"
    COWPEAS = "cowpeas"
    GROUNDNUTS = "groundnuts"
    SOYBEANS = "soybeans"
    MILLET = "millet"

class FishMeatSubcategory(str, Enum):
    FRESH_FISH = "fresh_fish"
    DRIED_FISH = "dried_fish"
    POULTRY = "poultry"
    BEEF = "beef"
    GOAT_MUTTON = "goat_mutton"
    PORK = "pork"
    SNAILS = "snails"

class SpicesVegetablesSubcategory(str, Enum):
    LEAFY_VEGETABLES = "leafy_vegetables"
    PEPPERS = "peppers"
    TOMATOES = "tomatoes"
    ONIONS = "onions"
    GINGER_GARLIC = "ginger_garlic"
    HERBS_SPICES = "herbs_spices"
    OKRA = "okra"
    CUCUMBER = "cucumber"

class TubersRootsSubcategory(str, Enum):
    YAMS = "yams"
    CASSAVA = "cassava"
    SWEET_POTATOES = "sweet_potatoes"
    IRISH_POTATOES = "irish_potatoes"
    COCOYAMS = "cocoyams"
    PLANTAINS = "plantains"
    DRIED_FISH = "dried_fish"
    FROZEN_FISH = "frozen_fish"
    FRESH_MEAT = "fresh_meat"
    PROCESSED_MEAT = "processed_meat"
    POULTRY = "poultry"

class PepperVegetablesSubcategory(str, Enum):
    PEPPERS = "peppers"
    LEAFY_VEGETABLES = "leafy_vegetables"
    ROOT_VEGETABLES = "root_vegetables"
    ONIONS_GARLIC = "onions_garlic"
    TOMATOES = "tomatoes"
    HERBS_SPICES = "herbs_spices"

class ProcessingLevel(str, Enum):
    NOT_PROCESSED = "not_processed"
    SEMI_PROCESSED = "semi_processed"
    PROCESSED = "processed"

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class PreOrderStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published" 
    PARTIAL_PAID = "partial_paid"
    AWAITING_DELIVERY = "awaiting_delivery"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class DriverStatus(str, Enum):
    OFFLINE = "offline"
    ONLINE = "online"
    BUSY = "busy"
    ON_DELIVERY = "on_delivery"

class DeliveryStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    ACCEPTED = "accepted" 
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class VehicleType(str, Enum):
    MOTORCYCLE = "motorcycle"
    CAR = "car"
    VAN = "van"
    TRUCK = "truck"
    BICYCLE = "bicycle"

class DriverSubscriptionStatus(str, Enum):
    TRIAL = "trial"
    ACTIVE = "active"
    EXPIRED = "expired"
    SUSPENDED = "suspended"

class RatingType(str, Enum):
    USER_RATING = "user_rating"
    PRODUCT_RATING = "product_rating"
    DRIVER_RATING = "driver_rating"
    ORDER_RATING = "order_rating"

class TransactionType(str, Enum):
    WALLET_FUNDING = "wallet_funding"
    WALLET_WITHDRAWAL = "wallet_withdrawal" 
    ORDER_PAYMENT = "order_payment"
    ORDER_REFUND = "order_refund"
    GIFT_CARD_PURCHASE = "gift_card_purchase"
    GIFT_CARD_REDEMPTION = "gift_card_redemption"
    COMMISSION_PAYMENT = "commission_payment"
    DRIVER_PAYMENT = "driver_payment"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class FundingMethod(str, Enum):
    BANK_TRANSFER = "bank_transfer"
    DEBIT_CARD = "debit_card"
    USSD = "ussd"
    BANK_DEPOSIT = "bank_deposit"
    GIFT_CARD = "gift_card"

class GiftCardStatus(str, Enum):
    ACTIVE = "active"
    REDEEMED = "redeemed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class CommunityRole(str, Enum):
    CREATOR = "creator"
    ADMIN = "admin"
    MEMBER = "member"

class CommunityPrivacy(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    RESTRICTED = "restricted"

class BusinessType(str, Enum):
    LIMITED = "ltd"
    NGO = "ngo"
    PLC = "plc"
    PARTNERSHIP = "partnership"
    SOLE_PROPRIETORSHIP = "sole_proprietorship"
    
class IdentificationType(str, Enum):
    NIN = "nin"
    BVN = "bvn"
    NATIONAL_ID = "national_id"
    VOTERS_CARD = "voters_card"
    DRIVERS_LICENSE = "drivers_license"

class DocumentType(str, Enum):
    CERTIFICATE_OF_INCORPORATION = "certificate_of_incorporation"
    TIN_CERTIFICATE = "tin_certificate"
    UTILITY_BILL = "utility_bill"
    NATIONAL_ID_DOC = "national_id_doc"
    HEADSHOT_PHOTO = "headshot_photo"

NIGERIAN_STATES = [
    "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa",
    "Benue", "Borno", "Cross River", "Delta", "Ebonyi", "Edo",
    "Ekiti", "Enugu", "FCT Abuja", "Gombe", "Imo", "Jigawa",
    "Kaduna", "Kano", "Katsina", "Kebbi", "Kogi", "Kwara",
    "Lagos", "Nasarawa", "Niger", "Ogun", "Ondo", "Osun",
    "Oyo", "Plateau", "Rivers", "Sokoto", "Taraba", "Yobe", "Zamfara"
]
