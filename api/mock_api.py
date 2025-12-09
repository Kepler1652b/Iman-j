from flask import Flask, jsonify

app = Flask(__name__)

# Mock data for movies, series, and episodes
mock_data = {
    20518: {
        "note": "پیام تلگرامی",
        "id": 20518,
        "title": "Vaincre ou mourir",
        "type": "movie",
        "description": "فیلم داستان نجیب‌زاده شریفی به نام فرانسوا آتاناس شارت دو لا کانتری است که به کمک دهقانان خشمگین تصمیم می‌گیرد سرزمین‌های از دست رفته را پس بگیرند.",
        "year": 2022,
        "duration": "1 ساعت و 40 دقیقه",
        "imdb": 5.4,
        "persian": True,
        "image": "https://dev.oldfilamtestdash.xyz/uploads/cache/poster_thumb/uploads/jpg/b17b9a3d2e23c9156485f93051589f2c.jpg",
        "cover": "https://dev.oldfilamtestdash.xyz/uploads/cache/cover_thumb/uploads/jpg/2111938fa8805974d199e69205c15ba8.jpg",
        "trailer": {
            "id": 426676,
            "type": "mp4",
            "url": "https://trailer.mamaldomi.xyz/Trailers/V/Vaincre.ou.mourir.2022.trailer.mp4?token=zJr_nV4Fn6iMew5RCEL2bIvalQEZ-wgiRyHs7N6g38c&expires=1762639025"
        },
        "genres": [{"id": 7, "title": "اکشن"}, {"id": 9, "title": "تاریخی"}],
        "countries": [{"id": 63, "title": "فرانسه", "image": "https://dev.oldfilamtestdash.xyz/uploads/cache/country_thumb/uploads/jpg/43ca4db37671753f9866f27005321cd3.jpg"}],
        "actors": [{"id": 43032, "name": "Hugo Becker", "image": "https://dev.oldfilamtestdash.xyz/uploads/cache/actor_thumb/uploads/jpg/12ea0b8f66f93ea259b61cf1ca282e3c.jpg"}]
    },
    20512: {
        "note": "پیام تلگرامی",
        "id": 20512,
        "title": "Penelope",
        "type": "serie",
        "description": "یک نوجوان 16 ساله که با دنیای پیشرفته امروزی خو نمی گیرد، برای شناختن خود، سفری در بیابان های دورافتاده شمال غربی اقیانوس آرام را آغاز می کند.",
        "year": 2024,
        "duration": "پایان فصل 1",
        "imdb": 6.2,
        "persian": False,
        "image": "https://dev.oldfilamtestdash.xyz/uploads/cache/poster_thumb/uploads/jpg/46b0f489e4c4daee8c264320e9ea8ee5.jpg",
        "cover": "https://dev.oldfilamtestdash.xyz/uploads/cache/cover_thumb/uploads/jpg/9455020b4025ed15abe25ca5414b2090.jpg",
        "trailer": {
            "id": 426689,
            "type": "mp4",
            "url": "https://trailer.mamaldomi.xyz/Trailers/P/Penelope.2024.trailer.mp4?token=P1ysLJmT0Upv9isXHponIYJWg5kyzKK1JZEwrqKPXM4&expires=1762639461"
        },
        "genres": [{"id": 14, "title": "درام"}],
        "countries": [{"id": 191, "title": "آمریکا", "image": "https://dev.oldfilamtestdash.xyz/uploads/cache/country_thumb/uploads/jpg/94b30ca9da3dde62162bcf9a4196eb7f.jpg"}],
        "actors": [{"id": 53002, "name": "Megan Stott", "image": "https://dev.oldfilamtestdash.xyz/uploads/cache/actor_thumb/uploads/jpg/6ce17795d292854a9633a96e81efa559.jpg"}],
        "season_count": 1
    },
    132246: {
        "note": "پیام تلگرامی",
        "id": 132246,
        "title": "Penelope - Episode 1",
        "type": "episode",
        "description": "اولین قسمت از فصل 1 سریال پنلوپه.",
        "year": 2024,
        "duration": "60 دقیقه",
        "imdb": 6.2,
        "persian": False,
        "image": "https://dev.oldfilamtestdash.xyz/uploads/cache/poster_thumb/uploads/jpg/46b0f489e4c4daee8c264320e9ea8ee5.jpg",
        "cover": "https://dev.oldfilamtestdash.xyz/uploads/cache/cover_thumb/uploads/jpg/9455020b4025ed15abe25ca5414b2090.jpg",
        "trailer": {
            "id": 426689,
            "type": "mp4",
            "url": "https://trailer.mamaldomi.xyz/Trailers/P/Penelope.2024.trailer.mp4?token=P1ysLJmT0Upv9isXHponIYJWg5kyzKK1JZEwrqKPXM4&expires=1762639461"
        },
        "genres": [{"id": 14, "title": "درام"}],
        "countries": [{"id": 191, "title": "آمریکا", "image": "https://dev.oldfilamtestdash.xyz/uploads/cache/country_thumb/uploads/jpg/94b30ca9da3dde62162bcf9a4196eb7f.jpg"}],
        "actors": [{"id": 53002, "name": "Megan Stott", "image": "https://dev.oldfilamtestdash.xyz/uploads/cache/actor_thumb/uploads/jpg/6ce17795d292854a9633a96e81efa559.jpg"}],
        "season_count": 1,
        "episode": {
            "id": 132246,
            "title": "قسمت 1",
            "description": "بسیار زیبا",
            "duration": "60 دقیقه",
            "season": {
                "id": 8226,
                "title": "فصل 1"
            }
        }
    }
}

@app.route('/api/movies/<int:movie_id>', methods=['GET'])
def get_movie(movie_id):
    movie = mock_data.get(movie_id)
    if movie and movie['type'] == 'movie':
        return jsonify(movie)
    else:
        return jsonify({"error": "Movie not found"}), 404

@app.route('/api/series/<int:series_id>', methods=['GET'])
def get_series(series_id):
    series = mock_data.get(series_id)
    if series and series['type'] == 'serie':
        return jsonify(series)
    else:
        return jsonify({"error": "Series not found"}), 404

@app.route('/api/episodes/<int:episode_id>', methods=['GET'])
def get_episode(episode_id):
    episode = mock_data.get(episode_id)
    if episode and 'episode' in episode:
        return jsonify(episode)
    else:
        return jsonify({"error": "Episode not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
