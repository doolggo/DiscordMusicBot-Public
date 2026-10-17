# Discord Music Bot

## 프로젝트 소개

Discord 음성 채널에서 음악을 재생하기 위해 Python으로 개발한 음악봇입니다.

기존 음악봇의 신청곡 재생 방식에서 벗어나, 사용자가 별도로 음악을 신청하지 않아도 새로운 음악을 들을 수 있는 기능을 구현하고자 개발했습니다.

## 개발 배경

Discord를 이용하면서 신청곡이 없을 때 음악 재생이 중단되는 점이 아쉬웠습니다.

이를 개선하고자 SoundCloud 기반 음악 검색 및 재생 기능과 무작위 음악 선택 기능을 개발했습니다.

## 사용 기술

- Python
- discord.py
- yt-dlp
- asyncio
- random
- Microsoft Azure Ubuntu VM

## 주요 개발 기능

- Discord 봇 명령어 처리
- 음성 채널을 통한 음악 재생
- 사용자 신청곡 처리
- 무작위 음악 선택 및 재생

## 프로젝트 파일

- bot.py : 음악봇 소스 코드
- requirements.txt : Python 라이브러리
- .gitignore : 업로드 제외 파일 설정

## 실행 준비

필요한 라이브러리 설치:

    pip install -r requirements.txt

Discord Developer Portal에서 발급받은 봇 토큰을 DISCORD_BOT_TOKEN 환경변수로 설정해야 합니다.

실행 명령어:

    python bot.py

음성 재생에는 FFmpeg 설치 및 추가 환경 설정이 필요할 수 있습니다.

## 개발 경험

Discord를 실제로 사용하며 느꼈던 불편함에서 출발하여 직접 필요한 기능을 구현했습니다.

Python의 비동기 처리와 Discord 봇 라이브러리를 활용했고, Microsoft Azure의 Ubuntu 가상 머신을 이용한 서버 운영도 경험했습니다.

## 참고사항

본 프로젝트는 개인 학습 및 개발 목적으로 제작되었습니다.

실행 환경과 외부 음악 서비스의 정책에 따라 일부 기능은 추가 설정 또는 수정이 필요할 수 있습니다.

Discord Bot Token과 인증 쿠키 등 민감정보는 저장소에 포함하지 않습니다.
