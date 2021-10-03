import configparser
import Scrape_categories as scrapper

parser = configparser.ConfigParser()
parser.read("Conf/config.ini")


def confParser(section):
    if not parser.has_section(section):
        print("No section info  rmation are available in config file for", section)
        return
    # Build dict
    tmp_dict = {}
    for option, value in parser.items(section):
        option = str(option)
        value = value.encode("utf-8")
        tmp_dict[option] = value
    return tmp_dict


def create_heading():
    f = open("Data/diy_products.csv", "w")
    f.write('"Web-scraper-order", "Web-scraper-start-url", "External Category", "Main category", "Main category href", "Sub category", "Sub category href", "Sub Sub category", "Sub Sub category href", "Product href", "Title", "Price", "Product Code", "Weight", "Height", "Length", "Width", "Thickness", "Diameter", "Depth", "Mesh Size", "Product specification", "Product Information", "Product Features", "Image 1", "Image 2", "Image 3", "Image 4", "Image 5"\n')
    f.close()


general_conf = confParser("general_conf")
CHROME_PATH = general_conf["chrome_path"].decode("utf-8")
base_url = general_conf["base_url"].decode("utf-8")
start_url = general_conf["start_url"].decode("utf-8")
start_cat = general_conf["start_cat"].decode("utf-8")

if __name__ == '__main__':
    create_heading()
    if start_url.endswith("/"):
        start_url = start_url[:-1]

    page_obj = scrapper.get_html(start_url)
    if page_obj is not None:
        if base_url == start_url:
            main_cat_nav = page_obj.find("ul", attrs={"class": "_7a1608a1 _3e15c9c2 fe78be23 a8075c22"})
            main_cat_list = main_cat_nav.findAll("li", attrs={"class": "_30ff2f6b"})
            for li in main_cat_list:
                name = li.find("span", attrs={"class": "a72f6a91 _5f559bf8 _408ec770"}).text.replace("\n", "").replace(",", "").replace('"', '').strip()
                if "clearance" not in name.lower():
                    sub_cat_list = li.findAll("li", attrs={"class": "_88a972ee"})
                    print(name)
                    for sub_cat in sub_cat_list:
                        try:
                            a_tag = sub_cat.find("a", attrs={"class": "a72f6a91 _9e151e55 _4fd271c8 _23ee746f"})
                            sub_cat_name = a_tag.text.replace("\n", "").replace(",", "").replace('"', '').strip()
                            sub_cat_link = base_url + a_tag.attrs["href"]
                            print(sub_cat_name + " => " + sub_cat_link)
                            scrapper.scrape_categories(name, sub_cat_name, sub_cat_link, CHROME_PATH, start_url, base_url)
                        except:
                            pass
                else:
                    print("Skipping clearance category.")
        else:
            start_cat = start_cat.replace("\n", "").replace(",", "").replace('"', '').strip()
            try:
                main_cat = page_obj.find("li", attrs={"data-test-id": "breadcrumbs-list-crumb-2"}).text.replace("\n", "").replace(",", "").replace('"', '').strip()
            except:
                main_cat = page_obj.find("a", attrs={"data-test-id": "category-bread-crumb-1"}).text.replace("\n", "").replace(",", "").replace('"', '').strip()
            if "clearance" not in main_cat.lower():
                scrapper.scrape_categories(main_cat, start_cat, start_url, CHROME_PATH, start_url, base_url)
            else:
                print("Skipping clearance category.")