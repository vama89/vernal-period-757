#1,2,3 refer to options 1,2,3 respectively
#as for the results [1stplace, 2nd, 3rd] the indexes for the list refer the options place
#so index 0 is first, index 1, is second etc.

#New Way to display this information. Order is important:
#[option1, option2, option3]
#least tallyed Vote should be the one with the largest bar graph so just substract by 100 for now.
def inViteVote(groupRankVotes):
    option1Count=0
    option2Count=0
    option3Count=0

    for votes in groupRankVotes:
        option1Count=option1Count+votes[0]
        option2Count=option2Count+votes[1]
        option3Count=option3Count+votes[2]

    results = [option1Count, option2Count, option3Count]
    finalResults=[]
    adjusterCount = max(results)+1
    #The least counted vote is the one most in demand via first preference.
    #this flips the results to make the least number, the "most wanted" in our decimal system
    for count in results:
        adjusted = adjusterCount-count
        finalResults.append(adjusted)

    """
    result = {option1Count:1, option2Count:2, option3Count:3}
    rankings = result.keys()

    finalTally=[]
    for num in rankings:
        finalTally.append(result[num])
    """

    #return finalTally
    return finalResults