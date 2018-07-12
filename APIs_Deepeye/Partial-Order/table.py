import datetime
from features import Features,Type
from view import View,Chart
month=['','Jan','Feb','Mar','Apr','May','June','July','Aug','Sept','Oct','Nov','Dec']


class Table(object):
    def __init__(self,instance,transformed,describe1,describe2):
        self.D=[]
        self.instance=instance
        self.transformed=transformed
        self.describe1,self.describe2=describe1,describe2
        self.describe=self.describe1+', '+self.describe2 if self.describe2 else self.describe1
        self.column_num=self.tuple_num=self.view_num=0
        self.names=[]
        self.types=[]
        self.origins=[]
        self.features=[]
        self.views=[]
        self.classify_id = -1
        self.classify_num = 1
        self.classes=[]

    def getIntervalBins(self,f):
        bins = []
        minTime = f.minmin
        maxTime = f.max
        if type(minTime)!=type(datetime.date(1995,10,11)) and minTime.year==maxTime.year and minTime.month==maxTime.month and minTime.day==maxTime.day:
            minHour = minTime.hour
            minMinute = minTime.minute
            minSecond = minTime.second
            maxHour = maxTime.hour
            maxMinute = maxTime.minute
            maxSecond = maxTime.second
            if minHour == maxHour:
                if minMinute == maxMinute:
                    #interval = 'SECOND'
                    for i in range(minSecond, maxSecond + 1):
                        t = datetime.datetime(minTime.year, minTime.month, minTime.day, minHour, minMinute, i)
                        bins.append([str(i) + 's', t, t, 0])
                else:
                    #interval = 'MINUTE'
                    for i in range(minMinute, maxMinute + 1):
                        t1 = datetime.datetime(minTime.year, minTime.month, minTime.day, minHour, i, 0)
                        t2 = datetime.datetime(minTime.year, minTime.month, minTime.day, minHour, i, 59)
                        bins.append([str(i) + 'm', t1, t2, 0])
            else:
                #interval = 'HOUR'
                for i in range(minHour, maxHour + 1):
                    t1 = datetime.datetime(minTime.year, minTime.month, minTime.day, i, 0, 0)
                    t2 = datetime.datetime(minTime.year, minTime.month, minTime.day, i, 59, 59)
                    bins.append([str(i) + ' oclock', t1, t2, 0])
        else:
            minYear = minTime.year
            minMonth = minTime.month
            minDay = minTime.day
            maxYear = maxTime.year
            maxMonth = maxTime.month
            maxDay = maxTime.day
            if minYear == maxYear:
                if minMonth == maxMonth:
                    #interval = 'DAY'
                    for i in range(minDay, maxDay + 1):
                        bins.append([str(i)+'th',datetime.date(minYear, minMonth, i),datetime.date(minYear, minMonth, i), 0])
                else:
                    #interval = 'MONTH'
                    for i in range(minMonth, maxMonth):
                        bins.append([month[i],datetime.date(minYear, i, 1),datetime.date(minYear, i + 1, 1)-datetime.timedelta(1), 0])
                    if maxMonth == 12:
                        bins.append(['Dec', datetime.date(minYear, 12, 1), datetime.date(minYear, 12, 31), 0])
                    else:
                        bins.append([month[maxMonth],datetime.date(minYear, maxMonth, 1),datetime.date(minYear, maxMonth + 1, 1) - datetime.timedelta(1), 0])
            else:
                #interval = 'YEAR'
                yearNum = maxYear - minYear + 1
                if yearNum > 20:
                    if yearNum % 10 > yearNum / 10:
                        yearDelta = yearNum / 10 + 1
                    else:
                        yearDelta = yearNum / 10
                    beginYear = minYear
                    while True:
                        endYear = beginYear + yearDelta - 1
                        if endYear > maxYear:
                            endYear = maxYear
                        if beginYear == endYear:
                            bins.append([str(beginYear), datetime.date(beginYear, 1, 1), datetime.date(endYear, 12, 31),0])
                        else:
                            bins.append([str(beginYear) + '~' + str(endYear), datetime.date(beginYear, 1, 1),datetime.date(endYear, 12, 31), 0])
                        if endYear == maxYear:
                            break
                        beginYear += yearDelta
                else:
                    for i in range(minYear, maxYear + 1):
                        bins.append([str(i), datetime.date(i, 1, 1), datetime.date(i, 12, 31), 0])
        f.interval_bins=bins
        f.bin_num=len(bins)
        f.interval='TIME'


    def generateViews(self):
        T=map(list,zip(*self.D))
        if self.transformed:
            for column_id in range(self.column_num):
                f = Features(self.names[column_id],self.types[column_id],self.origins[column_id])
                #calculate min,max for numerical
                if f.type==Type.numerical:
                    if self.classify_num==1 or not self.describe2:#not categorized or categorized scatter
                        f.min,f.max=min(T[column_id]),max(T[column_id])
                        f.minmin=f.min
                        if f.min==f.max:
                            self.types[column_id]=f.type=Type.none
                            self.features.append(f)
                            continue
                    else:
                        delta=self.tuple_num/self.classify_num
                        f.min=[min(T[column_id][class_id*delta:(class_id+1)*delta]) for class_id in range(self.classify_num)]
                        f.minmin=min(f.min)
                        f.max=[max(T[column_id][class_id*delta:(class_id+1)*delta]) for class_id in range(self.classify_num)]
                        if sum([f.max[class_id]-f.min[class_id] for class_id in range(self.classify_num)])==0:
                            self.types[column_id]=f.type=Type.none
                            self.features.append(f)
                            continue
                        if min(f.min)==max(f.min) and min(f.max)==max(f.max):
                            if sum([0 if T[column_id][class_id*delta:(class_id+1)*delta]==T[column_id][(class_id+1)*delta:(class_id+2)*delta] else 1 for class_id in range(self.classify_num-1)])==0:
                                self.types[column_id]=f.type=Type.none
                                self.features.append(f)
                                continue



                #calculate distinct,ratio for categorical,temporal
                if f.type==Type.categorical or f.type==Type.temporal:
                    f.distinct=self.tuple_num
                    f.ratio=1.0

                self.features.append(f)
        else:
            for column_id in range(self.column_num):
                f = Features(self.names[column_id],self.types[column_id],self.origins[column_id])

                #calculate min,max for numerical,temporal
                if f.type==Type.numerical or f.type==Type.temporal:
                    f.min,f.max=min(T[column_id]),max(T[column_id])
                    f.minmin=f.min
                    if f.min==f.max:
                        self.types[column_id]=f.type=Type.none
                        self.features.append(f)
                        continue

                d={}
                #calculate distinct,ratio for categorical,temporal
                if f.type == Type.categorical or f.type == Type.temporal:
                    for i in range(self.tuple_num):
                        if self.D[i][column_id] in d:
                            d[self.D[i][column_id]]+=1
                        else:
                            d[self.D[i][column_id]]=1
                    f.distinct = len(d)
                    if f.distinct==1:
                        self.types[column_id]=f.type=Type.none
                        self.features.append(f)
                        continue
                    f.ratio = 1.0 * f.distinct / self.tuple_num
                    f.distinct_values=[(k,d[k]) for k in sorted(d)]
                    if f.type==Type.temporal:
                        self.getIntervalBins(f)

                self.features.append(f)


        #generate 2D views
        if self.describe2=='' and self.classify_id==-1:
            for i in range(self.column_num):
                for j in range(self.column_num):
                    if i==j:
                        continue

                    fi=self.features[i]
                    fj=self.features[j]
                    if fi.type==Type.categorical and fj.type==Type.numerical and fi.ratio==1.0:
                        charts=[]
                        if fj.minmin>0 and fi.distinct<=5 and not (len(fj.name)>=6 and fj.name[0:4]=='AVG(' and fj.name[-1]==')'):
                            charts.append(Chart.pie)
                        if fi.distinct<=20:
                            charts.append(Chart.bar)
                    elif fi.type==Type.temporal and fj.type==Type.numerical and fi.ratio==1.0:
                        charts=[]
                        if fi.distinct<7:
                            charts.append(Chart.bar)
                        else:
                            charts.append(Chart.line)
                    elif (not self.transformed) and fi.type==Type.numerical and fj.type==Type.numerical and i<j:
                        charts=[Chart.scatter]
                    else:
                        charts=[]

                    for chart in charts:
                        v=View(self,i,j,-1,1,[T[i]],[T[j]],chart)
                        self.views.append(v)
                        self.view_num+=1
        #generate 3D views
        elif self.describe2:
            for i in range(self.column_num):
                for j in range(self.column_num):
                    fi=self.features[i]
                    fj=self.features[j]
                    if fi.type==Type.categorical and fj.type==Type.numerical and fj.minmin>0:
                        charts=[Chart.bar]
                    elif fi.type==Type.temporal and fj.type==Type.numerical:
                        if self.tuple_num/self.classify_num<7:
                            charts=[Chart.bar]
                        else:
                            charts=[Chart.line]
                    else:
                        charts=[]
                    for chart in charts:
                        delta=self.tuple_num/self.classify_num
                        series_data = [T[j][series * delta:(series + 1) * delta] for series in range(self.classify_num)]
                        v = View(self, i, j, self.classify_id, self.classify_num, [T[i][0:delta]], series_data, chart)
                        self.views.append(v)
                        self.view_num += 1
        else:
            for i in range(self.column_num):
                for j in range(self.column_num):
                    if i>=j or self.types[i]!=Type.numerical or self.types[j]!=Type.numerical:
                        continue
                    X=[]
                    Y=[]
                    id=0
                    for k in range(self.classify_num):
                        x=T[i][id:id+self.classes[k][1]]
                        y=T[j][id:id+self.classes[k][1]]
                        id+=self.classes[k][1]
                        X.append(x)
                        Y.append(y)
                    v=View(self,i,j,self.classify_id,self.classify_num,X,Y,Chart.scatter)
                    self.views.append(v)
                    self.view_num+=1

        self.instance.view_num+=self.view_num

    def dealWithGroup(self,column_id,begin,end,get_head,get_data):
        new_table = Table(self.instance, True, 'GROUP BY ' + self.names[column_id],'')
        if get_head:
            new_table.column_num = 1
            new_table.tuple_num = self.features[column_id].distinct
            new_table.names.append('CNT(' + self.names[column_id] + ')')
            new_table.types.append(Type.numerical)
            new_table.origins.append(column_id)
            for i in range(self.column_num):
                if self.types[i] == Type.numerical:
                    new_table.column_num += 2
                    new_table.names.extend(['SUM(' + self.names[i] + ')', 'AVG(' + self.names[i] + ')'])
                    if self.features[i].minmin<0:
                        new_table.types.extend([Type.none, Type.numerical])
                    else:
                        new_table.types.extend([Type.numerical,Type.numerical])
                    new_table.origins.extend([i, i])
            new_table.column_num += 1
            new_table.names.append(self.names[column_id])
            new_table.types.append(self.types[column_id])
            new_table.origins.append(column_id)
        if get_data:
            d = {}
            num=1#numerical column number
            for i in range(0, self.features[column_id].distinct):
                d[self.features[column_id].distinct_values[i][0]] = [0]
            for i in range(begin, end):
                d[self.D[i][column_id]][0] += 1
            for i in range(self.column_num):
                if self.types[i]==Type.numerical:
                    num+=2
                    for k in d:
                        d[k].extend([0,0])
            for i in range(begin,end):
                sum_column = 1
                for j in range(self.column_num):
                    if self.types[j] == Type.numerical:
                        d[self.D[i][column_id]][sum_column] += self.D[i][j]
                        sum_column += 2
            for k in d:
                for i in range(1,num,2):
                    if d[k][0]:
                        d[k][i + 1] = 1.0 * d[k][i] / d[k][0]
            for k in d:
                l = d[k]
                l.append(k)
                new_table.D.append(l)
            if self.features[column_id].type==Type.temporal:
                new_table.D.sort(key=lambda l:l[-1])
        return new_table

    def dealWithIntervalBin(self,column_id,begin,end,get_head,get_data):
        bins=self.features[column_id].interval_bins
        bin_num=self.features[column_id].bin_num
        interval=self.features[column_id].interval
        new_table = Table(self.instance, True, 'BIN ' + self.names[column_id] + ' BY ' + interval,'')
        if get_head:
            new_table.tuple_num = bin_num
            for i in range(self.column_num):
                if self.types[i] == Type.numerical:
                    new_table.column_num += 2
                    new_table.names.extend(['SUM(' + self.names[i] + ')', 'AVG(' + self.names[i] + ')'])
                    if self.features[i].minmin<0:
                        new_table.types.extend([Type.none,Type.numerical])
                    else:
                        new_table.types.extend([Type.numerical, Type.numerical])
                    new_table.origins.extend([i, i])
            new_table.column_num += 2
            new_table.names.extend(['CNT(' + self.names[column_id] + ')', self.names[column_id]])
            new_table.types.extend([Type.numerical, Type.temporal])
            new_table.origins.extend([column_id, column_id])
        if get_data:
            num=0
            new_table.D = [[] for i in range(bin_num)]
            for i in range(self.column_num):
                if self.types[i]==Type.numerical:
                    num+=2
                    for j in range(bin_num):
                        new_table.D[j].extend([0,0])
            for i in range(begin,end):
                date = self.D[i][column_id]
                if type(date) != type(bins[0][1]):
                    date = datetime.date(date.year, date.month, date.day)
                for j in range(bin_num):
                    if bins[j][1] <= date <= bins[j][2]:
                        bins[j][3] += 1
                        sum_column = 0
                        for k in range(self.column_num):
                            if self.types[k] == Type.numerical:
                                new_table.D[j][sum_column] += self.D[i][k]
                                sum_column += 2
                        break
            for i in range(bin_num):
                for j in range(0, num, 2):
                    if bins[i][3]:
                        new_table.D[i][j + 1] = 1.0*new_table.D[i][j] / bins[i][3]
                new_table.D[i].extend([bins[i][3], bins[i][0]])
        return new_table

    def dealWithHourBin(self,column_id,begin,end,get_head,get_data):
        new_table = Table(self.instance, True, 'BIN ' + self.names[column_id] + ' BY HOUR','')
        if get_head:
            new_table.column_num = 2
            new_table.tuple_num = 24
            new_table.names.extend([self.names[column_id] + ' oclock','CNT(' + self.names[column_id] + ')'])
            new_table.types.extend([Type.categorical,Type.numerical])
            new_table.origins.extend([column_id, column_id])
            for i in range(self.column_num):
                if self.types[i] == Type.numerical:
                    new_table.column_num += 2
                    new_table.names.extend(['SUM(' + self.names[i] + ')', 'AVG(' + self.names[i] + ')'])
                    if self.features[i].minmin<0:
                        new_table.types.extend([Type.none,Type.numerical])
                    else:
                        new_table.types.extend([Type.numerical, Type.numerical])
                    new_table.origins.extend([i, i])
        if get_data:
            num=0
            new_table.D = [[str(i), 0] for i in range(24)]
            for i in range(self.column_num):
                if self.types[i]==Type.numerical:
                    num+=2
                    for j in range(24):
                        new_table.D[j].extend([0,0])
            for i in range(begin,end):
                hour = self.D[i][column_id].hour
                new_table.D[hour][1] += 1
                sum_column=2
                for j in range(self.column_num):
                    if self.types[j]==Type.numerical:
                        new_table.D[hour][sum_column]+=self.D[i][j]
                        sum_column+=2
            for i in range(24):
                for j in range(2,num+2,2):
                    if new_table.D[i][1]:
                        new_table.D[i][j+1]=1.0*new_table.D[i][j]/new_table.D[i][1]
        return new_table

    def dealWithWeekBin(self,column_id,begin,end,get_head,get_data):
        weekdays = ['Mon', 'Tue', 'Wed', 'Thur', 'Fri', 'Sat', 'Sun']
        new_table=Table(self.instance,True,'BIN '+self.names[column_id]+' BY WEEKDAY','')
        if get_head:
            new_table.column_num=2
            new_table.tuple_num=7
            new_table.names.extend([self.names[column_id],'CNT(' + self.names[column_id] + ')'])
            new_table.types.extend([Type.categorical,Type.numerical])
            new_table.origins.extend([column_id,column_id])
            for i in range(self.column_num):
                if self.types[i]==Type.numerical:
                    new_table.column_num+=2
                    new_table.names.extend(['SUM(' + self.names[i] + ')', 'AVG(' + self.names[i] + ')'])
                    if self.features[i].minmin<0:
                        new_table.types.extend([Type.none,Type.numerical])
                    else:
                        new_table.types.extend([Type.numerical, Type.numerical])
                    new_table.origins.extend([i, i])
        if get_data:
            num=0
            new_table.D = [[weekdays[i], 0] for i in range(7)]
            for i in range(self.column_num):
                if self.types[i]==Type.numerical:
                    num+=2
                    for j in range(7):
                        new_table.D[j].extend([0,0])
            for i in range(begin,end):
                weekday=self.D[i][column_id].weekday()
                new_table.D[weekday][1] += 1
                sum_column=2
                for j in range(self.column_num):
                    if self.types[j]==Type.numerical:
                        new_table.D[weekday][sum_column]+=self.D[i][j]
                        sum_column+=2
            for i in range(7):
                for j in range(2,num+2,2):
                    if new_table.D[i][1]:
                        new_table.D[i][j+1]=1.0*new_table.D[i][j]/new_table.D[i][1]
        return new_table


    def dealWithPNBin(self,column_id,begin,end,get_head,get_data):
        new_table=Table(self.instance,True,'BIN '+self.names[column_id]+' BY ZERO','')
        if get_head:
            new_table.column_num = new_table.tuple_num = 2
            new_table.names.extend([self.names[column_id], 'CNT(' + self.names[column_id] + ')'])
            new_table.types.extend([Type.categorical, Type.numerical])
            new_table.origins.extend([column_id, column_id])
        if get_data:
            new_table.D = [['>0', 0], ['<=0', 0]]
            for i in range(begin,end):
                if self.D[i][column_id]>0:
                    new_table.D[0][1]+=1
                else:
                    new_table.D[1][1]+=1
        return new_table


    def getClassifyTable(self, classify_id, x_id, f,agg):
        t = f(x_id,0,0,True,False)
        new_table = Table(self.instance, True, 'GROUP BY ' + self.names[classify_id], t.describe1)
        new_table.tuple_num,new_table.column_num = t.tuple_num * self.features[classify_id].distinct,t.column_num
        new_table.names,new_table.types,new_table.origins = t.names[:],t.types[:],t.origins[:]
        new_table.classify_id=classify_id
        new_table.classify_num=self.features[classify_id].distinct
        new_table.classes=self.features[classify_id].distinct_values

        if not agg:
            for k in range(new_table.column_num):
                if new_table.names[k][0:4] == 'SUM(':
                    new_table.names[k] = new_table.names[k][4:-1]
                    new_table.types[k] = Type.numerical
                elif new_table.names[k][0:4] == 'AVG(' or new_table.names[k][0:4] == 'CNT(':
                    new_table.types[k] = Type.none

        begin_id = 0
        for k in range(self.features[classify_id].distinct):
            end_id = begin_id + self.features[classify_id].distinct_values[k][1]
            new_table.D.extend(f(x_id, begin_id, end_id,False,True).D)
            begin_id = end_id
        return new_table

    def dealWithTable(self):
        new_tables=[]

        self.generateViews()

        if self.transformed:
            return new_tables

        for i in range(self.column_num):
            if self.features[i].ratio<1.0 and (self.types[i]==Type.temporal or (self.types[i]==Type.categorical and self.features[i].distinct<=20)):
                new_tables.append(self.dealWithGroup(i, 0, self.tuple_num, True, True))

            if self.types[i]==Type.temporal:
                new_tables.append(self.dealWithIntervalBin(i,0,self.tuple_num,True,True))
                new_tables.append(self.dealWithWeekBin(i,0,self.tuple_num,True,True))
                if type(self.features[i].minmin) != type(datetime.date(1995, 10, 11)):
                    new_tables.append(self.dealWithHourBin(i,0,self.tuple_num,True,True))

            if self.types[i]==Type.numerical and self.features[i].minmin<0:
                new_tables.append(self.dealWithPNBin(i,0,self.tuple_num,True,True))

        for i in range(self.column_num):
            if self.types[i]!=Type.categorical or self.features[i].distinct>6:
                continue
            self.D.sort(key=lambda tuple:tuple[i])
            ######for categorized scatter########
            new_table=Table(self.instance,True,'GROUP BY '+self.names[i],'')
            new_table.tuple_num=self.tuple_num
            new_table.D=[[] for tuple in range(self.tuple_num)]
            new_table.classify_id = i
            new_table.classify_num = self.features[i].distinct
            new_table.classes = self.features[i].distinct_values
            for j in range(self.column_num):
                if self.types[j]==Type.numerical:
                    new_table.names.append(self.names[j])
                    new_table.types.append(Type.numerical)
                    new_table.origins.append(j)
                    new_table.column_num+=1
                    for k in range(self.tuple_num):
                        new_table.D[k].append(self.D[k][j])
            new_tables.append(new_table)
            ######for categorized scatter########
            for j in range(self.column_num):
                if i==j:
                    continue
                if (self.types[j]==Type.categorical and self.features[j].distinct<=20) or self.types[j]==Type.temporal:
                    s = set()
                    for k in range(self.tuple_num):
                        s.add((self.D[k][i], self.D[k][j]))
                    if len(s)>self.features[j].distinct and ((self.types[j]==Type.categorical and self.features[i].distinct<=self.features[j].distinct) or self.types[j]==Type.temporal):
                        if len(s)==self.instance.tuple_num:
                            new_table = self.getClassifyTable(i, j, self.dealWithGroup,False)
                        else:
                            new_table = self.getClassifyTable(i, j, self.dealWithGroup,True)
                        new_tables.append(new_table)

                if self.types[j]==Type.temporal:
                    new_tables.append(self.getClassifyTable(i,j,self.dealWithIntervalBin,True))
                    new_tables.append(self.getClassifyTable(i, j, self.dealWithWeekBin,True))
                    if type(self.features[j].minmin) != type(datetime.date(1995, 10, 11)):
                        new_tables.append(self.getClassifyTable(i, j, self.dealWithHourBin,True))

                if self.types[j]==Type.numerical and self.features[j].minmin<0:
                    new_tables.append(self.getClassifyTable(i,j,self.dealWithPNBin,True))

        return new_tables
