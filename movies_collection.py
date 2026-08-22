import requests
from lxml import html
import csv
import re


TMDB_BASE_URL = "https://www.themoviedb.org"
TMDB_HOT_URL_1 = "https://www.themoviedb.org/movie"
TMDB_HOT_URL_2 = "https://www.themoviedb.org/discover/movie/items"
MOVIE_INFO_CSV = "csv_data/hot_movies.csv"


def movie_date(movie_dates):
    movie_date = movie_dates[0].strip() if movie_dates else ""
    return re.search(r"\d{4}-\d{2}-\d{2}", movie_date).group() if movie_date else ""


def movie_time(movie_times):
    movie_time = movie_times[0].strip() if movie_times else ""
    hour = re.search(r"(\d+)h", movie_time)
    h = int(hour.group(1)) if hour else 0
    minute = re.search(r"(\d+)m", movie_time)
    m = int(minute.group(1)) if minute else 0
    return h*60+m


def get_movie_info(movie_urls):
    """
    获取电影名字、上映时间、类型、时长、评分、简介、导演、主演
    :param movie_urls:
    :return:
    """
    response = requests.get(movie_urls, timeout=60)
    movie_doc = html.fromstring(response.text)
    movie_titles = movie_doc.xpath("//*[@id='original_header']/div[2]/section/div[1]/h2/a/text()")
    movie_dates = movie_doc.xpath("//*[@id='original_header']/div[2]/section/div[1]/div/span[@class ='release']/text()")
    movie_types = movie_doc.xpath("//*[@id='original_header']/div[2]/section/div[1]/div/span[@class ='genres']/a/text()")
    movie_times = movie_doc.xpath("//*[@id='original_header']/div[2]/section/div[1]/div/span[@class ='runtime']/text()")
    movie_scores = movie_doc.xpath("//*[@class='user_score_chart']/@data-percent")
    movie_introductions = movie_doc.xpath("//*[@class='overview']/p/text()")
    movie_directors = movie_doc.xpath("//*[@class='people no_image']/li[1]/p[1]/a/text()")
    movie_actors = movie_doc.xpath("//*[@class='people scroller']/li[@class='card']/p/a/text()")

    movie_dict = {
        "电影名": movie_titles[0].strip() if movie_titles else "",
        "上映时间": movie_date(movie_dates),
        "类型": ",".join(movie_types).strip() if movie_types else "",
        "时长": movie_time(movie_times),
        "评分": movie_scores[0].strip() if movie_scores else "",
        "简介": movie_introductions[0].strip() if movie_introductions else "",
        "导演": movie_directors[0].strip() if movie_directors else "",
        "主演": ",".join(movie_actors).strip() if movie_actors else ""
    }
    return movie_dict




def save_videos(all_movies):
    with open(MOVIE_INFO_CSV, "w", encoding="UTF-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=all_movies[0].keys())
        writer.writeheader()
        writer.writerows(all_movies)


def main():
    all_movies = []
    for page in range(1,6):
        if page == 1:
            response = requests.get(TMDB_HOT_URL_1, timeout=60)
        else:
            response = requests.post(TMDB_HOT_URL_2,f"air_date.gte=&air_date.lte=&certification=&certification_country=CN&debug=&first_air_date.gte=&first_air_date.lte=&include_adult=false&include_softcore=false&latest_ceremony.gte=&latest_ceremony.lte=&page={page}&primary_release_date.gte=&primary_release_date.lte=&region=&release_date.gte=&release_date.lte=2027-02-22&show_me=everything&sort_by=popularity.desc&vote_average.gte=0&vote_average.lte=10&vote_count.gte=0&watch_region=CN&with_genres=&with_keywords=&with_networks=&with_origin_country=&with_original_language=&with_watch_monetization_types=&with_watch_providers=&with_release_type=&with_runtime.gte=0&with_runtime.lte=400", timeout=60)
        doc = html.fromstring(response.text)
        movie_list = doc.xpath("//*[@class='media-list-results contents']/div")
        for movie in movie_list:
            movie_urls = TMDB_BASE_URL + movie.xpath("./div/div[1]/a/@href")[0]
            if movie_urls:
                # 获取视频信息
                movie_info = get_movie_info(movie_urls)
                all_movies.append(movie_info)

    # 保存视频信息为csv文件
    save_videos(all_movies)







if __name__ == '__main__':
    main()