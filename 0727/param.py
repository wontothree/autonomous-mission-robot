# Message key
class Message():
    Sender = 'Sender'
    Receiver = 'Receiver'
    Command = 'Command'
    Data = 'Data'

class Sender():
    name = 'Robot name' #팀 이름
    solar = 'Solar'
    wind = 'Wind'

class Receiver():
    name = 'Robot name'
    solar = 'Solar'
    wind = 'Wind'

class Command():
    #공통
    Finish = 'F' #스테이션 동작 완료 확인
    #풍력터빈
    Run = 'R' #모터 동작
    #태양광 발전기
    CW = 'CW' #모터 시계방향으로 움직이기
    CCW = 'CCW' #모터 반시계방향으로 움직이기
    Stop = 'S' #모터 멈추기
    Data = 'D' #전력 데이터 송신
    