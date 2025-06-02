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
)  # output = functions_mapper["get_receiver_id_by_receiver_phone_number"](
#     llm_output="Hello world",
#     backend_output=CardsByPhoneNumberResponse(
#         cards=[
#             {
#                 "pan": "kkkkkkxxxxxxyyyyyy",
#                 "name": "Aslon",
#                 "processing": "HUMO",
#                 "mask": "*************1234",
#             },
#             {
#                 "pan": "kkkkkkxxxxxxyyasdfafsdfyyyy",
#                 "name": "Aslon",
#                 "processing": "HUMO",
#                 "mask": "*************1235",
#             },
#             {
#                 "pan": "kkkkkkxxxxxxyyasdfafsdfyyyy",
#                 "name": "Aslon",
#                 "processing": "HUMO",
#                 "mask": "*************1236",
#             },
#         ]
#     ).model_dump(),
#     version="v3",
# )


functions_mapper["get_categories"](
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

functions_mapper["get_suppliers_by_category"](
    llm_output="Hello world",
    backend_output=SupplierByCategoryResponse(
        payload=[
            Supplier(
                id=1,
                name="Supplier 1",
                categoryId=1,
                s3Url="https://img.icons8.com/?size=100&id=64062&format=png&color=000000",
            ),
            Supplier(
                id=2,
                name="Supplier 2",
                categoryId=1,
                s3Url="https://img.icons8.com/?size=100&id=64062&format=png&color=000000",
            ),
            Supplier(
                id=3,
                name="Supplier 3",
                categoryId=1,
                s3Url="https://img.icons8.com/?size=100&id=64062&format=png&color=000000",
            ),
            Supplier(
                id=4,
                name="Supplier 4",
                categoryId=1,
                s3Url="https://img.icons8.com/?size=100&id=64062&format=png&color=000000",
            ),
        ]
    ).model_dump(),
    version="v3",
)

output = CategoriesResponse(
    payload=[
        Category(
            id=1,
            name="Category 1",
            s3Url="https://img.icons8.com/?size=100&id=64062&format=png&color=000000",
            imagePath="https://img.icons8.com/?size=100&id=64062&format=png&color=000000",
        ),
    ],
)
with open("test_response.json", "w") as f:
    json.dump(output.model_dump(), f, ensure_ascii=False, indent=2)
