from backend.db.redis import RedisSettings, RedisDB
from definitions import DEV_ENV_PATH, TIMELINE_FILE
from dotenv import load_dotenv


if __name__ == '__main__':
    load_dotenv(DEV_ENV_PATH)
    settings = RedisSettings()
    redis = RedisDB(settings)
    with open(TIMELINE_FILE, 'w') as file:
        d = {info for info in redis.get_all_infos()}
        with_date = {data_ for data_ in filter(lambda data: data.datetime_original, d)}
        date_none = {data_ for data_ in filter(lambda data: data.datetime_original is None, d)}
        print('failed ', date_none)

        sorted_ = sorted(with_date, key=lambda data: data.datetime_original)
        file.writelines(
            item.save_path+'\n' for item in sorted_
        )

