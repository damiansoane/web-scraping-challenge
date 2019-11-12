#!/usr/bin/env python
# coding: utf-8




import pandas as pd
from splinter import Browser
from bs4 import BeautifulSoup
import datetime as dt
import requests


def scrape_all():

    browser = Browser('chrome', executable_path='chromedriver', headless=True)
    news_title, news_paragraph = mars_news(browser)

    data = {
        'news_title': news_title,
        'news_paragraph': news_paragraph,
        'featured_image': featured_image(browser),
        'hemispheres': hemispheres(browser),
        'weather': twitter_weather(browser),
        'facts': mars_facts,
        'last_modified': dt.datetime.now()
    }
    browser.quit()
    return data

def mars_news(browser):
    
    url = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'
    browser.visit(url)
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    

    try:
        slide = soup.select_one('ul.item_list li.slide')
        slide.find('div', class_='content_title')
        news_title = slide.find('div', class_='content_title').get_text()
        news_p = slide.find('div', class_='article_teaser_body').get_text()
    except AttributeError:
        return None, None
    return news_title, news_p
        

def featured_image(browser):   

    image_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(image_url)
    html = browser.html
    image_soup = BeautifulSoup(html, 'html.parser')
    
    image = browser.find_by_id('full_image')
    image.click()
    browser.is_element_present_by_text('more info')
    info = browser.find_link_by_partial_text('more info')
    info.click()


    html = browser.html
    png = BeautifulSoup(html, 'html.parser')

    try:
        image_url = png.select_one('figure.lede a img').get('src')
    except AttributeError:
        return None    
        
    return image_url


def twitter_weather(browser):

    weather_url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(weather_url)
    html = browser.html
    weather_soup = BeautifulSoup(html, 'html.parser')
    
    weather = weather_soup.find('div',attrs={'class': 'tweet', 'data-name': 'Mars Weather'})
    mars_weather = weather.find('p', 'tweet-text').get_text()
    return mars_weather


def mars_facts():
    try:
        facts = pd.read_html('https://space-facts.com/mars/')[0]
    except BaseException:
        return None

    facts.columns = ('fact title', 'the fact')
    facts

    return facts.to_html(classes='table')


def hemispheres(browser):


    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    images = []
    urls = browser.find_by_css('a.product-item h3')
    for i in range(len(urls)):
        hemi = {}
        browser.find_by_css('a.product-item h3')[i].click()
        sample = browser.find_link_by_text('Sample').first
        hemi['img_url'] = sample['href']
        hemi['title'] = browser.find_by_css('h2.title').text
        images.append(hemi)
        browser.back()
    return images

if __name__ == '__main__':
    print(scrape_all())    

