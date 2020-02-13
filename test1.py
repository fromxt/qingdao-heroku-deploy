import datetime

def last_day_of_month(any_day):
    """
    获取获得一个月中的最后一天
    :param any_day: 任意日期
    :return: string
    """
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)  # this will never fail
    return next_month - datetime.timedelta(days=next_month.day)
# 抽奖
def isLastDay():
    
    # 当前日期
    now = datetime.datetime.now().date()
    year,month,day = str(now).split("-")  # 切割
    # 年月日，转换为数字
    year = int(year)
    month = int(month)
    day = int(day)

    # 获取这个月最后一天
    last_day = last_day_of_month(datetime.date(year, month, day))
    # 判断当前日期是否为月末
    if str(now) == last_day:
        return True
    else:
        return False

backFileName = 'phone.back'
fileName = 'phone.txt'
# 月底恢复记录
def recoverRecord():
    with open(backFileName,"r",encoding="utf-8") as f:
        lines = f.readlines()
    with open(fileName,"w",encoding="utf-8") as f_w:
        for line in lines:
            f_w.write(line)

if __name__ == "__main__":
    if isLastDay():
        print('gg')
    else:
        recoverRecord()