'use strict';

/**
 * The root conferenceApp module.
 *
 * @type {conferenceApp|*|{}}
 */
var conferenceApp = conferenceApp || {};

/**
 * @ngdoc module
 * @name conferenceControllers
 *
 * @description
 * Angular module for controllers.
 *
 */
conferenceApp.controllers = angular.module('conferenceControllers', ['ui.bootstrap']);

/**
 * @ngdoc controller
 * @name MyProfileCtrl
 *
 * @description
 * A controller used for the My Profile page.
 */
conferenceApp.controllers.controller('MyProfileCtrl',
    function ($scope, $log, oauth2Provider, HTTP_ERRORS) {
        $scope.submitted = false;
        $scope.loading = false;

        /**
         * The initial profile retrieved from the server to know the dirty state.
         * @type {{}}
         */
        $scope.initialProfile = {};

        /**
         * Initializes the My profile page.
         * Update the profile if the user's profile has been stored.
         */
        $scope.init = function () {
            var retrieveProfileCallback = function () {
                $scope.profile = {};
                $scope.loading = true;
                gapi.client.conference.getProfile().
                    execute(function (resp) {
                        $scope.$apply(function () {
                            $scope.loading = false;
                            if (resp.error) {
                                // Failed to get a user profile.
                            } else {
                                // Succeeded to get the user profile.
                                $scope.profile.displayName = resp.result.displayName;
                                $scope.initialProfile = resp.result;
                            }
                        });
                    }
                );
            };
            if (!oauth2Provider.signedIn) {
                var modalInstance = oauth2Provider.showLoginModal();
                modalInstance.result.then(retrieveProfileCallback);
            } else {
                retrieveProfileCallback();
            }
        };

        /**
         * Invokes the conference.saveProfile API.
         *
         */
        $scope.saveProfile = function () {
            $scope.submitted = true;
            $scope.loading = true;
            gapi.client.conference.saveProfile($scope.profile).
                execute(function (resp) {
                    $scope.$apply(function () {
                        $scope.loading = false;
                        if (resp.error) {
                            // The request has failed.
                            var errorMessage = resp.error.message || '';
                            $scope.messages = 'Failed to update a profile : ' + errorMessage;
                            $scope.alertStatus = 'warning';
                            $log.error($scope.messages + 'Profile : ' + JSON.stringify($scope.profile));

                            if (resp.code && resp.code == HTTP_ERRORS.UNAUTHORIZED) {
                                oauth2Provider.showLoginModal();
                                return;
                            }
                        } else {
                            // The request has succeeded.
                            $scope.messages = 'The profile has been updated';
                            $scope.alertStatus = 'success';
                            $scope.submitted = false;
                            $scope.initialProfile = {
                                displayName: $scope.profile.displayName
                            };

                            $log.info($scope.messages + JSON.stringify(resp.result));
                        }
                    });
                });
        };

        $scope.pictureUpload = function(){
            //Hit the api
            //go into python
            //
        };

    });

/**
 * @ngdoc controller
 * @name RootCtrl
 *
 * @description
 * The root controller having a scope of the body element and methods used in the application wide
 * such as user authentications.
 *
 */
conferenceApp.controllers.controller('RootCtrl', function ($scope, $location,$log, oauth2Provider) {
    /**
     * Returns if the viewLocation is the currently viewed page.
     *
     * @param viewLocation
     * @returns {boolean} true if viewLocation is the currently viewed page. Returns false otherwise.
     */
    $scope.isActive = function (viewLocation) {
        return viewLocation === $location.path();
    };

    /**
     * Returns the OAuth2 signedIn state.
     *
     * @returns {oauth2Provider.signedIn|*} true if siendIn, false otherwise.
     */
    $scope.getSignedInState = function () {
        return oauth2Provider.signedIn;
    };

    /**
     * Calls the OAuth2 authentication method.
     */
    $scope.signIn = function () {
        oauth2Provider.signIn(function () {
            gapi.client.oauth2.userinfo.get().execute(function (resp) {
                $scope.$apply(function () {
                    if (resp.email) {
                        oauth2Provider.signedIn = true;
                        $scope.alertStatus = 'success';
                        $scope.rootMessages = 'Logged in with ' + resp.email;
                        //My addition to get to the dashboard and load items properly
                        $scope.makeProfile();
                        $location.path('/myDashboard').replace;
                    }
                });
            });
        });
    };

    $scope.makeProfile = function () {
        var retrieveProfileCallback = function () {
            $scope.profile = {};
            $scope.loading = true;
            gapi.client.conference.getProfile().
                execute(function (resp) {
                    $scope.$apply(function () {
                        $scope.loading = false;
                        if (resp.error) {
                            // Failed to get a user profile.
                        } else {
                            // Succeeded to get the user profile.
                            $scope.profile.displayName = resp.result.displayName;
                            $scope.initialProfile = resp.result;
                        }
                    });
                }
            );
        };
        if (!oauth2Provider.signedIn) {
            var modalInstance = oauth2Provider.showLoginModal();
            modalInstance.result.then(retrieveProfileCallback);
        } else {
            retrieveProfileCallback();
        }
    };

    /**
     * Render the signInButton and restore the credential if it's stored in the cookie.
     * (Just calling this to restore the credential from the stored cookie. So hiding the signInButton immediately
     *  after the rendering)
     */
    $scope.initSignInButton = function () {
        gapi.signin.render('signInButton', {
            'callback': function () {
                jQuery('#signInButton button').attr('disabled', 'true').css('cursor', 'default');
                if (gapi.auth.getToken() && gapi.auth.getToken().access_token) {
                    $scope.$apply(function () {
                        oauth2Provider.signedIn = true;
                    });
                }
            },
            'clientid': oauth2Provider.CLIENT_ID,
            'cookiepolicy': 'single_host_origin',
            'scope': oauth2Provider.SCOPES
        });
    };

    /**
     * Logs out the user.
     */
    $scope.signOut = function () {
        oauth2Provider.signOut();
        $scope.alertStatus = 'success';
        $scope.rootMessages = 'Logged out';
    };

    /**
     * Collapses the navbar on mobile devices.
     */
    $scope.collapseNavbar = function () {
        angular.element(document.querySelector('.navbar-collapse')).removeClass('in');
    };

});

/**
 * @ngdoc controller
 * @name OAuth2LoginModalCtrl
 *
 * @description
 * The controller for the modal dialog that is shown when an user needs to login to achive some functions.
 *
 */
conferenceApp.controllers.controller('OAuth2LoginModalCtrl',
    function ($scope, $modalInstance, $rootScope, oauth2Provider) {
        $scope.singInViaModal = function () {
            oauth2Provider.signIn(function () {
                gapi.client.oauth2.userinfo.get().execute(function (resp) {
                    $scope.$root.$apply(function () {
                        oauth2Provider.signedIn = true;
                        $scope.$root.alertStatus = 'success';
                        $scope.$root.rootMessages = 'Logged in with ' + resp.email;
                    });

                    $modalInstance.close();
                });
            });
        };
    });

/**
 * Method to show certain hangouts
 *
 */
conferenceApp.controllers.controller('HangoutCreationCtrl', function ($scope, $log){

    $scope.checked = $scope.checked || {};

    $scope.friendButton = function(hangoutForm) {
        /*
        $(document).ready(function() {
        var iCnt = 0;
        // CREATE A "DIV" ELEMENT AND DESIGN IT USING JQUERY ".css()" CLASS.
        var container = $(document.createElement('div')).css({
            padding: '5px', margin: '20px', width: '170px',
            borderTopColor: '#999', borderBottomColor: '#999',
            borderLeftColor: '#999', borderRightColor: '#999'
        });
        $('#btAdd').click(function() {
            if (iCnt <= 50) {
                iCnt = iCnt + 1;
                // ADD TEXTBOX.
                $(container).prepend('<input type=text class="input" id=tb' + iCnt + ' ' +
                            'ng-model="checked.friend' + iCnt + '" placeholder="Friend ' + iCnt +'"'+'required/>');

                if (iCnt == 100) {        // SHOW SUBMIT BUTTON IF ATLEAST "1" ELEMENT HAS BEEN CREATED.
                    var divSubmit = $(document.createElement('div'));
                    $(divSubmit).append('<input type=button class="bt" onclick="GetTextValue()"' + 
                            'id=btSubmit value=Submit />');   
                }
                $('#main').after(container, divSubmit);   // ADD BOTH THE DIV ELEMENTS TO THE "main" CONTAINER.
            }
            else {      // AFTER REACHING THE SPECIFIED LIMIT, DISABLE THE "ADD" BUTTON. (20 IS THE LIMIT WE HAVE SET)
                $(container).append('<label>Reached the limit</label>'); 
                $('#btAdd').attr('class', 'bt-disable'); 
                $('#btAdd').attr('disabled', 'disabled');
            }
        });
        $('#btRemove').click(function() {   // REMOVE ELEMENTS ONE PER CLICK.
            if (iCnt != 0) { $('#tb' + iCnt).remove(); iCnt = iCnt - 1; }
            if (iCnt == 0) { $(container).empty(); 
                $(container).remove(); 
                $('#btSubmit').remove(); 
                $('#btAdd').removeAttr('disabled'); 
                $('#btAdd').attr('class', 'bt') 
            }
        });
        $('#btRemoveAll').click(function() {    // REMOVE ALL THE ELEMENTS IN THE CONTAINER.
            $(container).empty(); 
            $(container).remove(); 
            $('#btSubmit').remove(); iCnt = 0; 
            $('#btAdd').removeAttr('disabled'); 
            $('#btAdd').attr('class', 'bt');
        });
    });

    // PICK THE VALUES FROM EACH TEXTBOX WHEN "SUBMIT" BUTTON IS CLICKED.
    var divValue, values = '';
    function GetTextValue() {
        $(divValue).empty(); 
        $(divValue).remove(); values = '';
        $('.input').each(function() {
            divValue = $(document.createElement('div')).css({
                padding:'5px', width:'200px'
            });
            values += this.value + '<br />'
        });
        $(divValue).append('<p><b>Your selected values</b></p>' + values);
        $('body').append(divValue);
    }*/
    };

    $scope.allOptionsChecked = function(hangoutForm) {
        if ($scope.checked.location && $scope.checked.time && $scope.checked.day) {
            return true;
        }
        return false;
    };

    $scope.locationTime = function(hangoutForm) {
        if ($scope.checked.location && $scope.checked.time && !$scope.checked.day) {
            return true;
        }
        return false;
    };

    $scope.locationDay = function(hangoutForm) {
        if ($scope.checked.location && $scope.checked.day && !$scope.checked.time) {
            return true;
        }
        return false;

    };

    $scope.timeDay = function(hangoutForm) {
        if ($scope.checked.time && $scope.checked.day && !$scope.checked.location){
            return true;
        }
        return false;
    };

    $scope.time = function(hangoutForm) {
        if ($scope.checked.time && !$scope.checked.day && !$scope.checked.location){
            return true;
        }
        return false;
    };
    
    $scope.day = function(hangoutForm) {
       if ($scope.checked.day && !$scope.checked.time && !$scope.checked.location){
        return true;
       }
       return false;
    };
    
    $scope.location = function(hangoutForm) {
       if ($scope.checked.location && !$scope.checked.day && !$scope.checked.time){
        return true;
       }
       return false;
    };

    $scope.createHangout = function (hangoutForm) {
        //Grab all the individual friends and put them into a list
        //Seems I need these entities as strings in order for it to work with the python model
        var friendList = [$scope.checked.friend1, $scope.checked.friend2, $scope.checked.friend3];
        $scope.checked.friendList = JSON.stringify(friendList);
        
        var userVote = [$scope.checked.option1, $scope.checked.option2, $scope.checked.option3];
        //Convert to integers
        var i;
        for(i=0; i<3; i++){
            userVote[i]=parseInt(userVote[i]);
        };
        $scope.checked.groupVoteRanks = JSON.stringify(userVote);

        gapi.client.conference.createHangout($scope.checked).
            execute(function(resp){
                $scope.$apply(function() {
                    if (resp.error){
                        $log.error('There was an Error Yo');
                    }
                    else {
                        $log.info("Success Bitch!");
                        $log.info(resp);
                        $log.info(resp.result);
                    }
                });
            });
    };

});

conferenceApp.controllers.controller('MyDashboardCtrl', function($scope,$log, $routeParams){
    $scope.invited = function () {
        //Check if in the backend he was invited and didn't vote
        /*
        if he was invited return Events
            Under true, showcase the resp of the gapi
        else return false
        */

        gapi.client.conference.invited().
            execute(function(resp){
                $scope.$apply(function() {
                    if (resp.error){
                        $log.error('There was an Error Yo');
                    }
                    else {
                        $log.info("Success Bitch!");
                        $scope.invitedHangouts = []
                        $scope.invitedHangout=[]
                        angular.forEach(resp.items, function(invitedHangout){
                            $scope.invitedHangouts.push(invitedHangout);
                        });
                    }
                });
            });

    };

    $scope.votedWaiting = function () {
        //Check if he voted and is waiting on the event
        /*
        if he was VotedandisWaiting return Events
            Under true, showcase the resp of the gapi
        else return false
        */

        gapi.client.conference.votedWaiting().
            execute(function(resp){
                $scope.$apply(function() {
                    if (resp.error){
                        $log.error('There was an Error Yo');
                    }
                    else {
                        $log.info("Success Bitch!");
                        $scope.hangouts = []
                        $scope.hangout=[]
                        angular.forEach(resp.items, function(hangout){
                            $scope.hangouts.push(hangout);
                        });
                    }
                });
            });
    };

    $scope.done = function () {
        /*
        if he was invited return Events
            Under true, showcase the resp of the gapi
        else return false
        */

        //Same as invited or voteWaiting
        //Get the results and just display the information details across the page
        gapi.client.conference.done().
            execute(function(resp){
                $scope.$apply(function() {
                    if (resp.error){
                        $log.error('There was an Error Yo');
                    }
                    else {
                        $log.info("Success Bitch!");
                        $scope.doneHangouts = []
                        $scope.doneHangout=[]
                        angular.forEach(resp.items, function(doneHangout){
                            $scope.doneHangouts.push(doneHangout);
                        });
                    }
                });
            });
    };

});

conferenceApp.controllers.controller('RegLogsCtrl', function($scope,$log,$location){
    /*
    Get the models for registration

    send through the api and see if it has been created. if not send a reply
    back that user already exists and try another login.
    */

    //Set the global variable
    //Run encryption or do a put here. Security issue.
    $scope.regLogInfo = $scope.regLogInfo || {};

    $scope.emailRegistration = function(registrationForm){

        //Api hit to register and save

        /*
            If email is able to save then
                save the data and direct to the dashboard
                Then trigger the signedIn state to true change the navbar
                oauth2Provider.signedIn = True
                //$location.path('/myDashboard').replace;
            if not able to save, then redirect back to the registration page.
                I think release the lock where it shows javascript that you need to change password
        */
        $log.info($scope.regLogInfo)

        gapi.client.conference.emailRegistration($scope.regLogInfo).
            execute(function(resp){
                $scope.$apply(function() {
                    if (resp.error){
                        $log.error('There was an Error Yo');
                    }
                    else {
                        $log.info("Success Bitch!");
                    }
            });
        });
    };


});

conferenceApp.controllers.controller('VoteCtrl', function($scope,$log,$routeParams){

    $scope.votes = $scope.votes || {};

    $scope.vote = function(voteForm){
        $scope.votes.webSafeKey = $routeParams.webSafeKey

        gapi.client.conference.vote($scope.votes).
                execute(function(resp){
                    $scope.$apply(function() {
                        if (resp.error){
                            $log.error('There was an Error Yo');
                        }
                        else {
                            $log.info("Success Bitch!");
                            $log.info($scope.votes);
                            //send back to the dashboard. Use the location
                        }
                    });
                });
    };

});

conferenceApp.controllers.controller('ResultsCtrl', function($scope, $log, $routeParams){
        
        $scope.bardata = $scope.bardata || {};
        $scope.names = $scope.names || {};

        $scope.d3j = function () {
            var bardata = $scope.bardata;
            var names = ['Hangout1', 'Hangout2', 'Hangout3'];

            var height = 200,
                width = 400,
                barWidth = 50,
                barOffset = 5;

            var yScale = d3.scale.linear()
                    .domain([0, d3.max(bardata)])
                    .range([0, height])

            var xScale = d3.scale.ordinal()
                    .domain(d3.range(0, bardata.length))
                    .rangeBands([0,width])
            /*
            var tooltip = d3.select('body').append('div')
                    .style('position', 'absolute')
                    .style('padding', '0 10px')
                    .style('background', 'white')
                    .style('opacity', .9)
            */
            var myChart = d3.select('#chart').append('svg')
                    .attr('width', width)
                    .attr('height', height)
                    .selectAll('rect').data(bardata)
                    .enter().append('rect')
                        .style('fill', '#C61C6F')
                        .attr('width', xScale.rangeBand())
                        .attr('x', function(d,i) {
                            return xScale(i);
                        })
                        .attr('height', 0)
                        .attr('y', height)
                        /*
                        .on('mouseover', function(d) {

                            tooltip.transition()
                                .style('opacity', .9)

                            tooltip.html(d)
                                .style('left', (d3.event.pageX - 35) + 'px')
                                .style('top', (d3.event.pageY - 30) + 'px')

                            d3.select(this)
                                .style('opacity', .5)
                        })
                        */
                        .on('mouseout', function(d) {

                            d3.select(this)
                                .style('opacity', 1)
                        })

            myChart.transition()
                    .attr('height', function(d) {
                        return yScale(d);
                    })
                    .attr('y', function(d) {
                        return height - yScale(d);
                    })
                    .delay(function(d, i) {
                        return i * 80;
                    })

            myChart.select('svg')
                .data(bardata)
                .enter().append('text')
                .style('fill', 'black')
                .attr('x', function(d,i) {
                            return xScale(i);
                        })
                .attr('y', function(d) {
                        return height - yScale(d) + 9;
                    })
                .attr('height', function(d) {
                        return yScale(d);
                    })
                .attr('dy', '.35em')
                .attr('dx', '1.5em')
                .attr('font-size', '10px')
                .attr('font-family', 'sans-serif')
                .data(names)
                .text(function(d) { return d; });

            };

            /*DEPRECATED NOT NEEDED

            $scope.truthy = function () {
                return $scope.truthValue;
            };
        
            $scope.stillVoting = function () {
            
            gapi.client.conference.stillVoting({
                webSafeKey: $routeParams.webSafeKey
            }).
                execute(function(resp){
                    $scope.$apply(function() {
                        if (resp.error){
                            $log.error('There was an Error Yo');
                        }
                        else {
                            $log.info("Success Bitch!");
                            $log.info(resp.data);
                            $scope.truthValue = resp.data
                            //or parse resp.items here and set a new $scope variable    
                        }
                    });
                });

    };*/

        $scope.getResultsWaiting = function () {

        gapi.client.conference.getResultsWaiting({
            webSafeKey: $routeParams.webSafeKey
        }).
            execute(function(resp){
                $scope.$apply(function() {
                    if (resp.error){
                        $log.error('There was an Error Yo');
                    }
                    else {
                        $log.info("Success Bitch!");
                        $scope.results = []
                        $scope.result=[]
                        angular.forEach(resp.items, function(result){
                            $scope.results.push(result);
                        });
                        $scope.bardata = JSON.parse(resp.items[0]['finalResults']);
                        $log.info(resp.items[0]);
                        $scope.d3j();
                        //or parse resp.items here and set a new $scope variable
                        //friends
                        //Need Logic to get friends who's ranks are added.
                        var notVotedFriends=[];
                        var votedFriends=[];
                        var s, friends = JSON.parse(resp.items[0]['friendList']);
                        var iterFriends = Object.keys(friends)

                        for(s of iterFriends){
                        if (friends[s]['voteRank'][0]==0){
                            notVotedFriends.push(s);
                        }
                        else{
                            votedFriends.push(s);
                        }
                        };

                        //THOSE THAT DID NOT VOTE
                        $scope.friends = []
                        $scope.friend=[]
                        angular.forEach(notVotedFriends, function(friend){
                            $scope.friends.push(friend);
                        });
                        
                        //THOSE THAT DID VOTE
                        $scope.vFriends = []
                        $scope.vFriend=[]
                        angular.forEach(votedFriends, function(vFriend){
                            $scope.vFriends.push(vFriend);
                        });

                        //post process items (correct Date Structure)
                        //post process itesm (correct Time (am or pm))
                    }
                });
            });
    };

        $scope.getResultsFinal = function () {
        gapi.client.conference.getResultsFinal({
            webSafeKey: $routeParams.webSafeKey
        }).
            execute(function(resp){
                $scope.$apply(function() {
                    if (resp.error){
                        $log.error('There was an Error Yo');
                    }
                    else {
                        $log.info("Success Bitch!");
                        $scope.results = []
                        $scope.result=[]
                        angular.forEach(resp.items, function(result){
                            $scope.results.push(result);
                        });
                        $scope.bardata = JSON.parse(resp.items[0]['finalResults']);
                        $scope.d3j();

                        $log.info($scope.results);
                        var event1=[
                                    {"date1":resp.items[0]['date1'], 
                                    "time1":resp.items[0]['time1'],
                                    "locationName1": resp.items[0]['locationName1'],
                                    "address1": resp.items[0]['address1']
                                    }
                                    ];

                        var event2=[
                                    {"date2":resp.items[0]['date2'], 
                                    "time2":resp.items[0]['time2'],
                                    "locationName2": resp.items[0]['locationName2'],
                                    "address2": resp.items[0]['address2']
                                    }
                                    ];

                        var event3=[
                                    {"date3":resp.items[0]['date3'], 
                                    "time3":resp.items[0]['time3'],
                                    "locationName3": resp.items[0]['locationName3'],
                                    "address3": resp.items[0]['address3']
                                    }
                                    ];

                        //display the winner Event information
                        $log.info($scope.bardata);
                        var finalResults = $scope.bardata
                        var winnerVal = Math.max.apply(null, $scope.bardata);
                        var winnerOptionNum = finalResults.indexOf(winnerVal);

                        //BUGS OUT ON else if statement and don't know why right now
                        if (winnerOptionNum == 0) {
                            $scope.firstResults = []
                            $scope.firstResult=[]
                            angular.forEach(event1, function(firstResult){
                                $scope.firstResults.push(firstResult);
                            });
                        }
                        else {

                        }
                        if (winnerOptionNum == 1) {
                            $scope.firstResults = []
                            $scope.firstResult=[]
                            angular.forEach(event2, function(firstResult){
                                $scope.firstResults.push(firstResult);
                            });
                        }
                        else {

                        } 
                        if (winnerOptionNum == 2) {
                            $scope.firstResults = []
                            $scope.firstResult=[]
                            angular.forEach(event3, function(firstResult){
                                $scope.firstResults.push(firstResult);
                            });
                        }
                        else {

                        }

                        var friends = JSON.parse(resp.items[0]['friendList']);
                        var s, friendList = Object.keys(friends);
                        var going=[];
                        var maybeGoing=[];
                        var notGoing=[];

                        //display Those going (first choice)
                        for(s of friendList){
                            if (friends[s]['confirmation'] == 1){
                                going.push(s);
                            }
                            else{
                                maybeGoing.push(s);
                            }
                        }

                        $scope.prefereds = []
                        $scope.prefer=[]
                        angular.forEach(going, function(prefer){
                            $scope.prefereds.push(prefer);
                        });

                        $scope.mays = []
                        $scope.may=[]
                        angular.forEach(maybeGoing, function(may){
                            $scope.mays.push(may);
                        });


                        //display Maybe

                        //display those definitely not
                    }
                });
            });

        };
    
});

conferenceApp.controllers.controller('ShowAllCtrl', function($scope, $log) {
 
    $scope.getHangoutsMade = function() {
            gapi.client.conference.getHangoutsMade().
                execute(function (resp) {
                    $scope.$apply(function(){
                        if(resp.error) {
                            $scope.message = 'Error Boss';
                            $log.error($scope.message);

                        } else {
                            $scope.message = 'Success Boss';
                            $log.info($scope.message);
                            $scope.mades = []
                            $scope.made=[]
                        angular.forEach(resp.items, function(made){
                            $scope.mades.push(made);
                        });
                        }
                    });

                });
        };

    $scope.getHangoutsInProgress = function() {
            gapi.client.conference.getHangoutsInProgress().
                execute(function (resp) {
                    $scope.$apply(function(){
                        if(resp.error) {
                            $scope.message = 'Error Boss';
                            $log.error($scope.message);

                        } else {
                            $scope.message = 'Success Boss';
                            $log.info($scope.message);
                            $scope.votes = []
                            $scope.vote=[]
                        angular.forEach(resp.items, function(vote){
                            $scope.votes.push(vote);
                        });
                        }
                    });

                });
        };
});
