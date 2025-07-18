import json
from functions_to_format.functions import functions_mapper
from tool_call_models.cards import CardsByPhoneNumberResponse
from tool_call_models.paynet import (
    CategoriesResponse,
    SupplierByCategoryResponse,
    SupplierFieldsResponse,
    Supplier,
    Category,
    SuppliersField,
    FieldOptions,
)


# functions_mapper = {
#     "get_balance": get_balance, # ready
#     "get_weather": get_weather,
#     "get_news": get_news,
#     "get_products": get_products, # ready
#     "search_products": search_products, # ready
#     "get_notifications": get_notifications,
#     "get_contact": get_contact, # not ready
#     "chatbot_answer": chatbot_answer, # ready
#     "unauthorized_response": unauthorized_response,
#     "get_number_by_receiver_name": get_number_by_receiver_name, # ready or not -- IDK
#     "get_receiver_id_by_reciver_phone_number": get_receiver_id_by_receiver_phone_number, # not required
#     "get_receiver_id_by_receiver_phone_number": get_receiver_id_by_receiver_phone_number, # not required
#     "get_categories": get_categories, # ready
#     "get_fields_of_supplier": get_fields_of_supplier, # not ready
#     "get_suppliers_by_category": get_suppliers_by_category, # ready
#     "start_page_widget": start_page_widget, # not ready
#     "send_money_to_someone_via_card": send_money_to_someone_via_card #  not ready
#     "get_home_balances": get_home_balances, # ready
# }


# get categories json
get_categories = functions_mapper["get_categories"](
    llm_output="Hello world",
    backend_output=CategoriesResponse(
        payload=[
            Category(
                id=1,
                name="Category 1",
                s3Url="https://img.icons8.com/?size=100&id=64062&format=png&color=000000",
                imagePath="https://img.icons8.com/?size=100&id=64062&format=png&color=000000",
            ),
            Category(
                id=2,
                name="Category 2",
                s3Url="https://img.icons8.com/?size=100&id=64062&format=png&color=000000",
                imagePath="https://img.icons8.com/?size=100&id=64062&format=png&color=000000",
            ),
            Category(
                id=3,
                name="Category 3",
                s3Url="https://img.icons8.com/?size=100&id=64062&format=png&color=000000",
                imagePath="https://img.icons8.com/?size=100&id=64062&format=png&color=000000",
            ),
            Category(
                id=4,
                name="Category 4",
                s3Url="https://img.icons8.com/?size=100&id=64062&format=png&color=000000",
                imagePath="https://img.icons8.com/?size=100&id=64062&format=png&color=000000",
            ),
        ]
    ).model_dump(),
    version="v3",
)


# get_categories - show categories widget
from tool_call_models.paynet import CategoriesResponse, Category

categories = [
    {
        "id": 1,
        "name": "Uyali aloqa",
        "imagePath": None,
        "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671056545-57d63349-cdc1-4438-982f-23ae508dd782",
    },
    {
        "id": 2,
        "name": "Uy telefoni",
        "imagePath": None,
        "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671056505-ad89d454-3f47-4e68-bc26-74fd2d32c5e2",
    },
    {
        "id": 3,
        "name": "Internet",
        "imagePath": None,
        "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671056578-a950e105-f0f2-4b8f-af05-766d730593e9",
    },
    {
        "id": 4,
        "name": "Xizmatlar",
        "imagePath": None,
        "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671056264-e1c665dc-ed0e-4617-9835-ddac232a1ffe",
    },
    {
        "id": 5,
        "name": "Televidenie",
        "imagePath": None,
        "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671056745-0899c2dc-f194-41e2-9a30-b1c16d45ef3e",
    },
    {
        "id": 6,
        "name": "Taxi",
        "imagePath": None,
        "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671056657-eb712c52-a9ee-4293-b6ff-38eaaa052401",
    },
    {
        "id": 7,
        "name": "Kommunal xizmatlar",
        "imagePath": None,
        "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671056712-902ee66f-9ad1-4d73-940a-c5f174b01ae0",
    },
    {
        "id": 9,
        "name": "Online platformalar",
        "imagePath": None,
        "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671057830-ef6d3711-ff17-44b3-9107-1a3e8f6085aa",
    },
    {
        "id": 11,
        "name": "Ta`lim",
        "imagePath": None,
        "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671058625-3b117d55-22a0-42e6-aed0-a48c995586c3",
    },
    {
        "id": 18,
        "name": "Xayriya",
        "imagePath": None,
        "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671056624-ea0e5f25-4998-4e49-9129-f8f6fed1fe94",
    },
    {
        "id": 23,
        "name": "Muddatli to'lovlar",
        "imagePath": None,
        "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671057272-e9da9dfc-c49b-47eb-9592-a201866ab5fe",
    },
    {
        "id": 26,
        "name": "Sport",
        "imagePath": None,
        "s3Url": "https://s3.smartbank.uz/mobile-ui/1ff1f772-fae4-44f3-b5d2-a20554966b5c",
    },
    {
        "id": 27,
        "name": "Mehmonxonalar va turizm",
        "imagePath": None,
        "s3Url": "https://s3.smartbank.uz/mobile-ui/58cbc39e-3906-4c97-b8ec-af9ece6d0d23",
    },
    {
        "id": 28,
        "name": "Sug'urta",
        "imagePath": None,
        "s3Url": "https://s3.smartbank.uz/mobile-ui/5ab0d1bc-c3e7-4098-bd03-449ea84e74c5",
    },
    {
        "id": 29,
        "name": "Tibbiyot",
        "imagePath": None,
        "s3Url": "https://s3.smartbank.uz/mobile-ui/2c365621-57e2-4a6a-b895-f76716bb0033",
    },
    {
        "id": 30,
        "name": "Yuridik xizmatlar",
        "imagePath": None,
        "s3Url": "https://s3.smartbank.uz/mobile-ui/4edc3627-310d-4773-a2f6-8e358b4f5e07",
    },
]
categories = CategoriesResponse(
    payload=[Category(**c) for c in categories]
).model_dump()

get_categories = functions_mapper["get_categories"](
    llm_output="Hello world",
    backend_output=categories,
    version="v3",
)

## get_fields_of_supplier - to show fiellds of supplier
from tool_call_models.paynet import Field, SupplierFieldsResponse

paylad = {
    "checkUp": True,
    "checkUpWithResponse": True,
    "checkUpAfterPayment": False,
    "fieldList": [
        {
            "identName": "paymentNo1",
            "name": "TETK",
            "order": 1,
            "type": "COMBOBOX",
            "pattern": "FILIALS",
            "minValue": None,
            "maxValue": None,
            "fieldSize": 5,
            "isMain": None,
            "valueList": [
                str({"value": 6204, "name": "Olot TETK"}),
                str({"value": 6207, "name": "Buxoro TETK"}),
                str({"value": 6212, "name": "Vobkent TETK"}),
                str({"value": 6215, "name": "G'ijduvon TETK"}),
                str({"value": 6219, "name": "Kogon TETK"}),
                str({"value": 6230, "name": "Qorako'l TETK"}),
                str({"value": 6232, "name": "Qorovulbozor TETK"}),
                str({"value": 6240, "name": "Peshku TETK"}),
                str({"value": 6242, "name": "Romitan TETK"}),
                str({"value": 6246, "name": "Jondor TETK"}),
                str({"value": 6258, "name": "Shofirkon TETK"}),
                str({"value": 6401, "name": "Buxoro ShETK"}),
            ],
        },
        {
            "identName": "amount",
            "name": "Summa",
            "order": 3,
            "type": "MONEY",
            "pattern": None,
            "minValue": 500,
            "maxValue": 5000000,
            "fieldSize": 12,
            "isMain": None,
            "valueList": [],
        },
        {
            "identName": "paymentNo",
            "name": "Shaxsiy raqami",
            "order": 2,
            "type": "STRING",
            "pattern": None,
            "minValue": None,
            "maxValue": None,
            "fieldSize": 8,
            "isMain": True,
            "valueList": [],
        },
    ],
}
fields = SupplierFieldsResponse(payload=SuppliersField(**paylad)).model_dump()

get_fields_of_supplier = functions_mapper["get_fields_of_supplier"](
    llm_output="Hello world",
    backend_output=fields,
    version="v3",
)


## get suppliers by category json - get_suppliers_by_category
suppliers = {
    "payload": [
        {
            "id": 932,
            "name": "Elektr energiya",
            "categoryId": 7,
            "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671090211-0992368e-af07-49ff-a384-0a4641b377be",
        },
        {
            "id": 933,
            "name": "Tabiiy gaz",
            "categoryId": 7,
            "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671091467-5f760f9b-67a6-41a5-8ffe-3117a6da8618",
        },
        {
            "id": 933,
            "name": "Suyultirilgan Gaz",
            "categoryId": 7,
            "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671091550-b8aee728-c600-4c05-b1b5-3f131eba9bf0",
        },
        {
            "id": 934,
            "name": "HGT Gaz servis",
            "categoryId": 7,
            "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671091596-2b6e458e-c8a9-4430-a912-3706321f9f2d",
        },
        {
            "id": 935,
            "name": "Chiqindilarni olib ketish",
            "categoryId": 7,
            "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671091635-55cb00c7-2efb-454c-8ca5-330626a2a9fb",
        },
        {
            "id": 936,
            "name": "Veolia Energy Tashkent",
            "categoryId": 7,
            "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671091668-b3758fa8-ef28-4a62-b2bf-11e260014581",
        },
    ]
}
get_suppliers_by_category = functions_mapper["get_suppliers_by_category"](
    llm_output="Hello world",
    backend_output=SupplierByCategoryResponse(**suppliers).model_dump(),
    version="v3",
)

from tool_call_models.home_balance import HomeBalance, HomeBalanceDetails

# home balance widget
get_home_balances = functions_mapper["get_home_balances"](
    llm_output="Hello world",
    backend_output=HomeBalance(
        **{
            "homeName": "г. Ташкент, Учтепинский район, кв. 31, Д",
            "gas": {"balance": 55470000, "details": {"2080": 1676000, "13839": 554700}},
            "electricity": {"balance": 251758006, "details": {"13842": 2517586}},
            "garbage": {"balance": 490000000, "details": {"13841": 4900000}},
            "coldWater": {"balance": 278190000, "details": {"13840": 2781900}},
            "internet": {"balance": 100000000, "details": {"13843": 1000000}},
        },
    ).model_dump(),
    version="v3",
)


from tool_call_models.cards import CardsBalanceResponse

# card balance test - build_balance_ui
balance = {
    "custNo": "60005982",
    "phoneNumber": "998331191213",
    "firstname": "ASLONXO‘JA",
    "middlename": "JALOLIDDINOVICH",
    "lastname": "HAMIDOV",
    "birthDate": "2001-12-13",
    "pinfl": "51312016860023",
    "createdAt": "2024-04-09T20:37:13.764699",
    "cardList": [
        {
            "panMask": "7478",
            "panToken": "87a4be2d-7115-4d63-bf93-d76450b2b1fc",
            "requestId": "87a4be2d-7115-4d63-bf93-d76450b2b1fc",
            "pan": "************7478",
            "expiry": "2604",
            "bankIssuer": "SmartBank",
            "uzcardToken": None,
            "processingSystem": "humo",
            "salaryAmount": 500000000,
            "isVerified": True,
            "createdAt": "2024-04-09T20:42:48.535911",
            "cardDetails": {
                "cardDetailsId": 7846,
                "cardName": "Smartbank Virtual",
                "cardColor": "0006",
                "cardIsPrimary": False,
            },
            "cardBalance": {"balance": "9222", "status": 0},
            "isVirtual": True,
            "bankIcon": {
                "bankLogo": "https://s3.smartbank.uz/bank-logos/smart.png",
                "bankLogoMini": "https://s3.smartbank.uz/bank-logos/smart-mini.png",
                "bankWhiteLogo": "https://s3.smartbank.uz/bank-logos/smart-white.png",
                "bankWhiteLogoMini": "https://s3.smartbank.uz/bank-logos/smart-mini-white.png",
            },
        },
        {
            "panMask": "5289",
            "panToken": "ea8dc9ea-7aba-4bbc-b219-c37f8b6dcfd5",
            "requestId": "ea8dc9ea-7aba-4bbc-b219-c37f8b6dcfd5",
            "pan": "************5289",
            "expiry": "2602",
            "bankIssuer": "Kapital",
            "uzcardToken": None,
            "processingSystem": "humo",
            "salaryAmount": 500000000,
            "isVerified": True,
            "createdAt": "2024-07-02T10:55:27.266157",
            "cardDetails": {
                "cardDetailsId": 23192,
                "cardName": "kapital",
                "cardColor": "0000",
                "cardIsPrimary": False,
            },
            "cardBalance": {"balance": "0", "status": 0},
            "isVirtual": False,
            "bankIcon": {
                "bankLogo": "https://s3.smartbank.uz/bank-logos/kapital.png",
                "bankLogoMini": "https://s3.smartbank.uz/bank-logos/kapital-mini.png",
                "bankWhiteLogo": "https://s3.smartbank.uz/bank-logos/kapital-white.png",
                "bankWhiteLogoMini": "https://s3.smartbank.uz/bank-logos/kapital-mini-white.png",
            },
        },
        {
            "panMask": "7704",
            "panToken": "8e96ef48-6c03-431a-bc7b-081af3c98d1d",
            "requestId": "8e96ef48-6c03-431a-bc7b-081af3c98d1d",
            "pan": "************7704",
            "expiry": "2907",
            "bankIssuer": "SmartBank",
            "uzcardToken": None,
            "processingSystem": "humo",
            "salaryAmount": 500000000,
            "isVerified": True,
            "createdAt": "2024-07-16T11:34:28.535018",
            "cardDetails": {
                "cardDetailsId": 42946,
                "cardName": "Smartbank fiz",
                "cardColor": "0000",
                "cardIsPrimary": False,
            },
            "cardBalance": {"balance": "2219330", "status": 0},
            "isVirtual": False,
            "bankIcon": {
                "bankLogo": "https://s3.smartbank.uz/bank-logos/smart.png",
                "bankLogoMini": "https://s3.smartbank.uz/bank-logos/smart-mini.png",
                "bankWhiteLogo": "https://s3.smartbank.uz/bank-logos/smart-white.png",
                "bankWhiteLogoMini": "https://s3.smartbank.uz/bank-logos/smart-mini-white.png",
            },
        },
        {
            "panMask": "9710",
            "panToken": "c39cef39-07ab-4439-8c2b-25d07a912c28",
            "requestId": "c39cef39-07ab-4439-8c2b-25d07a912c28",
            "pan": "************9710",
            "expiry": "2910",
            "bankIssuer": "BRB",
            "uzcardToken": None,
            "processingSystem": "humo",
            "salaryAmount": 500000000,
            "isVerified": True,
            "createdAt": "2024-10-23T13:00:01.056936",
            "cardDetails": {
                "cardDetailsId": 166412,
                "cardName": "brb",
                "cardColor": "0000",
                "cardIsPrimary": False,
            },
            "cardBalance": {"balance": "50000", "status": 0},
            "isVirtual": False,
            "bankIcon": {
                "bankLogo": "https://s3.smartbank.uz/bank-logos/brb.png",
                "bankLogoMini": "https://s3.smartbank.uz/bank-logos/brb-mini.png",
                "bankWhiteLogo": "https://s3.smartbank.uz/bank-logos/brb-white.png",
                "bankWhiteLogoMini": "https://s3.smartbank.uz/bank-logos/brb-mini-white.png",
            },
        },
    ],
}
get_balance = functions_mapper["get_balance"](
    llm_output="Hello world",
    backend_output=CardsBalanceResponse(**balance).model_dump(),
    version="v3",
)


# get_products --- show products widget
from tool_call_models.smartbazar import (
    SearchProductsResponse,
    ProductItem,
    Meta,
    MainCategory,
    MainCategoryParent,
    Brand,
    Offer,
)


category = MainCategory(
    id=1,
    name="Category 1",
    slug="category-1",
    depth=1,
    parent=MainCategoryParent(id=None, name=None, slug=None, depth=None, parent=None),
    exist_children=False,
    product_count=10,
    order=1,
    status=1,
    created_at="2024-01-01T00:00:00",
    updated_at="2024-01-01T00:00:00",
)
offer = Offer(
    id=1,
    original_price=1000000,
    price=900000,
    three_month_price=350000,
    six_month_price=200000,
    nine_month_price=150000,
    twelve_month_price=100000,
    eighteen_month_price=80000,
    discount=True,
    discount_percent=10,
    discount_start_at="2024-01-01T00:00:00",
    discount_expire_at="2024-12-31T23:59:59",
    merchant=None,
    status={"active": True},
    market_type="b2c",
)
product = ProductItem(
    id=123,
    remote_id="ABC123",
    name_ru="Смартфон Samsung Galaxy S21",
    name_uz="Samsung Galaxy S21 смартфони",
    slug="samsung-galaxy-s21",
    brand=Brand(
        id=1,
        name="Samsung",
        name_ru="Samsung",
        name_uz="Samsung",
        default_lang="uz",
    ),
    main_categories=[category],
    short_name_uz="Galaxy S21",
    short_name_ru="Galaxy S21",
    main_image={
        "mobile": "https://i5.walmartimages.com/seo/Pre-Owned-Samsung-Galaxy-S21-5G-SM-G991U1-128GB-Pink-US-Model-Factory-Unlocked-Cell-Phone-Refurbished-Like-New_268fd090-9e5d-4287-98f8-4ad4ac93de54.71fd3099cec626bd02fc726424299241.jpeg?odnWidth=180&odnHeight=180&odnBg=ffffff",
        "desktop": "https://i5.walmartimages.com/seo/Pre-Owned-Samsung-Galaxy-S21-5G-SM-G991U1-128GB-Pink-US-Model-Factory-Unlocked-Cell-Phone-Refurbished-Like-New_268fd090-9e5d-4287-98f8-4ad4ac93de54.71fd3099cec626bd02fc726424299241.jpeg?odnWidth=180&odnHeight=180&odnBg=ffffff",
    },
    created_at="2024-01-15T10:30:00",
    updated_at="2024-01-16T15:45:00",
    count=50,
    tracking=True,
    offers=[offer, offer, offer],
    status={"active": True},
    view_count=1000,
    order_count=25,
    like_count=150,
    rate=4,
    cancelled_count=2,
)

get_products = functions_mapper["get_products"](
    llm_output="Hello world",
    backend_output=SearchProductsResponse(
        items=[
            product,
            product,
            product,
            product,
        ],
        meta=Meta(
            current_page=1, from_=1, last_page=1, path=None, per_page=1, to=1, total=1
        ),
    ).model_dump(),
)


# text widget test
build_text_widget = functions_mapper["chatbot_answer"](
    llm_output="""Вот баланс ваших карт и счетов, хотите произвести оплату за телефон или перевод? 
    Привет! Я Бек, умный голосовой помощник.
    Расскажу про наши продукты и сервисы, а так же помогу с оплатами и переводами. 
    Просто нажмите на меня и спросите что вас интересует, например:
""",
    backend_output=None,
    version="v3",
)


# get number by receiver name ---- to show contacts after and update the content using custom action of divkit
get_number_by_receiver_name = functions_mapper["get_number_by_receiver_name"](
    llm_output="Aslon",
    backend_output={"receiver_name": "Aslon"},
    version="v3",
)
