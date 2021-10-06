# The selenium module
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import requests, time, re
import ExcelOperations as EO
from bs4 import BeautifulSoup
import DownloadImage as downloader


already_found_url = []


def get_html(url):
    error_count = 0
    error = True
    page_obj = None
    while error and error_count < 3:
        try:
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
            r.encoding = "utf-8"
            page = r.text
            page_obj = BeautifulSoup(page, "lxml")
            error = False
        except:
            error = True
            error_count = error_count + 1
            print("%s URL not accessible " % (url))

    return page_obj


def get_alphabets_unit(value):
    only_alpha = ""
    for char in value:
        if char.isalpha():
            only_alpha += char
    return only_alpha


def convert_to_standard_unit(value):
    non_decimal = re.compile(r'[^\d.-]+')
    unit = get_alphabets_unit(value).strip()
    try:
        if unit.lower() == "kg":
            return value
        elif unit.lower() == "cm":
            return value
        elif unit.lower() == "g":
            value = non_decimal.sub('', value).strip()
            if "." in value:
                value = str(float(value) / 1000) + "kg"
            else:
                value = str(int(value) / 1000) + "kg"
        elif unit.lower() == "mm":
            value = non_decimal.sub('', value).strip()
            if "." in value:
                value = str(float(value) / 10) + "cm"
            else:
                value = str(int(value) / 10) + "cm"
        elif unit.lower() == "m":
            value = non_decimal.sub('', value).strip()
            if "." in value:
                value = str(float(value) * 100) + "cm"
            else:
                value = str(int(value) * 100) + "cm"
    except Exception as e:
        pass
    return value


def increase_price_15_percent(price):
    price = price.replace("£", "").strip()
    price = float(price)
    price = price + (price * 0.15)
    return str(price) + "£"


def scrape_product(driver, main_cat, cat_name, cat_link, sub_cat_name, sub_cat_link, sub_sub_cat_name, sub_sub_cat_link, product_title, product_link, start_url):
    try:
        driver.get(product_link)
        time.sleep(1)
        page_obj = BeautifulSoup(driver.page_source, "lxml")
        if page_obj is not None:
            product_price = page_obj.find("div", attrs={"data-test-id": "product-primary-price"}).text.strip().replace("\n", "").replace(",", "").replace('"', '').strip()
            product_price = increase_price_15_percent(product_price)
            product_details_section = page_obj.find("section", attrs={"class": "_2cf5ecfb _042bbf7f"})
            product_details_section = product_details_section.find("div", attrs={"class": "fef30cae _5e7ce7a9 _461d0ef9 d4281212"})
            #product_details_div = product_details_section.find("div", attrs={"data-test-id": "ProductDescText"})
            product_info_section = product_details_section.findAll("div", attrs={"class": "_7be6e5a0 _66dabd6a e0657c31"})
            product_details_div = product_info_section[0]
            spec_table = product_details_section.find("table", attrs={"class": "f16ac490 eddf1b8e"}).find("tbody").findAll("tr")
            spec_table_html = str(product_info_section[-1])
            special_fields = {}
            for data in spec_table:
                heading = data.find("th").text.replace("\n", "").replace(",", "").replace('"', '').replace("|", "").replace("#", "").strip()
                val = data.find("td").text.replace("\n", "").replace(",", "").replace('"', '').replace("|", "").replace("#", "").strip()
                value = convert_to_standard_unit(val)
                if val != value:
                    spec_table_html = spec_table_html.replace(val, value)
                if "height" in heading.lower():
                    special_fields["height"] = value
                elif "length" in heading.lower():
                    special_fields["length"] = value
                elif "weight" in heading.lower():
                    special_fields["weight"] = value
                elif "width" in heading.lower():
                    special_fields["width"] = value
                elif "thickness" in heading.lower():
                    special_fields["thickness"] = value
                elif "diameter" in heading.lower():
                    special_fields["diameter"] = value
                elif "depth" in heading.lower():
                    special_fields["depth"] = value
                elif "mesh size" in heading.lower():
                    special_fields["mesh size"] = value
                elif "product code" in heading.lower():
                    special_fields["code"] = value

            spec_table_html = spec_table_html.replace(",", "")

            try:
                #images_div = page_obj.findAll("div", attrs={"class": "slick-list"})[-1]
                images_div = page_obj.findAll("div", attrs={"class": "slick-list"})[0]
                images_list = images_div.findAll("img")
                list_images = []
                for img in images_list:
                    list_images.append(img.attrs["src"])
                list_images = list(set(list_images))
                while len(list_images) < 5:
                    list_images.append("")
            except Exception as e:
                list_images = ["", "", "", "", ""]

            list_images_names = []
            for x in range(0, 5):
                if list_images[x] is not "":
                    file_name = special_fields["code"] + "_img_" + str(x)
                    file_name = downloader.download_image(list_images[x], file_name)
                    list_images_names.append(file_name)
                else:
                    list_images_names.append("")

            try:
                try:
                    product_details_div.find("button").decompose()
                except:
                    pass
                product_info = str(product_details_div).replace(",", "")
                product_feat = ""
            except:
                product_info = ""
                product_feat = ""
            print("=> Scraped product = " + product_title)
            EO.write_excel_file(main_cat, cat_name, sub_cat_name, sub_sub_cat_name, product_title, product_price, list_images_names, spec_table_html, special_fields, product_info)
    except Exception as e:
        print(e)


def scrape_products_list(CHROME_PATH, start_url, base_url, main_cat, cat_name, cat_link, sub_cat_name, sub_cat_link, sub_sub_cat_name, sub_sub_cat_link, products_page_link):
    link_to_go = products_page_link
    if link_to_go in already_found_url:
        print("Already scraped => " + link_to_go)
    else:
        WINDOW_SIZE = "1920,1080"
        CHROME_DRIVER_PATH = "ChromDriver/chromedriver"
        driver = None
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
        chrome_options.binary_location = CHROME_PATH
        chrome_options.add_argument('disable-infobars')
        chrome_options.add_argument("disable-notifications")
        driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, options=chrome_options)
        try:
            driver.get(link_to_go)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            execute = True
            counter = 0
            loading = True
            try:
                load_more = driver.find_element_by_xpath('//*[@id="content"]/div/div[1]/div/div/div[2]/div[3]/div/div[3]/div[2]/main/div/a[2]')
            except:
                loading = False
                load_more = None
            if loading:
                while execute or counter < 3:
                    try:
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        load_more.click()
                        time.sleep(1)
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(3)
                        counter = 0
                        execute = True
                    except:
                        execute = False
                        counter = counter + 1
            page_obj = BeautifulSoup(driver.page_source, 'lxml')
            products_div = page_obj.findAll("ul", attrs={"class": "_40158784 _6b5bb6a7 _190cafcd"})[0]
            products_list = products_div.findAll("li", attrs={"class": "b9bdc658"})
            for product in products_list:
                try:
                    a_tag = product.find("a", attrs={"data-test-id": "product-panel-main-section"})
                    product_title = a_tag.find("p", attrs={"data-test-id": "productTitle"}).text.replace("\n", "").replace("\r", "").replace(",", "").replace('"', '').strip()
                    product_link = base_url + a_tag.attrs["href"]
                    scrape_product(driver, main_cat, cat_name, cat_link, sub_cat_name, sub_cat_link, sub_sub_cat_name, sub_sub_cat_link, product_title, product_link, start_url)
                except Exception as e:
                    pass
        except Exception as e:
            print(e)
        finally:
            driver.close()
            already_found_url.append(link_to_go)


def scrape_sub_categories(main_cat, cat_name, cat_link, sub_cat_name, sub_cat_link, CHROME_PATH, start_url, base_url):
    page_obj = get_html(sub_cat_link)
    if page_obj is not None:
        try:
            #sub_sub_categories = page_obj.findAll("div", attrs={"class": "sc-1ulaoyw-0 fqZatT"})[0]
            #sub_sub_categories = sub_sub_categories.find("div", attrs={"data-test-id": "grid-sections"})
            #sub_sub_categories_list = sub_sub_categories.findAll("a", attrs={"class": "sc-cnb8ll-0 hHvddy"})

            sub_sub_categories_list = page_obj.findAll("ul", attrs={"id": "side-navigation-menu-1"})[0].findAll("li")

            for sub_sub_cat in sub_sub_categories_list:
                try:
                    a_tag = sub_sub_cat.find("a")
                    sub_sub_cat_name = a_tag.text.replace("\n", "").replace("\r", "").replace(",", "").replace('"', '').strip()
                    #sub_sub_cat_name = sub_sub_cat.find("div", attrs={"data-test-id": "category-tile-content"}).find("h3").text.replace("\n", "").replace("\r", "").replace(",", "").replace('"', '').strip()
                    #sub_sub_cat_link = base_url + sub_sub_cat.attrs["href"]
                    sub_sub_cat_link = base_url + a_tag.attrs["href"]
                    print("Sub Sub Category = " + sub_sub_cat_name)
                    scrape_products_list(CHROME_PATH, start_url, base_url, main_cat, cat_name, cat_link, sub_cat_name, sub_cat_link, sub_sub_cat_name, sub_sub_cat_link, sub_sub_cat_link)
                except Exception as e:
                    pass
        except:
            print("Sub Sub Category = ")
            scrape_products_list(CHROME_PATH, start_url, base_url, main_cat, cat_name, cat_link, sub_cat_name, sub_cat_link, "", "", sub_cat_link)


def scrape_categories(main_cat, cat_name, cat_url, CHROME_PATH, start_url, base_url):
    page_obj = get_html(cat_url)
    if page_obj is not None:
        try:
            #sub_categories = page_obj.findAll("div", attrs={"class": "sc-1ulaoyw-0 fqZatT"})[0]
            #sub_categories = sub_categories.find("div", attrs={"data-test-id": "grid-sections"})
            #sub_categories_list = sub_categories.findAll("a", attrs={"class": "sc-cnb8ll-0 hHvddy"})

            ####
            sub_categories_list = page_obj.findAll("ul", attrs={"id": "side-navigation-menu-1"})[0].findAll("li")
            for sub_cat in sub_categories_list:
                try:
                    a_tag = sub_cat.find("a")
                    # sub_cat_name = sub_cat.find("div", attrs={"data-test-id": "category-tile-content"}).find("h3").text.replace("\n", "").replace("\r", "").replace(",", "").replace('"', '').strip()
                    sub_cat_name = a_tag.text.replace("\n", "").replace("\r", "").replace(",", "").replace('"',
                                                                                                           '').strip()
                    # sub_cat_link = base_url + sub_cat.attrs["href"]
                    sub_cat_link = base_url + a_tag.attrs["href"]
                    print("Sub Category = " + sub_cat_name)
                    scrape_sub_categories(main_cat, cat_name, cat_url, sub_cat_name, sub_cat_link, CHROME_PATH,
                                          start_url, base_url)
                except Exception as e:
                    pass
        except:
            print("Sub Sub Category = ")
            scrape_products_list(CHROME_PATH, start_url, base_url, main_cat, cat_name, cat_url, "",
                                 "", "", "", cat_url)
