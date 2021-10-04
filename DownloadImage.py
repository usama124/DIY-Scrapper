## Importing Necessary Modules
import requests  # to get image from the web
import shutil  # to save it locally


def download_image(image_url, filename):
    try:
        # Open the url image, set stream to True, this will return the stream content.
        r = requests.get(image_url, stream=True)

        # Check if the image was retrieved successfully
        if r.status_code == 200:
            # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
            r.raw.decode_content = True
            #print(r.headers)
            img_ext = r.headers["Content-Type"].split("/")[-1]
            filename = "images/" + filename + "." + img_ext
            # Open a local file with wb ( write binary ) permission.
            with open(filename, 'wb') as f:
                shutil.copyfileobj(r.raw, f)

            print('Image sucessfully Downloaded: ', filename)
        else:
            print('Image Couldn\'t be retreived' + image_url)
        return filename
    except Exception as e:
        print(e)
        return ""

#download_image("https://media.diy.com/is/image/Kingfisher/akoa-kaki-green-armchair~5059340125909_03i?$MOB_PREV$&$width=2500&$height=2500", "img1")