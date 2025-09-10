from pymongo import MongoClient
from config import MONGO_URI, DB_NAME

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

companies_data = [
    {
        "rank": 1,
        "name": "Walmart",
        "revenues_million": 648125,
        "revenue_percent_change": 6.0,
        "profits_million": 15511,
        "profits_percent_change": 32.8,
        "assets_million": 252399,
        "employees": 2100000,
        "change_in_rank": None,
        "years_on_list": 30
    },
    {
        "rank": 2,
        "name": "Amazon",
        "revenues_million": 574785,
        "revenue_percent_change": 11.8,
        "profits_million": 30425,
        "profits_percent_change": None,
        "assets_million": 527854,
        "employees": 1525000,
        "change_in_rank": 2,
        "years_on_list": 16
    },
    {
        "rank": 7,
        "name": "Apple",
        "revenues_million": 383285,
        "revenue_percent_change": -2.8,
        "profits_million": 96995,
        "profits_percent_change": -2.8,
        "assets_million": 352583,
        "employees": 161000,
        "change_in_rank": 1,
        "years_on_list": 22
    },
    {
        "rank": 8,
        "name": "UnitedHealth Group",
        "revenues_million": 371622,
        "revenue_percent_change": 14.6,
        "profits_million": 22381,
        "profits_percent_change": 11.2,
        "assets_million": 273720,
        "employees": 440000,
        "change_in_rank": 2,
        "years_on_list": 28
    },
    {
        "rank": 9,
        "name": "Berkshire Hathaway",
        "revenues_million": 364482,
        "revenue_percent_change": 20.7,
        "profits_million": 96223,
        "profits_percent_change": None,
        "assets_million": 1069978,
        "employees": 396500,
        "change_in_rank": 5,
        "years_on_list": 28
    },
    {
        "rank": 10,
        "name": "CVS Health",
        "revenues_million": 357776,
        "revenue_percent_change": 11.0,
        "profits_million": 8344,
        "profits_percent_change": 101.1,
        "assets_million": 249728,
        "employees": 259500,
        "change_in_rank": 1,
        "years_on_list": 29
    },
    {
        "rank": 15,
        "name": "Toyota Motor",
        "revenues_million": 312018.2,
        "revenue_percent_change": 13.7,
        "profits_million": 34214.4,
        "profits_percent_change": 88.9,
        "assets_million": 595915.2,
        "employees": 380793,
        "change_in_rank": 4,
        "years_on_list": 30
    },
    {
        "rank": 17,
        "name": "Alphabet",
        "revenues_million": 307394,
        "revenue_percent_change": 8.7,
        "profits_million": 73795,
        "profits_percent_change": 23.1,
        "assets_million": 402392,
        "employees": 182502,
        "change_in_rank": None,
        "years_on_list": 16
    },
    {
        "rank": 20,
        "name": "Costco Wholesale",
        "revenues_million": 242290,
        "revenue_percent_change": 6.8,
        "profits_million": 6292,
        "profits_percent_change": 7.7,
        "assets_million": 68994,
        "employees": 316000,
        "change_in_rank": 6,
        "years_on_list": 30
    },
    {
        "rank": 21,
        "name": "JPMorgan Chase",
        "revenues_million": 239425,
        "revenue_percent_change": 54.7,
        "profits_million": 49552,
        "profits_percent_change": 31.5,
        "assets_million": 3875393,
        "employees": 309926,
        "change_in_rank": 32,
        "years_on_list": 30
    },
    {
        "rank": 26,
        "name": "Microsoft",
        "revenues_million": 211915,
        "revenue_percent_change": 6.9,
        "profits_million": 72361,
        "profits_percent_change": -0.5,
        "assets_million": 411976,
        "employees": 221000,
        "change_in_rank": 4,
        "years_on_list": 27
    },
    {
        "rank": 31,
        "name": "Samsung Electronics",
        "revenues_million": 198256.7,
        "revenue_percent_change": -15.3,
        "profits_million": 11081.7,
        "profits_percent_change": -73.9,
        "assets_million": 351936.8,
        "employees": 267860,
        "change_in_rank": -6,
        "years_on_list": 30
    },
    {
        "rank": 38,
        "name": "Bank of America",
        "revenues_million": 171912,
        "revenue_percent_change": 49.4,
        "profits_million": 26515,
        "profits_percent_change": -3.7,
        "assets_million": 3180151,
        "employees": 212985,
        "change_in_rank": 44,
        "years_on_list": 30
    },
    {
        "rank": 40,
        "name": "Elevance Health",
        "revenues_million": 171340,
        "revenue_percent_change": 9.4,
        "profits_million": 5987,
        "profits_percent_change": -0.6,
        "assets_million": 108928,
        "employees": 104900,
        "change_in_rank": 11,
        "years_on_list": 23
    },
    {
        "rank": 41,
        "name": "BMW Group",
        "revenues_million": 168102.6,
        "revenue_percent_change": 12.1,
        "profits_million": 12205.2,
        "profits_percent_change": -35.3,
        "assets_million": 277104,
        "employees": 154950,
        "change_in_rank": 16,
        "years_on_list": 30
    },
    {
        "rank": 46,
        "name": "Centene",
        "revenues_million": 153999,
        "revenue_percent_change": 6.5,
        "profits_million": 2702,
        "profits_percent_change": 124.8,
        "assets_million": 84641,
        "employees": 67700,
        "change_in_rank": 14,
        "years_on_list": 9
    },
    {
        "rank": 48,
        "name": "Home Depot",
        "revenues_million": 152669,
        "revenue_percent_change": -3.0,
        "profits_million": 15143,
        "profits_percent_change": -11.5,
        "assets_million": 76530,
        "employees": 463100,
        "change_in_rank": None,
        "years_on_list": 30
    },
    {
        "rank": 62,
        "name": "Banco Santander",
        "revenues_million": 137244.8,
        "revenue_percent_change": 38.3,
        "profits_million": 11973.8,
        "profits_percent_change": 18.5,
        "assets_million": 1984826.6,
        "employees": 207206,
        "change_in_rank": 42,
        "years_on_list": 30
    },
    {
        "rank": 66,
        "name": "Meta Platforms",
        "revenues_million": 134902,
        "revenue_percent_change": 15.7,
        "profits_million": 39098,
        "profits_percent_change": 68.5,
        "assets_million": 229623,
        "employees": 67317,
        "change_in_rank": 15,
        "years_on_list": 8
    },
    {
        "rank": 67,
        "name": "HSBC Holdings",
        "revenues_million": 134901,
        "revenue_percent_change": 53.6,
        "profits_million": 23533,
        "profits_percent_change": 46.8,
        "assets_million": 3038677,
        "employees": 220861,
        "change_in_rank": 63,
        "years_on_list": 30
    }
]

db.companies.insert_many(companies_data)
print("✅ 20 companies inserted successfully!")
