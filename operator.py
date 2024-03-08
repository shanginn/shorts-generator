import requests
from typing import List
from termcolor import colored

class Stock:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def search_pexels(self, query: str, per_page: int) -> dict:
        base_url = "https://api.pexels.com/videos/search"
        headers = {
            "Authorization": self.api_key
        }

        url = f"{base_url}?query={query}&per_page={per_page}"

        return requests.get(url, headers=headers).json()

    def search_for_stock_videos(
        self,
        query: str,
        min_dur: int
    ) -> List[str]:
        per_page = 10
        response = self.search_pexels(query, per_page)

        raw_urls = []
        video_url = []
        video_res = 0
        try:
            # loop through each video in the result
            for i in range(per_page):
                # check if video has desired minimum duration
                if response["videos"][i]["duration"] < min_dur:
                    continue
                raw_urls = response["videos"][i]["video_files"]
                temp_video_url = ""

                # loop through each url to determine the best quality
                for video in raw_urls:
                    # Check if video has a valid download link
                    if ".com/external" in video["link"]:
                        # Only save the URL with the largest resolution
                        if (video["width"] * video["height"]) > video_res:
                            temp_video_url = video["link"]
                            video_res = video["width"] * video["height"]

                # add the url to the return list if it's not empty
                if temp_video_url != "":
                    video_url.append(temp_video_url)

        except Exception as e:
            print(colored("[-] No Videos found.", "red"))
            print(colored(e, "red"))

        # Let user know
        print(colored(f"\t=> \"{query}\" found {len(video_url)} Videos", "cyan"))

        # Return the video url
        return video_url
