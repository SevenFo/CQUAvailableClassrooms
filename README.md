# CQUAvailableClassrooms
查询重庆大学教学楼的空教室

+ 由于微信的小程序空教室查询的功能还未更新，自己潦草地写了个爬虫
+ 从新教务网的API接口抓取全校的课程时间表数据，保存到本地数据库之后进行查询
+ 项目还在完善中，当前只有基础查询功能
+ 开发了一个小程序，感兴趣的同学可以加入一起玩儿（email:siky@cqu.edu.cn）！
+ ![avatar](miniappcode.jpg)

#### 使用指南
```python
if __name__ == "__main__":
    tt = UniversityTimetableGeter()#实例化
    tt.init_finder()#初始化楼栋代码
    tt.get_NULL_room_by_day_db(17, 7)#查询第17周星期7，虎溪一教的空教室
```
#### 输出示例
```
...
教室：150 空闲时段：1111111111100
教室：201 空闲时段：1110000001111
教室：202 空闲时段：0000000001111
教室：203 空闲时段：0000000001111
教室：204 空闲时段：0000000001111
教室：205 空闲时段：0000000001111
教室：206 空闲时段：1111111100000
教室：207 空闲时段：1111111100000
教室：208 空闲
教室：209 空闲
教室：210 空闲时段：1111111111111
...

二进制代码从高到低代表第1节到第13节，1表示占用，0表示空闲
```