# demo_sorter.py

def sort_products(products, key):
    """
    Sorts a list of products based on a specified key.

    :param products: List of product dictionaries.
    :param key: The key to sort the products by.
    :return: Sorted list of products.
    """
    return sorted(products, key=lambda x: x[key])

# Sample array of products
products = [
    {"name": "Product A", "price": 30.00},
    {"name": "Product B", "price": 20.00},
    {"name": "Product C", "price": 25.00},
]

# Sorting products by price
sorted_products_by_price = sort_products(products, "price")

# Displaying sorted products by price
print("Sorted products by price:")
for product in sorted_products_by_price:
    print(f"Name: {product['name']}, Price: {product['price']}")

# Additional demonstration of sorting by name
sorted_products_by_name = sort_products(products, "name")

# Displaying sorted products by name
print("\nSorted products by name:")
for product in sorted_products_by_name:
    print(f"Name: {product['name']}, Price: {product['price']}")
