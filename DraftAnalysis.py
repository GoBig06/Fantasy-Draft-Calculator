import os
import sys
import json
import collections

from PyQt4 import QtCore, QtGui

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

class DraftAnalysisEvents(QtCore.QObject):
    def draftAnalysisEventsself(self,msgType,ack):
        self.emit(QtCore.SIGNAL(_fromUtf8("draftAnalysisMessage(PyQt_PyObject)")),(msgType,ack))
        if msgType != None:
            self.emit(QtCore.SIGNAL(_fromUtf8("draftAnalysisMessage_%s(PyQt_PyObject)"%(msgType))),ack)

class DraftAnalysis:
    def __init__(self,numTeams,leagueFormat):
        self.keepGoing = True
        self.numTeams = numTeams
        self.leagueFormat = leagueFormat
        self.draftCorrelationCutOff = 0.85
        self.desiredPlayerDict = collections.defaultdict(dict)
        self.jsonFile = '%s_%s_TEAM_DRAFT_DATA.json'  % (str(self.leagueFormat), str(self.numTeams))
        self.DraftDataDict = {}
        self.currentDraftDict = {}
        self.draftedPlayerList = []
        self.loadJsonToDict()

    def loadJsonToDict(self):
        tempDict = {}
        with open(self.jsonFile, "r") as json_file:
            #self.DraftDataDict = [json.loads(line) for line in json_file]
            for line in json_file:
                 tempDict = json.loads(line)
                 for key in tempDict:
                    self.DraftDataDict[key] = tempDict[key]
                    break

    def mockDraftCorrelation(self,currentDraftDict):
        player_drafted_counter = 0
        self.draftCorrelationArray = []
        #for key in currentDraftDict:
        for draft in self.DraftDataDict:
            for player in currentDraftDict:
                if int(len(currentDraftDict)) > self.DraftDataDict[draft][str(player)]:
                    player_drafted_counter = player_drafted_counter + 1
            numPicks = float(len(currentDraftDict))
            draftCorrelation = player_drafted_counter/numPicks
            if draftCorrelation > self.draftCorrelationCutOff:
                self.draftCorrelationArray.append(draft)
            player_drafted_counter = 0


    def playerOdds(self,player,pick):
        player_undrafted= 0
        for draftNumber in self.draftCorrelationArray:
            if pick < int(self.DraftDataDict[draftNumber][str(player)]):
                player_undrafted = player_undrafted + 1
        try:
            percentAvail = player_undrafted/float(len(self.draftCorrelationArray))
        except:
            percentAvail = 'Calculation Error.  Possible lack of data to complete calculations.'
        return percentAvail


    def run(self):
        while self.keepGoing:
            if self.update is True:
                self.mockDraftCorrelation()
                self.playerOdds()

