import os
from bs4 import BeautifulSoup

def create_dictionary(*args: list) -> dict:
        
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

        Returns:
            dictionary: returns market_data as dictionary
        """
        
        market_data = {}
                
        for index, market_item in enumerate(args):
                
                    title = market_item.find('div', class_= "market-reports-title").text.strip().split()[0]
                    date = market_item.find('div', class_= "market-data-dl-date").text.strip()
                    link = market_item.find('a').get("href")
                    
                    new_item = dict([("date", date), ("title", title), ("link", link)])
                    append_item = dict([(index, new_item)])
                    market_data.update(append_item)
                    
        return market_data
    


                    
def create_folders(default_path: str, fname: str) -> str:
    """Creates folders relative to the default path then the folder name. 

    Args:
        key string: key (name of data) from the dictionary

    Returns:
        string: return string dir_name to used as the file location for creating the files
    """
        
    folder_name = " ".join(fname.split("_")).lower()
    print(os.getcwd())
    dir_name = os.path.join(os.getcwd(), default_path+"\\"+folder_name)
    print(dir_name)
    
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)

    return dir_name

def _test_import():
    return "Hello World"
