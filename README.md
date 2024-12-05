# Parser

## Gopro2gpx install

```bash
git clone https://github.com/seogaemo/gopro2gpx.git
cd gopro2gpx
python3 setup.py install
```

## Flow

- GoPro 데이터 파싱 (gopro2gpx lib 사용) -> gpx 파일 추출
- gpx 파일에서 영상 정보 및 **duration별 position** 추출
- 해당 duration 기반으로 영상에서 still frame 추출
- still frame S3에 업로드
- postgres에 commit (위치 정보, 사용된 영상, key 값 등)
