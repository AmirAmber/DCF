# visualisation
# dcf calculator
# margins growth and ratios
#risk parameter

def get_next_key(list_of_keys,current_key):
    key_index = list_of_keys.index(current_key)
    if key_index == range(len(list_of_keys)):
        return list_of_keys[0]
    else:
        new_key = key_index + 1
        return list_of_keys[new_key]

list_length = 500
ticker_list = []
api_length = 10
api_list =[]
for ticker in range(list_length):
    ticker_list.append(ticker)

for api_key in range(api_length):
    api_list.append(api_key)
print(api_list)

def Financial_Parameters_For_Ticker(ticker,current_k):

    return  [{'a': 1}, {'b': 2}, {'d': 3}]

def send_list_of_ticker_objects_with_parameters(list_of_tickers,list_of_api_keys):
    request_count = 0
    key_count = 0

    list_of_ticker_objects = []

    for ticker in range(len(list_of_tickers)):
        while list_of_api_keys[key_count] != list_of_api_keys[-2]:
            if request_count == 150:
                key_count += 1
                current_key = get_next_key(list_of_api_keys,list_of_api_keys[key_count])
                request_count -= 150
                continue
            else:
                current_key = get_next_key(list_of_api_keys,list_of_api_keys[key_count])
                assighned_comp = Financial_Parameters_For_Ticker(list_of_tickers[ticker],current_key)
                list_of_ticker_objects.append(assighned_comp)
                request_count += 3
    return list_of_ticker_objects

please_work = send_list_of_ticker_objects_with_parameters(ticker_list,api_list)
print(please_work)
print(len(please_work))