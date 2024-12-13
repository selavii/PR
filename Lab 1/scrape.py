import requests
from bs4 import BeautifulSoup
from functools import reduce
from datetime import datetime, timezone


url = 'https://maximum.md/ro/telefoane-si-gadgeturi/telefoane-si-comunicatii/smartphoneuri/'


response = requests.get(url)

def scrape_func(text):
    soup = BeautifulSoup(text, 'html.parser')
    products = soup.find_all('div', class_='js-content product__item')

    product_list = []

    for product in products[:5]:
        name_tag = product.find('div', class_='product__item__title')
        name = name_tag.get_text(strip=True) if name_tag else "No name"

        price_tag = product.find('div', class_='product__item__price-current')
        price_text = price_tag.get_text(strip=True) if price_tag else "Price not found"

        try:
            price_mdl = int(price_text.replace('lei', ''))
        except ValueError:
            price_mdl = 0

        link_tag = product.find('a', href=True)
        product_link = 'https://maximum.md' + link_tag['href'] if link_tag else "Link not found"


        product_response = requests.get(product_link)
        if product_response.status_code == 200:
            product_soup = BeautifulSoup(product_response.text, 'html.parser')

            feature_list = product_soup.find('ul', class_='feature-list')
            features = {}
            if feature_list:
                for item in feature_list.find_all('li', class_='feature-list-item'):
                    key_tag = item.find('span', class_='feature-list-item_left')
                    value_tag = item.find('span', class_='feature-list-item_right')

                    if key_tag and value_tag:
                        key = key_tag.get_text(strip=True)
                        value = value_tag.get_text(strip=True)
                        features[key] = value

            else:
                print("Feature list not found on the product page.")

            timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')

            product_list.append({
                'name': name,
                'price': price_mdl,
                'link': product_link,
                'features': features,
                'timestamp': timestamp
            })

            filtered_products = list(filter(lambda x: 10000 <= x['price'] <= 20000, product_list))

            eur_conversion_rate = 0.052
            products_in_eur = list(
                map(lambda x: {**x, 'price_eur': round(x['price'] * eur_conversion_rate, 2)}, filtered_products))

            prices_in_eur = [i['price_eur'] for i in products_in_eur]
            total_price_eur = reduce(lambda x, y: x + y, prices_in_eur)

        else:
            print(f"Failed to retrieve details from {product_link}")

    print("\nFiltered Products:")
    for product in products_in_eur:
        print(
            f"Name: {product['name']}\nPrice: {product['price']} MDL\nPrice in EUR: {product['price_eur']}\nTimestamp: {product['timestamp']}")
        for key, value in product['features'].items():
            print(f"{key}: {value}")
        print("\n=====================\n")

    print(f"\nTotal Price of Filtered Products in EUR: {total_price_eur}")

    return products_in_eur

def serialize_to_json(filtered_products):
    json_str = "[\n"
    for product in filtered_products:
        json_str += "  {\n"
        json_str += f'    "Name": "{product["name"]}",\n'
        json_str += f'    "Price": {product["price"]},\n'
        json_str += f'    "Price in EUR": {product["price_eur"]:.2f}\n'
        json_str += "  },\n"

    json_str = json_str.rstrip(",\n")
    json_str += "\n]"
    return json_str


def serialize_to_xml(filtered_products):
    xml_str = "<products>\n"
    for product in filtered_products:
        xml_str += "  <product>\n"
        xml_str += f'    <Name>{product["name"]}</Name>\n'
        xml_str += f'    <Price>{product["price"]}</Price>\n'
        xml_str += f'    <Price_in_EUR>{product["price_eur"]:.2f}</Price_in_EUR>\n'
        xml_str += "  </product>\n"

    xml_str += "</products>"
    return xml_str


if __name__ == "__main__":
    if response.status_code == 200:
        filtered_products = scrape_func(response.text)
        
        json_output = serialize_to_json(filtered_products)
        print("JSON Output:")
        print(json_output)
        #
        # xml_output = serialize_to_xml(filtered_products)
        # print("\nXML Output:")
        # print(xml_output)
    else:
        print(f"Failed to retrieve the listing page. Status Code: {response.status_code}")
