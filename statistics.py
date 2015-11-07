__author__ = 'otton'

import subprocess
import json
import sys

from PySide import QtGui

def sqrt(x):
    return x**(1.0/2.0)

class Window(QtGui.QWidget):

    def __init__(self,parent=None):
        super(Window, self).__init__(parent)

        self.initUI()

    def initUI(self):


        okButton = QtGui.QPushButton("GetStats")
        cancelButton = QtGui.QPushButton("Cancel")
        self.textbox = QtGui.QLineEdit()
        #faster for testing stuff
        self.textbox.setText("Your steamid")


        hbox = QtGui.QHBoxLayout()
        self.beginCalendar=QtGui.QCalendarWidget()
        self.endCalendar=QtGui.QCalendarWidget()
        hbox.addWidget(self.beginCalendar)
        hbox.addWidget(self.endCalendar)




        vbox = QtGui.QVBoxLayout()
        hbox2= QtGui.QHBoxLayout()
        hbox2.addWidget(self.textbox)
        hbox2.addWidget(okButton)
        vbox.addWidget(QtGui.QLabel("Steamid:"))
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

        okButton.clicked.connect(self.okButtonClicked)
        self.setGeometry(300, 300, 300, 150)
        self.setWindowTitle('LogsAverager')
        self.show()

    def okButtonClicked(self):
        print(self.textbox.text())
        beginDate=self.beginCalendar.selectedDate().toString("dd/MM/yyyy")
        endDate=self.endCalendar.selectedDate().toString("dd/MM/yyyy")

        toExecute="python searcher.py "+self.textbox.text()+" "+beginDate+" "+endDate
        print(toExecute)
        output_s=subprocess.check_output(toExecute, shell=True)
        output=json.loads(output_s.decode())
        self.wid2=Window2()
        self.wid2.setJson(output)



class Window2(QtGui.QWidget):
    def __init__(self,parent=None):
        super(Window2, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.table= QtGui.QTableWidget(9, 9, self)
        self.columns=[
        "KillsAverage","KillsSD",
        "DeathsAverage","DeathsSD",
        "AssistsAverage","AssistsSD",
        "DPMAverage","DPMSD"
        ,"Sample Size"
        ]
        self.rows=[
        "scout","soldier","pyro",
        "demoman","heavyweapons","engineer",
        "medic","sniper","spy"
        ]
        self.table.setHorizontalHeaderLabels(self.columns)
        self.table.setVerticalHeaderLabels(self.rows)
        vbox = QtGui.QVBoxLayout()
        self.table.setSizePolicy(QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Minimum)
        vbox.addWidget(self.table)
        quitButton=QtGui.QPushButton("Quit")
        quitButton.clicked.connect(self.hide)
        vbox.addWidget(quitButton)

        self.setLayout(vbox)
        self.setGeometry(300, 300, 300, 150)
        self.setWindowTitle('Table')

        self.table.setItem(0,0,QtGui.QTableWidgetItem("test"))
        self.table.itemClicked.connect(self.itemClicked)
        self.show()

    def setJson(self,json):
        for row in range(0,self.table.rowCount()):
            class_stat=json[self.rows[row]]

            kills=class_stat["kills"]
            killsAverage="-"
            killsSD="-"
            kills_n=float(kills["n"])
            if(kills_n>0):
                killsAverage=kills["sum"]/kills_n
                killsSD=(kills["squared_sum"]/kills_n) - killsAverage**2
                killsSD=sqrt(killsSD)
                if(kills_n<15 and kills_n>1):#bessel correction
                    killsSD*=sqrt(kills_n/(kills_n-1))

            deaths=class_stat["deaths"]
            deathsAverage="-"
            deathsSD="-"
            deaths_n=float(deaths["n"])
            if(deaths_n>0):
                deathsAverage=deaths["sum"]/deaths_n
                deathsSD=(deaths["squared_sum"]/deaths_n) - deathsAverage**2
                deathsSD=sqrt(deathsSD)
                if(deaths_n<15 and deaths_n>1):
                    deathsSD*=sqrt(deaths_n/(deaths_n-1))

            assists=class_stat["assists"]
            assistsAverage="-"
            assistsSD="-"
            assists_n=float(assists["n"])
            if(assists_n>0):
                assistsAverage=assists["sum"]/assists_n
                assistsSD=(assists["squared_sum"]/assists_n) - assistsAverage**2
                assistsSD=sqrt(assistsSD)
                if(assists_n<15 and assists_n>1):
                    assistsSD*=sqrt(assists_n/(assists_n-1))

            dpm=class_stat["dpm"]
            dpmAverage="-"
            dpmSD="-"
            dpm_n=float(dpm["n"])
            if(dpm_n>0):
                dpmAverage=dpm["sum"]/dpm_n
                dpmSD=(dpm["squared_sum"]/dpm_n) - dpmAverage**2
                dpmSD=sqrt(dpmSD)
                if(dpm_n<15 and dpm_n>1):
                    dpmSD*=sqrt(dpm_n/(dpm_n-1))

            self.table.setItem(row,0,QtGui.QTableWidgetItem(str(killsAverage)))
            self.table.setItem(row,1,QtGui.QTableWidgetItem(str(killsSD)))
            self.table.setItem(row,2,QtGui.QTableWidgetItem(str(deathsAverage)))
            self.table.setItem(row,3,QtGui.QTableWidgetItem(str(deathsSD)))
            self.table.setItem(row,4,QtGui.QTableWidgetItem(str(assistsAverage)))
            self.table.setItem(row,5,QtGui.QTableWidgetItem(str(assistsSD)))
            self.table.setItem(row,6,QtGui.QTableWidgetItem(str(dpmAverage)))
            self.table.setItem(row,7,QtGui.QTableWidgetItem(str(dpmSD)))
            self.table.setItem(row,8,QtGui.QTableWidgetItem(str(dpm_n)))#all the n's should be equal, I need to deprecate this current json output from searchet.py

    def itemClicked(self,item):
        print("testt")


def main():
    app = QtGui.QApplication(sys.argv)

    wid = Window()
    return app.exec_()

if __name__=="__main__":
    exit(main())
