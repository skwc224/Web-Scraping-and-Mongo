from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd


def init_browser():
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)

def scrape():
    browser = init_browser()
    
    news_title, news_p = scrape_news()
    
    data = {
        "news_title": news_title,
        "news_paragraph": news_p,
        "featured_image": scrape_image(),
        "weather": scrape_weather(),
        "facts": scrape_facts(),
        "hemispheres": scrape_hemispheres(),
    }

    browser.quit()
    return data


def scrape_news():
    browser = init_browser()

    url = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'
    browser.visit(url)

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    news_title = soup.find('div', class_='content_title').text.strip()
    news_p = soup.find('div', class_='rollover_description_inner').text.strip()

    return news_title, news_p


def scrape_image():
    browser = init_browser()
    
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    full_image = browser.find_by_id('full_image')
    full_image.click()

    browser.is_element_present_by_text('more info')
    more_info = browser.find_link_by_partial_text('more info')
    more_info.click()

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    featured_image = soup.select_one('figure.lede a img').get('src')

    featured_image_url = f'https://www.jpl.nasa.gov{featured_image}'

    return featured_image_url


def scrape_weather():
    browser = init_browser()

    url = "https://twitter.com/marswxreport?lang=en"
    browser.visit(url)

    html = browser.html
    soup = BeautifulSoup(html, "html.parser")

    mars_weather = soup.find('div', class_='js-tweet-text-container').text.strip()
    mars_weather.replace('\n', ' ')

    return mars_weather


def scrape_facts():
    url = 'https://space-facts.com/mars/'
    tables = pd.read_html(url)
    
    df = tables[0]
    df.columns = ['Mars planet', 'value']
    df.set_index('Mars planet', inplace=True)

    return df.to_html(classes="table table-striped")


def scrape_hemispheres():
    browser = init_browser()

    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    hemisphere_image_urls = []
    hemisphere = {}

    links = browser.find_by_css('a.itemLink.product-item h3')

    for x in range(len(links)):
        hemisphere['title'] = browser.find_by_css('a.itemLink.product-item h3').text
        
        browser.find_by_css('a.itemLink.product-item h3')[x].click()
        hemisphere['img_url'] = browser.find_link_by_text('Sample')['href']
        
        hemisphere_image_urls.append(hemisphere)

        browser.back()

    return hemisphere_image_urls