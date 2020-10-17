from com.utils import utils
import com.config as config

JSON_INFO = utils.users_info_load(config.users_path)
user_uname = "18740455867"
user_info = {
    "code": "zt18740455867",
    "industry": "computer",
    "ps": "张同",
    "today": 0
}
if __name__ == '__main__':
    JSON_INFO["users_info"][user_uname] = user_info
    utils.users_info_dump(config.users_path, JSON_INFO)
