from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from math import radians, cos, sin, asin, sqrt

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# ==========================================
# [1] 데이터 설정 (좌표 수정 필수!)
# ==========================================

# 0. 숙소 목록 (난바 / 교토)
# ★여기에 주신 링크의 실제 좌표를 넣어주세요!★
ACCOMMODATIONS = {
    "namba": {"name": "오사카 숙소(난바)", "lat": 34.6631, "lon": 135.5020},  # 예: 난바역 근처
    "kyoto": {"name": "교토 숙소", "lat": 34.9850, "lon": 135.7580}         # 예: 교토역 근처
}

# 1. 친구들의 데이터
# color 옵션: red, blue, green, yellow, purple, pink, orange, gray
FRIENDS_DATA = [
    {
        "name": "윤진",
        "color": "red",
        "places": [
            {"name": "타몬군 팝업(핸즈 신사이바시)", "lat": 34.6750, "lon": 135.5000, "link": "https://maps.app.goo.gl/AfrZXGYPY7DvLfQGA?g_st=ac "},
            {"name": "타몬군 팝업(핸즈 아베노)", "lat": 34.6475, "lon": 135.5100, "link": "https://maps.app.goo.gl/aMzjBJnzVVYRSJxCA?g_st=ac "},
            {"name": "애니메이트 우메다", "lat": 34.7024, "lon": 135.4959, "link": "https://maps.app.goo.gl/qeBB15DFMCWu72nP8?g_st=ac "},
            {"name": "애니메이트 닛폰바시", "lat": 34.6595, "lon": 135.5058, "link": "https://maps.app.goo.gl/yVUQxsAnipduCjJ89 "},
            {"name": "애니메이트 교토", "lat": 35.0034, "lon": 135.7681, "link": "https://maps.app.goo.gl/PoPZW2KnD8Ncbpdw5?g_st=ac "},
            {"name": "이모야킨지로", "lat": 34.7050, "lon": 135.4900, "link": "https://maps.app.goo.gl/9uNHmzJzDLahafrR8?g_st=ac"},
            {"name": "도지하마 전망대", "lat": 34.6950, "lon": 135.4900, "link": "https://maps.app.goo.gl/SXtmtmCE2Qd38Go89?g_st=ac"},
        ]
    },
    {
        "name": "은성",
        "color": "blue",
        "places": [
            {"name": "니시키 카츠즈시(교토)", "lat": 35.0050, "lon": 135.7600, "link": "https://maps.app.goo.gl/7XgSYiTApXQnkdAf9"},
            {"name": "야키니쿠 나나시", "lat": 34.6700, "lon": 135.5000, "link": "https://maps.app.goo.gl/6vtc1qn7Dd3YGgxHA"},
            {"name": "이나후쿠 우동(교토)", "lat": 34.9670, "lon": 135.7700, "link": "https://maps.app.goo.gl/pwHjYXQpGEjGPYqf6"},
            {"name": "소바 로우지나(교토)", "lat": 35.0100, "lon": 135.7650, "link": "https://maps.app.goo.gl/ebMmBhHR8teDnuxx8"},
            {"name": "타치스시 마구로", "lat": 34.6650, "lon": 135.5020, "link": "https://maps.app.goo.gl/ZDPcBYYE7DSk125AA"},
            {"name": "본쿠라야 오코노미야키", "lat": 34.6680, "lon": 135.5010, "link": "https://maps.app.goo.gl/t8LZsbhy4FuY5oHdA"},
            {"name": "쿠시야 모노가타리(우메다)", "lat": 34.7030, "lon": 135.4970, "link": "https://maps.app.goo.gl/bDhQcSLicPRFX5Wa9"}
        ]
    },
    {
        "name": "준영",
        "color": "green",
        "places": [
            {"name": "토치토치 파르코", "lat": 34.6720, "lon": 135.4990, "link": "https://maps.app.goo.gl/q7w11kTAUKMuWxQC6"}
        ]
    }
]

# ==========================================
# [2] 거리 계산 함수 (Haversine 알고리즘)
# ==========================================
def haversine(lon1, lat1, lon2, lat2):
    """
    두 지점(위도, 경도) 사이의 거리를 km 단위로 계산
    """
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # 지구 반지름 (km)
    return c * r

# ==========================================
# [3] API 라우터
# ==========================================
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/data")
async def get_map_data():
    """
    각 장소가 '오사카 숙소'와 가까운지 '교토 숙소'와 가까운지 계산해서
    'region' 태그(namba 또는 kyoto)를 자동으로 달아줍니다.
    """
    processed_friends = []
    
    for friend in FRIENDS_DATA:
        # 원본 데이터 보호를 위해 복사
        new_friend = {"name": friend["name"], "color": friend["color"], "places": []}
        
        for place in friend["places"]:
            # 1. 난바 숙소까지의 거리
            dist_namba = haversine(ACCOMMODATIONS["namba"]["lon"], ACCOMMODATIONS["namba"]["lat"], place["lon"], place["lat"])
            
            # 2. 교토 숙소까지의 거리
            dist_kyoto = haversine(ACCOMMODATIONS["kyoto"]["lon"], ACCOMMODATIONS["kyoto"]["lat"], place["lon"], place["lat"])
            
            # 3. 더 가까운 곳을 'region'으로 설정
            if dist_namba < dist_kyoto:
                region = "namba"
                final_dist = dist_namba
            else:
                region = "kyoto"
                final_dist = dist_kyoto
                
            # 장소 정보에 지역(region)과 거리(distance) 정보 추가
            new_place = place.copy()
            new_place["region"] = region
            new_place["distance"] = round(final_dist, 2)
            
            new_friend["places"].append(new_place)
            
        # 4. 거리순으로 정렬 (가까운 순서대로)
        new_friend["places"].sort(key=lambda x: x["distance"])
        processed_friends.append(new_friend)
        
    return {"accommodations": ACCOMMODATIONS, "friends": processed_friends}