from collect_market_data import GetMarketData
from market_functions.iemop_paths import MR_PATHS, ONE_DATA_PATHS, URI, default_path # Move the imports to another file

if __name__ == "__main__":
    get = GetMarketData(url=URI, default_path=default_path)
    for i in [MR_PATHS, ONE_DATA_PATHS]:
        get.download_data(**i)
