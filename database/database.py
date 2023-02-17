from schemas.schemas import Product
from schemas.schemas import Category


products_db = [
    Product(id=0,
            name="MacBook Pro 2023 M2 Max",
            full_name="Apple Laptop MacBook Pro 2023 con chip M2 Max",
            price=3499.00,
            image="https://m.media-amazon.com/images/I/61fd2oCrvyL._AC_SL1500_.jpg",
            category=Category.LAPTOP),
    Product(id=1,
            name="SAMSUNG Smart TV 32 pulgadas",
            full_name="SAMSUNG Smart TV Class QLED Q60A de 32 pulgadas - 4K UHD",
            price=497.99,
            image="https://m.media-amazon.com/images/I/71G6eW8H8hL._AC_SL1500_.jpg",
            category=Category.ELECTRONICOS),
    Product(id=2,
            name="Herman Miller Embody Chair",
            full_name="Herman Miller Embody Chair",
            price=1830.00,
            image="https://images.hermanmiller.group/m/37278be690af2129/W-HM_Pound_Ridge_10_EmbodyOffice_029-Hero_20200304105920002.png",
            category=Category.OFICINA)
]
