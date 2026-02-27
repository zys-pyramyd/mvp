
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
    GRAINS_CEREALS = "grains_cereals"
    BEANS_LEGUMES = "beans_legumes"
    FISH_MEAT = "fish_meat"
    SPICES_VEGETABLES = "spices_vegetables" 
    TUBERS_ROOTS = "tubers_roots"
    FLOUR_FLAKES = "flour_flakes"
    DRINKS_BEVERAGE = "drinks_beverage"
    SNACKS_CONFECTIONARIES = "snacks_confectionaries"
    SWEETS_SUGAR = "sweets_sugar"
    FARM_INPUTS = "farm_inputs"
    OTHER = "other"

# Subcategories
class GrainsCerealsSubcategory(str, Enum):
    MAIZE = "maize"
    RICE = "rice"
    WHEAT = "wheat"
    OAT = "oat"
    BARLEY = "barley"
    SORGHUM = "sorghum"
    MILLET = "millet"
    RYE = "rye"
    TRITICALE = "triticale"

class BeansLegumesSubcategory(str, Enum):
    LENTILS = "lentils"
    PEAS = "peas"
    BEANS = "beans"
    BROAD_BEANS = "broad_beans"
    GROUNDNUT = "groundnut"
    SOYBEANS = "soybeans"

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
    YAM = "yam"
    CASSAVA = "cassava"
    SWEET_POTATO = "sweet_potato"
    CHINESE_YAM = "chinese_yam"
    TARO = "taro"
    POTATO = "potato"
    CARROTS = "carrots"
    TURNIPS = "turnips"
    PARSNIPS = "parsnips"
    RADISH = "radish"
    CELERIAC = "celeriac"
    GINGER = "ginger"
    TURMERIC = "turmeric"
    BEETS = "beets"
    BURDOCK_ROOT = "burdock_root"

class FlourFlakesSubcategory(str, Enum):
    ALL_PURPOSE_FLOUR = "all_purpose_flour"
    YAM_FLOUR = "yam_flour"
    CASSAVA_FLAKES_GARRI = "cassava_flakes_garri"
    CASSAVA_FLOUR = "cassava_flour"
    BREAD_FLOUR = "bread_flour"
    CAKE_FLOUR = "cake_flour"
    PASTRY_FLOUR = "pastry_flour"
    WHOLE_WHEAT = "whole_wheat"
    SELF_RISING_FLOUR = "self_rising_flour"
    SEMOLINA_FLOUR = "semolina_flour"
    NUT_FLOUR = "nut_flour"
    COCONUT_FLOUR = "coconut_flour"
    RICE_FLOUR = "rice_flour"
    OTHERS = "others"

class DrinksBeverageSubcategory(str, Enum):
    MILK = "milk"
    CHOCOLATE_DRINKS = "chocolate_drinks"
    WATER = "water"
    SOFT_DRINKS_CARBONATED = "soft_drinks_carbonated"
    JUICES_SMOOTHIES = "juices_smoothies"
    HOT_BEVERAGE = "hot_beverage"
    ENERGY_DRINKS = "energy_drinks"
    HEALTH_DRINKS = "health_drinks"
    DAIRY_PLANT_BASED = "dairy_plant_based"
    CORDIALS_SQUASH = "cordials_squash"

class SnacksConfectionariesSubcategory(str, Enum):
    CHOCOLATES = "chocolates"
    CANDY_GUMMY = "candy_gummy"
    CHIPS_CRISPS = "chips_crisps"
    PRETZELS_CRACKERS = "pretzels_crackers"
    POPCORN = "popcorn"
    NUTS_SEEDS = "nuts_seeds"
    DRIED_FRUITS_TRAIL_MIX = "dried_fruits_trail_mix"
    GRANOLA_ENERGY_BARS = "granola_energy_bars"
    COOKIES_BISCUITS = "cookies_biscuits"
    SNACK_CAKES_PASTRIES = "snack_cakes_pastries"

class SweetsSugarSubcategory(str, Enum):
    SUGAR = "sugar"
    HONEY = "honey"
    DATES = "dates"
    AGAVE = "agave"
    ARTIFICIAL_SWEETENER = "artificial_sweetener"
    SYRUPS = "syrups"

class ProcessingLevel(str, Enum):
    UNPROCESSED = "unprocessed"
    PROCESSED = "processed"
    ULTRAPROCESSED = "ultraprocessed"

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    HELD_IN_ESCROW = "held_in_escrow"
    DISPUTED = "disputed"
    PREORDER_PENDING = "preorder_pending"

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
