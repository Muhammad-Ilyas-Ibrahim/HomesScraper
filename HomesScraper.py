from requests_html import HTMLSession
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import pandas as pd
import os

# Create an HTMLSession object
session = HTMLSession()

# Main URL
main_url = "https://www.homes.com/irvine-ca/92618/?property_type=1,2,32,64,8"

# Send a GET request and render JavaScript content
response = session.get(main_url)

# Extract property URLs using CSS selector
property_links = response.html.find("a[href^='/property/']")

# Base URL
base_url = "https://www.homes.com"

# List to store complete URLs
complete_links = []

# Iterate through the property links and join with the base URL
for link in property_links:
    property_url = link.attrs["href"]
    complete_link = urljoin(base_url, property_url)
    soup = BeautifulSoup(response.content, "html.parser")
    complete_links.append(complete_link)
    
complete_links = list(set(complete_links))
data = []
for index, link in enumerate(complete_links):
    response = session.get(link, timeout=8)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract image URLs
    image_elements = soup.find_all(
        'img', class_='js-open-gallery aspect-ratio-image')
    image_urls = [img['data-image'] for img in image_elements]

    # Extract price
    price = soup.find('span', class_='property-info-price').text.strip()

    # Extract address
    city_elem = soup.find('a', class_='standard-link text-only')
    zip_elem = city_elem.find_next_sibling('a', class_='standard-link text-only')
    city = city_elem.get_text(strip=True)
    zip_code = zip_elem.get_text(strip=True)
    neighborhood_elem = soup.find('span', class_='property-info-neighborhood')
    if neighborhood_elem:
        neighborhood_text = neighborhood_elem.a.get_text(strip=True)
    else:
        neighborhood_text = ''
    address = f"{city} {zip_code} | {neighborhood_text}"

    # Extract number of beds and baths
    bedsBaths = soup.find_all('span', class_='property-info-feature')
    beds_elem = bedsBaths[0]
    beds = beds_elem.find('span', class_='property-info-feature-detail').text.strip()
    baths_elem = bedsBaths[1]
    baths = baths_elem.find('span', class_='property-info-feature-detail').text
    
    # Description
    description = soup.find('p', class_='ldp-description-text').get_text(strip=True)
   
    # Agent information
    # Name
    agent_elems = soup.find_all('a', class_='agent-information agent-information-fullname standard-link text-only')
    if agent_elems:
        agent_elem = agent_elems[1]
        agent_name = agent_elem.text
    else:
        agent_name = "N/A"
    
    # Phone
    agent_elem = soup.find('a', class_="agent-information agent-information-phone-number standard-link text-only")
    if agent_elem:
        agent_phone = agent_elem.text
    else:
        agent_phone = "N/A"
    # Email
    agent_elem = soup.find('span', class_="agent-information agent-information-email")
    if agent_elem:
        agent_email = agent_elem.text
    else:
        agent_email = "N/A"
    
    # Builder's Information
    # Builder's Name
    agent_elem = soup.find('div', class_="agent-name")
    if agent_elem:
        builder_name = agent_elem.text.strip()
    else:
        builder_name = "N/A"
    # Phone 
    agent_elem = soup.find('div', class_="agent-phone")
    if agent_elem:
        builder_phone = agent_elem.text.strip()
    else:
        builder_phone = "N/A"
    data.append({
        "Page Link": link,
        "Images_urls": image_urls, 
        "Price": price,
        "Address": address,
        "Beds": beds,
        "Baths": baths,
        "Description": description,
        "Agent Name": agent_name,
        "Agent Phone": agent_phone,
        "Agent Email": agent_email,
        "Builder Name": builder_name,
        "Builder Phone": builder_phone
    })
    print(f"Scraped Page: {index +1}/{len(complete_links)}", end='\r')
# Saving data to excel
if os.path.exists("property_data.xlsx"):
    df = pd.DataFrame(data)
    existing_df = pd.read_excel("property_data.xlsx")
    combined_df = pd.concat([existing_df, df], ignore_index=True)
    combined_df.to_excel("property_data.xlsx", index=False)
else:    
    df = pd.DataFrame(data)
    excel_file = "property_data.xlsx"
    df.to_excel(excel_file, index=False)
    


