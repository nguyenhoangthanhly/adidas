def get_region_mapping():
    return {
    'Midwest': 0,
    'Northeast': 1,
    'South': 2,
    'Southeast': 3,
    'West': 4
    }

def get_state_mapping():
    return {
    'Alabama': 0, 'Alaska': 1, 'Arizona': 2, 'Arkansas': 3, 'California': 4,
    'Colorado': 5, 'Connecticut': 6, 'Delaware': 7, 'Florida': 8, 'Georgia': 9,
    'Hawaii': 10, 'Idaho': 11, 'Illinois': 12, 'Indiana': 13, 'Iowa': 14,
    'Kansas': 15, 'Kentucky': 16, 'Louisiana': 17, 'Maine': 18, 'Maryland': 19,
    'Massachusetts': 20, 'Michigan': 21, 'Minnesota': 22, 'Mississippi': 23,
    'Missouri': 24, 'Montana': 25, 'Nebraska': 26, 'Nevada': 27,
    'New Hampshire': 28, 'New Jersey': 29, 'New Mexico': 30, 'New York': 31,
    'North Carolina': 32, 'North Dakota': 33, 'Ohio': 34, 'Oklahoma': 35,
    'Oregon': 36, 'Pennsylvania': 37, 'Rhode Island': 38, 'South Carolina': 39,
    'South Dakota': 40, 'Tennessee': 41, 'Texas': 42, 'Utah': 43,
    'Vermont': 44, 'Virginia': 45, 'Washington': 46, 'West Virginia': 47,
    'Wisconsin': 48, 'Wyoming': 49
    }

def get_city_mapping():
    return {
    'Albany': 0, 'Albuquerque': 1, 'Anchorage': 2, 'Atlanta': 3, 'Baltimore': 4,
    'Billings': 5, 'Birmingham': 6, 'Boise': 7, 'Boston': 8, 'Burlington': 9,
    'Charleston': 10, 'Charlotte': 11, 'Cheyenne': 12, 'Chicago': 13,
    'Columbus': 14, 'Dallas': 15, 'Denver': 16, 'Des Moines': 17, 'Detroit': 18,
    'Fargo': 19, 'Hartford': 20, 'Honolulu': 21, 'Houston': 22,
    'Indianapolis': 23, 'Jackson': 24, 'Knoxville': 25, 'Las Vegas': 26,
    'Little Rock': 27, 'Los Angeles': 28, 'Louisville': 29, 'Manchester': 30,
    'Miami': 31, 'Milwaukee': 32, 'Minneapolis': 33, 'New Orleans': 34,
    'New York': 35, 'Newark': 36, 'Oklahoma City': 37, 'Omaha': 38,
    'Orlando': 39, 'Philadelphia': 40, 'Phoenix': 41, 'Portland': 42,
    'Providence': 43, 'Richmond': 44, 'Salt Lake City': 45, 'San Francisco': 46,
    'Seattle': 47, 'Sioux Falls': 48, 'St. Louis': 49, 'Wichita': 50,
    'Wilmington': 51
    }

def get_product_mapping():
    return {
    "Men's Apparel": 0, "Men's Athletic Footwear": 1, "Men's Street Footwear": 2,
    "Women's Apparel": 3, "Women's Athletic Footwear": 4, "Women's Street Footwear": 5
    }

def get_sales_method_mapping():
    return {
    'In-store': 0,
    'Online': 1,
    'Outlet': 2
    }

def get_retailer_mapping():
    return {
    'Amazon': 0, 'Foot Locker': 1, "Kohl's": 2, 'Sports Direct': 3,
    'Walmart': 4, 'West Gear': 5
    }

def find_seasons(monthNumber):
    if monthNumber in [1, 2, 3]:
        return 1

    elif monthNumber in [4, 5, 6]:
        return 2

    elif monthNumber in [7, 8 ,9]:
        return 3

    elif monthNumber in [10, 11, 12]:
        return 4

def prepare_data(data_predict,
            region_mapping,state_mapping,
            city_mapping,product_mapping,
            retailer_mapping,sales_method_mapping):

    # data_predict['Region'] = data_predict['Region'].map(region_mapping)
    # data_predict['State'] = data_predict['State'].map(state_mapping)
    # data_predict['City'] = data_predict['City'].map(city_mapping)
    # data_predict['Product'] = data_predict['Product'].map(product_mapping)
    # data_predict['Retailer'] = data_predict['Retailer'].map(retailer_mapping)
    # data_predict['Sales Method'] = data_predict['Sales Method'].map(sales_method_mapping)
    data_predict['Region'] = data_predict['Region'].apply(lambda x: str(x) if isinstance(x, list) else x).map(region_mapping)
    data_predict['State'] = data_predict['State'].apply(lambda x: str(x) if isinstance(x, list) else x).map(state_mapping)
    data_predict['City'] = data_predict['City'].apply(lambda x: str(x) if isinstance(x, list) else x).map(city_mapping)
    data_predict['Product'] = data_predict['Product'].apply(lambda x: str(x) if isinstance(x, list) else x).map(product_mapping)
    data_predict['Retailer'] = data_predict['Retailer'].apply(lambda x: str(x) if isinstance(x, list) else x).map(retailer_mapping)
    data_predict['Sales Method'] = data_predict['Sales Method'].apply(lambda x: str(x) if isinstance(x, list) else x).map(sales_method_mapping)
    # Add additional features if needed, such as season
    data_predict['Season'] = data_predict['Month'].apply(find_seasons)
    
    return data_predict
