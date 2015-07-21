Just Notes for me as I develop

user = varrogancia (first part before the @gmail.com)
userID = varrogancia@gmail.com
key = ndb.Key(Profile, Varrogancia@gmail.com)

Endpoints is a whole class of library functions one of which seems to have some oauth capabilities via google when you sign in. It comes preloaded when you sign in with user information.

What does the Database look like:
groupVoteRanks - vote tallying algorithm
friendlist (only indicator is if they vote...but need to account for preferences of them not caring of the vote)
Not Care - [0,0,0]...I think just move it to the right place

partytotal
totalcounter

FriendList is actually a dictionary:
friendName: {dictionary w/ more informaion}

{dictionary} = {
	profileID: 12312312
	voterank: --->initialized to 0....so that's how you know they didn't vote yet.
	firstchoice:
	confirmation:
}

Place it in a $scope variable

Notes to using $location service to route page correctly:
Place $location in the function below:
app.factory('oauth2Provider', function ($modal,$location) {
    var oauth2Provider = {
        CLIENT_ID: '1056255259427-h8spnd6q8ovv8cn6fdmqk6kc259mb6k6.apps.googleusercontent.com',
        SCOPES: 'email profile',
        signedIn: false
    }
Then in the function below. Place the $location.path function
    /**
     * Calls the OAuth2 authentication method.
     */
    oauth2Provider.signIn = function (callback) {
        gapi.auth.signIn({
            'clientid': oauth2Provider.CLIENT_ID,
            'cookiepolicy': 'single_host_origin',
            'accesstype': 'online',
            'approveprompt': 'auto',
            'scope': oauth2Provider.SCOPES,
            'callback': callback
        });
        $location.path('/myDashboard').replace;
    };