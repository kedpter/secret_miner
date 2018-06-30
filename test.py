import threading
import time

# def doit(stop_event, arg):
#     print('wait 3s')
#     while not stop_event.wait(3):
#         print("working on %s" % arg)
#     print("Stopping as you wish.")

# def main():
#     pill2kill = threading.Event()
#     t = threading.Thread(target=doit, args=(pill2kill, "task"))
#     t.start()
#     # time.sleep(8)
#     # pill2kill.set()
#     t.join()
#     print('main loop enter here')

# main()

from multiprocessing import Process


def f(name):
    while True:
        time.sleep(1)
        print('hello', name)


if __name__ == '__main__':
    p = Process(target=f, args=('bob', ))
    p.start()
    time.sleep(5)
    p.terminate()
    p.join()
    print('hi')
