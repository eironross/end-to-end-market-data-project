"""
02/09/2024 15:04 author: @eiron

Market Data Scraper - headless version
This is the main program for the app.
file pattern = L3Zhci93d3cvaHRtbC93cC1jb250ZW50L3VwbG9hZHMvZG93bmxvYWRzL2RhdGEvZmluYWxsd2FwL2ZpbmFsX2x3YXBfMjAyNDAxMj[Uu]Y3N2 <- bracket: two value changes each item

"""
# Import the paths from different files
from market_functions.iemop_paths import MR_PATHS, ONE_DATA_PATHS, RTD_PATHS, OTHER_PATHS, URI, default_path
from market_functions import logger, move_files

# Libraries
import requests
import os
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from datetime import date, timedelta
from zipfile import ZipFile

class GetMarketData():
    
    log = logger.log_iemop()
    date = date.today()
    
    def __init__(self, url:str = None, default_path: str = None):
        
        self.local_paths = {}
        
        if url is None or default_path is None:
            raise "URL or Default was None please provide url and default path"
        
        self.default_path = default_path
        self.url = url
        
    def __repr__(self):
        return "GetMarketData(url='{}',default_path='{}')".format(self.url,self.default_path)
    
    @staticmethod
    def _isformat(file_name: str, format: str) -> bool:
        """
            _isformat checks the formatting of the file
        Args:
            file_name (str): file_name from the scraped data from IEMOP
        """
        return True if file_name.endswith(format) else False
     
    def _create_dictionary(self, *args: list) -> dict:
        
        """
            Creates dictionary for the scraped data from IEMOP. 
            
            e.g
            
            market_data = {
                index: {
                    "date": "buzz",
                    "title": "foo",
                    "link": "bar"
                }
            }
            
            index: int
            title: str
            link: str
            date: str
        Returns:
            dictionary: returns market_data as dictionary
        """
        
        market_data = {}
        
        if not args:
            return {}
        
        for index, market_item in enumerate(args):
                
                    title = market_item.find('div', class_= "market-reports-title").text.strip().split()[0]
                    date = market_item.find('div', class_= "market-data-dl-date").text.strip()
                    link = market_item.find('a').get("href")
                    
                    new_item = dict([("date", date), ("title", title), ("link", self.url+link)])
                    append_item = dict([(index, new_item)])
                    market_data.update(append_item)
                    
        return market_data
    

    def _create_files(self, data: dict, direc: str) -> None:
        
        """__create_files: receives data as dictionary, direc (directory or path)
        
        This method will access the generated link from IEMOP then convert the response data from binary data to actual files then save the data to the target location
    
        """
        
        if not data:
            return None
        
        for i, item in data.items():
            
            file_loc = os.path.join(os.sep, direc, item.get("title"))
            
            with requests.get(item.get("link")) as response: 
                self.log.info("Date: {} File: {} Status: {}".format(item.get("date"), item.get("title"), response.status_code))
                with open(file_loc, "wb") as file:
                    file.write(response.content)  

            if self._isformat(item.get("title"), "zip"):
                with ZipFile(file_loc, "r") as my_zip:
                    my_zip.extractall(direc)
                
                os.remove(file_loc)
                    
    def _create_folders(self, key: str) -> str:
        """Creates folders relative to the default path then the folder name. 

        Args:
            key string: key (name of data) from the dictionary

        Returns:
            string: return string dir_name to used as the file location for creating the files
        """
       
        folder_name = " ".join(key.split("_")).title()
        dir_name = os.path.join(os.sep, self.default_path, folder_name)
        
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
            self.log.info(f"Created folder for: {folder_name} ")
                
        return dir_name
                
    def download_data(self, **kwargs: dict):
        """
        The inputs should be in form a dictionary - a key value pair
        e.g. PATHS = {"foo": "bar"} 
        
        GetMarketData.download_data(**PATHS) or GetMarketData.download_data(foo="bar")

        Also, Input can be:
        e.g.
        GetMarketData.download_data(lwap_original=MR.PATHS.get("lwap_original")) <- .get() method is accessing the dictionary using the key to get the value

        expected output: kwargs = {"lwap_original": "/load-weighted-average-prices-original"}

        or the whole dictionary can be passed as argument

        e.g.

        GetMarketData.download_data(**MR_PATH)

        * - args or arguments (list)
        ** - kwargs or keyword arguments (dictionary)
        
        """
        
        if not kwargs:
            raise "Expected to have an input at least one keyword argument, I got None"
        
        try:
            #Will place the kwargs to a variable
            self.local_paths = kwargs
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            #chrome_options.add_argument('--blink-settings=imagesEnabled=false')
            
            # accessing paths of iemop    
            for key, value in self.local_paths.items(): 
                with Chrome(options=chrome_options) as driver:
                    
                    self.uri = self.url+value
                    self.log.info(self.uri)
                    
                    # TODO: Try using playwright
                    driver.set_page_load_timeout(20)
                    driver.get(self.uri) # Note that the IEMOP pages may be slow at times. Retry the driver if ganon yung case
                    html = driver.page_source # fully rendered page.
                    
                    if not html:
                        self.log.warning("No data receive will try to regather..")
                        return self.download_data(self.local_paths) # Trying to call the function again if html is None value
                
                    self.log.info("{} -> Path: {} Error: {} Status: {}".format(key, value, None, None))
                    
                    market_items = BeautifulSoup(html, "html.parser").find_all('div', class_= "market-reports-item")
                    print(market_items)
                    if market_items is []:
                        self.log.warning("No data received Exiting.. ")
                        # Get the current index then use it to slice the dictionary then retry downloading from there
                        #return self.download_data(**MR_PATHS[:])

                    # date = market_items[0].find('div', class_= "market-reports-title").text.strip().split()[0]
                    # check_date = self.date - timedelta(days=1) # D-1
                    
                    # checks if the data for d-1 was already uploaded
                    # if date.find(check_date.strftime("%Y%m%d")) == -1:
                    #     raise "Data was not yet uploaded in the IEMOP's website"
                    
                    data = self._create_dictionary(*market_items)
                    direc = self._create_folders(key)
                    self._create_files(data, direc)
                    
                    self.log.info("Downloading completed for {} .. Exiting...".format(key))
                    
        except TimeoutException:
            self.log.exception("Exception has been thrown. ")
            

if __name__ == "__main__":
    get = GetMarketData(url=URI, default_path=default_path)
    get.download_data(**MR_PATHS)