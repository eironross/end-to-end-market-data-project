"""
02/09/2024 15:04 author: @eiron

Market Data Scraper - headless version
This is the main program for the app.


"""
# Built-in imports
import os
import sys

# Import the paths from different files
from market_functions.iemop_paths import MR_PATHS, ONE_DATA_PATHS, URI, default_path
from market_functions import logger, move_files
from market_functions.utility import create_dictionary, create_folders

# Libraries
import requests
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from datetime import date, timedelta
from zipfile import ZipFile

class GetMarketData():
    
    log = logger.log_iemop()
    
    def __init__(self, url:str = None, default_path: str = None):
        
        self.local_paths = {}    
        self.date = date.today()
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
    
    @staticmethod       
    def _headless_option() -> None:
        
        # Adding argument to run selenium headless    
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        chrome_options.add_experimental_option("detach", True)
        return chrome_options
    
    def _preprocess_market_data(self, market_items: list, path: str) -> list:
        
        date = market_items[0].find('div', class_= "market-data-dl-date").text.strip().split()
        date = " ".join(date[0:3])
        
        if path in MR_PATHS.keys():
            check_date = self.date # D-1   
            items = market_items 
        else:
            check_date = self.date - timedelta(days=1)
            items = [market_items[0]] # Work around to avoid error on using 'find' in Python use 'find' in bs4 instead
            
           
        print(items)
        print(type(date), type(check_date.strftime("%d %B %Y")), ONE_DATA_PATHS.keys(), path)
        #checks if the data for d-1 was already uploaded
        if not date == check_date.strftime("%d %B %Y"):
             raise Exception("Data was not yet uploaded in the IEMOP's website")
         
        return create_dictionary(*items)
    
    def _create_files(self, data: dict, direc: str) -> None:
    
        """__create_files: receives data as dictionary, direc (directory or path)
        
        This method will access the generated link from IEMOP then convert the response data from binary data to actual files then save the data to the target location

        """
    
        if not data:
            return None
        
        for i, item in data.items():
            
            file_loc = os.path.join(os.getcwd(), direc+"\\"+item.get("title"))
            
            market_data_link = self.uri+item.get("link")
            
            with requests.get(market_data_link) as response: 
                self.log.info("Date: {} File: {} Status: {}".format(
                    item.get("date"), 
                    item.get("title"), 
                    response.status_code))
                
                with open(file_loc, "wb") as file:
                    file.write(response.content)  

            if self._isformat(item.get("title"), "zip"):
                with ZipFile(file_loc, "r") as my_zip:
                    my_zip.extractall(direc)
                
                os.remove(file_loc)
    
                
    def download_data(self, **kwargs: dict):
        
        if not kwargs:
            raise "Expected to have an input at least one keyword argument, I got None"
        
        try:
            #Will place the kwargs to a variable
            self.local_paths = kwargs
            options = self._headless_option()
            
            # accessing paths of iemop    
            for key, value in self.local_paths.items(): 
                with Chrome(options=options) as driver:
                    self.uri = self.url+value
                    self.log.info(self.uri)
                    driver.set_page_load_timeout(20)
                    
                    # Note that the IEMOP pages may be slow at times. Retry the driver if ganon yung case
                    driver.get(self.uri) 
                    
                    # Page fully rendered.
                    html = driver.page_source 
                    
                    if not html:
                        raise Exception("No data receive will try to regather..")
                        
                        # Trying to call the function again if html is None value                        
                        # return self.download_data(self.local_paths) 
                        
                        # return -1 # Return -1 subprocess will reprocess the script retry it

                    self.log.info("{} -> Path: {} ".format(key, value))
                    
                    # Parsing html to find_all market-reports-items elements
                    market_items = BeautifulSoup(html, "html.parser").find_all('div', class_= "market-reports-item")
  
                    if market_items == []:
                        self.log.warning("No data received Exiting.. ")
                        
                        return -1 # Return -1 subprocess will reprocess the script retry it
                    
                        # Get the current index then use it to slice the dictionary then retry downloading from there
                        #return self.download_data(**MR_PATHS[:])

                    data = self._preprocess_market_data(market_items=market_items,path=key)
                    self.log.info(data)
                    direc = create_folders(default_path=default_path, fname=key)
                    self.log.info(f"Created folder for: {direc} ")
                    self._create_files(data, direc)
                    self.log.info("Downloading completed for {} .. Exiting...".format(key))
                    
        except TimeoutException:
            self.log.exception("Exception has been thrown. ")
            self.log.exception("Retrying.... ")
            

if __name__ == "__main__":
    get = GetMarketData(url=URI, default_path=default_path)
    for i in [MR_PATHS, ONE_DATA_PATHS]:
        get.download_data(**i)
