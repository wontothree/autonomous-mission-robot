# PrimeHub 클래스를 가져옵니다.
from spike import PrimeHub
from spike.control import wait_for_seconds

# 허브를 초기화합니다.
your_hub = PrimeHub()

# 스마일리 얼굴에 불을 켭니다.
your_hub.light_matrix.show_image('Happy')
wait_for_seconds(5)
your_hub.light_matrix.off()

# 다른 이미지를 추가합니다.
your_hub.loght_matrix.show_image('HEART')
wait_for_seconds(5)
your_hub.light_matrix.off()