from multiprocessing import freeze_support

from tasks.dispatcher import dispatch


if __name__ == '__main__':
    freeze_support()
    dispatch()
