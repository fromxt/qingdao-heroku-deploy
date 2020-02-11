import schedule
import threading
import time
import web
urls = (
    '/qingdao', 'qingdao',
    '/addphone', 'addphone',
    '/removephone', 'removephone'
)

# app = web.application(urls,globals())
app = web.application(urls)

def go():
    print('go')

schedule.every().second.do(go)

def scheduleTask():
    while True:
        # 启动服务
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    threads = []
    threads.append(threading.Thread(target=scheduleTask))
    for t in threads:
        t.start()