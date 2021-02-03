import requests
from bs4 import BeautifulSoup
import pandas as pd


# Mimics a search engine.
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/75.0.3770.100 Safari/537.36'}


# Determines if the HTML tag exists, if it does not, the function returns none.
def check_none(div_string):
    if div_string is not None:
        return div_string
    else:
        return 'None'


def retrieve_url_list_size(url_link):
    # Get function navigates to the first page.
    r = requests.get(url_link + '1', headers=header)
    c = r.content
    # Beautiful Soup parses the HTML.
    soup = BeautifulSoup(c, "html.parser")
    # This retrieves the large panel on the right side, capturing the aparments.
    arching_containter = soup.find("div", {"class": "placardContainer"})
    # Finds the page range text.
    page_range = arching_containter.find('p', {"class": 'searchResults'}).find('span', {"class": 'pageRange'}).text
    # Splits the page range by spaces.
    page, first_page, of, last_page = page_range.split(' ')
    # Returns the first & last page.
    return int(first_page), int(last_page)

# Returns dataframe for Apartment Title, Street, Town, State, Zip Code, Amenities, Price, & Phone.
def get_listings(url_links):
    # The list of all search URLs.
    base_urls = []
    # Determines if the parameter is a single string or a list.
    if isinstance(url_links, str):
        # Provided that the parameter is a string, convert it to a list.
        base_urls.append(url_links)
    else:
        # If the parameter is a list, keep the list.
        base_urls = url_links

    # Stages the dataframe instances
    web_content_list = []

    # Loop through the URLs
    for link in base_urls:
        # Declares first & last page of the URL
        first_page, last_page = retrieve_url_list_size(link)
        # For this URL, loop through each page result.
        for page_number in range(first_page, last_page + 1):
            # Get function navigates to the looped page.
            r = requests.get(link + str(page_number) + "/", headers=header)
            c = r.content
            # Beautiful Soup parses the HTML.
            soup = BeautifulSoup(c, "html.parser")
            # Retrieve the Placard Header, which contains the address & apartment title.
            placard_header = soup.find_all("header", {"class": "placard-header has-logo"})
            # Retrieve the Placard Content, which contains the property information.
            placard_content = soup.find_all("section", {"class": "placard-content"})

            # ZIP Placard Header & Placard Content to match the apartment title & information.
            for item_header, item_content in zip(placard_header, placard_content):
                # Check if the title exists.
                title = check_none(
                    item_header.find("div", {"class": "property-information"}).find("div", {"class": "property-title"}))
                if title != 'None':
                    # Retrieve the title.
                    title = title.text

                # Check if the price exists.
                price = check_none(
                    item_content.find("div", {"class": "content-wrapper"}).find("div", {"class": "price-range"}))
                if price != 'None':
                    # Retrieve price.
                    price = price.text
                    if ' - ' in price:
                        # This will happen if the content is a range; thus, retrieve the bottom value.
                        price = price[:price.index(' - ')]
                    if '$' in price:
                        # Remove the dollar sign for float value.
                        price = price.replace('$', '')
                    if ',' in price:
                        # Remove comma for float, occurs if large than $1k.
                        price = price.replace(',', '')
                    try:
                        # Finalize Price
                        price = float(price)
                    except:
                        # If floating fails, NULL the value.
                        price = 0

                # Check if the phone exists.
                phone = check_none(item_content.find("div", {"class": "content-wrapper"}).find("a", {
                    "class": "phone-link js-phone"}))
                if phone != 'None':
                    # Declare phone & clean the result.
                    phone = phone.text.replace('\n', '')

                # Check if amenities exist.
                amenities = check_none(item_content.find("div", {"class": "property-amenities"}))
                if amenities != 'None':
                    # Declare amenities & clean the result.
                    amenities = amenities.text.replace('\n', ',')
                    amenities = amenities[1:len(amenities) - 1]

                # Check if address exists.
                address = check_none(item_header.find("div", {"class": "property-information"}).find("div", {
                    "class": "property-address js-url"}))
                if address != 'None':
                    # Declare address.
                    address = address.text
                    try:
                        # Attempting to split the address to declare street, town, state, & zip code.
                        street, town, state_zipcode = address.split(', ')
                        # State & Zip code separated by space, not commas. Thus, splot the state & zip code by space.
                        state, zipcode = state_zipcode.split(' ')
                    except Exception as err:
                        # If the splicing fails, aggregate the address into the street.
                        street = address
                        town = 'NULL'
                        state = 'NULL'
                        zipcode = 'NULL'
                # Append the tuple to the web_content_list.
                web_content_list.append((title, street, town, state, zipcode, amenities, price, phone))

    # Translate the list of tuples into a Data Frame.
    return pd.DataFrame(web_content_list,
                        columns=['Title', 'Street', 'Town', 'State', 'Zip Code', 'Amenities', 'Price', 'Phone'])
