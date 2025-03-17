import re

def extract_game_id(link: str) -> str:
    match = re.search(r"app/(\d+)", link)
    return match.group(1) if match else None

def get_game_image_url(link: str) -> str:
    game_id = extract_game_id(link)
    if game_id:
        return f"https://shared.cloudflare.steamstatic.com/store_item_assets/steam/apps/{game_id}/header.jpg"
    return "https://via.placeholder.com/460x215?text=Image+Not+Available"
