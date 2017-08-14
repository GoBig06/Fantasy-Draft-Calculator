import os
import sys
import MockDraft
import DraftAnalysis

def main(start,stop):
    #Initiate Obj
    MockDraftObj = MockDraft.MockDraft2Json(start,stop)
    #Download html file
    MockDraftObj.get_mock_draft_results()
    #Parse all the draft data and make json dictionaries for all draft types
    MockDraftObj.parse_mock_draft_result()
    #Anlayze the Data
    DraftAnalysisObj = DraftAnalysis.DraftAnalysis(10,'FULL_PPR')
    DraftAnalysisObj.calculatePlayerOdd()

if __name__ == "__main__":
    main(4202045,4272005)