from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from time import sleep
import streamlit as st
from streamlit_tags import st_tags
from pyairtable.orm import Model, fields as F
import os

class ProductData(Model):
    name = F.TextField("Product Name")
    product_description = F.TextField("Product Description")
    product_specs = F.TextField("Product Specs")
    rating = F.TextField("Rating")
    num_ratings = F.TextField("# of Ratings")
    favorites = F.TextField("# of Favorites")
    sold = F.TextField("# of Product Sold")
    price_range = F.TextField("Price Range")
    seller_name = F.TextField("Seller Name")
    seller_ratings = F.TextField("Seller # of Ratings")
    seller_response_rate = F.TextField("Seller Response Rate")
    seller_response_time = F.TextField("Seller Response Time")
    seller_joined = F.TextField("Seller Joined")
    seller_products = F.TextField("Seller # of Products")
    seller_followers = F.TextField("Seller # of Followers")
    seller_url = F.TextField("Seller URL")
    five_star_review = F.TextField("Main Five-Star Review")
    one_star_review = F.TextField("Main One-Star Review")
    url = F.TextField("Shopee URL")
    class Meta:
        base_id = "appX1S3wBWu6Rc9gn"
        table_name = "tblb90xL7jVk4fmGz"
        api_key = os.getenv('AIRTABLE_API_KEY')

def get_soup(driver):
    html = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    soup = BeautifulSoup(html, "html.parser")
    return soup

def page_is_loaded(driver):
    print("oh")
    return driver.find_element(By.TAG_NAME, "body") != None

def scrape(links):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    chrome_options = Options()

    chrome_service = Service(r"chromedriver.exe")
    chrome_options.add_argument(f'user-agent={user_agent}')
    chrome_options.add_argument(f'--headless')
    browser = webdriver.Chrome(service=chrome_service, options=chrome_options)

    for url in links:
        sleep(10)
        browser.get(url)
        wait = WebDriverWait(browser, 5)
        wait.until(page_is_loaded)
        login_attempt = 0

        while login_attempt < 5:
            if ("https://shopee.ph/buyer/" in browser.current_url):
                sleep(3)
                email = os.getenv('EMAIL')
                password = os.getenv('PASSWORD')
                browser.find_element(By.CSS_SELECTOR, "input[type='text']").send_keys(email)
                browser.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(password)
                sleep(1)
                browser.find_element(By.CSS_SELECTOR, "button.wyhvVD._1EApiB.hq6WM5.L-VL8Q.cepDQ1._7w24N1").click()
                break
            else:
                sleep(5)
                login_attempt += 1

        sleep(2)
        wait = WebDriverWait(browser, 5)
        wait.until(page_is_loaded)
        sleep(30)
        attempt = 0
        st.divider()
        st.write("Product Data for URL: " + url)
        while attempt < 5:
            try:
                browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                sleep(3)
                soup = get_soup(browser)

                name = soup.select("div._44qnta>span")[0].text
                rating = soup.select('div._046PXf')[0].text + " stars"
                num_ratings = soup.select("[class='_1k47d8']")[0].text + " ratings"
                image_section_data = soup.select('div.Ne7dEf')
                favorites = [x for x in image_section_data if "Favorite" in x.text][0].text
                sold = soup.select("div.e9sAa2")[0].text + " sold"
                price_range = soup.select('div.pqTWkA')[0].text
                specifications = soup.select("div.dR8kXc")
                product_specs = ""
                for x in specifications:
                    if x.select("label")[0].text == "Category":
                        product_specs += "Category: " + " > ".join([i.text for i in x.select("a")])
                    else:
                        product_specs += x.select("label")[0].text + ": " + x.select("*:not(label)")[0].text + "\n"

                product_description_lines = soup.select("p.irIKAp")
                product_description = "\n".join([x.text for x in product_description_lines])

                seller_container = soup.select("section.NLeTwo.page-product__shop")[0]

                seller_name = seller_container.select('div.VlDReK')[0].text

                seller_data = seller_container.select('.R7Q8ES')

                seller_ratings = [x for x in seller_data if x.select("label")[0].text == "Ratings"][0].select("span")[0].text + " total ratings"

                seller_response_rate = [x for x in seller_data if x.select("label")[0].text == "response rate"][0].select("span")[0].text

                seller_joined = [x for x in seller_data if x.select("label")[0].text == "joined"][0].select("span")[0].text

                seller_products = [x for x in seller_data if x.select("label")[0].text == "products"][0].select("span")[0].text

                seller_response_time = [x for x in seller_data if x.select("label")[0].text == "response time"][0].select("span")[0].text

                seller_followers = [x for x in seller_data if x.select("label")[0].text == "follower"][0].select("span")[0].text

                seller_url = "https://shopee.ph" + seller_container.select('a.R7Q8ES')[0].get('href')

                reviews_filters = browser.find_elements(By.CSS_SELECTOR, ".product-rating-overview__filter")
                five_star_review_filter = [x for x in reviews_filters if "5 Star" in x.text][0]
                five_star_review_filter.click()
                sleep(5)
                soup = get_soup(browser)
                five_star_review_lines = soup.select(".shopee-product-rating")[0].select("[class='Rk6V+3']")[0].select('div')
                five_star_review = "\n".join([x.text for x in five_star_review_lines])

                one_star_review_filter = [x for x in reviews_filters if "1 Star" in x.text][0]
                one_star_review_filter.click()
                sleep(5)
                soup = get_soup(browser)
                one_star_review_lines = soup.select(".shopee-product-rating")[0].select("[class='Rk6V+3']")[0].select('div')
                one_star_review = "\n".join([x.text for x in one_star_review_lines])

                break
            except Exception as e:
                print(e)
                sleep(3)
                attempt += 1

        st.write("Name: " + name)
        st.write("Rating: " + rating)
        st.write("Num of Favorites: " + favorites)
        st.write("Num of Product Sold: " + sold)
        st.write("Price Range: " + price_range)
        st.write("Product Specs: " + product_specs)
        st.write("Product Description: " + product_description)
        st.write("Seller Name: " + seller_name)
        st.write("Seller Num of Ratings: " + seller_ratings)
        st.write("Seller Response Rate: " + seller_response_rate)
        st.write("Seller Joined: " + seller_joined)
        st.write("Seller Num of Products: " + seller_products)
        st.write("Seller Response Time: " + seller_response_time)
        st.write("Seller Num of Followers: " + seller_followers)
        st.write("Seller URL: " + seller_url)
        st.write("Main Five Star Review: " + five_star_review)
        st.write("Main One Star Review: " + one_star_review)

        product_data = ProductData(
            name=name,
            product_description=product_description,
            product_specs=product_specs,
            rating=rating,
            num_ratings=num_ratings,
            favorites=favorites,
            sold=sold,
            price_range=price_range,
            seller_name=seller_name,
            seller_ratings=seller_ratings,
            seller_response_rate=seller_response_rate,
            seller_response_time=seller_response_time,
            seller_joined=seller_joined,
            seller_products=seller_products,
            seller_followers=seller_followers,
            seller_url=seller_url,
            five_star_review=five_star_review,
            one_star_review=one_star_review,
            url=url
        )
        product_data.save()
        st.write("Done for URL: " + url)

    st.divider()
    st.write("Finished scraping. Check out https://airtable.com/appX1S3wBWu6Rc9gn/tblb90xL7jVk4fmGz/viw6QDwsYgk9NiJYK")

st.title("Shopee Product Data Scraper")

shopee_links = st_tags(
    label='Enter Shopee URLs:',
    text='Press enter to add more',
    key='1')

if st.button('Scrape'):
    scrape(shopee_links)
