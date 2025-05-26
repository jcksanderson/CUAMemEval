import json

def json_to_item_price_dictionary(filepath):
    """
    Reads a JSON file containing a list of items and converts it into a dictionary
    where keys are item names and values are their prices.

    Args:
        filepath (str): The path to the JSON file.

    Returns:
        dict: A dictionary with item names as keys and prices as values.
              Returns an empty dictionary if the file is not found,
              the JSON is malformed, or an error occurs.
    """
    item_price_dict = {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f) # Load the JSON data from the file

            if not isinstance(data, list):
                print(f"Error: JSON data in '{filepath}' is not a list.")
                return {}

            for item in data:
                if isinstance(item, dict) and 'name' in item and 'price' in item:
                    name = item['name']
                    price = item['price']
                    item_price_dict[name] = price
                else:
                    print(f"Warning: Skipping item due to missing 'name' or 'price', or incorrect format: {item}")
            return item_price_dict

    except FileNotFoundError:
        print(f"Error: File not found at '{filepath}'")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{filepath}'. Check file format.")
        return {}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {}

if __name__ == "__main__":
    # Update to use the correct path for the benchmark
    json_filepath = "../../amazon/data/products.json"

    print(f"Attempting to read product data from: '{json_filepath}'")

    product_prices = json_to_item_price_dictionary(json_filepath)

    if product_prices:
        print(product_prices)
    else:
        print(f"\nCould not load or process data from '{json_filepath}'. Please check previous error messages.")

   
