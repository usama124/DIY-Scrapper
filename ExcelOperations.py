import openpyxl


def create_heading():

    headers = ["General Category", "External Category", "Main Category", "Sub Category", "Sub Sub Category", "Title", "Price", "SKU", "Weight", "Height", "Length", "Width", "Thickness", "Diameter", "Depth", "Mesh Size", "Product Specification", "Product Information", "Image 1", "Image 2", "Image 3", "Image 4", "Image 5"]
    workbook_name = "Data/diy_products_excel.xlsx"

    wb_obj = openpyxl.Workbook()
    sheet = wb_obj.active
    sheet.append(headers)
    wb_obj.save(filename=workbook_name)


def write_excel_file(main_cat, cat_name, sub_cat_name, sub_sub_cat_name, product_title, product_price, list_images, spec_table_html, special_fields, product_info):
    workbook_name = "Data/diy_products_excel.xlsx"
    wb = openpyxl.load_workbook(workbook_name)
    page = wb.active

    data = ["MACHINERY & EQUIPMENT", main_cat, cat_name, sub_cat_name, sub_sub_cat_name, product_title, product_price, special_fields.get("code", ""),
            special_fields.get("weight", ""), special_fields.get("height", ""), special_fields.get("length", ""), special_fields.get("width", ""), special_fields.get("thickness", ""), special_fields.get("diameter", ""), special_fields.get("depth", ""), special_fields.get("mesh size", ""),
            spec_table_html, product_info, list_images[0], list_images[1], list_images[2], list_images[3], list_images[4]]

    page.append(data)
    wb.save(filename=workbook_name)
