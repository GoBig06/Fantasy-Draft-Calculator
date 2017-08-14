import os
import sys
from bs4 import BeautifulSoup
import json

class MockDraft2Json:
    def __init__(self):
        self.start = 0
        self.stop = 0
        self.currentMockDraft = 0
        self.htmlDir = os.getcwd() + '\html_files'
        self.draftDict = {}
        self.draftType = None
        self.numTeams = None
        print self.htmlDir
        if not os.path.exists(self.htmlDir):
            os.makedirs(self.htmlDir)

    def startDownload(self):
        print 'Starting Downloads'
        self.get_mock_draft_results()
        # Parse all the draft data and make json dictionaries for all draft types
        self.parse_mock_draft_result()

    def get_mock_draft_results(self):
        for i in range(self.start,self.stop,1):
            os.system('wget64 https://fantasyfootballcalculator.com/draft/%i -P "%s"' % (i,self.htmlDir))

    def readMockDraftHtml(self):
        with open (self.currentMockDraft, "r") as myfile:
            self.htmlFile = myfile
            self.soup = BeautifulSoup(self.htmlFile)

    def findDraftType(self):
        with open (self.currentMockDraft, "r") as myfile:
            for line in myfile:
                if 'PPR Mock Draft' in line:
                    self.draftType = 'FULL_PPR'
                    break
                if 'Dynasty Mock Draft' in line:
                    self.draftType = 'DYNASTY'
                    break
                if '2-QB Mock Draft' in line:
                    self.draftType = '2_QB'
                    break
                if 'Standard Mock Draft' in line:
                    self.draftType = 'STANDARD'
                    break
                if 'Dynasty Rookie Mock Draft' in line:
                    self.draftType = 'Dynasty_Rookie'
                    break

    def findNumberOfTeams(self,count):
        if count == 15*8:
            self.numTeams = 8
        elif count == 15*10:
            self.numTeams = 10
        elif count == 15*12:
            self.numTeams = 12
        elif count == 15*14:
            self.numTeams = 14
        elif count == 15*16:
            self.numTeams = 16
        else:
            self.numTeams = None

    def parse_mock_draft_result(self):
        start = 'title="'
        end   = '">'
        for draftNumber in range(self.start, self.stop, 1):
            self.currentMockDraft = self.htmlDir +'\\' + str(draftNumber)
            self.findDraftType()
            self.readMockDraftHtml()
            try:
                table = self.soup.find_all('table')[0]
                #First row is draft order
                row_count = 0
                column_count = 0
                draftPick = 1
                for row in table.find_all('tr'):
                    row_count = row_count + 1
                    columns = row.find_all('td')
                    for column in columns:
                        column = str(column)
                        if column.find(start) > 0:
                            player_name = column[column.find(start)+len(start) : column.find(end,column.find(start))]
                            #Create Dictonary
                            self.draftDict[player_name] = draftPick
                            draftPick = draftPick + 1
                            column_count = column_count +1
                if row_count == 19:
                    self.findNumberOfTeams(column_count)
                    self.storeDictAsJson(draftNumber)
                else:
                    print 'Draft %s did not complete.  Values will be ignored.' % draftNumber
            except:
                print 'Error opening table for draft %s skipping' % draftNumber

    def storeDictAsJson(self,draftNumber):
        if self.numTeams is None:
            print 'Draft %s was not completed. Skipping.' % draftNumber
        else:
            tempDraftDict = {}
            tempDraftDict[draftNumber] = self.draftDict
            jsonFile = '%s_%s_TEAM_DRAFT_DATA.json'  % (str(self.draftType), str(self.numTeams))

            if not os.path.isfile(jsonFile):
                with open(jsonFile, "w") as json_file:
                        json_file.write("{}\n".format(json.dumps(tempDraftDict)))
            else:
                with open(jsonFile, "a") as json_file:
                    json_file.write("{}\n".format(json.dumps(tempDraftDict)))
