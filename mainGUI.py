import os
import sys
import time

import DraftAnalysis
import MockDraft

import mainwindow

from PyQt4 import QtCore, QtGui, Qt
from PyQt4.Qt import QWidget

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s
try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

def enableFields(enable=[]):
    '''enable fields in the gui'''
    for field in enable:
        field.setEnabled(True)

def disableFields(disable=[]):
    '''disable fields in the gui'''
    for field in disable:
        field.setEnabled(False)

class FF_MainWindow(mainwindow.Ui_MainWindow):
    def __init__(self):
        self.stopMockDraft = 0
        self.startMockDraft = 0
        self.LeagueType = "STANDARD"
        self.LeagueSize = 8
        self.selectedPlayer = "David Johnson"
        self.playerList = []
        self.playerListSearch = []
        self.playerDraftedDict = {}
        self.rowPosition = 0
        self.columnPosition = 0
        self.draftCount = 1
        self.draftPosition = 1
        self.countDown = False
        self.roundToCalculate = 1
        self.MockDraftObj = MockDraft.MockDraft2Json()
        self.DraftAnalysisEvents = DraftAnalysis.DraftAnalysisEvents()

    def setupUi2(self,MainWindow):
        self.MainWindow = MainWindow
        #Get Draft Data
        QtCore.QObject.connect(self.lineEditStartMockDraft, QtCore.SIGNAL(_fromUtf8("textEdited(QString)")), self.lineEditStartMockDraftChanged)
        QtCore.QObject.connect(self.lineEditMockDraftEnd, QtCore.SIGNAL(_fromUtf8("textEdited(QString)")), self.lineEditStopMockDraftChanged)
        QtCore.QObject.connect(self.pushButtonDownloadDraftData, QtCore.SIGNAL(_fromUtf8("clicked()")), self.pushButtonDownloadDraftDataChanged)

        #Set League parameters
        QtCore.QObject.connect(self.comboBoxLeagueType, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(QString)")), self.comboBoxLeagueTypeChanged)
        QtCore.QObject.connect(self.comboBoxNumberOfTeams, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(QString)")), self.comboBoxNumberOfTeamsChanged)
        QtCore.QObject.connect(self.comboBoxDraftPick, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(QString)")), self.comboBoxDraftPickChanged)
        #Load Draft Data
        QtCore.QObject.connect(self.pushButtonLoadFantasyData, QtCore.SIGNAL(_fromUtf8("clicked()")), self.LoadDraftData)
        #Player List
        QtCore.QObject.connect(self.listWidgetPlayerList, QtCore.SIGNAL(_fromUtf8("itemSelectionChanged()")), self.listWidgetPlayerListClicked)
        QtCore.QObject.connect(self.lineEditPlayerSearch,  QtCore.SIGNAL(_fromUtf8("returnPressed()")),self.startPlayerSearch)
        QtCore.QObject.connect(self.pushButtonDraftPlayer, QtCore.SIGNAL(_fromUtf8("clicked()")), self.draftSelectedPlayer)
        QtCore.QObject.connect(self.pushButtonUndoDraftedPlayer, QtCore.SIGNAL(_fromUtf8("clicked()")), self.undraftSelectedPlayer)
        #Draft Stats
        QtCore.QObject.connect(self.comboBoxCalculateOddsRound, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(QString)")),self.roundToCalculateOdds)
        QtCore.QObject.connect(self.pushButtonCalculateDraftOdds, QtCore.SIGNAL(_fromUtf8("clicked()")),self.calculateDraft)
        #CallBacks to update text browser

    ########## Get draft data ########
    def lineEditStartMockDraftChanged(self):
        self.MockDraftObj.start = int(self.lineEditStartMockDraft.text())

    def lineEditStopMockDraftChanged(self):
        self.MockDraftObj.stop = int(self.lineEditMockDraftEnd.text())

    def pushButtonDownloadDraftDataChanged(self):
        if (self.MockDraftObj.stop != 0) and (self.MockDraftObj.start != 0):
            if self.MockDraftObj.stop > self.MockDraftObj.start:
                self.MockDraftObj.startDownload()
            else:
                txtStr = "Invalid combination of draft numbers"
                self.textBrowserCalculateOdds.append(txtStr)
        else:
            txtStr = "Invalid combination of draft numbers"
            self.textBrowserCalculateOdds.append(txtStr)

    ######### End draft data ###############
    def comboBoxLeagueTypeChanged(self):
        LeagueType = str(self.comboBoxLeagueType.currentText())
        if LeagueType == 'Standard':
            self.LeagueType = 'STANDARD'
        if LeagueType == 'PPR':
            self.LeagueType = 'FULL_PPR'
        if LeagueType == '2 QB':
            self.LeagueType = '2_QB'
        if LeagueType == 'Dynasty':
            self.LeagueType = 'DYNASTY'
        if LeagueType == 'Dynasty':
            self.LeagueType = 'DYNASTY ROOKIE'

    def comboBoxNumberOfTeamsChanged(self):
        LeagueSize = str(self.comboBoxNumberOfTeams.currentText())
        if LeagueSize == '8 Team':
            self.LeagueSize = 8
            self.upDateDraftPick()
        if LeagueSize == '10 Team':
            self.LeagueSize = 10
            self.upDateDraftPick()
        if LeagueSize == '12 Team':
            self.upDateDraftPick()
            self.LeagueSize = 12
            self.upDateDraftPick()
        if LeagueSize == '14 Team':
            self.LeagueSize = 14
            self.upDateDraftPick()

    def comboBoxDraftPickChanged(self):
        try:
            self.draftPosition = int(str(self.comboBoxDraftPick.currentText()).strip('Pick '))
        except:
            foo = 'do nothing'

    def upDateDraftPick(self):
        self.comboBoxDraftPick.clear()
        for leagueSize in range(8,14,2):
            if leagueSize == self.LeagueSize:
                for pick in range(1,(leagueSize+1),1):
                    var = 'Pick ' + str(pick)
                    self.comboBoxDraftPick.addItem(str(var))

    def LoadDraftData(self):
        disableFields([self.comboBoxLeagueType,self.comboBoxNumberOfTeams,self.comboBoxDraftPick,self.pushButtonLoadFantasyData])
        enableFields([self.pushButtonResetDraftData])
        self.upDateDraftTable()
        self.loadPlayerList()
        self.calculatePicks()
        self.DraftAnalysisObj = DraftAnalysis.DraftAnalysis(self.LeagueSize,self.LeagueType)

    ######## Player Drafting CODE ##################
    def loadPlayerList(self,):

        playListFile = os.getcwd() + '\\Player_List.txt'
        self.listWidgetPlayerList.clear()
        with open(playListFile,'r') as file:
            for line in file:
                self.playerList.append(line.strip())
        self.updatePlayerList(self.playerList)
        enableFields([self.lineEditPlayerSearch,self.pushButtonDraftPlayer,self.lineEditPlayerSearch,self.listWidgetPlayerList])

    def updatePlayerList(self,playerList):
        self.listWidgetPlayerList.clear()
        for player in playerList:
            self.listWidgetPlayerList.addItem(player)

    def startPlayerSearch(self):
        enableFields([self.pushButtonDraftPlayer])
        tempPlayerList = []
        currentText = str(self.lineEditPlayerSearch.text())
        for player in self.playerList:
            if currentText in player:
                self.playerListSearch.append(player)
        self.updatePlayerList(self.playerListSearch)
        self.playerListSearch = []

    def listWidgetPlayerListClicked(self):
        self.lineEditPlayerSearch.setText(_fromUtf8(str(self.listWidgetPlayerList.currentItem().text())))
        self.selectedPlayer = self.lineEditPlayerSearch.text()

    def draftSelectedPlayer(self):
        enableFields([self.pushButtonUndoDraftedPlayer])
        self.setTableWithSelectedPlay()

    def undraftSelectedPlayer(self):
        #TO DO
        foo='bar'
        playerToAddBack= str(self.tableWidgetDraftTable.currentItem().text())
        tempStr = str(self.lineEditPlayerSearch.text())
        if playerToAddBack != '':
            self.playerList.insert(0,playerToAddBack)
        if tempStr != '':
            self.playerList.remove(tempStr)
        self.updatePlayerList(self.playerList)
        self.lineEditPlayerSearch.clear()
        column = self.tableWidgetDraftTable.currentColumn()
        row = self.tableWidgetDraftTable.currentRow()
        self.tableWidgetDraftTable.setItem(row,column,QtGui.QTableWidgetItem(tempStr))

    def removePlayerFromList(self):
        self.playerDraftedDict[self.selectedPlayer] = self.draftCount
        self.playerList.remove(self.selectedPlayer)
        self.updatePlayerList(self.playerList)
        self.lineEditPlayerSearch.clear()


    ######## Player Drafting CODE ##################

    ######## DRAFT TABLE CODE ##################
    def upDateDraftTable(self):
        #Add Rows
        self.tableWidgetDraftTable.setRowCount(15)
        #Add Columns
        self.tableWidgetDraftTable.setColumnCount(self.LeagueSize)


    def setTableWithSelectedPlay(self):
        self.tableWidgetDraftTable.setItem(self.rowPosition, self.columnPosition, QtGui.QTableWidgetItem(self.selectedPlayer))
        self.updateRowAndColumns()
        self.draftCount = self.draftCount + 1
        self.removePlayerFromList()

    def updateRowAndColumns(self):
        #Check to see if we are at a corner
        #If so go to the next round
        if self.draftCount % (self.LeagueSize) == 0:
            self.rowPosition = self.rowPosition + 1
            #reset columns
            #even reset to league size
            #Odd reset to 1
            if self.rowPosition % 2 != 0:
                self.columnPosition = (self.LeagueSize -1)
                self.countDown = True
            else:
                self.columnPosition = 0
                self.countDown = False
        else:
            if self.countDown:
                self.columnPosition = self.columnPosition - 1
            else:
                self.columnPosition = self.columnPosition +1
    ######## DRAFT TABLE CODE ##################

    ######## DRAFT Calculations CODE ##################
    def calculateDraft(self):
        self.DraftAnalysisObj.mockDraftCorrelation(self.playerDraftedDict)
        precentAvailable = self.DraftAnalysisObj.playerOdds(self.selectedPlayer,self.draftPickArray[self.roundToCalculate-1])
        if isinstance(precentAvailable, basestring):
            txtStr = precentAvailable
        else:
            txtStr = str(self.selectedPlayer) + 'is available %4.2f percent of the time' % (precentAvailable*100)
        self.textBrowserCalculateOdds.append(txtStr)

    def roundToCalculateOdds(self):
        round = str(self.comboBoxCalculateOddsRound.currentText())
        self.roundToCalculate = int(round.strip('Round '))

    def calculatePicks(self):
        self.draftPickArray = []
        for round in range(1,16):
            if round % 2 != 0:
                self.draftPickArray.append((round-1)*self.LeagueSize + self.draftPosition )
            else:
                self.draftPickArray.append(round*self.LeagueSize - self.draftPosition + 1)

    ######## DRAFT Calculations CODE ##################
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = FF_MainWindow()
    ui.setupUi(MainWindow)
    ui.setupUi2(MainWindow)
    MainWindow.show()
    try:
        sys.exit(app.exec_())
    except:
        pass
    #Close threads
    # finally:
    #     if ui.:
