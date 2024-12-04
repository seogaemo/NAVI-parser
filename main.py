import os
import json
import math
import warnings
import os.path as osp
from tqdm import tqdm
from dotenv import load_dotenv
from uuid import uuid4

from utils.db import DB
from utils.parse import Parse
from utils.s3 import S3Uploader
from utils.extractor import FrameExtractor

load_dotenv()
warnings.filterwarnings("ignore")


class App:
    def __init__(self, path) -> None:
        self.path = path
        self.videos = self.getVideos()

        self.videoPoints = []
        self.getParsedData()

        self.s3 = S3Uploader()
        self.db = DB()
        self.processing()

    def getVideos(self):
        videos = []
        for root, _, files in os.walk(self.path):
            for file in files:
                if file.lower().endswith(".mp4"):
                    videos.append(osp.join(root, file))
        return videos

    def loadParsedData(self):
        with open("parsed.json", "r") as f:
            self.videoPoints = json.loads(f.read())

    def getParsedData(self):
        if osp.exists("parsed.json"):
            confirm = input(
                "Do you want to use the existing parsed data? (Y/n): "
            )
            if confirm == "y" or confirm == "":
                self.loadParsedData()
                return

        for video in tqdm(self.videos, desc="Parsing videos", unit="video"):
            parse = Parse(video)

            # 초당 하나씩 필터링
            filteredData = []
            currentSecond = -1

            for entry in parse.gpxData["points"]:
                durationSecond = int(entry["duration"])
                if durationSecond > currentSecond:
                    filteredData.append(entry)
                    currentSecond = durationSecond

            # 좌표, 속도, 영상 정보 등
            self.videoPoints.append({parse.gpxData["video"]: filteredData})

        self.saveParsedData()

    def saveParsedData(self):
        with open("parsed.json", "w") as f:
            f.write(json.dumps(self.videoPoints, indent=2))

    def processing(self):
        # length 구하기
        length = 0
        for videoPoint in self.videoPoints:
            for _, points in videoPoint.items():
                length += len(points)

        with tqdm(total=length, desc="Processing frames", unit="frame") as pbar:
            for videoPoint in self.videoPoints:
                for videoPath, points in videoPoint.items():
                    extractor = FrameExtractor(
                        osp.join(path, *videoPath.split("/")[1:])
                    )

                    for point in points:
                        try:
                            id = str(uuid4())
                            frame = extractor.extractFrame(
                                math.trunc(point["duration"])
                                - 0.15  # 오류 방지
                            )
                            isFrame = frame is not None

                            # S3에 업로드
                            key = f"{id}.jpg"
                            self.s3.uploadFrame(frame, key)

                            # DB에 저장
                            self.db.insertData(
                                {
                                    "id": id,
                                    "lat": point["lat"],
                                    "lng": point["lng"],
                                    "ele": point["ele"],
                                    "time": point["time"],
                                    "duration": point["duration"],
                                    "speed": point["speed"],
                                    "video": videoPath,
                                    "image": isFrame,
                                }
                            )

                            pbar.update(1)
                        except Exception as e:
                            print(e)

                    del extractor


if __name__ == "__main__":
    path = osp.join("/", "Volumes", "T7", "road-data")
    app = App(path)
