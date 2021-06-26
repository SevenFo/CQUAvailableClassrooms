from os import P_DETACH, curdir, times
from typing import List
import sqlite3
import requests
import json
import re
from requests.api import head
import time

from requests.sessions import session


class UniversityTimetableGeter():
    def __init__(self) -> None:
        self.url_base = "http://my.cqu.edu.cn/"
        self.max_week = "timetable-api/course/maxWeek"
        self.courseCate = "timetable-api/optionFinder/courseCategory"
        self.courseDept = "resource-api/department/list?"
        self.buildings = "resource-api/optionFinder/buildingFinder"
        self.session = "timetable-api/optionFinder/session?blankOption=false"
        self.activtytype = "timetable-api/optionFinder/schedule-temp-activity-type?blankOption=true"
        self.campusNum = "resource-api/optionFinder/campusShortNm?blankOption=true"
        self.exam = "exam-api/api/all-exam-schedule"
        self.session = requests.session()
        self.url_coursesfilter = "http://my.cqu.edu.cn/timetable-api/class/timetable/list/filter"
        self.activty = "timetable-api/class/timetable/act-timetable"
        self.classstring = "111111111111"  # 代表上课时间
        self.con = sqlite3.connect("uni_timetable.db")
        print("created db")
        self.cur = self.con.cursor()
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS courses(id TEXT PRIMARY KEY NOT NULL,name TEXT,age INT)")
        self.database_name = "courses"

        self.course_filter_params = {
            'courseDepartmentId': None,
            'roomName': None,
            'teachingWeekFormat': None,
            'weekDayFormat': '4',
            'startPeriod': None,
            'endPeriod': None,
            'courseCategory': None,
            'periodFormat': None,
            'roomId': None,
            'roomBuildingId': None,
            'exprProjectId': None,
            'pageSize': '10',
            'currentPage': '1'
        }
        self.courseCateList = ["所有课程", "集中实践",
                               '分散实践', '普通课程', '通识教育课程', '非限制选秀课程']

    def insert_data(self, course_name: str = None, week: int = None, week_day: int = None, p_start: int = None, p_end: int = None, campuse_id: str = None, building_id: str = None, room_id: int = None):
        print('INSERT INTO {database_name} VALUES ("{course_name}", {week}, {weekday}, {p_start}, {p_end}, "{campuse_id}", "{building_id}", {room_id}, NULL)'.format(
            database_name=self.database_name, course_name=course_name, week=week, weekday=week_day, p_start=p_start, p_end=p_end, campuse_id=campuse_id, building_id=building_id, room_id=room_id))
        self.con.execute('INSERT INTO {database_name} VALUES ("{course_name}", {week}, {weekday}, {p_start}, {p_end}, "{campuse_id}", "{building_id}", {room_id}, NULL)'.format(
            database_name=self.database_name, course_name=course_name, week=week, weekday=week_day, p_start=p_start, p_end=p_end, campuse_id=campuse_id, building_id=building_id, room_id=room_id))

    def insert_data_v2(self, course_name: str = None, week: int = None, week_day: int = None, period: int = None, campuse_id: str = None, building_id: str = None, room_id: int = None):
        print('INSERT INTO {database_name} VALUES ("{course_name}", {week}, {weekday}, "{campuse_id}", "{building_id}", {room_id}, {period}, NULL)'.format(
            database_name=self.database_name, course_name=course_name, week=week, weekday=week_day, period=period, campuse_id=campuse_id, building_id=building_id, room_id=room_id))
        try:
            self.con.execute('INSERT INTO {database_name} VALUES ("{course_name}", {week}, {weekday}, "{campuse_id}", "{building_id}", {room_id}, {period}, NULL)'.format(
                database_name=self.database_name, course_name=course_name, week=week, weekday=week_day, period=period, campuse_id=campuse_id, building_id=building_id, room_id=room_id))
        except Exception as e:
            print(e)

    def db_close(self):
        self.con.commit()
        self.con.close()

    def select_data(self, week: int = None, weekday: int = None, roomid: int = None, buildtype: str = "1") -> list:
        if(roomid is not None):
            self.cur.execute(
                'SELECT * FROM {} WHERE week={} AND weekday={} AND room_id={} AND building_id="{}"'.format(self.database_name, week, weekday, roomid, buildtype))
        else:
            self.cur.execute(
                'SELECT * FROM {} WHERE week={} AND weekday={} AND building_id="{}"'.format(self.database_name, week, weekday, buildtype))
        return self.cur.fetchall()

    def init_finder(self):
        response = self.session.get(self.url_base+self.max_week)
        response = json.loads(response.content.decode("utf8"))
        self.max_week = response["data"]

        response = self.session.get(self.url_base+self.buildings)
        building_list = json.loads(response.content.decode("utf8"))
        self.buildings = {}
        for building in building_list:
            self.buildings.update({building['name']: building['id']})
        print(self.buildings)
        print("\n\n")

    def get_courses_info(self, course_dept_id=None, weekday=None, start_period=None, end_period=None, room_name=None, course_cate=None, period_format=None, room_id=None, room_building_id=None, expr=None, week=None, page_size=10, current_page=1) -> tuple:
        self.course_filter_params["courseDepartmentId"] = course_dept_id
        self.course_filter_params["weekDayFormat"] = weekday
        self.course_filter_params["startPeriod"] = start_period
        self.course_filter_params["endPeriod"] = end_period
        self.course_filter_params["courseCategory"] = course_cate
        self.course_filter_params["periodFormat"] = period_format
        self.course_filter_params["roomId"] = room_id
        self.course_filter_params["roomBuildingId"] = room_building_id
        self.course_filter_params["exprProjectId"] = expr
        self.course_filter_params["teachingWeekFormat"] = week
        self.course_filter_params["roomName"] = room_name

        self.course_filter_params["pageSize"] = page_size
        self.course_filter_params["currentPage"] = current_page
        response = self.session.get(
            url=self.url_coursesfilter, params=self.course_filter_params)
        response = json.loads(response.content.decode("utf8"))
        return (response["data"]["content"], response["data"]["totalPages"])

    #
    def get_activity_info(self, week: str = None, week_day: int = None, campuse: str = None) -> list:
        activity_list = []
        header = {
            'Host': 'my.cqu.edu.cn',
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/plain, */*'
        }
        data = {
            "teachingWeek": week,
            "weekDay": week_day,
            "campusId": campuse
        }
        response = self.session.post(
            url=self.url_base+self.activty, json=data, headers=header)
        response = json.loads(response.content.decode("utf8"))
        return response["data"]

    def get_exam_info(self, room_building_id, page_size, current_page):
        data = {
            "campusId": "4",
            "buildingId": room_building_id,
            "startWeek": None,
            "startWeekDay": None,
            "startTime": None,
            "endWeek": None,
            "endWeekDay": None,
            "endTime": None,
            "pageSize": page_size,
            "currentPage": current_page
        }
        header = {
            'Host': 'my.cqu.edu.cn',
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/plain, */*'
        }
        response = self.session.post(
            url=self.url_base+self.exam, json=data, headers=header)
        response = json.loads(response.content.decode("utf8"))
        return (response["data"]["content"], response["data"]["totalPages"])
    # return room list

    def get_NULL_room_by_day(self, week: int = None, weekday=None) -> list:
        nullclassroom = []
        for roomName in list(range(1101, 1151))+list(range(1201, 1251))+list(range(1301, 1351))+list(range(1401, 1451)):
            activity_list = tt.get_activity_info(
                week=str(week), week_day=weekday, campuse="4")
            courseList = (tt.get_courses_info(
                course_cate=tt.courseCateList[0], room_building_id=tt.buildings['一教学楼-D区'], room_name=roomName, week=week, weekday=weekday, page_size=10))
            classbin = 4095  # 12位1
            if(not len(courseList) == 0):
                for course in courseList:
                    period = tt.get_start_and_end_class(course)
                    _period = tt.classstring[:period[0]-1] + \
                        "00"+tt.classstring[period[1]:]
                    # print("字符串：{}".format(_period))
                    classbin = classbin & int(_period, 2)

                print("教室：{}空闲时段：{:012b}".format(roomName, classbin))
            else:
                for activity in activity_list:
                    try:
                        if(int(activity["roomName"][1:]) == roomName):
                            print("教室不上课有活动")
                            period = tt.get_start_and_end_class(activity)
                            period = tt.get_start_and_end_class(course)
                            _period = tt.classstring[:period[0]-1] + \
                                "00"+tt.classstring[period[1]:]
                            # print("字符串：{}".format(_period))
                            classbin = classbin & int(_period, 2)
                    except Exception as e:
                        # print(e)
                        pass
                print("教室：{}空闲".format(roomName))
                nullclassroom.append(roomName)
        return nullclassroom

    def get_NULL_room_by_day_db(self, week: int = None, weekday=None, room_id: int = None, buildtype: str = "1") -> list:
        nullclassroom = []
        for roomName in list(range(101, 151))+list(range(201, 251))+list(range(301, 351))+list(range(401, 451)):
            classbin = 0  # 13位1
            courseList = self.select_data(
                week=week, weekday=weekday, roomid=roomName, buildtype=buildtype)
            if(not len(courseList) == 0):
                for course in courseList:
                    # _period = self.classstring[:course[3]
                    #                            ] + "00"+self.classstring[course[4]:]
                    # # print("字符串：{}".format(_period))
                    # if(course[5] == 342):
                    #     time.sleep(1)
                    classbin = classbin | course[6]
                print("教室：{} 空闲时段：{:0>13b}".format(roomName, classbin))
            else:
                print("教室：{} 空闲".format(roomName))
                nullclassroom.append(roomName+1000)
        return nullclassroom

    def update_dbdata(self):
        for week in range(1, 21):
            for weekday in range(1, 7):
                print("添加week {} weekday {}的数据".format(week, weekday))
                page = 1
                while(1):
                    print("正在写入第{}页".format(page))
                    course_list = self.get_courses_info(
                        weekday=weekday, week=week, room_building_id=self.buildings["综合楼-D区"], current_page=page, page_size=500)
                    for course in course_list[0]:
                        _p = self.get_start_and_end_class(course)
                        try:
                            self.insert_data(course_name=course["courseName"], week=week, week_day=weekday, p_start=_p[0],
                                             p_end=_p[1], campuse_id="D", building_id="Z", room_id=int(course["roomName"][-3:]))
                        except Exception as e:
                            print(e)
                    self.con.commit()
                    if(page == course_list[1] or course_list[1] == 0):
                        break
                    else:
                        page = page+1
        self.db_close()

    def update_dbdata_courrse(self):
        page = 1
        while(1):
            course_list = self.get_courses_info(
                room_building_id=self.buildings["综合楼-D区"], page_size=1000, current_page=page)
            repatten_room = "(?P<campus>\w+)(?P<buildingtype>\w+)(?P<roomid>\d{3})"
            print(len(course_list[0]))
            for course in course_list[0]:
                room_name = course["roomName"]
                if(len(room_name) > 5 or course["period"] is None):
                    continue
                result = re.findall(repatten_room, room_name)[0]
                campus = result[0]
                buildtype = result[1]
                roomid = int(result[2])
                period = int("{:0<13}".format(course["period"]), 2)
                week = course["teachingWeek"]
                week_num = -1

                while(1):
                    week_num = week.find("1", week_num+1)
                    if(week_num != -1):
                        # print(week_num)
                        self.insert_data_v2(course["courseName"], week=week_num+1, week_day=course["weekDay"],
                                            period=period, campuse_id=campus, room_id=roomid, building_id=buildtype)
                    else:
                        break
            if(page == course_list[1] or course_list[1] == 0):
                break
            else:
                page = page+1
                print("读取 {} 页".format(page))
                time.sleep(1)
                self.con.commit()

        self.db_close()
        print("写入数据库成功")

    def update_dbdata_courrse(self):
        page = 1
        while(1):
            course_list = self.get_courses_info(
                room_building_id=self.buildings["综合楼-D区"], page_size=1000, current_page=page)
            repatten_room = "(?P<campus>\w+)(?P<buildingtype>\w+)(?P<roomid>\d{3})"
            print(len(course_list[0]))
            for course in course_list[0]:
                room_name = course["roomName"]
                if(len(room_name) > 5 or course["period"] is None):
                    continue
                result = re.findall(repatten_room, room_name)[0]
                campus = result[0]
                buildtype = result[1]
                roomid = int(result[2])
                period = int("{:0<13}".format(course["period"]), 2)
                week = course["teachingWeek"]
                week_num = -1

                while(1):
                    week_num = week.find("1", week_num+1)
                    if(week_num != -1):
                        # print(week_num)
                        self.insert_data_v2(course["courseName"], week=week_num+1, week_day=course["weekDay"],
                                            period=period, campuse_id=campus, room_id=roomid, building_id=buildtype)
                    else:
                        break
            if(page == course_list[1] or course_list[1] == 0):
                break
            else:
                page = page+1
                print("读取 {} 页".format(page))
                time.sleep(1)
                self.con.commit()

        self.db_close()
        print("写入数据库成功")

    def update_dbdata_exam(self):
        page = 1
        while(1):
            exam_list = self.get_exam_info(
                room_building_id=self.buildings["综合楼-D区"], page_size=100, current_page=page)
            repatten_room = "(?P<campus>\w+)(?P<buildingtype>\w+)(?P<roomid>\d{3})"
            print(len(exam_list[0]))
            for course in exam_list[0]:
                room_name = course["roomName"]
                if(len(room_name) > 5):
                    continue
                result = re.findall(repatten_room, room_name)[0]
                campus = result[0]
                buildtype = result[1]
                roomid = int(result[2])
                start_time = int(course["startTime"][:2])
                end_time = int(course["endTime"][:2])
                print((start_time, end_time))
                week = course["week"]

                # 处理开始时间和结束时间
                duration = end_time-start_time+1
                period = ""
                if(start_time >= 19):
                    period = "0000000001111"
                elif(start_time < 12):
                    period = "1111000000000"
                else:
                    period = "0000111110000"
                period = int(period, 2)
                ##################

                self.insert_data_v2(course["courseName"], week=week, week_day=course["weekDay"],
                                    period=period, campuse_id=campus, room_id=roomid, building_id=buildtype)
            if(page == exam_list[1] or exam_list[1] == 0):
                break
            else:
                page = page+1
                print("读取 {} 页".format(page))
                time.sleep(1)
                self.con.commit()

        self.db_close()
        print("写入数据库成功")

    def update_dbdata_activity(self):
        repatten_room = "(?P<campus>\w+)(?P<buildingtype>\w+)(?P<roomid>\d{3})"
        act_list = self.get_activity_info(campuse="4")
        for act in act_list:
            room_name = act["roomName"]
            if(len(room_name) > 5):
                continue
            result = re.findall(repatten_room, room_name)[0]
            campus = result[0]
            buildtype = result[1]
            roomid = int(result[2])
            period = int("{:0<13}".format(act["period"]), 2)
            week = act["teachingWeek"]
            week_num = -1
            while(1):
                week_num = week.find("1", week_num+1)
                if(week_num is not -1):
                    # print(week_num)
                    self.insert_data_v2(act["tempActType"], week=week_num+1, week_day=act["weekDay"],
                                        period=period, campuse_id=campus, room_id=roomid, building_id=buildtype)
                else:
                    break
        self.db_close()
        print("写入数据库成功")

    def get_start_and_end_class(self, course):
        repatten = '(?P<start>\d+)-(?P<end>\d+)'
        return(int(re.findall(repatten, course["periodFormat"])[0][0]), int(re.findall(repatten, course["periodFormat"])[0][1]))


if __name__ == "__main__":
    tt = UniversityTimetableGeter()
    tt.init_finder()
    tt.get_NULL_room_by_day_db(17, 7)
